"""
Vercel Deployment Service
Handles automated deployment of generated websites to Vercel platform.
"""

import os
import requests
import hashlib
import time
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime

logger = logging.getLogger(__name__)


class VercelDeploymentError(Exception):
    """Custom exception for Vercel deployment errors."""
    pass


class VercelService:
    """Service for deploying websites to Vercel."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Vercel service.
        
        Args:
            token: Vercel API token (defaults to env variable)
        """
        self.token = token or os.getenv("VERCEL_TOKEN")
        if not self.token:
            raise ValueError("VERCEL_TOKEN environment variable is required")
        
        self.base_url = "https://api.vercel.com"
        self.team_id = os.getenv("VERCEL_TEAM_ID")  # Optional
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy.
        
        Returns:
            Configured requests.Session
        """
        session = requests.Session()
        
        # Implement exponential backoff retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,  # Wait 1s, 2s, 4s, 8s, 16s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })
        
        return session
    
    def _get_query_params(self) -> Dict[str, str]:
        """Build query parameters for team-scoped requests."""
        params = {}
        if self.team_id:
            params["teamId"] = self.team_id
        return params
    
    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """
        Compute SHA-1 hash of a file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Hexadecimal SHA-1 hash
        """
        hash_func = hashlib.sha1()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def compute_content_hash(content: bytes) -> str:
        """
        Compute SHA-1 hash of byte content.
        
        Args:
            content: Byte content
        
        Returns:
            Hexadecimal SHA-1 hash
        """
        return hashlib.sha1(content).hexdigest()
    
    def upload_file(self, file_path: str) -> Tuple[str, str, int]:
        """
        Upload a file to Vercel.
        
        Args:
            file_path: Local path to the file
        
        Returns:
            Tuple of (file_name, sha_hash, file_size)
        
        Raises:
            VercelDeploymentError: If upload fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Compute hash and size
        sha = self.compute_content_hash(content)
        file_size = len(content)
        
        logger.info(f"Uploading {file_path.name} ({file_size} bytes, SHA: {sha})")
        
        # Upload to Vercel
        url = f"{self.base_url}/v2/now/files"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-vercel-digest": sha,
            "Content-Length": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        
        try:
            response = self.session.post(
                url,
                data=content,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Successfully uploaded {file_path.name}")
            return str(file_path.name), sha, file_size
            
        except requests.RequestException as e:
            logger.error(f"Failed to upload {file_path.name}: {str(e)}")
            raise VercelDeploymentError(f"File upload failed: {str(e)}")
    
    def upload_content(self, filename: str, content: bytes) -> Tuple[str, str, int]:
        """
        Upload file content directly to Vercel.
        
        Args:
            filename: Name of the file
            content: File content as bytes
        
        Returns:
            Tuple of (filename, sha_hash, file_size)
        
        Raises:
            VercelDeploymentError: If upload fails
        """
        # Compute hash and size
        sha = self.compute_content_hash(content)
        file_size = len(content)
        
        logger.info(f"Uploading {filename} ({file_size} bytes, SHA: {sha})")
        
        # Upload to Vercel
        url = f"{self.base_url}/v2/now/files"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "x-vercel-digest": sha,
            "Content-Length": str(file_size),
            "Content-Type": "application/octet-stream"
        }
        
        try:
            response = self.session.post(
                url,
                data=content,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Successfully uploaded {filename}")
            return filename, sha, file_size
            
        except requests.RequestException as e:
            logger.error(f"Failed to upload {filename}: {str(e)}")
            raise VercelDeploymentError(f"File upload failed: {str(e)}")
    
    def create_deployment(
        self,
        project_name: str,
        files: List[Dict[str, any]],
        environment: str = "preview",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new deployment on Vercel.
        
        Args:
            project_name: Name of the Vercel project
            files: List of file dictionaries with 'file', 'sha', and 'size' keys
            environment: Target environment (preview/production)
            metadata: Optional metadata for the deployment
        
        Returns:
            Deployment details dictionary
        
        Raises:
            VercelDeploymentError: If deployment creation fails
        """
        # Prepare deployment payload
        payload = {
            "name": project_name,
            "files": files,
            "projectSettings": {
                "framework": None  # Auto-detect
            },
            "meta": metadata or {"deployed_via": "autowebiq"}
        }
        
        # Set target environment
        if environment == "production":
            payload["target"] = "production"
        
        logger.info(f"Creating deployment for project: {project_name}")
        
        url = f"{self.base_url}/v13/deployments"
        params = self._get_query_params()
        
        try:
            response = self.session.post(
                url,
                json=payload,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            deployment_info = {
                "id": data["id"],
                "url": data["url"],
                "state": data.get("readyState", "QUEUED"),
                "created_at": data.get("createdAt"),
                "creator": data.get("creator", {}),
                "regions": data.get("regions", [])
            }
            
            logger.info(f"Deployment created: {deployment_info['id']} at {deployment_info['url']}")
            return deployment_info
            
        except requests.RequestException as e:
            logger.error(f"Failed to create deployment: {str(e)}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise VercelDeploymentError(f"Deployment creation failed: {str(e)}")
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """
        Get the current status of a deployment.
        
        Args:
            deployment_id: The deployment ID
        
        Returns:
            Status dictionary with 'state', 'ready', and optional 'error_message'
        
        Raises:
            VercelDeploymentError: If status check fails
        """
        url = f"{self.base_url}/v13/deployments/{deployment_id}"
        params = self._get_query_params()
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            state = data.get("readyState", "QUEUED")
            
            return {
                "state": state,
                "ready": (state == "READY"),
                "error_message": data.get("errorMessage"),
                "url": data.get("url")
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to get deployment status: {str(e)}")
            raise VercelDeploymentError(f"Status check failed: {str(e)}")
    
    def wait_for_deployment(
        self,
        deployment_id: str,
        timeout: int = 600,
        poll_interval: int = 5
    ) -> Dict:
        """
        Poll deployment status until ready or timeout.
        
        Args:
            deployment_id: The deployment ID to monitor
            timeout: Maximum seconds to wait (default: 10 minutes)
            poll_interval: Seconds between checks (default: 5)
        
        Returns:
            Final deployment status
        
        Raises:
            TimeoutError: If deployment doesn't complete within timeout
            VercelDeploymentError: If deployment fails
        """
        start_time = time.time()
        attempt = 0
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                raise TimeoutError(
                    f"Deployment {deployment_id} did not complete within {timeout}s"
                )
            
            status = self.get_deployment_status(deployment_id)
            attempt += 1
            
            logger.info(
                f"[{attempt}] Deployment {deployment_id} state: {status['state']} "
                f"(elapsed: {int(elapsed)}s)"
            )
            
            if status["state"] == "READY":
                logger.info(f"Deployment {deployment_id} is ready!")
                return status
            
            if status["state"] == "ERROR":
                error_msg = status.get("error_message", "Unknown error")
                raise VercelDeploymentError(f"Deployment failed: {error_msg}")
            
            if status["state"] == "CANCELED":
                raise VercelDeploymentError("Deployment was canceled")
            
            # Wait before next poll
            time.sleep(poll_interval)
    
    def deploy_website(
        self,
        project_name: str,
        html_content: str,
        css_content: Optional[str] = None,
        js_content: Optional[str] = None,
        environment: str = "preview"
    ) -> Dict:
        """
        Deploy a complete website with HTML, CSS, and JS.
        
        Args:
            project_name: Name for the Vercel project
            html_content: HTML content
            css_content: Optional CSS content
            js_content: Optional JavaScript content
            environment: Target environment (preview/production)
        
        Returns:
            Deployment details with URL
        
        Raises:
            VercelDeploymentError: If deployment fails
        """
        logger.info(f"Starting deployment for {project_name}")
        
        # Upload files
        uploaded_files = []
        
        # Upload HTML
        filename, sha, size = self.upload_content("index.html", html_content.encode('utf-8'))
        uploaded_files.append({"file": filename, "sha": sha, "size": size})
        
        # Upload CSS if provided
        if css_content:
            filename, sha, size = self.upload_content("styles.css", css_content.encode('utf-8'))
            uploaded_files.append({"file": filename, "sha": sha, "size": size})
        
        # Upload JS if provided
        if js_content:
            filename, sha, size = self.upload_content("script.js", js_content.encode('utf-8'))
            uploaded_files.append({"file": filename, "sha": sha, "size": size})
        
        # Create deployment
        deployment = self.create_deployment(
            project_name=project_name,
            files=uploaded_files,
            environment=environment,
            metadata={
                "deployed_via": "autowebiq",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Wait for deployment to be ready
        final_status = self.wait_for_deployment(deployment["id"])
        
        return {
            "success": True,
            "deployment_id": deployment["id"],
            "deployment_url": f"https://{deployment['url']}",
            "preview_url": f"https://{deployment['url']}",
            "state": final_status["state"],
            "project_name": project_name,
            "environment": environment
        }
