# Git Integration Manager for AutoWebIQ
# Handles git operations and GitHub integration

import os
import subprocess
from typing import Dict, List, Optional
from datetime import datetime
import requests
from pathlib import Path

class GitManager:
    """
    Manages Git operations for workspace projects.
    Supports commit, push, pull, branches, and GitHub integration.
    """
    
    def __init__(self):
        self.github_api = "https://api.github.com"
    
    async def init_repository(
        self,
        workspace_path: str,
        user_name: str = "AutoWebIQ User",
        user_email: str = "user@autowebiq.com"
    ) -> Dict:
        """
        Initialize git repository in workspace.
        
        Args:
            workspace_path: Path to workspace directory
            user_name: Git user name
            user_email: Git user email
        """
        try:
            # Check if git is already initialized
            git_dir = os.path.join(workspace_path, '.git')
            if os.path.exists(git_dir):
                return {
                    "status": "success",
                    "message": "Git repository already initialized"
                }
            
            # Initialize git
            subprocess.run(
                ["git", "init"],
                cwd=workspace_path,
                check=True,
                capture_output=True
            )
            
            # Configure user
            subprocess.run(
                ["git", "config", "user.name", user_name],
                cwd=workspace_path,
                check=True
            )
            
            subprocess.run(
                ["git", "config", "user.email", user_email],
                cwd=workspace_path,
                check=True
            )
            
            # Create initial .gitignore
            gitignore_content = """# Dependencies
node_modules/
venv/
__pycache__/

# Environment
.env
.env.local

# Build
dist/
build/
*.pyc

# IDE
.vscode/
.idea/

# Logs
*.log
"""
            gitignore_path = os.path.join(workspace_path, '.gitignore')
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            
            return {
                "status": "success",
                "message": "Git repository initialized successfully"
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git init failed: {e.stderr.decode() if e.stderr else str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize git: {str(e)}"
            }
    
    async def get_status(self, workspace_path: str) -> Dict:
        """
        Get git status.
        
        Returns:
            {
                "status": "success",
                "branch": str,
                "modified": List[str],
                "untracked": List[str],
                "staged": List[str]
            }
        """
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            branch = branch_result.stdout.strip() or "main"
            
            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            modified = []
            untracked = []
            staged = []
            
            for line in status_result.stdout.split('\n'):
                if not line:
                    continue
                
                status = line[:2]
                filename = line[3:]
                
                if status[0] in ['M', 'A', 'D', 'R']:
                    staged.append(filename)
                if status[1] == 'M':
                    modified.append(filename)
                if status == '??':
                    untracked.append(filename)
            
            return {
                "status": "success",
                "branch": branch,
                "modified": modified,
                "untracked": untracked,
                "staged": staged,
                "clean": len(modified) == 0 and len(untracked) == 0 and len(staged) == 0
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git status failed: {e.stderr if e.stderr else str(e)}"
            }
    
    async def stage_files(
        self,
        workspace_path: str,
        files: Optional[List[str]] = None
    ) -> Dict:
        """
        Stage files for commit.
        
        Args:
            workspace_path: Path to workspace
            files: List of file paths to stage, or None to stage all
        """
        try:
            if files is None or len(files) == 0:
                # Stage all files
                subprocess.run(
                    ["git", "add", "."],
                    cwd=workspace_path,
                    check=True,
                    capture_output=True
                )
                message = "All files staged"
            else:
                # Stage specific files
                subprocess.run(
                    ["git", "add"] + files,
                    cwd=workspace_path,
                    check=True,
                    capture_output=True
                )
                message = f"Staged {len(files)} file(s)"
            
            return {
                "status": "success",
                "message": message
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git add failed: {e.stderr.decode() if e.stderr else str(e)}"
            }
    
    async def commit(
        self,
        workspace_path: str,
        message: str,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None
    ) -> Dict:
        """
        Create a git commit.
        
        Args:
            workspace_path: Path to workspace
            message: Commit message
            author_name: Optional author name
            author_email: Optional author email
        """
        try:
            cmd = ["git", "commit", "-m", message]
            
            if author_name and author_email:
                cmd.extend(["--author", f"{author_name} <{author_email}>"])
            
            result = subprocess.run(
                cmd,
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "success",
                "message": "Committed successfully",
                "output": result.stdout
            }
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            
            if "nothing to commit" in error_msg:
                return {
                    "status": "info",
                    "message": "Nothing to commit, working tree clean"
                }
            
            return {
                "status": "error",
                "message": f"Git commit failed: {error_msg}"
            }
    
    async def get_commit_history(
        self,
        workspace_path: str,
        limit: int = 10
    ) -> Dict:
        """
        Get commit history.
        
        Returns list of commits with hash, author, date, message
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ae|%ad|%s"],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
            
            return {
                "status": "success",
                "commits": commits
            }
        
        except subprocess.CalledProcessError:
            return {
                "status": "success",
                "commits": []  # No commits yet
            }
    
    async def create_github_repo(
        self,
        github_token: str,
        repo_name: str,
        description: str = "",
        private: bool = False
    ) -> Dict:
        """
        Create a new GitHub repository.
        
        Args:
            github_token: GitHub personal access token
            repo_name: Repository name
            description: Repository description
            private: Whether repo should be private
        """
        try:
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": False
            }
            
            response = requests.post(
                f"{self.github_api}/user/repos",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                return {
                    "status": "success",
                    "message": "Repository created successfully",
                    "repo_url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "ssh_url": repo_data["ssh_url"]
                }
            else:
                return {
                    "status": "error",
                    "message": f"GitHub API error: {response.json().get('message', 'Unknown error')}"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create GitHub repo: {str(e)}"
            }
    
    async def add_remote(
        self,
        workspace_path: str,
        remote_name: str,
        remote_url: str
    ) -> Dict:
        """Add git remote"""
        try:
            subprocess.run(
                ["git", "remote", "add", remote_name, remote_url],
                cwd=workspace_path,
                check=True,
                capture_output=True
            )
            
            return {
                "status": "success",
                "message": f"Remote '{remote_name}' added successfully"
            }
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            
            if "already exists" in error_msg:
                # Update existing remote
                subprocess.run(
                    ["git", "remote", "set-url", remote_name, remote_url],
                    cwd=workspace_path,
                    check=True,
                    capture_output=True
                )
                return {
                    "status": "success",
                    "message": f"Remote '{remote_name}' updated"
                }
            
            return {
                "status": "error",
                "message": f"Failed to add remote: {error_msg}"
            }
    
    async def push(
        self,
        workspace_path: str,
        remote: str = "origin",
        branch: str = "main",
        set_upstream: bool = True
    ) -> Dict:
        """
        Push commits to remote.
        
        Args:
            workspace_path: Path to workspace
            remote: Remote name (default: origin)
            branch: Branch name (default: main)
            set_upstream: Set upstream branch
        """
        try:
            cmd = ["git", "push"]
            
            if set_upstream:
                cmd.extend(["-u", remote, branch])
            else:
                cmd.extend([remote, branch])
            
            result = subprocess.run(
                cmd,
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "success",
                "message": "Pushed to remote successfully",
                "output": result.stdout + result.stderr
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git push failed: {e.stderr if e.stderr else str(e)}"
            }
    
    async def pull(
        self,
        workspace_path: str,
        remote: str = "origin",
        branch: str = "main"
    ) -> Dict:
        """Pull changes from remote"""
        try:
            result = subprocess.run(
                ["git", "pull", remote, branch],
                cwd=workspace_path,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "success",
                "message": "Pulled changes successfully",
                "output": result.stdout
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Git pull failed: {e.stderr if e.stderr else str(e)}"
            }
    
    async def create_branch(
        self,
        workspace_path: str,
        branch_name: str,
        checkout: bool = True
    ) -> Dict:
        """Create a new branch"""
        try:
            if checkout:
                subprocess.run(
                    ["git", "checkout", "-b", branch_name],
                    cwd=workspace_path,
                    check=True,
                    capture_output=True
                )
            else:
                subprocess.run(
                    ["git", "branch", branch_name],
                    cwd=workspace_path,
                    check=True,
                    capture_output=True
                )
            
            return {
                "status": "success",
                "message": f"Branch '{branch_name}' created successfully"
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Failed to create branch: {e.stderr.decode() if e.stderr else str(e)}"
            }
    
    async def list_branches(self, workspace_path: str) -> Dict:
        """List all branches"""
        try:
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=workspace_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = []
            current_branch = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('*'):
                    current_branch = line[2:]
                    branches.append({"name": current_branch, "current": True})
                else:
                    branches.append({"name": line, "current": False})
            
            return {
                "status": "success",
                "branches": branches,
                "current_branch": current_branch
            }
        
        except subprocess.CalledProcessError:
            return {
                "status": "success",
                "branches": [],
                "current_branch": "main"
            }


# Singleton instance
_git_manager = None

def get_git_manager() -> GitManager:
    """Get or create singleton git manager"""
    global _git_manager
    if _git_manager is None:
        _git_manager = GitManager()
    return _git_manager
