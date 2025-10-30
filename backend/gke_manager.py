# Google Kubernetes Engine Workspace Manager for AutoWebIQ
# Manages dynamic workspace deployments on GKE with subdomain routing

import os
import logging
import yaml
import subprocess
import json
import requests
from typing import Dict, Optional
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger(__name__)

class GKEManager:
    """Manages Kubernetes workspaces on GKE"""
    
    def __init__(self):
        self.project_id = os.environ.get('GCP_PROJECT_ID', 'autowebiq-476616')
        self.cluster_name = os.environ.get('GKE_CLUSTER_NAME', 'autowebiq-cluster')
        self.cluster_region = os.environ.get('GKE_CLUSTER_REGION', 'asia-south1')
        self.namespace = 'autowebiq-workspaces'
        self.preview_host = os.environ.get('PREVIEW_HOST', 'preview.autowebiq.com')
        self.cloudflare_api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
        self.cloudflare_zone_id = os.environ.get('CLOUDFLARE_ZONE_ID')
        self.gcp_key_path = '/app/gcp-service-account.json'
        
        # Check if GKE is configured
        self.is_configured = os.path.exists(self.gcp_key_path)
        if self.is_configured:
            logger.info("GKE Manager initialized successfully")
        else:
            logger.warning("GCP service account key not found. GKE features disabled.")
    
    async def authenticate_gke(self) -> bool:
        """Authenticate with GKE cluster"""
        try:
            # Activate service account
            subprocess.run([
                'gcloud', 'auth', 'activate-service-account',
                '--key-file', self.gcp_key_path
            ], check=True, capture_output=True)
            
            # Set project
            subprocess.run([
                'gcloud', 'config', 'set', 'project', self.project_id
            ], check=True, capture_output=True)
            
            # Get cluster credentials
            subprocess.run([
                'gcloud', 'container', 'clusters', 'get-credentials',
                self.cluster_name,
                '--region', self.cluster_region
            ], check=True, capture_output=True)
            
            logger.info("Successfully authenticated with GKE")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"GKE authentication failed: {e.stderr.decode() if e.stderr else str(e)}")
            return False
    
    async def create_workspace(self, user_id: str, project_id: str, code_data: Dict) -> Dict:
        """
        Create a new workspace deployment on GKE
        Returns: workspace info with subdomain URL
        """
        if not self.is_configured:
            return {
                "status": "error",
                "message": "GKE not configured. Please set up GCP credentials."
            }
        
        try:
            # Authenticate first
            auth_success = await self.authenticate_gke()
            if not auth_success:
                return {
                    "status": "error",
                    "message": "GKE authentication failed"
                }
            
            # Generate unique subdomain (project_id as subdomain)
            subdomain = f"{project_id[:16]}"  # Limit to 16 chars for DNS
            preview_url = f"https://{subdomain}.{self.preview_host}"
            
            # Create deployment manifest
            deployment_manifest = self._create_deployment_manifest(
                user_id, project_id, subdomain
            )
            
            # Apply deployment to GKE
            result = await self._apply_manifest(deployment_manifest)
            
            if result['status'] == 'success':
                # Create Cloudflare DNS record for subdomain
                await self._create_dns_record(subdomain)
                
                # Store code in ConfigMap
                await self._store_code(project_id, code_data)
                
                logger.info(f"Workspace {project_id} created with URL: {preview_url}")
                
                return {
                    "status": "success",
                    "project_id": project_id,
                    "subdomain": subdomain,
                    "preview_url": preview_url,
                    "message": "Workspace deployed successfully"
                }
            else:
                return result
            
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            return {
                "status": "error",
                "message": f"Workspace creation failed: {str(e)}"
            }
    
    def _create_deployment_manifest(self, user_id: str, project_id: str, subdomain: str) -> Dict:
        """Create Kubernetes deployment manifest for workspace"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"workspace-{project_id}",
                "namespace": self.namespace,
                "labels": {
                    "app": "autowebiq-workspace",
                    "user-id": user_id,
                    "project-id": project_id,
                    "subdomain": subdomain
                }
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "project-id": project_id
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "autowebiq-workspace",
                            "project-id": project_id,
                            "subdomain": subdomain
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "workspace",
                            "image": "aashikzm098/autowebiq-workspace:latest",
                            "imagePullPolicy": "Always",
                            "ports": [
                                {"containerPort": 80, "name": "http"},
                                {"containerPort": 3000, "name": "frontend"},
                                {"containerPort": 8001, "name": "backend"}
                            ],
                            "env": [
                                {"name": "USER_ID", "value": user_id},
                                {"name": "PROJECT_ID", "value": project_id},
                                {"name": "SUBDOMAIN", "value": subdomain}
                            ],
                            "resources": {
                                "limits": {"cpu": "500m", "memory": "512Mi"},
                                "requests": {"cpu": "250m", "memory": "256Mi"}
                            },
                            "volumeMounts": [{
                                "name": "code-volume",
                                "mountPath": "/workspace/code"
                            }]
                        }],
                        "volumes": [{
                            "name": "code-volume",
                            "configMap": {
                                "name": f"code-{project_id}"
                            }
                        }]
                    }
                }
            }
        }
    
    async def _apply_manifest(self, manifest: Dict) -> Dict:
        """Apply Kubernetes manifest using kubectl"""
        try:
            # Write manifest to temp file
            manifest_yaml = yaml.dump(manifest)
            temp_file = f"/tmp/manifest-{manifest['metadata']['name']}.yaml"
            
            with open(temp_file, 'w') as f:
                f.write(manifest_yaml)
            
            # Apply manifest
            result = subprocess.run(
                ['kubectl', 'apply', '-f', temp_file],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Manifest applied: {result.stdout}")
            
            # Clean up temp file
            os.remove(temp_file)
            
            return {
                "status": "success",
                "message": "Deployment created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply manifest: {e.stderr}")
            return {
                "status": "error",
                "message": f"Deployment failed: {e.stderr}"
            }
        except Exception as e:
            logger.error(f"Manifest application error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _store_code(self, project_id: str, code_data: Dict):
        """Store generated code in ConfigMap"""
        try:
            configmap = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": f"code-{project_id}",
                    "namespace": self.namespace
                },
                "data": {
                    "index.html": code_data.get('frontend_code', ''),
                    "server.py": code_data.get('backend_code', ''),
                    "metadata.json": json.dumps({
                        "project_id": project_id,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "plan": code_data.get('plan', {})
                    })
                }
            }
            
            await self._apply_manifest(configmap)
            logger.info(f"Code stored for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to store code: {e}")
    
    async def _create_dns_record(self, subdomain: str) -> bool:
        """Create Cloudflare DNS A record for subdomain"""
        if not self.cloudflare_api_token or not self.cloudflare_zone_id:
            logger.warning("Cloudflare credentials not set. DNS record not created.")
            return False
        
        try:
            # Get Ingress LoadBalancer IP
            ip_address = await self._get_ingress_ip()
            
            if not ip_address:
                logger.warning("Could not get ingress IP. DNS record not created.")
                return False
            
            # Create DNS record
            url = f"https://api.cloudflare.com/client/v4/zones/{self.cloudflare_zone_id}/dns_records"
            headers = {
                "Authorization": f"Bearer {self.cloudflare_api_token}",
                "Content-Type": "application/json"
            }
            data = {
                "type": "A",
                "name": f"{subdomain}.{self.preview_host}",
                "content": ip_address,
                "ttl": 120,
                "proxied": True
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                logger.info(f"DNS record created for {subdomain}.{self.preview_host}")
                return True
            else:
                logger.error(f"Cloudflare API error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create DNS record: {e}")
            return False
    
    async def _get_ingress_ip(self) -> Optional[str]:
        """Get LoadBalancer IP from ingress"""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'ingress',
                'autowebiq-ingress',
                '-n', self.namespace,
                '-o', 'jsonpath={.status.loadBalancer.ingress[0].ip}'
            ], capture_output=True, text=True, check=True)
            
            ip_address = result.stdout.strip()
            logger.info(f"Ingress IP: {ip_address}")
            return ip_address if ip_address else None
            
        except Exception as e:
            logger.error(f"Failed to get ingress IP: {e}")
            return None
    
    async def delete_workspace(self, project_id: str) -> Dict:
        """Delete workspace deployment"""
        try:
            # Delete deployment
            subprocess.run([
                'kubectl', 'delete', 'deployment',
                f"workspace-{project_id}",
                '-n', self.namespace
            ], capture_output=True, check=True)
            
            # Delete ConfigMap
            subprocess.run([
                'kubectl', 'delete', 'configmap',
                f"code-{project_id}",
                '-n', self.namespace
            ], capture_output=True)
            
            logger.info(f"Workspace {project_id} deleted")
            
            return {
                "status": "success",
                "message": "Workspace deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete workspace: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_workspace_status(self, project_id: str) -> Dict:
        """Get workspace deployment status"""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'deployment',
                f"workspace-{project_id}",
                '-n', self.namespace,
                '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            deployment = json.loads(result.stdout)
            
            return {
                "status": "success",
                "deployment_status": deployment['status'],
                "available_replicas": deployment['status'].get('availableReplicas', 0),
                "ready": deployment['status'].get('availableReplicas', 0) > 0
            }
            
        except subprocess.CalledProcessError:
            return {
                "status": "error",
                "message": "Workspace not found"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def list_user_workspaces(self, user_id: str) -> list:
        """List all workspaces for a user"""
        try:
            result = subprocess.run([
                'kubectl', 'get', 'deployments',
                '-n', self.namespace,
                '-l', f"user-id={user_id}",
                '-o', 'json'
            ], capture_output=True, text=True, check=True)
            
            deployments = json.loads(result.stdout)
            
            workspaces = []
            for deployment in deployments.get('items', []):
                labels = deployment['metadata'].get('labels', {})
                workspaces.append({
                    "name": deployment['metadata']['name'],
                    "project_id": labels.get('project-id'),
                    "subdomain": labels.get('subdomain'),
                    "preview_url": f"https://{labels.get('subdomain')}.{self.preview_host}",
                    "status": deployment['status'],
                    "created_at": deployment['metadata'].get('creationTimestamp')
                })
            
            return workspaces
            
        except Exception as e:
            logger.error(f"Failed to list workspaces: {e}")
            return []

# Global instance
gke_manager = GKEManager()
