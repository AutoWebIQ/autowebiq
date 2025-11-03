"""
Manual Deployment System - Emergent Style
Instant preview hosting with subdomain support
"""
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
import httpx
import zipfile
import io
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class ManualDeploymentManager:
    """
    Manage manual deployments with instant preview
    Similar to Emergent's deployment system
    """
    
    def __init__(self):
        """Initialize deployment manager"""
        self.domain = os.environ.get('DOMAIN', 'autowebiq.com')
        self.preview_host = os.environ.get('PREVIEW_HOST', 'preview.autowebiq.com')
        self.cloudflare_zone_id = os.environ.get('CLOUDFLARE_ZONE_ID')
        self.cloudflare_token = os.environ.get('CLOUDFLARE_API_TOKEN')
        self.deploy_base_path = Path('/var/www/deployments')
        self.deploy_base_path.mkdir(parents=True, exist_ok=True)
    
    async def deploy_project(
        self,
        project_id: str,
        user_id: str,
        files: Dict[str, str],
        subdomain: Optional[str] = None
    ) -> Dict:
        """
        Deploy a project with instant preview
        
        Args:
            project_id: Project ID
            user_id: User ID
            files: Dict of filename -> content
            subdomain: Optional custom subdomain (default: project_id)
            
        Returns:
            Dict with deployment details
        """
        try:
            # Generate subdomain
            if not subdomain:
                subdomain = f"{user_id[:8]}-{project_id[:8]}"
            
            # Create deployment directory
            deploy_path = self.deploy_base_path / subdomain
            deploy_path.mkdir(parents=True, exist_ok=True)
            
            # Write files
            for filename, content in files.items():
                file_path = deploy_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
            
            # Generate preview URL
            preview_url = f"https://{subdomain}.{self.preview_host}"
            
            # Create Cloudflare DNS record (if configured)
            if self.cloudflare_zone_id and self.cloudflare_token:
                await self._create_dns_record(subdomain)
            
            deployment_info = {
                'deployment_id': f"dep_{project_id}_{int(datetime.now(timezone.utc).timestamp())}",
                'project_id': project_id,
                'user_id': user_id,
                'subdomain': subdomain,
                'preview_url': preview_url,
                'status': 'active',
                'files_count': len(files),
                'deployed_at': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"✅ Project deployed: {preview_url}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"❌ Deployment error: {str(e)}")
            raise
    
    async def _create_dns_record(self, subdomain: str) -> bool:
        """Create Cloudflare DNS record for subdomain"""
        try:
            headers = {
                'Authorization': f'Bearer {self.cloudflare_token}',
                'Content-Type': 'application/json'
            }
            
            # Check if record exists
            async with httpx.AsyncClient() as client:
                # Create DNS record
                dns_data = {
                    'type': 'CNAME',
                    'name': f"{subdomain}.{self.preview_host}",
                    'content': self.preview_host,
                    'ttl': 1,
                    'proxied': True
                }
                
                response = await client.post(
                    f"https://api.cloudflare.com/client/v4/zones/{self.cloudflare_zone_id}/dns_records",
                    headers=headers,
                    json=dns_data,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"✅ DNS record created: {subdomain}")
                    return True
                else:
                    logger.warning(f"⚠️ DNS creation failed: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ DNS record error: {str(e)}")
            return False
    
    async def update_deployment(
        self,
        deployment_id: str,
        project_id: str,
        files: Dict[str, str]
    ) -> Dict:
        """
        Update an existing deployment
        
        Args:
            deployment_id: Deployment ID
            project_id: Project ID
            files: Updated files
            
        Returns:
            Dict with update details
        """
        try:
            # Find deployment directory
            deploy_dirs = list(self.deploy_base_path.glob(f"*{project_id[:8]}"))
            
            if not deploy_dirs:
                raise ValueError(f"Deployment not found: {deployment_id}")
            
            deploy_path = deploy_dirs[0]
            
            # Update files
            for filename, content in files.items():
                file_path = deploy_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding='utf-8')
            
            return {
                'deployment_id': deployment_id,
                'project_id': project_id,
                'status': 'updated',
                'files_updated': len(files),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Update deployment error: {str(e)}")
            raise
    
    async def delete_deployment(
        self,
        project_id: str,
        subdomain: Optional[str] = None
    ) -> Dict:
        """
        Delete a deployment
        
        Args:
            project_id: Project ID
            subdomain: Optional subdomain
            
        Returns:
            Dict with deletion details
        """
        try:
            # Find and delete deployment directory
            if subdomain:
                deploy_path = self.deploy_base_path / subdomain
            else:
                deploy_dirs = list(self.deploy_base_path.glob(f"*{project_id[:8]}"))
                deploy_path = deploy_dirs[0] if deploy_dirs else None
            
            if deploy_path and deploy_path.exists():
                import shutil
                shutil.rmtree(deploy_path)
                logger.info(f"✅ Deployment deleted: {deploy_path}")
            
            return {
                'project_id': project_id,
                'status': 'deleted',
                'deleted_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Delete deployment error: {str(e)}")
            raise
    
    async def get_deployment_info(
        self,
        project_id: str,
        db
    ) -> Optional[Dict]:
        """
        Get deployment information
        
        Args:
            project_id: Project ID
            db: Database connection
            
        Returns:
            Dict with deployment info or None
        """
        try:
            # Check if deployment exists
            deploy_dirs = list(self.deploy_base_path.glob(f"*{project_id[:8]}"))
            
            if not deploy_dirs:
                return None
            
            deploy_path = deploy_dirs[0]
            subdomain = deploy_path.name
            
            # Count files
            files = list(deploy_path.rglob('*'))
            file_count = len([f for f in files if f.is_file()])
            
            return {
                'project_id': project_id,
                'subdomain': subdomain,
                'preview_url': f"https://{subdomain}.{self.preview_host}",
                'status': 'active',
                'files_count': file_count,
                'deploy_path': str(deploy_path)
            }
            
        except Exception as e:
            logger.error(f"❌ Get deployment info error: {str(e)}")
            return None
    
    async def list_user_deployments(
        self,
        user_id: str,
        db
    ) -> list:
        """
        List all deployments for a user
        
        Args:
            user_id: User ID
            db: Database connection
            
        Returns:
            List of deployment dicts
        """
        try:
            # Find all deployments for user
            user_prefix = user_id[:8]
            deploy_dirs = list(self.deploy_base_path.glob(f"{user_prefix}-*"))
            
            deployments = []
            for deploy_path in deploy_dirs:
                subdomain = deploy_path.name
                
                # Extract project_id from subdomain
                parts = subdomain.split('-')
                project_id = parts[1] if len(parts) > 1 else 'unknown'
                
                deployments.append({
                    'subdomain': subdomain,
                    'project_id': project_id,
                    'preview_url': f"https://{subdomain}.{self.preview_host}",
                    'status': 'active'
                })
            
            return deployments
            
        except Exception as e:
            logger.error(f"❌ List deployments error: {str(e)}")
            return []
    
    def prepare_files_from_project(self, project_data: Dict) -> Dict[str, str]:
        """
        Prepare files dict from project data
        
        Args:
            project_data: Project document
            
        Returns:
            Dict of filename -> content
        """
        files = {}
        
        # Get generated code
        generated_code = project_data.get('generated_code', '')
        
        if generated_code:
            # Check if it's multi-page or single page
            if '<!-- PAGE:' in generated_code:
                # Multi-page website
                pages = generated_code.split('<!-- PAGE:')
                for page_content in pages[1:]:  # Skip first empty split
                    lines = page_content.split('\n', 1)
                    if len(lines) >= 2:
                        filename = lines[0].strip().replace(' -->', '')
                        content = lines[1]
                        files[filename] = content
            else:
                # Single page
                files['index.html'] = generated_code
        else:
            # Create placeholder
            files['index.html'] = '''<!DOCTYPE html>
<html>
<head>
    <title>AutoWebIQ Project</title>
</head>
<body>
    <h1>Project Preview</h1>
    <p>No content generated yet.</p>
</body>
</html>'''
        
        return files

# Singleton instance
manual_deployment_manager = ManualDeploymentManager()
