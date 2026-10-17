# AWS S3 Configuration

Castoria supports AWS S3 as a storage destination. Depending on your deployment environment, you can use:

- **IAM User:** For local development or external deployments using AWS access keys.
- **IAM Role:** Recommended for AWS-native deployments using temporary credentials.

## IAM Permissions

Attach the following IAM policy to the IAM User or IAM Role used by Castoria.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CastoriaS3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::<bucket-name>"
    },
    {
      "Sid": "CastoriaS3ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::<bucket-name>/<object-path>/*"
    }
  ]
}
```

Replace `<bucket-name>` and `<object-path>` with your S3 bucket name and the prefix where Castoria is allowed to upload files.

For example:

```text
s3://my-bucket/castoria/music/
```

To allow uploads across the entire bucket, use:

```text
arn:aws:s3:::<bucket-name>/*
```

> **Note:** Castoria currently requires `s3:PutObject` for uploading files. `s3:ListBucket` is optional for the current upload workflow. Additional permissions may be required depending on your bucket configuration, such as SSE-KMS encryption.

## IAM Role (AWS-Native Deployments)

For applications running on AWS infrastructure, attach the IAM policy to an appropriate IAM Role.

Boto3 automatically retrieves temporary credentials from supported AWS execution environments.

Follow the official AWS documentation:

- [Using IAM Roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)

For other AWS services, configure the appropriate execution role or task role.

## IAM User (Local or External Deployments)

For environments that require long-term credentials, create a dedicated IAM User and attach the IAM policy.

Follow the official AWS documentation:

- [Managing IAM User Access Keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-keys-admin-managed.html)

Avoid using AWS root account credentials.

## AWS CLI & Profiles

For local development, install AWS CLI and configure a named profile.

Official documentation:

- [Install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Configure Named Profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)

Create a named profile:

```bash
aws configure --profile castoria
```

Verify your credentials:

```bash
aws sts get-caller-identity --profile castoria
```

Run Castoria using the configured AWS profile:

```bash
AWS_PROFILE=castoria uv run castoria youtube-music download \
  --link "https://www.youtube.com/watch?v=VIDEO_ID" \
  --storage s3 \
  --dest "s3://my-bucket/castoria/music"
```
