---
name: Terraform Infrastructure as Code
skill_id: terraform-infrastructure
version: 1.0.0
description: Production-grade Terraform development with HCL best practices, module design, state management, multi-cloud patterns, and AI-enhanced infrastructure as code for scalable cloud deployments
category: DevOps & Infrastructure
tags:
  - terraform
  - infrastructure-as-code
  - iac
  - devops
  - cloud
  - aws
  - azure
  - gcp
  - multi-cloud
  - state-management
  - modules
author: mcp-skillset
license: MIT
created: 2025-11-25
last_updated: 2025-11-25
toolchain:
  - Terraform 1.5+
  - HCL
  - terraform-docs
  - tflint
  - checkov
frameworks:
  - Terraform
  - Terragrunt (optional)
  - Atlantis (optional)
related_skills:
  - aws-cdk-development
  - systematic-debugging
  - security-testing
  - test-driven-development
---

# Terraform Infrastructure as Code

## Overview

This skill provides comprehensive guidance for building production-grade infrastructure with Terraform following 2024-2025 best practices. Terraform is the industry standard for Infrastructure as Code (IaC), enabling version-controlled, reproducible, and automated cloud infrastructure management across AWS, Azure, GCP, and 100+ providers.

## When to Use This Skill

Use this skill when:
- Provisioning cloud infrastructure (compute, storage, networking, databases)
- Managing multi-environment deployments (dev, staging, production)
- Implementing immutable infrastructure patterns
- Orchestrating complex multi-cloud architectures
- Automating infrastructure changes with CI/CD pipelines
- Creating reusable infrastructure modules for teams
- Migrating from manual cloud console provisioning to IaC

## Core Principles

### 1. State Management is Critical
**Terraform state is the source of truth - protect it**

```hcl
# CORRECT: Remote state with locking
terraform {
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "prod/vpc/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"  # Prevents concurrent modifications

    # State versioning for recovery
    versioning = true
  }
}

# WRONG: Local state in production
# terraform {
#   backend "local" {
#     path = "terraform.tfstate"  # Never use local state in teams!
#   }
# }
```

**State Best Practices**:
- ✅ Always use remote state backends (S3, Azure Blob, GCS, Terraform Cloud)
- ✅ Enable state locking to prevent concurrent runs
- ✅ Enable encryption at rest for sensitive data
- ✅ Use versioning for state file recovery
- ✅ Separate state files per environment and major component
- ❌ Never commit `.tfstate` files to version control
- ❌ Never share state files via email or Slack

### 2. Module Design for Reusability
**Build composable, tested modules with clear interfaces**

```hcl
# modules/vpc/main.tf - Well-designed module
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be valid IPv4 CIDR block"
  }
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod"
  }
}

variable "tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    {
      Name        = "${var.environment}-vpc"
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.tags
  )
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

# Usage in root module
module "vpc" {
  source = "./modules/vpc"

  vpc_cidr    = "10.0.0.0/16"
  environment = "prod"
  tags = {
    Team    = "platform"
    Project = "myapp"
  }
}
```

**Module Design Checklist**:
- ✅ Single responsibility - one purpose per module
- ✅ Input validation with variable validation blocks
- ✅ Descriptive variable names and descriptions
- ✅ Sensible defaults where appropriate
- ✅ Outputs for all important resource attributes
- ✅ README.md with examples and terraform-docs
- ✅ Versioning for published modules

### 3. Resource Naming and Tagging
**Consistent naming prevents confusion and enables automation**

```hcl
locals {
  # Standardized naming convention
  name_prefix = "${var.project}-${var.environment}"

  # Common tags applied to all resources
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
    Team        = var.team
    CostCenter  = var.cost_center
    CreatedAt   = timestamp()
  }
}

resource "aws_instance" "app_server" {
  # Clear, consistent naming
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-app-server"
      Role = "application"
    }
  )
}

resource "aws_s3_bucket" "data" {
  # DNS-compliant naming
  bucket = "${local.name_prefix}-data-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    local.common_tags,
    {
      Name       = "${local.name_prefix}-data-bucket"
      DataClass  = "sensitive"
      Encryption = "required"
    }
  )
}
```

