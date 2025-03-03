# Architecture Diagram

This is a text representation of the architecture. Replace this with an actual diagram before final submission.

```
┌───────────────┐     ┌────────────────┐     ┌────────────────┐     ┌───────────────┐
│  SFTP Client  │────▶│  AWS Transfer  │────▶│  S3 Bucket     │────▶│  EventBridge  │
└───────────────┘     │  Family Server │     │  (encrypted)   │     │  Rule         │
                      └────────────────┘     └────────────────┘     └───────┬───────┘
                                                                            │
                                                                            ▼
                     ┌────────────────┐      ┌───────────────┐      ┌───────────────┐
                     │  S3 Bucket     │◀─────│  Lambda       │◀─────│  EventBridge  │
                     │  (decrypted)   │      │  Function     │      │  Event        │
                     └────────────────┘      └───────────────┘      └───────────────┘
```

## Flow Description

1. **SFTP Client uploads file**: A user uploads an encrypted file to the AWS Transfer SFTP server.
2. **File stored in S3**: The file is automatically stored in the Amazon S3 bucket in an "encrypted" state.
3. **EventBridge rule triggered**: When the file is uploaded to S3, an event is sent to Amazon EventBridge.
4. **Lambda function invoked**: EventBridge triggers the Lambda function.
5. **File decryption**: The Lambda function downloads the file, decrypts it, and uploads the decrypted file back to S3 with a prefix "decrypted/".

## AWS Services Used

- **AWS Transfer Family**: Provides SFTP service for secure file uploads
- **Amazon S3**: Stores both encrypted and decrypted files
- **Amazon EventBridge**: Detects and routes events when files are uploaded to S3
- **AWS Lambda**: Performs the file decryption logic
- **IAM**: Provides necessary permissions for each service

## Security Considerations

- All components use IAM roles with least privilege permissions
- SFTP server requires SSH key authentication
- S3 bucket blocks all public access
- Lambda has access only to the specific S3 bucket needed for operation

This architecture is deployed as a CloudFormation stack, enabling consistent and repeatable deployments across multiple environments. 