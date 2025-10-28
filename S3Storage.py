from datetime import datetime
import json
import boto3
import os
from typing import Dict, List, Any, Optional

class S3Storage:
    def __init__(self, bucket_name: str = 'tennis-slots-bucket',
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = None,
                 endpoint_url: Optional[str] = None):
        """
        Initialize S3Storage with AWS credentials.
        
        Args:
            bucket_name: Name of the S3 bucket
            aws_access_key_id: AWS access key (defaults to AWS_ACCESS_KEY_ID env var)
            aws_secret_access_key: AWS secret key (defaults to AWS_SECRET_ACCESS_KEY env var)
            region_name: AWS region (defaults to AWS_DEFAULT_REGION env var)
            endpoint_url: Custom endpoint URL for S3-compatible services (defaults to AWS_S3_ENDPOINT_URL env var)
        """
        self.bucket = bucket_name
        self.key = 'seen_slots.json'
        
        # Get credentials from parameters or environment variables
        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = region_name or os.getenv('AWS_DEFAULT_REGION', 'eu-north-1')
        
        # Validate required credentials
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            raise ValueError("AWS credentials not provided. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
        
        # Get endpoint URL from parameter or environment variable
        self.endpoint_url = endpoint_url or os.getenv('AWS_S3_ENDPOINT_URL')
        
        # Initialize S3 client
        s3_params = {
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key,
            'region_name': self.region_name
        }
        
        # Only add endpoint_url if it's provided
        if self.endpoint_url:
            s3_params['endpoint_url'] = self.endpoint_url
        
        self.s3 = boto3.client('s3', **s3_params)

    def save_slots(self, slots):

        # print("Saving to the S3 bucket...")
        # print(slots)

        # Download existing
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=self.key)
            data = json.loads(obj['Body'].read())
        except:
            data = {'slots': {}}

        # print(data)
        # Add new slots
        for slot in slots:
            # print(slot)
            slot_id = slot['date'] + 'T' + slot['text']
            # print(slot_id)
            if slot_id not in data['slots']:
                data['slots'][slot_id] = {
                    'slot': slot,
                    'found_at': datetime.now().isoformat()
                }

        # Upload back
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=json.dumps(data)
        )

    def get_slots(self):
        # Download existing
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=self.key)
            data = json.loads(obj['Body'].read())
        except:
            data = {'slots': {}}
        return data