**Naming Conventions**:
- Use lowercase with hyphens: `myapp-prod-web-server`
- Include environment: `dev-`, `staging-`, `prod-`
- Add resource type suffix: `-vpc`, `-subnet`, `-sg`
- Ensure uniqueness where required (S3 buckets)

### 4. Data Sources vs Resources
**Use data sources to reference existing infrastructure**

```hcl
# CORRECT: Use data source for existing resources
data "aws_vpc" "existing" {
  tags = {
    Name = "legacy-vpc"
  }
}

resource "aws_subnet" "new_subnet" {
  vpc_id     = data.aws_vpc.existing.id  # Reference existing VPC
  cidr_block = "10.0.100.0/24"
}

# CORRECT: Use data sources for AMIs, availability zones
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

# WRONG: Don't import existing resources unless migrating
# resource "aws_vpc" "imported" {
#   # This will try to CREATE, not reference
#   cidr_block = "10.0.0.0/16"
# }
```

### 5. Variable Hierarchy and Precedence
**Understand variable precedence for flexible configuration**

```hcl
# 1. variables.tf - Define with defaults
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

# 2. terraform.tfvars - Common values
instance_type = "t3.small"

# 3. prod.tfvars - Environment-specific
# terraform apply -var-file="prod.tfvars"
instance_type = "t3.large"

# 4. Environment variables - CI/CD pipelines
# export TF_VAR_instance_type="t3.xlarge"

# 5. CLI flags - Highest precedence
# terraform apply -var="instance_type=t3.2xlarge"

# Precedence order (highest to lowest):
# CLI -var > Environment TF_VAR_ > .tfvars files > defaults
```

## Best Practices

### Project Structure
```
terraform-project/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   ├── staging/
│   │   └── ... (same structure)
│   └── prod/
│       └── ... (same structure)
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── README.md
│   │   └── versions.tf
│   ├── compute/
│   │   └── ...
│   └── database/
│       └── ...
├── global/
│   ├── iam/
│   │   └── main.tf
│   └── route53/
│       └── main.tf
├── .tflint.hcl
├── .terraform-version
└── README.md
```

### Dependency Management
```hcl
# CORRECT: Explicit depends_on for non-obvious dependencies
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_logging.arn
}

resource "aws_lambda_function" "app" {
  # Lambda needs policy attached before creation
  depends_on = [aws_iam_role_policy_attachment.lambda_logs]

  function_name = "my-function"
  role          = aws_iam_role.lambda.arn
  # ...
}

# CORRECT: Use implicit dependencies via references
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id  # Implicit dependency on VPC
  cidr_block = "10.0.1.0/24"
}

# WRONG: Unnecessary explicit depends_on
resource "aws_subnet" "bad_example" {
  vpc_id     = aws_vpc.main.id
  depends_on = [aws_vpc.main]  # Redundant! Reference creates dependency
  cidr_block = "10.0.2.0/24"
}
```

### Conditional Resources
```hcl
variable "create_database" {
  description = "Whether to create RDS database"
  type        = bool
  default     = true
}

variable "environment" {
  type = string
}

# Create resource conditionally
resource "aws_db_instance" "main" {
  count = var.create_database ? 1 : 0

  identifier     = "myapp-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.micro"
  # ...
}

# Reference conditional resource
output "database_endpoint" {
  value = var.create_database ? aws_db_instance.main[0].endpoint : null
}

# Dynamic blocks for repeated nested blocks
resource "aws_security_group" "app" {
  name   = "app-sg"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

### Lifecycle Management
```hcl
resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type

  lifecycle {
    # Create new resource before destroying old
    create_before_destroy = true

    # Prevent accidental deletion
    prevent_destroy = true

    # Ignore changes to specific attributes
    ignore_changes = [
      ami,  # Allow manual AMI updates
      tags["CreatedAt"],
    ]
  }
}

# Prevent deletion of critical resources
resource "aws_s3_bucket" "critical_data" {
  bucket = "critical-data-bucket"

  lifecycle {
    prevent_destroy = true
  }
}
```

## Common Patterns

### Multi-Environment with Workspaces
```hcl
# Use Terraform workspaces for environment separation
# terraform workspace new dev
# terraform workspace new prod

