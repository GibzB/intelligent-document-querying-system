# Intelligent Document Querying System

AWS Bedrock-powered document querying system with Aurora PostgreSQL vector database.

## Project Structure

```
project-root/
│
├── stack1/                    # VPC, Aurora Serverless, S3
│   ├── main.tf
│   ├── outputs.tf
│   └── variables.tf
│
├── stack2/                    # Bedrock Knowledge Base
│   ├── main.tf
│   ├── outputs.tf
│   └── variables.tf
│
├── modules/
│   ├── vpc/
│   ├── aurora_serverless/
│   ├── s3/
│   └── bedrock_kb/
│
├── scripts/
│   ├── aurora_sql.sql
│   └── upload_to_s3.py
│
├── spec-sheets/               # Place your PDF files here
│
├── python/                    # Complete Python utilities
│   ├── bedrock_utils.py
│   ├── lambda_function.py
│   ├── requirements.txt
│   └── test_valid_prompt.py
│
└── README.md
```

## Features

- **Modular Terraform Architecture**: Separated into reusable modules
- **Two-Stack Deployment**: Infrastructure and Bedrock components
- **Aurora PostgreSQL Serverless**: Vector database with pgvector
- **S3 Document Storage**: Secure document repository
- **Bedrock Knowledge Base**: AI-powered document querying
- **Enhanced Python Utilities**: Complete with validation and error handling

## Deployment Steps

### Step 1: Deploy Infrastructure Stack

1. **Navigate to Stack 1** (VPC, Aurora, S3):
   ```bash
   cd stack1
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Review and modify variables** in `variables.tf` as needed:
   - AWS region
   - VPC CIDR block
   - Aurora Serverless configuration
   - S3 bucket settings

4. **Deploy the infrastructure**:
   ```bash
   terraform apply
   ```
   Review the planned changes and type "yes" to confirm.

5. **Note the outputs**, particularly:
   - Aurora cluster ARN
   - Aurora cluster endpoint
   - S3 bucket ARN
   - RDS secret ARN

### Step 2: Prepare Aurora Database

1. **Run the SQL setup script** using Aurora Query Editor or psql:
   ```bash
   # Use the SQL commands in scripts/aurora_sql.sql
   ```

2. **Update the bedrock user password** in the script with the actual password from Secrets Manager:
   ```bash
   aws secretsmanager get-secret-value --secret-id [bedrock-user-secret] --region us-east-1
   ```

### Step 3: Deploy Bedrock Knowledge Base Stack

1. **Navigate to Stack 2**:
   ```bash
   cd ../stack2
   ```

2. **Initialize Terraform**:
   ```bash
   terraform init
   ```

3. **Update variables** in `variables.tf` with outputs from Stack 1:
   - `aurora_cluster_arn`
   - `documents_bucket_arn`
   - `rds_secret_arn`

4. **Deploy the Bedrock components**:
   ```bash
   terraform apply
   ```

### Step 4: Upload Documents and Sync

1. **Place your PDF files** in the `spec-sheets/` folder

2. **Update the S3 upload script** with your bucket name:
   ```python
   # Edit scripts/upload_to_s3.py
   bucket_name = "your-bucket-name-here"
   ```

3. **Upload documents to S3**:
   ```bash
   python scripts/upload_to_s3.py
   ```

4. **Sync the Knowledge Base**:
   - Go to AWS Console → Bedrock → Knowledge Bases
   - Find your knowledge base → Data sources
   - Click "Sync" to process uploaded documents

## Using the Python Utilities

The enhanced Python utilities include:

### Enhanced Functions
- `query_knowledge_base(query, kb_id)`: Query with error handling
- `generate_response(prompt, model_id, temperature, top_p, max_tokens)`: Generate responses with validation
- `valid_prompt(prompt, model_id)`: AI-powered prompt classification

### Testing
```bash
cd python
python3 test_valid_prompt.py
```

## Troubleshooting

- **Permissions issues**: Ensure AWS credentials have necessary permissions
- **Database connection**: Check security group allows port 5432 access
- **S3 upload failures**: Verify write permissions to S3 bucket
- **Terraform errors**: Ensure compatible version and correct module sources
- **Bedrock access**: Ensure models are enabled in Bedrock console

## Cost Optimization

- Aurora Serverless scales to zero when not in use
- Use `terraform destroy` when not actively testing
- Monitor usage in AWS Cost Explorer
- Consider using smaller instance types for development
