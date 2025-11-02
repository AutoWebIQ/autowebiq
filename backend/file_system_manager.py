# File System Manager for AutoWebIQ Workspaces
# Handles file operations within user workspaces

import os
import json
from typing import Dict, List, Optional
from pathlib import Path
import mimetypes

class FileSystemManager:
    """
    Manages file operations within workspace directories.
    Provides safe file access with path validation.
    """
    
    def __init__(self, base_path: str = "/tmp/workspaces"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def _get_workspace_path(self, user_id: str, project_id: str) -> Path:
        """Get and validate workspace path"""
        workspace_path = Path(self.base_path) / user_id / project_id
        return workspace_path
    
    def _validate_path(self, workspace_path: Path, file_path: str) -> Path:
        """Validate that file path is within workspace"""
        full_path = (workspace_path / file_path).resolve()
        
        # Security: Ensure path is within workspace
        if not str(full_path).startswith(str(workspace_path.resolve())):
            raise ValueError("Invalid file path: outside workspace")
        
        return full_path
    
    async def read_file(
        self, 
        user_id: str, 
        project_id: str, 
        file_path: str
    ) -> Dict:
        """
        Read a file from workspace.
        
        Returns:
            {
                "status": "success" | "error",
                "content": str,
                "encoding": str,
                "size": int,
                "mime_type": str
            }
        """
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            full_path = self._validate_path(workspace_path, file_path)
            
            if not full_path.exists():
                return {
                    "status": "error",
                    "message": "File not found"
                }
            
            if not full_path.is_file():
                return {
                    "status": "error",
                    "message": "Path is not a file"
                }
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(str(full_path))
            
            # Read file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "status": "success",
                "content": content,
                "encoding": "utf-8",
                "size": full_path.stat().st_size,
                "mime_type": mime_type or "text/plain"
            }
            
        except UnicodeDecodeError:
            # Try reading as binary
            with open(full_path, 'rb') as f:
                content = f.read()
            
            return {
                "status": "success",
                "content": content.hex(),  # Return hex for binary files
                "encoding": "binary",
                "size": full_path.stat().st_size,
                "mime_type": mime_type or "application/octet-stream"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read file: {str(e)}"
            }
    
    async def write_file(
        self,
        user_id: str,
        project_id: str,
        file_path: str,
        content: str
    ) -> Dict:
        """
        Write content to a file in workspace.
        Creates parent directories if needed.
        """
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            full_path = self._validate_path(workspace_path, file_path)
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": "File saved successfully",
                "size": full_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to write file: {str(e)}"
            }
    
    async def delete_file(
        self,
        user_id: str,
        project_id: str,
        file_path: str
    ) -> Dict:
        """Delete a file from workspace"""
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            full_path = self._validate_path(workspace_path, file_path)
            
            if not full_path.exists():
                return {
                    "status": "error",
                    "message": "File not found"
                }
            
            if full_path.is_file():
                full_path.unlink()
            elif full_path.is_dir():
                import shutil
                shutil.rmtree(full_path)
            
            return {
                "status": "success",
                "message": "File deleted successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete file: {str(e)}"
            }
    
    async def list_directory(
        self,
        user_id: str,
        project_id: str,
        directory_path: str = ""
    ) -> Dict:
        """
        List contents of a directory.
        
        Returns:
            {
                "status": "success",
                "files": List[{
                    "name": str,
                    "path": str,
                    "type": "file" | "directory",
                    "size": int,
                    "modified": str
                }]
            }
        """
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            full_path = self._validate_path(workspace_path, directory_path)
            
            if not full_path.exists():
                return {
                    "status": "error",
                    "message": "Directory not found"
                }
            
            if not full_path.is_dir():
                return {
                    "status": "error",
                    "message": "Path is not a directory"
                }
            
            files = []
            for item in full_path.iterdir():
                relative_path = item.relative_to(workspace_path)
                
                file_info = {
                    "name": item.name,
                    "path": str(relative_path),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": item.stat().st_mtime
                }
                files.append(file_info)
            
            # Sort: directories first, then files alphabetically
            files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            return {
                "status": "success",
                "files": files
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list directory: {str(e)}"
            }
    
    async def create_directory(
        self,
        user_id: str,
        project_id: str,
        directory_path: str
    ) -> Dict:
        """Create a new directory"""
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            full_path = self._validate_path(workspace_path, directory_path)
            
            full_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "status": "success",
                "message": "Directory created successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create directory: {str(e)}"
            }
    
    async def get_file_tree(
        self,
        user_id: str,
        project_id: str,
        max_depth: int = 5
    ) -> Dict:
        """
        Get complete file tree structure.
        
        Returns nested structure for file explorer UI.
        """
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            
            if not workspace_path.exists():
                return {
                    "status": "error",
                    "message": "Workspace not found"
                }
            
            def build_tree(path: Path, current_depth: int = 0) -> Dict:
                """Recursively build file tree"""
                if current_depth >= max_depth:
                    return None
                
                relative_path = path.relative_to(workspace_path)
                
                node = {
                    "name": path.name if path != workspace_path else "root",
                    "path": str(relative_path) if path != workspace_path else "",
                    "type": "directory" if path.is_dir() else "file"
                }
                
                if path.is_file():
                    node["size"] = path.stat().st_size
                    node["extension"] = path.suffix
                elif path.is_dir():
                    node["children"] = []
                    try:
                        for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                            # Skip hidden files and common ignore patterns
                            if item.name.startswith('.') or item.name in ['node_modules', '__pycache__', 'venv', 'dist', 'build']:
                                continue
                            
                            child = build_tree(item, current_depth + 1)
                            if child:
                                node["children"].append(child)
                    except PermissionError:
                        pass
                
                return node
            
            tree = build_tree(workspace_path)
            
            return {
                "status": "success",
                "tree": tree
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to build file tree: {str(e)}"
            }
    
    async def search_files(
        self,
        user_id: str,
        project_id: str,
        query: str,
        file_pattern: str = "*"
    ) -> Dict:
        """
        Search for files matching pattern.
        """
        try:
            workspace_path = self._get_workspace_path(user_id, project_id)
            
            if not workspace_path.exists():
                return {
                    "status": "error",
                    "message": "Workspace not found"
                }
            
            results = []
            
            for file_path in workspace_path.rglob(file_pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(workspace_path)
                    
                    # Skip ignored directories
                    if any(part in ['node_modules', '__pycache__', 'venv', '.git'] for part in relative_path.parts):
                        continue
                    
                    # Check if filename matches query
                    if query.lower() in file_path.name.lower():
                        results.append({
                            "name": file_path.name,
                            "path": str(relative_path),
                            "size": file_path.stat().st_size
                        })
            
            return {
                "status": "success",
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to search files: {str(e)}"
            }


# Singleton instance
_fs_manager = None

def get_file_system_manager() -> FileSystemManager:
    """Get or create singleton file system manager"""
    global _fs_manager
    if _fs_manager is None:
        _fs_manager = FileSystemManager()
    return _fs_manager