locals {
  environment = terraform.workspace

  # Environment-specific configuration
  config = {
    dev = {
      instance_type = "t3.micro"
      instance_count = 1
    }
    prod = {
      instance_type = "t3.large"
      instance_count = 3
    }
  }

  current_config = local.config[local.environment]
}

resource "aws_instance" "app" {
  count         = local.current_config.instance_count
  ami           = var.ami_id
  instance_type = local.current_config.instance_type

  tags = {
    Name        = "${local.environment}-app-${count.index}"
    Environment = local.environment
  }
}
```

### For_Each for Resource Sets
```hcl
# CORRECT: Use for_each for sets of similar resources
variable "availability_zones" {
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

locals {
  subnet_cidrs = {
    "us-east-1a" = "10.0.1.0/24"
    "us-east-1b" = "10.0.2.0/24"
    "us-east-1c" = "10.0.3.0/24"
  }
}

resource "aws_subnet" "private" {
  for_each = local.subnet_cidrs

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = each.key

  tags = {
    Name = "private-${each.key}"
  }
}

# Reference outputs from for_each
output "subnet_ids" {
  value = { for k, v in aws_subnet.private : k => v.id }
}
```

### Remote State Data Sources
```hcl
# Reference outputs from another Terraform state
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "myapp-terraform-state"
    key    = "prod/vpc/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_instance" "app" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = data.terraform_remote_state.vpc.outputs.private_subnet_ids[0]
}
```

### Null Resource for Provisioning
```hcl
resource "null_resource" "setup_cluster" {
  # Trigger on cluster configuration changes
  triggers = {
    cluster_id = aws_eks_cluster.main.id
    config_hash = md5(file("${path.module}/kubeconfig.yaml"))
  }

  provisioner "local-exec" {
    command = <<-EOT
      kubectl apply -f ${path.module}/manifests/
      helm install myapp ./charts/myapp
    EOT

    environment = {
      KUBECONFIG = aws_eks_cluster.main.kubeconfig
    }
  }
}
```

## Anti-Patterns to Avoid

### ❌ DON'T: Hardcode values
```hcl
# WRONG: Hardcoded configuration
resource "aws_instance" "app" {
  ami           = "ami-12345678"  # Will break in other regions!
  instance_type = "t3.micro"

  tags = {
    Environment = "production"  # Hardcoded environment
  }
}

# CORRECT: Use variables and data sources
data "aws_ami" "app" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "name"
    values = ["myapp-*"]
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.app.id
  instance_type = var.instance_type

  tags = merge(local.common_tags, {
    Name = "${var.environment}-app"
  })
}
```

### ❌ DON'T: Use count with lists that may reorder
```hcl
# WRONG: Count with list - reordering causes recreations
variable "instance_names" {
  default = ["web1", "web2", "web3"]
}

resource "aws_instance" "app" {
  count         = length(var.instance_names)
  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name = var.instance_names[count.index]
  }
}
# If you remove "web2", "web3" gets destroyed and recreated!

# CORRECT: Use for_each with map
variable "instances" {
  default = {
    web1 = { type = "t3.micro" }
    web2 = { type = "t3.small" }
    web3 = { type = "t3.micro" }
  }
}

resource "aws_instance" "app" {
  for_each = var.instances

  ami           = var.ami_id
  instance_type = each.value.type

  tags = {
    Name = each.key
  }
}
# Now you can safely add/remove instances without affecting others
```

### ❌ DON'T: Mix environments in same state
```hcl
# WRONG: All environments in one state file
# terraform apply  # Applies to dev AND prod!

# CORRECT: Separate directories and state files
# environments/dev/main.tf
# environments/prod/main.tf
```

### ❌ DON'T: Use local-exec for critical operations
```hcl
# WRONG: Critical operations in local-exec
resource "null_resource" "bad_db_init" {
  provisioner "local-exec" {
    command = "psql -c 'CREATE DATABASE app'"
  }
}
# If this fails, no error in Terraform!

