# GitHub Integration for AutoWebIQ
# Handles repository creation, forking, and code push

import os
import logging
import requests
import base64
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class GitHubManager:
    """Manages GitHub repository operations"""
    
    def __init__(self):
        # GitHub OAuth credentials
        self.client_id = os.environ.get('GITHUB_CLIENT_ID')
        self.client_secret = os.environ.get('GITHUB_CLIENT_SECRET')
        self.api_base = "https://api.github.com"
    
    async def create_repository(
        self,
        access_token: str,
        repo_name: str,
        description: str,
        private: bool = False
    ) -> Dict:
        """
        Create a new GitHub repository for user
        """
        try:
            url = f"{self.api_base}/user/repos"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": True,  # Initialize with README
                "has_issues": True,
                "has_projects": False,
                "has_wiki": False
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                repo_data = response.json()
                logger.info(f"Repository created: {repo_data['html_url']}")
                return {
                    "status": "success",
                    "repo_url": repo_data['html_url'],
                    "clone_url": repo_data['clone_url'],
                    "repo_name": repo_data['full_name'],
                    "message": "Repository created successfully"
                }
            else:
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"GitHub API error: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Failed to create repository: {error_msg}"
                }
                
        except Exception as e:
            logger.error(f"Repository creation failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def push_code_to_repo(
        self,
        access_token: str,
        repo_name: str,
        code_files: Dict[str, str],
        commit_message: str = "Initial commit from AutoWebIQ"
    ) -> Dict:
        """
        Push generated code files to GitHub repository
        
        Args:
            access_token: GitHub personal access token
            repo_name: Full repository name (username/repo)
            code_files: Dict mapping file paths to content
                       e.g., {"index.html": "<html>...", "server.py": "..."}
            commit_message: Commit message
        """
        try:
            # Get the default branch SHA
            branch_info = await self._get_branch_info(access_token, repo_name, "main")
            if not branch_info:
                return {
                    "status": "error",
                    "message": "Could not get repository branch info"
                }
            
            # Create/update each file
            results = []
            for file_path, content in code_files.items():
                result = await self._create_or_update_file(
                    access_token,
                    repo_name,
                    file_path,
                    content,
                    commit_message
                )
                results.append(result)
            
            # Check if all succeeded
            failed = [r for r in results if r['status'] != 'success']
            if failed:
                return {
                    "status": "partial",
                    "message": f"{len(results) - len(failed)}/{len(results)} files pushed successfully",
                    "failed_files": failed
                }
            
            logger.info(f"Code pushed to {repo_name}")
            return {
                "status": "success",
                "message": f"All {len(results)} files pushed successfully",
                "repo_url": f"https://github.com/{repo_name}"
            }
            
        except Exception as e:
            logger.error(f"Code push failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _get_branch_info(self, access_token: str, repo_name: str, branch: str) -> Optional[Dict]:
        """Get branch information"""
        try:
            url = f"{self.api_base}/repos/{repo_name}/git/ref/heads/{branch}"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get branch info: {e}")
            return None
    
    async def _create_or_update_file(
        self,
        access_token: str,
        repo_name: str,
        file_path: str,
        content: str,
        commit_message: str
    ) -> Dict:
        """Create or update a file in repository"""
        try:
            url = f"{self.api_base}/repos/{repo_name}/contents/{file_path}"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Check if file exists (to get SHA for update)
            check_response = requests.get(url, headers=headers)
            file_sha = None
            if check_response.status_code == 200:
                file_sha = check_response.json()['sha']
            
            # Encode content to base64
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # Create/update file
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": "main"
            }
            
            if file_sha:
                data["sha"] = file_sha  # Required for update
            
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                return {
                    "status": "success",
                    "file": file_path,
                    "message": "File created/updated successfully"
                }
            else:
                error_msg = response.json().get('message', 'Unknown error')
                return {
                    "status": "error",
                    "file": file_path,
                    "message": error_msg
                }
                
        except Exception as e:
            logger.error(f"File creation failed: {e}")
            return {
                "status": "error",
                "file": file_path,
                "message": str(e)
            }
    
    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get GitHub user information"""
        try:
            url = f"{self.api_base}/user"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "username": user_data['login'],
                    "name": user_data.get('name'),
                    "email": user_data.get('email'),
                    "avatar_url": user_data.get('avatar_url'),
                    "bio": user_data.get('bio')
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    async def list_user_repositories(self, access_token: str) -> list:
        """List user's repositories"""
        try:
            url = f"{self.api_base}/user/repos"
            headers = {
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            params = {
                "sort": "updated",
                "per_page": 100
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                repos = response.json()
                return [
                    {
                        "name": repo['name'],
                        "full_name": repo['full_name'],
                        "url": repo['html_url'],
                        "description": repo.get('description'),
                        "private": repo['private'],
                        "updated_at": repo['updated_at']
                    }
                    for repo in repos
                ]
            return []
            
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            return []

# Global instance
github_manager = GitHubManager()
