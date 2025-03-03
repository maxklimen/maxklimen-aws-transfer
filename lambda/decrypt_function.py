import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda function that decrypts files uploaded to S3 via AWS Transfer Family.
    
    Args:
        event: The event dict from EventBridge
        context: Lambda context
    
    Returns:
        dict: Response with status and details
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract bucket and key information from the event
        # For S3 events through EventBridge
        if 'detail' in event and 'bucket' in event['detail'] and 'object' in event['detail']:
            bucket_name = event['detail']['bucket']['name']
            object_key = event['detail']['object']['key']
        else:
            logger.error("Invalid event structure: Missing required fields")
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid event structure')
            }
        
        logger.info(f"Processing file s3://{bucket_name}/{object_key}")
        
        # Skip processing already decrypted files to avoid recursion
        if object_key.startswith('decrypted/'):
            logger.info(f"Skipping already decrypted file: {object_key}")
            return {
                'statusCode': 200,
                'body': json.dumps('File already decrypted, skipping')
            }
        
        # Download the encrypted file
        download_path = f"/tmp/{os.path.basename(object_key)}"
        s3_client.download_file(bucket_name, object_key, download_path)
        logger.info(f"Downloaded file to {download_path}")
        
        # Perform decryption (mock implementation)
        decrypted_path = decrypt_file(download_path)
        logger.info(f"Decrypted file saved at {decrypted_path}")
        
        # Upload the decrypted file back to S3
        decrypted_key = f"decrypted/{object_key}"
        s3_client.upload_file(decrypted_path, bucket_name, decrypted_key)
        logger.info(f"Uploaded decrypted file to s3://{bucket_name}/{decrypted_key}")
        
        # Clean up temporary files
        os.remove(download_path)
        os.remove(decrypted_path)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File decryption successful',
                'source': {
                    'bucket': bucket_name,
                    'key': object_key
                },
                'destination': {
                    'bucket': bucket_name,
                    'key': decrypted_key
                }
            })
        }
        
    except ClientError as e:
        logger.error(f"S3 error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error processing S3 object: {str(e)}")
        }
    except Exception as e:
        logger.error(f"Error decrypting file: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error decrypting file: {str(e)}")
        }

def decrypt_file(file_path):
    """
    Mock decryption function. In a real-world scenario, this would
    implement actual decryption logic such as PGP, AES, etc.
    
    Args:
        file_path: Path to the encrypted file
        
    Returns:
        str: Path to the decrypted file
    """
    output_path = f"{file_path}.decrypted"
    
    # For demonstration purposes, we're just copying the file
    # In a real implementation, this would decrypt the file
    with open(file_path, 'rb') as src_file:
        with open(output_path, 'wb') as dest_file:
            # In a real implementation, this would be:
            # dest_file.write(decrypt(src_file.read()))
            dest_file.write(src_file.read())
    
    logger.info(f"Mock decryption completed for {file_path}")
    return output_path

# For local testing
if __name__ == "__main__":
    # Test event structure similar to what EventBridge would send
    test_event = {
        "detail": {
            "bucket": {
                "name": "test-bucket"
            },
            "object": {
                "key": "incoming/test-file.txt"
            }
        }
    }
    
    print(lambda_handler(test_event, None)) 