# CORRECT: Use proper resources or automation tools
resource "postgresql_database" "app" {
  name = "app"
}
```

## Testing Strategy

```hcl
# 1. Validate syntax
# terraform validate

# 2. Format code
# terraform fmt -recursive

# 3. Plan before apply
# terraform plan -out=tfplan

# 4. Use Terratest for automated testing (Go)
package test

import (
    "testing"
    "github.com/gruntwork-io/terratest/modules/terraform"
    "github.com/stretchr/testify/assert"
)

func TestVPCCreation(t *testing.T) {
    terraformOptions := terraform.WithDefaultRetryableErrors(t, &terraform.Options{
        TerraformDir: "../modules/vpc",
        Vars: map[string]interface{}{
            "vpc_cidr": "10.0.0.0/16",
            "environment": "test",
        },
    })

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    vpcID := terraform.Output(t, terraformOptions, "vpc_id")
    assert.NotEmpty(t, vpcID)
}
```

## Security & Compliance

### Sensitive Data Handling
```hcl
# Mark sensitive outputs
output "database_password" {
  value     = random_password.db_password.result
  sensitive = true  # Hides from logs
}

# Use AWS Secrets Manager or Parameter Store
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/db/password"
}

resource "aws_db_instance" "main" {
  # ...
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}
```

### Policy as Code with Checkov
```bash
# Install checkov
pip install checkov

# Scan Terraform code
checkov -d ./terraform

# Example output:
# FAILED checks:
# - CKV_AWS_20: S3 Bucket has an ACL defined which allows public access
# - CKV_AWS_21: Ensure S3 bucket has versioning enabled
```

### Terraform Security Checklist
- ✅ Never commit sensitive values to version control
- ✅ Use encrypted remote state backend
- ✅ Enable MFA for state backend access
- ✅ Scan code with Checkov, tfsec, or Snyk
- ✅ Use least-privilege IAM roles for Terraform execution
- ✅ Review and approve plans before apply
- ✅ Use Sentinel or OPA for policy enforcement
- ✅ Rotate credentials regularly

## CI/CD Integration

```yaml
# GitHub Actions example
name: Terraform

on:
  push:
    branches: [main]
  pull_request:

jobs:
  terraform:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./environments/prod

    steps:
      - uses: actions/checkout@v3

      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.6.0

      - name: Terraform Format
        run: terraform fmt -check

      - name: Terraform Init
        run: terraform init
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Terraform Validate
        run: terraform validate

      - name: Terraform Plan
        run: terraform plan -out=tfplan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        run: terraform apply -auto-approve tfplan
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Multi-Cloud Patterns

```hcl
# Provider configuration for multi-cloud
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  alias  = "primary"
}

provider "azurerm" {
  features {}
  alias = "secondary"
}

# Use providers with aliases
resource "aws_s3_bucket" "primary" {
  provider = aws.primary
  bucket   = "myapp-primary-data"
}

resource "azurerm_storage_account" "secondary" {
  provider            = azurerm.secondary
  name                = "myappsecondarystorage"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}
```

## Related Skills

- **aws-cdk-development**: Alternative IaC with programming languages
- **systematic-debugging**: Debug Terraform state and plan issues
- **security-testing**: Security scanning of Terraform configurations
- **test-driven-development**: Test infrastructure code before deployment

## Additional Resources

- Terraform Documentation: https://developer.hashicorp.com/terraform/docs
- Terraform Registry: https://registry.terraform.io
- Terraform Best Practices: https://www.terraform-best-practices.com
- Terratest: https://terratest.gruntwork.io
- Checkov: https://www.checkov.io
- tfsec: https://aquasecurity.github.io/tfsec

## Example Questions to Ask

- "How do I structure a multi-environment Terraform project?"
- "What's the best way to manage Terraform state for a team?"
- "Show me how to create reusable modules with input validation"
- "How do I migrate existing AWS resources to Terraform?"
- "What's the difference between count and for_each?"
- "How do I implement a blue-green deployment with Terraform?"
- "Show me how to integrate Terraform with GitHub Actions"
