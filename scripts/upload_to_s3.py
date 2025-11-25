#!/usr/bin/env python3
"""
S3 Upload Script for Heavy Machinery Spec Sheets
Uploads all files from spec-sheets folder to S3 bucket
"""

import os
import boto3
from botocore.exceptions import ClientError
import mimetypes

# Configuration - UPDATE THESE VALUES
bucket_name = "doc-query-system-dev-documents-471848907879"  # Update with your bucket name
prefix = ""  # Optional: specify a folder path in S3
local_folder = "../spec-sheets"  # Path to local spec-sheets folder

def upload_files_to_s3():
    """Upload all files from spec-sheets folder to S3"""
    
    # Initialize S3 client
    s3_client = boto3.client('s3', region_name='us-east-1')
    
    # Check if local folder exists
    if not os.path.exists(local_folder):
        print(f"Error: Local folder '{local_folder}' does not exist")
        return False
    
    # Get list of files to upload
    files_to_upload = []
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            # Create S3 key maintaining folder structure
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = os.path.join(prefix, relative_path).replace('\\', '/') if prefix else relative_path.replace('\\', '/')
            files_to_upload.append((local_path, s3_key))
    
    if not files_to_upload:
        print(f"No files found in '{local_folder}'")
        return False
    
    print(f"Found {len(files_to_upload)} files to upload to bucket '{bucket_name}'")
    
    # Upload files
    success_count = 0
    for local_path, s3_key in files_to_upload:
        try:
            # Determine content type
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type is None:
                content_type = 'binary/octet-stream'
            
            # Upload file
            print(f"Uploading: {local_path} -> s3://{bucket_name}/{s3_key}")
            
            extra_args = {'ContentType': content_type}
            s3_client.upload_file(local_path, bucket_name, s3_key, ExtraArgs=extra_args)
            
            success_count += 1
            print(f"✓ Successfully uploaded: {s3_key}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"✗ Failed to upload {local_path}: {error_code} - {e.response['Error']['Message']}")
        except Exception as e:
            print(f"✗ Unexpected error uploading {local_path}: {str(e)}")
    
    print(f"\nUpload complete: {success_count}/{len(files_to_upload)} files uploaded successfully")
    
    if success_count > 0:
        print(f"\nNext steps:")
        print(f"1. Go to AWS Console -> Bedrock -> Knowledge Bases")
        print(f"2. Find your knowledge base and go to Data sources")
        print(f"3. Click 'Sync' to process the uploaded documents")
    
    return success_count == len(files_to_upload)

def list_bucket_contents():
    """List current contents of the S3 bucket"""
    try:
        s3_client = boto3.client('s3', region_name='us-east-1')
        
        print(f"\nCurrent contents of bucket '{bucket_name}':")
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("  (bucket is empty)")
            
    except ClientError as e:
        print(f"Error listing bucket contents: {e.response['Error']['Message']}")

if __name__ == "__main__":
    print("S3 Upload Script for Heavy Machinery Spec Sheets")
    print("=" * 50)
    
    # Verify bucket name is updated
    if "UPDATE_WITH_YOUR_BUCKET" in bucket_name:
        print("ERROR: Please update the 'bucket_name' variable with your actual S3 bucket name")
        exit(1)
    
    # Upload files
    success = upload_files_to_s3()
    
    # List bucket contents
    list_bucket_contents()
    
    if success:
        print("\n✓ All files uploaded successfully!")
    else:
        print("\n⚠ Some files failed to upload. Check the error messages above.")