import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import logging
from typing import Optional, Tuple

# Load environment variables
load_dotenv()

class S3Service:
    def __init__(self):
        """Initialize the S3 service with AWS credentials."""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def upload_image(self, file_data: bytes, file_name: str, content_type: str) -> Tuple[bool, Optional[str]]:
        """
        Upload an image to S3.
        
        Args:
            file_data: The binary data of the image
            file_name: The name to give the file in S3
            content_type: The MIME type of the image
            
        Returns:
            Tuple of (success: bool, url: Optional[str])
            If successful, returns (True, url). If failed, returns (False, None)
        """
        try:
            # Generate a unique key for the file
            key = f"images/{file_name}"
            
            # Upload the file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_data,
                ContentType=content_type
            )
            
            # Generate the URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"
            return True, url
            
        except ClientError as e:
            logging.error(f"Error uploading to S3: {str(e)}")
            return False, None
        except Exception as e:
            logging.error(f"Unexpected error uploading to S3: {str(e)}")
            return False, None

    def delete_image(self, image_url: str) -> bool:
        """
        Delete an image from S3.
        
        Args:
            image_url: The full URL of the image to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Extract the key from the URL
            key = image_url.split(f"https://{self.bucket_name}.s3.amazonaws.com/")[1]
            
            # Delete the object
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            logging.error(f"Error deleting from S3: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error deleting from S3: {str(e)}")
            return False 