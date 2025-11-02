# Deployment Integration Manager for AutoWebIQ
# Supports Vercel, Netlify, Railway, AWS

import os
import requests
import json
from typing import Dict, Optional
import subprocess
import zipfile
import io

class DeploymentManager:
    """
    Manages deployments to multiple platforms:
    - Vercel
    - Netlify
    - Railway
    - AWS (S3 + CloudFront)
    """
    
    def __init__(self):
        self.vercel_api = "https://api.vercel.com"
        self.netlify_api = "https://api.netlify.com/api/v1"
        self.railway_api = "https://backboard.railway.app/graphql/v2"
    
    async def deploy_to_vercel(
        self,
        project_path: str,
        project_name: str,
        vercel_token: str
    ) -> Dict:
        """Deploy to Vercel"""
        try:
            # Create deployment
            headers = {
                "Authorization": f"Bearer {vercel_token}",
                "Content-Type": "application/json"
            }
            
            # Get files
            files_dict = {}
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if '.git' in root or 'node_modules' in root:
                        continue
                    
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        files_dict[rel_path] = {
                            "file": content.decode('utf-8', errors='ignore')
                        }
            
            data = {
                "name": project_name,
                "files": files_dict,
                "projectSettings": {
                    "framework": "vite"
                },
                "target": "production"
            }
            
            response = requests.post(
                f"{self.vercel_api}/v13/deployments",
                headers=headers,
                json=data,
                timeout=300
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    "status": "success",
                    "url": f"https://{result.get('url')}",
                    "deployment_id": result.get('id'),
                    "platform": "vercel"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Vercel deployment failed: {response.text}"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Vercel deployment error: {str(e)}"
            }
    
    async def deploy_to_netlify(
        self,
        project_path: str,
        site_name: str,
        netlify_token: str
    ) -> Dict:
        """Deploy to Netlify"""
        try:
            headers = {
                "Authorization": f"Bearer {netlify_token}",
                "Content-Type": "application/zip"
            }
            
            # Create zip file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(project_path):
                    if '.git' in root or 'node_modules' in root:
                        continue
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, project_path)
                        zip_file.write(file_path, arcname)\n            
            zip_buffer.seek(0)
            
            # Create site if doesn't exist
            site_response = requests.post(
                f"{self.netlify_api}/sites",
                headers={\"Authorization\": f\"Bearer {netlify_token}\"},
                json={\"name\": site_name},
                timeout=60
            )
            
            if site_response.status_code in [200, 201]:
                site_id = site_response.json().get('id')
            else:
                # Site might already exist
                sites_response = requests.get(
                    f"{self.netlify_api}/sites",
                    headers={\"Authorization\": f\"Bearer {netlify_token}\"},
                    timeout=60
                )
                sites = sites_response.json()
                site = next((s for s in sites if s.get('name') == site_name), None)
                if site:
                    site_id = site.get('id')
                else:
                    return {
                        "status": "error",
                        "message": "Failed to create/find Netlify site"
                    }
            
            # Deploy
            deploy_response = requests.post(
                f"{self.netlify_api}/sites/{site_id}/deploys",
                headers=headers,
                data=zip_buffer.getvalue(),
                timeout=300
            )
            
            if deploy_response.status_code in [200, 201]:
                result = deploy_response.json()
                return {
                    "status": "success",
                    "url": result.get('ssl_url') or result.get('url'),
                    "deployment_id": result.get('id'),
                    "platform": "netlify"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Netlify deployment failed: {deploy_response.text}"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Netlify deployment error: {str(e)}"
            }
    
    async def deploy_to_railway(
        self,
        project_path: str,
        project_name: str,
        railway_token: str
    ) -> Dict:
        """Deploy to Railway"""
        try:
            headers = {
                "Authorization": f"Bearer {railway_token}",
                "Content-Type": "application/json"
            }
            
            # Create project via GraphQL
            mutation = """
            mutation CreateProject($name: String!) {
                projectCreate(input: { name: $name }) {
                    id
                    name
                }
            }
            """
            
            response = requests.post(
                self.railway_api,
                headers=headers,
                json={
                    "query": mutation,
                    "variables": {"name": project_name}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                project_id = result.get('data', {}).get('projectCreate', {}).get('id')
                
                if project_id:
                    return {
                        "status": "success",
                        "message": "Railway project created. Please connect GitHub repository for deployment.",
                        "project_id": project_id,
                        "platform": "railway",
                        "instructions": [
                            "1. Push your code to GitHub",
                            "2. Connect GitHub repo to Railway project",
                            "3. Railway will auto-deploy"
                        ]
                    }
            
            return {
                "status": "error",
                "message": f"Railway deployment failed: {response.text}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Railway deployment error: {str(e)}"
            }
    
    async def get_deployment_status(
        self,
        platform: str,
        deployment_id: str,
        token: str
    ) -> Dict:
        """Get deployment status"""
        try:
            if platform == "vercel":
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{self.vercel_api}/v13/deployments/{deployment_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "success",
                        "state": data.get('readyState'),
                        "url": f"https://{data.get('url')}"
                    }
            
            elif platform == "netlify":
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{self.netlify_api}/deploys/{deployment_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "success",
                        "state": data.get('state'),
                        "url": data.get('ssl_url') or data.get('url')
                    }
            
            return {
                "status": "error",
                "message": "Unknown platform or failed to fetch status"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get status: {str(e)}"
            }


# Singleton instance
_deployment_manager = None

def get_deployment_manager() -> DeploymentManager:
    """Get or create singleton deployment manager"""
    global _deployment_manager
    if _deployment_manager is None:
        _deployment_manager = DeploymentManager()
    return _deployment_manager
