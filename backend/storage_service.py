# AWS S3 + CloudFront Storage Service
# Handles file uploads, image optimization, and CDN delivery

import boto3
from botocore.exceptions import ClientError
from PIL import Image
import io
import os
import uuid
from typing import Optional, Dict, List
from datetime import datetime
import hashlib

class StorageService:
    """AWS S3 + CloudFront storage service for AutoWebIQ"""
    
    def __init__(self):
        # AWS Configuration
        self.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        self.s3_bucket = os.environ.get('S3_BUCKET_NAME', 'autowebiq-storage')
        self.cloudfront_domain = os.environ.get('CLOUDFRONT_DOMAIN', 'd2xfo0u3kipoyw.cloudfront.net')
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.aws_region
        )
        
        # Cloudinary fallback (you have credentials in .env)
        self.cloudinary_cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        self.cloudinary_api_key = os.environ.get('CLOUDINARY_API_KEY')
        self.cloudinary_api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = 'application/octet-stream',
        folder: str = 'uploads',
        public: bool = True
    ) -> Dict:
        """
        Upload file to S3 and return CloudFront URL
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type
            folder: S3 folder path
            public: Whether file should be publicly accessible
        
        Returns:
            Dict with s3_key, s3_url, cloudfront_url, file_size
        """
        try:
            # Generate unique filename
            file_ext = os.path.splitext(filename)[1]
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d')
            s3_key = f"{folder}/{timestamp}/{unique_id}{file_ext}"
            
            # Upload to S3
            extra_args = {
                'ContentType': content_type,
            }
            
            # Note: Don't use ACL if bucket has ACLs disabled
            # Bucket policy should handle public access instead
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=file_content,
                **extra_args
            )
            
            # Generate URLs
            s3_url = f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
            cloudfront_url = f"https://{self.cloudfront_domain}/{s3_key}"
            
            return {
                'success': True,
                's3_key': s3_key,
                's3_url': s3_url,
                'cloudfront_url': cloudfront_url,
                'cdn_url': cloudfront_url,  # Alias for convenience
                'file_size': len(file_content),
                'content_type': content_type
            }
            
        except ClientError as e:
            print(f"S3 upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_image(
        self,
        image_content: bytes,
        filename: str,
        optimize: bool = True,
        max_width: int = 1920,
        quality: int = 85
    ) -> Dict:
        """
        Upload image with optimization
        
        Args:
            image_content: Image content as bytes
            filename: Original filename
            optimize: Whether to optimize image
            max_width: Maximum width for optimization
            quality: JPEG quality (1-100)
        
        Returns:
            Dict with upload info including optimized URL
        """
        try:
            # Optimize image if requested
            if optimize:
                image_content = self._optimize_image(
                    image_content,
                    max_width=max_width,
                    quality=quality
                )
            
            # Determine content type
            file_ext = os.path.splitext(filename)[1].lower()
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml'
            }
            content_type = content_type_map.get(file_ext, 'image/jpeg')
            
            # Upload to S3
            result = self.upload_file(
                file_content=image_content,
                filename=filename,
                content_type=content_type,
                folder='images',
                public=True
            )
            
            if result['success']:
                result['optimized'] = optimize
                result['max_width'] = max_width if optimize else None
                result['quality'] = quality if optimize else None
            
            return result
            
        except Exception as e:
            print(f"Image upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _optimize_image(
        self,
        image_content: bytes,
        max_width: int = 1920,
        quality: int = 85
    ) -> bytes:
        """Optimize image - resize and compress"""
        try:
            # Open image
            img = Image.open(io.BytesIO(image_content))
            
            # Convert RGBA to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            print(f"Image optimization error: {e}")
            # Return original if optimization fails
            return image_content
    
    def upload_website(
        self,
        html_content: str,
        project_id: str,
        user_id: str
    ) -> Dict:
        """
        Upload generated website HTML to S3
        
        Args:
            html_content: Generated HTML content
            project_id: Project ID
            user_id: User ID
        
        Returns:
            Dict with S3 key and CloudFront URL
        """
        try:
            # Generate path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{project_id}_{timestamp}.html"
            
            # Upload HTML
            result = self.upload_file(
                file_content=html_content.encode('utf-8'),
                filename=filename,
                content_type='text/html',
                folder=f'websites/{user_id}',
                public=True
            )
            
            if result['success']:
                result['preview_url'] = result['cloudfront_url']
                result['project_id'] = project_id
                result['user_id'] = user_id
            
            return result
            
        except Exception as e:
            print(f"Website upload error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"S3 delete error: {e}")
            return False
    
    def list_user_files(self, user_id: str, folder: str = 'websites') -> List[Dict]:
        """List all files for a user"""
        try:
            prefix = f"{folder}/{user_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                s3_key = obj['Key']
                files.append({
                    's3_key': s3_key,
                    'cloudfront_url': f"https://{self.cloudfront_domain}/{s3_key}",
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
            
            return files
            
        except ClientError as e:
            print(f"S3 list error: {e}")
            return []
    
    def get_file_url(self, s3_key: str, use_cdn: bool = True) -> str:
        """Get URL for a file"""
        if use_cdn:
            return f"https://{self.cloudfront_domain}/{s3_key}"
        else:
            return f"https://{self.s3_bucket}.s3.{self.aws_region}.amazonaws.com/{s3_key}"
    
    def health_check(self) -> Dict:
        """Check if S3 and credentials are working"""
        try:
            # Try to list bucket (just to verify access)
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            
            return {
                'status': 'healthy',
                'bucket': self.s3_bucket,
                'region': self.aws_region,
                'cloudfront': self.cloudfront_domain
            }
        except ClientError as e:
            return {
                'status': 'error',
                'error': str(e)
            }


# Global storage instance
storage_service = StorageService()
