---
name: Security & Vulnerability Testing
skill_id: security-testing
version: 1.0.0
description: Production-grade security testing with agentic vulnerability detection, SAST/DAST tools, OWASP Top 10 coverage, threat modeling, and AI-powered security analysis achieving 92% detection accuracy (OpenAI Aardvark benchmark 2024)
category: Security & Testing
tags:
  - security
  - vulnerability-testing
  - penetration-testing
  - owasp
  - sast
  - dast
  - threat-modeling
  - security-automation
  - ai-security
  - code-review
author: mcp-skillset
license: MIT
created: 2025-11-25
last_updated: 2025-11-25
toolchain:
  - OWASP ZAP
  - Snyk
  - Bandit (Python)
  - GitGuardian
  - Checkov (IaC)
frameworks:
  - OWASP Testing Framework
  - STRIDE Threat Modeling
  - MITRE ATT&CK
related_skills:
  - test-driven-development
  - systematic-debugging
  - fastapi-web-development
  - terraform-infrastructure
---

# Security & Vulnerability Testing

## Overview

Master security testing with AI-powered vulnerability detection, automated SAST/DAST scanning, and threat modeling. OpenAI's Aardvark achieves 92% vulnerability detection accuracy (2024), and multi-agent security tools find 4x more vulnerabilities than traditional scanners.

## When to Use This Skill

- Performing security audits on web applications and APIs
- Identifying OWASP Top 10 vulnerabilities before production
- Implementing security gates in CI/CD pipelines
- Conducting threat modeling for new features
- Reviewing code for security anti-patterns
- Testing authentication and authorization logic
- Scanning infrastructure as code for misconfigurations
- Preparing for penetration testing or security compliance

## Core Principles

### 1. OWASP Top 10 (2021) Coverage

```python
# A01:2021 – Broken Access Control
# ❌ BAD: Missing authorization check
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int):
    return await db.get(User, user_id)  # Anyone can access any profile!

# ✅ GOOD: Verify user authorization
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Forbidden")
    return await db.get(User, user_id)

# A02:2021 – Cryptographic Failures
# ❌ BAD: Weak password hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # NEVER USE MD5!

# ✅ GOOD: Strong password hashing with bcrypt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
password_hash = pwd_context.hash(password)

# A03:2021 – Injection
# ❌ BAD: SQL injection vulnerability
query = f"SELECT * FROM users WHERE email = '{email}'"  # NEVER!
cursor.execute(query)

# ✅ GOOD: Parameterized queries
query = "SELECT * FROM users WHERE email = %s"
cursor.execute(query, (email,))

# Or use ORM (SQLAlchemy, Django ORM)
user = await db.execute(select(User).where(User.email == email))

# A04:2021 – Insecure Design
# ✅ Implement rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/login")
@limiter.limit("5/minute")
async def login(credentials: LoginRequest):
    # Prevent brute force attacks
    pass

# A05:2021 – Security Misconfiguration
# ❌ BAD: Debug mode in production
app = FastAPI(debug=True)  # NEVER in production!

# ✅ GOOD: Environment-aware configuration
app = FastAPI(debug=settings.DEBUG)

# A06:2021 – Vulnerable and Outdated Components
# ✅ Run: pip-audit, snyk test, npm audit

# A07:2021 – Identification and Authentication Failures
# ✅ Use OAuth2 with JWT, implement MFA

# A08:2021 – Software and Data Integrity Failures
# ✅ Sign releases, verify checksums, use SRI for CDN resources

# A09:2021 – Security Logging and Monitoring Failures
# ✅ Log all authentication attempts, failed access, sensitive operations

# A10:2021 – Server-Side Request Forgery (SSRF)
# ❌ BAD: Unchecked URL fetching
url = request.json.get("url")
response = await httpx.get(url)  # Can access internal services!

# ✅ GOOD: Whitelist allowed domains
ALLOWED_DOMAINS = ["api.example.com", "cdn.example.com"]

def is_safe_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc in ALLOWED_DOMAINS

if not is_safe_url(url):
    raise HTTPException(400, "Invalid URL")
```

### 2. Static Analysis Security Testing (SAST)

```bash
# Python: Bandit
pip install bandit
bandit -r ./app -f json -o security-report.json

# Example issues Bandit detects:
# - Hardcoded passwords
# - Use of eval() or exec()
# - SQL injection risks
# - Weak cryptography

# JavaScript/TypeScript: ESLint Security Plugin
npm install --save-dev eslint-plugin-security
# Add to .eslintrc.json:
# "plugins": ["security"]

# Infrastructure: Checkov (Terraform, CloudFormation, Kubernetes)
pip install checkov
checkov -d ./terraform --output json

# Secrets: GitGuardian or detect-secrets
pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline

# Multi-language: Snyk
npm install -g snyk
snyk test
snyk code test  # SAST
snyk container test myapp:latest  # Container scanning
```

