import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the function
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda'))
import decrypt_function

class TestLambdaFunction(unittest.TestCase):
    """Test cases for the decrypt_function Lambda."""

    @patch('decrypt_function.s3_client')
    def test_successful_decryption(self, mock_s3_client):
        """Test the successful decryption path."""
        # Mock S3 download and upload
        mock_s3_client.download_file = MagicMock()
        mock_s3_client.upload_file = MagicMock()
        
        # Create a mock event
        event = {
            "detail": {
                "bucket": {
                    "name": "test-bucket"
                },
                "object": {
                    "key": "incoming/test-file.txt"
                }
            }
        }
        
        # Mock file operations
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'test data')):
            with patch('os.remove'):
                # Call the function
                response = decrypt_function.lambda_handler(event, None)
                
                # Verify response
                self.assertEqual(response['statusCode'], 200)
                response_body = json.loads(response['body'])
                self.assertEqual(response_body['message'], 'File decryption successful')
                
                # Verify S3 operations
                mock_s3_client.download_file.assert_called_once_with(
                    'test-bucket', 'incoming/test-file.txt', '/tmp/test-file.txt'
                )
                mock_s3_client.upload_file.assert_called_once()

    @patch('decrypt_function.s3_client')
    def test_already_decrypted_file(self, mock_s3_client):
        """Test skipping already decrypted files."""
        # Create a mock event with a file in the decrypted folder
        event = {
            "detail": {
                "bucket": {
                    "name": "test-bucket"
                },
                "object": {
                    "key": "decrypted/incoming/test-file.txt"
                }
            }
        }
        
        # Call the function
        response = decrypt_function.lambda_handler(event, None)
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('already decrypted', response['body'])
        
        # Verify no S3 operations were called
        mock_s3_client.download_file.assert_not_called()
        mock_s3_client.upload_file.assert_not_called()

    @patch('decrypt_function.s3_client')
    def test_invalid_event_structure(self, mock_s3_client):
        """Test handling invalid event structure."""
        # Create an invalid event
        event = {
            "wrong_format": True
        }
        
        # Call the function
        response = decrypt_function.lambda_handler(event, None)
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('Invalid event structure', response['body'])
        
        # Verify no S3 operations were called
        mock_s3_client.download_file.assert_not_called()
        mock_s3_client.upload_file.assert_not_called()

    @patch('decrypt_function.s3_client')
    def test_s3_client_error(self, mock_s3_client):
        """Test handling S3 client errors."""
        # Mock S3 download to raise an exception
        mock_s3_client.download_file.side_effect = Exception("S3 error")
        
        # Create a mock event
        event = {
            "detail": {
                "bucket": {
                    "name": "test-bucket"
                },
                "object": {
                    "key": "incoming/test-file.txt"
                }
            }
        }
        
        # Call the function
        response = decrypt_function.lambda_handler(event, None)
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Error', response['body'])

if __name__ == '__main__':
    unittest.main() 