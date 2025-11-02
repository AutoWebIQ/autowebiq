# Iterative Chat Manager for AutoWebIQ
# Handles conversational development with context memory

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import json
from model_router import get_model_router
from file_system_manager import get_file_system_manager

class ConversationContext:
    """Manages conversation context for iterative development"""
    
    def __init__(self, project_id: str, user_id: str):
        self.project_id = project_id
        self.user_id = user_id
        self.messages: List[Dict] = []
        self.project_state: Dict = {}
        self.file_history: List[Dict] = []
        self.created_at = datetime.utcnow()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
    
    def get_context_summary(self, last_n: int = 10) -> str:
        """Get summary of recent conversation"""
        recent = self.messages[-last_n:]
        summary = []
        
        for msg in recent:
            role = msg["role"]
            content = msg["content"][:200]  # Truncate long messages
            summary.append(f"{role}: {content}")
        
        return "\n".join(summary)
    
    def update_project_state(self, state: Dict):
        """Update current project state"""
        self.project_state.update(state)
        self.project_state["updated_at"] = datetime.utcnow().isoformat()


class IterativeChatManager:
    """
    Manages iterative chat sessions with context awareness.
    Enables users to refine their applications conversationally.
    """
    
    def __init__(self):
        self.router = get_model_router()
        self.fs_manager = get_file_system_manager()
        self.contexts: Dict[str, ConversationContext] = {}
    
    def get_or_create_context(self, project_id: str, user_id: str) -> ConversationContext:
        """Get or create conversation context for a project"""
        key = f"{user_id}_{project_id}"
        
        if key not in self.contexts:
            self.contexts[key] = ConversationContext(project_id, user_id)
        
        return self.contexts[key]
    
    async def process_iterative_request(
        self,
        project_id: str,
        user_id: str,
        message: str,
        db
    ) -> Dict:
        """
        Process an iterative chat request.
        
        User can say things like:
        - "Make the button blue"
        - "Add a login form"
        - "Change the API endpoint to use POST"
        - "Fix the responsive design on mobile"
        
        The system understands context and makes precise changes.
        """
        context = self.get_or_create_context(project_id, user_id)
        
        # Add user message to context
        context.add_message("user", message)
        
        try:
            # Get project from database
            project = await db.projects.find_one({"id": project_id, "user_id": user_id})
            if not project:
                return {
                    "status": "error",
                    "message": "Project not found"
                }
            
            # Get current project files
            files = await self._get_project_files(project_id, user_id)
            
            # Update context with current state
            context.update_project_state({
                "files": list(files.keys()),
                "file_count": len(files),
                "has_frontend": any("frontend" in f for f in files.keys()),
                "has_backend": any("backend" in f for f in files.keys())
            })
            
            # Analyze the request and determine action
            action = await self._analyze_request(message, context, files)
            
            if action["type"] == "modify_files":
                # Modify specific files
                result = await self._modify_files(
                    project_id,
                    user_id,
                    message,
                    action["files_to_modify"],
                    files,
                    context
                )
                
                # Add assistant response to context
                context.add_message(
                    "assistant",
                    result["message"],
                    {"changes": result.get("changes", [])}
                )
                
                return result
            
            elif action["type"] == "generate_new":
                # Generate new files/features
                result = await self._generate_new_feature(
                    project_id,
                    user_id,
                    message,
                    files,
                    context
                )
                
                context.add_message(
                    "assistant",
                    result["message"],
                    {"new_files": result.get("new_files", [])}
                )
                
                return result
            
            elif action["type"] == "clarification_needed":
                # Need more info from user
                clarification = await self._generate_clarification(message, context)
                
                context.add_message("assistant", clarification)
                
                return {
                    "status": "clarification_needed",
                    "message": clarification
                }
            
            else:
                # General response
                response = await self._generate_response(message, context)
                
                context.add_message("assistant", response)
                
                return {
                    "status": "success",
                    "message": response,
                    "action": "response"
                }
        
        except Exception as e:
            error_msg = f"Failed to process request: {str(e)}"
            context.add_message("assistant", error_msg, {"error": True})
            
            return {
                "status": "error",
                "message": error_msg
            }
    
    async def _get_project_files(self, project_id: str, user_id: str) -> Dict[str, str]:
        """Get all current project files"""
        files = {}
        
        # Get file tree
        tree_result = await self.fs_manager.get_file_tree(user_id, project_id)
        
        if tree_result["status"] == "success":
            # Recursively collect all files
            async def collect_files(node, current_path=""):
                if node["type"] == "file":
                    file_path = node["path"]
                    file_result = await self.fs_manager.read_file(user_id, project_id, file_path)
                    if file_result["status"] == "success":
                        files[file_path] = file_result["content"]
                elif node["type"] == "directory" and "children" in node:
                    for child in node["children"]:
                        await collect_files(child, current_path)
            
            await collect_files(tree_result["tree"])
        
        return files
    
    async def _analyze_request(
        self,
        message: str,
        context: ConversationContext,
        files: Dict[str, str]
    ) -> Dict:
        """
        Analyze user request to determine action type.
        
        Returns:
            {
                "type": "modify_files" | "generate_new" | "clarification_needed" | "general",
                "files_to_modify": List[str],
                "confidence": float
            }
        """
        # Use Gemini for analysis (good at understanding context)
        system_message = """You are an expert at understanding developer requests.
Analyze the user's message and determine what they want to do.

Return ONLY a JSON object:
{
  "type": "modify_files" | "generate_new" | "clarification_needed" | "general",
  "reasoning": "why this classification",
  "files_to_modify": ["list of files if type is modify_files"],
  "confidence": 0.0-1.0
}

Types:
- modify_files: User wants to change existing files
- generate_new: User wants new features/files
- clarification_needed: Need more information
- general: General question/discussion"""

        conversation_summary = context.get_context_summary()
        available_files = "\n".join(files.keys())
        
        prompt = f"""User request: "{message}"

Recent conversation:
{conversation_summary}

Available files:
{available_files}

Project state:
- Files: {len(files)}
- Frontend: {context.project_state.get('has_frontend', False)}
- Backend: {context.project_state.get('has_backend', False)}

Analyze this request and classify it."""

        try:
            response = await self.router.generate_completion(
                task_type="content",
                prompt=prompt,
                system_message=system_message,
                session_id=f"analyze_{context.project_id}_{datetime.utcnow().timestamp()}"
            )
            
            # Extract JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
        
        except Exception as e:
            print(f"Analysis failed: {e}")
        
        # Fallback to simple keyword matching
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["change", "modify", "update", "fix", "make", "edit"]):
            return {
                "type": "modify_files",
                "files_to_modify": list(files.keys())[:3],  # Guess first 3 files
                "confidence": 0.5
            }
        elif any(word in message_lower for word in ["add", "create", "new", "generate"]):
            return {
                "type": "generate_new",
                "confidence": 0.5
            }
        else:
            return {
                "type": "general",
                "confidence": 0.3
            }
    
    async def _modify_files(
        self,
        project_id: str,
        user_id: str,
        request: str,
        files_to_modify: List[str],
        current_files: Dict[str, str],
        context: ConversationContext
    ) -> Dict:
        """
        Modify specific files based on user request.
        Uses Claude Sonnet 4 for code modifications.
        """
        changes = []
        
        for file_path in files_to_modify:
            if file_path not in current_files:
                continue
            
            current_content = current_files[file_path]
            file_type = self._detect_file_type(file_path)
            
            # Use appropriate model based on file type
            if file_type == "frontend":
                task_type = "frontend"  # Claude
            elif file_type == "backend":
                task_type = "backend"   # GPT
            else:
                task_type = "content"   # Gemini
            
            system_message = f"""You are an expert developer. Modify the given file based on the user's request.

CRITICAL RULES:
1. Return ONLY the complete modified file content
2. Preserve all existing functionality unless specifically asked to change
3. Maintain code style and formatting
4. Add comments for significant changes
5. Ensure the changes are minimal and focused

Current file: {file_path}"""

            conversation_context = context.get_context_summary(last_n=5)
            
            prompt = f"""User request: "{request}"

Recent context:
{conversation_context}

Current file content:
```
{current_content}
```

Modify this file to fulfill the user's request. Return the complete modified file."""

            try:
                modified_content = await self.router.generate_completion(
                    task_type=task_type,
                    prompt=prompt,
                    system_message=system_message,
                    session_id=f"modify_{project_id}_{datetime.utcnow().timestamp()}"
                )
                
                # Clean up response (remove markdown code blocks)
                import re
                modified_content = re.sub(r'^```[a-z]*\n', '', modified_content, flags=re.MULTILINE)
                modified_content = re.sub(r'\n```$', '', modified_content, flags=re.MULTILINE)
                
                # Write modified file
                write_result = await self.fs_manager.write_file(
                    user_id,
                    project_id,
                    file_path,
                    modified_content
                )
                
                if write_result["status"] == "success":
                    changes.append({
                        "file": file_path,
                        "action": "modified",
                        "size": write_result.get("size", 0)
                    })
                    
                    # Track in history
                    context.file_history.append({
                        "file": file_path,
                        "action": "modified",
                        "timestamp": datetime.utcnow().isoformat(),
                        "request": request
                    })
            
            except Exception as e:
                print(f"Failed to modify {file_path}: {e}")
                changes.append({
                    "file": file_path,
                    "action": "failed",
                    "error": str(e)
                })
        
        if changes:
            files_changed = [c["file"] for c in changes if c["action"] == "modified"]
            message = f"✅ Modified {len(files_changed)} file(s):\n" + "\n".join(f"• {f}" for f in files_changed)
            
            return {
                "status": "success",
                "message": message,
                "changes": changes,
                "action": "modify_files"
            }
        else:
            return {
                "status": "error",
                "message": "No files were modified"
            }
    
    async def _generate_new_feature(
        self,
        project_id: str,
        user_id: str,
        request: str,
        existing_files: Dict[str, str],
        context: ConversationContext
    ) -> Dict:
        """Generate new files/features"""
        # Use appropriate agent based on request
        # For now, simplified implementation
        
        system_message = """You are an expert developer. Generate new code based on the user's request.
Return file paths and their contents as JSON:

{
  "files": {
    "path/to/file.ext": "file content here",
    "another/file.ext": "content"
  },
  "description": "What was created"
}"""

        existing_structure = "\n".join(existing_files.keys())
        conversation_context = context.get_context_summary(last_n=5)
        
        prompt = f"""User request: "{request}"

Recent context:
{conversation_context}

Existing project structure:
{existing_structure}

Generate new files to fulfill this request. Return as JSON."""

        try:
            response = await self.router.generate_completion(
                task_type="backend",  # GPT for technical generation
                prompt=prompt,
                system_message=system_message,
                session_id=f"generate_{project_id}_{datetime.utcnow().timestamp()}"
            )
            
            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                new_files = result.get("files", {})
                
                # Write new files
                created = []
                for file_path, content in new_files.items():
                    write_result = await self.fs_manager.write_file(
                        user_id,
                        project_id,
                        file_path,
                        content
                    )
                    
                    if write_result["status"] == "success":
                        created.append(file_path)
                
                return {
                    "status": "success",
                    "message": f"✅ Created {len(created)} new file(s):\n" + "\n".join(f"• {f}" for f in created),
                    "new_files": created,
                    "action": "generate_new"
                }
        
        except Exception as e:
            print(f"Generation failed: {e}")
        
        return {
            "status": "error",
            "message": "Failed to generate new files"
        }
    
    async def _generate_clarification(self, message: str, context: ConversationContext) -> str:
        """Generate clarifying questions"""
        system_message = """You are a helpful AI assistant. The user's request is unclear.
Generate 2-3 specific clarifying questions to better understand what they want."""

        prompt = f"""User request: "{message}"

Project context:
- Files: {len(context.project_state.get('files', []))}
- Has frontend: {context.project_state.get('has_frontend', False)}
- Has backend: {context.project_state.get('has_backend', False)}

Ask clarifying questions to understand their request better."""

        response = await self.router.generate_completion(
            task_type="content",
            prompt=prompt,
            system_message=system_message,
            session_id=f"clarify_{context.project_id}"
        )
        
        return response
    
    async def _generate_response(self, message: str, context: ConversationContext) -> str:
        """Generate a general response"""
        system_message = """You are a helpful AI development assistant.
Answer the user's question or engage in conversation about their project."""

        conversation_context = context.get_context_summary()
        
        prompt = f"""User: "{message}"

Recent conversation:
{conversation_context}

Project state:
{json.dumps(context.project_state, indent=2)}

Respond helpfully."""

        response = await self.router.generate_completion(
            task_type="content",
            prompt=prompt,
            system_message=system_message,
            session_id=f"chat_{context.project_id}"
        )
        
        return response
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type from path"""
        if any(x in file_path for x in ["frontend", "src", "components", ".jsx", ".tsx", ".vue"]):
            return "frontend"
        elif any(x in file_path for x in ["backend", "api", "routes", ".py", "main.py"]):
            return "backend"
        elif any(x in file_path for x in ["test", "spec", ".test."]):
            return "test"
        else:
            return "other"
    
    async def get_conversation_history(self, project_id: str, user_id: str) -> List[Dict]:
        """Get full conversation history"""
        context = self.get_or_create_context(project_id, user_id)
        return context.messages
    
    async def clear_context(self, project_id: str, user_id: str):
        """Clear conversation context"""
        key = f"{user_id}_{project_id}"
        if key in self.contexts:
            del self.contexts[key]


# Singleton instance
_chat_manager = None

def get_iterative_chat_manager() -> IterativeChatManager:
    """Get or create singleton chat manager"""
    global _chat_manager
    if _chat_manager is None:
        _chat_manager = IterativeChatManager()
    return _chat_manager