**SAST Integration in CI/CD**:
```yaml
# GitHub Actions
- name: Run Bandit Security Scan
  run: |
    pip install bandit
    bandit -r . -f json -o bandit-report.json
  continue-on-error: true

- name: Upload Security Report
  uses: actions/upload-artifact@v3
  with:
    name: security-reports
    path: bandit-report.json
```

### 3. Dynamic Analysis Security Testing (DAST)

```bash
# OWASP ZAP (Zed Attack Proxy)
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://example.com \
  -r zap-report.html

# Nikto (web server scanner)
nikto -h https://example.com -o nikto-report.txt

# Nuclei (fast vulnerability scanner)
nuclei -u https://example.com -t ~/nuclei-templates/

# Burp Suite (commercial, GUI-based)
# Manual testing and automated scanning
```

**DAST Best Practices**:
- Run against staging environment, not production
- Use authenticated scans (provide session cookies)
- Schedule regular scans (weekly or per deployment)
- Combine with SAST for comprehensive coverage

### 4. Threat Modeling with STRIDE

```
STRIDE Framework (Microsoft):

S - Spoofing Identity
  ✅ Use multi-factor authentication
  ✅ Implement certificate pinning
  ❌ Never trust client-provided identity

T - Tampering with Data
  ✅ Use HTTPS/TLS for all communication
  ✅ Implement request signing (HMAC)
  ❌ Never accept unsigned data from clients

R - Repudiation
  ✅ Log all critical operations with timestamps
  ✅ Implement audit trails
  ❌ Never allow users to deny actions

I - Information Disclosure
  ✅ Encrypt sensitive data at rest and in transit
  ✅ Implement proper access controls
  ❌ Never expose internal error details

D - Denial of Service
  ✅ Implement rate limiting and throttling
  ✅ Use CDN and DDoS protection (Cloudflare)
  ❌ Never allow unbounded resource consumption

E - Elevation of Privilege
  ✅ Follow principle of least privilege
  ✅ Validate permissions at every access point
  ❌ Never trust user roles from client
```

**Threat Modeling Process**:
1. Diagram system architecture (data flows)
2. Identify threats using STRIDE for each component
3. Prioritize threats (likelihood × impact)
4. Mitigate high-priority threats
5. Validate mitigations with testing

### 5. Secret Management

```python
# ❌ BAD: Secrets in code
API_KEY = "sk-1234567890abcdef"  # NEVER!
DATABASE_URL = "postgresql://user:pass@host/db"

# ❌ BAD: Secrets in version control
# .env file committed to git

# ✅ GOOD: Environment variables (12-factor app)
import os
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ GOOD: Secret management services
# AWS Secrets Manager
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/api-key')
API_KEY = secret['SecretString']

# HashiCorp Vault
import hvac
client = hvac.Client(url='http://vault:8200', token=vault_token)
secret = client.secrets.kv.v2.read_secret_version(path='api-key')
API_KEY = secret['data']['data']['key']

# Kubernetes Secrets
# Mounted as files or environment variables
```

**Secret Scanning**:
```bash
# GitGuardian (detects 500+ secret types)
pip install ggshield
ggshield secret scan path .

# TruffleHog (git history scanning)
docker run -it trufflesecurity/trufflehog:latest github --repo https://github.com/myorg/myrepo

# Gitleaks
gitleaks detect --source . --report-path gitleaks-report.json
```

## Security Testing Checklist

### Authentication & Authorization
- ✅ Password strength requirements enforced
- ✅ Rate limiting on login endpoints (5 attempts/minute)
- ✅ MFA available for sensitive operations
- ✅ JWT tokens expire (15-60 minutes)
- ✅ Refresh tokens rotated on use
- ✅ Authorization checked on every endpoint
- ✅ Session invalidated on logout
- ✅ CSRF tokens implemented for state-changing operations

### Input Validation
- ✅ All inputs validated (length, type, format)
- ✅ Parameterized queries (no string concatenation)
- ✅ File upload restrictions (type, size, virus scanning)
- ✅ HTML/JavaScript sanitized before rendering
- ✅ URL validation (whitelist allowed domains)
- ✅ API rate limiting per user/IP

### Data Protection
- ✅ HTTPS/TLS 1.2+ enforced
- ✅ Sensitive data encrypted at rest (AES-256)
- ✅ Passwords hashed with bcrypt/argon2
- ✅ PII minimized and properly protected
- ✅ Database backups encrypted
- ✅ Secure cookie flags (HttpOnly, Secure, SameSite)

### Infrastructure
- ✅ Firewall rules follow least privilege
- ✅ Security groups/network policies configured
- ✅ Unused services disabled
- ✅ Regular security patches applied
- ✅ Secrets not in version control
- ✅ Container images scanned for vulnerabilities

### Logging & Monitoring
- ✅ Failed authentication attempts logged
- ✅ Authorization failures logged
- ✅ Sensitive operations audited
- ✅ Security alerts configured
- ✅ Logs centralized and tamper-proof
- ✅ GDPR/compliance requirements met

## AI-Powered Security Testing (2024)

### OpenAI Aardvark Architecture
```
Agentic Security Testing Workflow:

1. Code Analysis
   - Read codebase and understand behavior
   - Identify potential vulnerability surfaces

2. Test Generation
   - Generate test cases targeting vulnerabilities
   - Create exploit attempts

3. Test Execution
   - Run tests in sandbox environment
   - Observe application behavior

4. Reasoning Loop
   - Analyze results
   - Generate new hypotheses
   - Iterate until vulnerability confirmed or ruled out

Benchmark: 92% detection rate on synthetic vulnerabilities
```

### Multi-Agent Security (SecureVibes)
```
Agent Roles:
1. Architecture Mapper: Build system model
2. Threat Modeler: Apply STRIDE framework
3. Code Reviewer: Static analysis with AI reasoning
4. Penetration Tester: Generate and execute exploits

Result: 16-17 vulnerabilities found (4x vs single-agent)
```

## Common Vulnerabilities & Fixes

### SQL Injection
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)

# ✅ Fixed
query = "SELECT * FROM users WHERE id = %s"
db.execute(query, (user_id,))
```

### Cross-Site Scripting (XSS)
```javascript
// ❌ Vulnerable
document.innerHTML = userInput;

// ✅ Fixed
document.textContent = userInput;
// Or use a sanitization library
import DOMPurify from 'dompurify';
document.innerHTML = DOMPurify.sanitize(userInput);
```

### Insecure Direct Object Reference (IDOR)
```python
# ❌ Vulnerable
@app.get("/files/{file_id}")
async def download(file_id: int):
    return FileResponse(f"/uploads/{file_id}.pdf")

# ✅ Fixed
@app.get("/files/{file_id}")
async def download(file_id: int, user: User = Depends(get_current_user)):
    file = await db.get(File, file_id)
    if file.owner_id != user.id:
        raise HTTPException(403, "Forbidden")
    return FileResponse(file.path)
```

### XML External Entity (XXE)
```python
# ❌ Vulnerable
import xml.etree.ElementTree as ET
tree = ET.parse(user_uploaded_xml)

# ✅ Fixed
from defusedxml.ElementTree import parse
tree = parse(user_uploaded_xml)
```

## Penetration Testing Workflow

```bash
# 1. Reconnaissance
nmap -sV -sC target.com
whatweb target.com
whois target.com

# 2. Vulnerability Scanning
nuclei -u https://target.com -t ~/nuclei-templates/
nikto -h https://target.com

# 3. Exploitation (ethical, authorized only!)
# Use Metasploit, Burp Suite, custom scripts

# 4. Post-Exploitation
# Document findings, severity, remediation

# 5. Reporting
# Create detailed report with PoC, impact, fixes
```

## Security Code Review Guidelines

```python
# Security-focused code review checklist:

# 1. Authentication
# - Are passwords hashed properly?
# - Is rate limiting implemented?
# - Are sessions managed securely?

# 2. Authorization
# - Is every endpoint protected?
# - Are permissions checked correctly?
# - Can users access other users' data?

# 3. Input Validation
# - Are all inputs validated?
# - Is SQL injection prevented?
# - Is XSS prevented?

# 4. Output Encoding
# - Is user data sanitized before display?
# - Are error messages generic?

# 5. Cryptography
# - Are modern algorithms used (AES-256, RSA-2048+)?
# - Are keys stored securely?
# - Is HTTPS enforced?

# 6. Error Handling
# - Are exceptions caught and logged?
# - Do error messages leak information?

# 7. Logging
# - Are security events logged?
# - Are logs protected from tampering?
```

## Related Skills

- **test-driven-development**: Write security tests first
- **systematic-debugging**: Debug security issues systematically
- **fastapi-web-development**: Secure FastAPI applications
- **terraform-infrastructure**: Scan IaC for security issues

## Additional Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten
- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide
- OWASP ZAP: https://www.zaproxy.org
- Snyk: https://snyk.io
- GitGuardian: https://www.gitguardian.com
- OpenAI Aardvark (2024): https://openai.com/index/agentic-ai-for-security-research

## Example Questions

- "How do I prevent SQL injection in this endpoint?"
- "Scan this code for OWASP Top 10 vulnerabilities"
- "Show me how to implement rate limiting for authentication"
- "How do I securely store API keys in production?"
- "What's the difference between SAST and DAST?"
- "Perform a threat model using STRIDE for this feature"
- "How do I detect secrets accidentally committed to git?"
