# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Automated Security Scanning

This project uses multiple automated security scanning tools to identify and address vulnerabilities:

### 1. Dependabot (GitHub Native)

**What it does:**
- Automatically scans dependencies for known vulnerabilities
- Creates pull requests for security updates
- Runs weekly on Mondays at 9:00 AM EST
- Groups minor and patch updates for easier review

**Configuration:** `.github/dependabot.yml`

**How to use:**
- Review and merge Dependabot PRs promptly
- PRs are automatically labeled with `dependencies` and `security`
- Critical security updates are prioritized

### 2. Safety CLI

**What it does:**
- Scans Python dependencies against the Safety DB vulnerability database
- Checks for known security vulnerabilities in installed packages
- Provides detailed vulnerability reports with CVE information

**Usage:**
```bash
# Basic security scan
make security-check

# Comprehensive security audit with reports
make security-check-full

# Install security tools
make security-install
```

### 3. pip-audit

**What it does:**
- Audits Python packages for known vulnerabilities
- Uses the PyPA Advisory Database
- Provides detailed descriptions and remediation guidance

**Usage:**
```bash
# Included in security-check targets
make security-check
make security-check-full
```

### 4. Bandit

**What it does:**
- Static security analysis for Python code
- Identifies common security issues in code
- Checks for:
  - SQL injection vulnerabilities
  - Shell injection risks
  - Insecure cryptographic practices
  - Hardcoded passwords/secrets
  - Insecure deserialization

**Usage:**
```bash
# Full security audit includes Bandit
make security-check-full
```

### 5. detect-secrets

**What it does:**
- Prevents secrets from being committed to the repository
- Scans for API keys, tokens, passwords, and other sensitive data
- Runs as part of pre-publish checks

**Usage:**
```bash
# Run secret detection
make pre-publish

# Manual secret scan
detect-secrets scan
```

## GitHub Actions Workflows

### Security Scan Workflow (`.github/workflows/security.yml`)

**Triggers:**
- Every push to main/develop branches
- Every pull request to main/develop branches
- Weekly scheduled scan (Mondays at 9:00 AM UTC)
- Manual workflow dispatch

**What it does:**
1. Runs Safety vulnerability scan
2. Runs pip-audit vulnerability scan
3. Runs Bandit security linter
4. Runs detect-secrets scan
5. Uploads security reports as artifacts
6. Provides security summary in workflow output

**Artifacts:** Security reports are retained for 30 days and can be downloaded from workflow runs.

### CI Workflow (`.github/workflows/ci.yml`)

**Includes:**
- Code quality checks (ruff, black)
- Type checking (mypy)
- Test suite with coverage
- Runs on Python 3.11, 3.12, 3.13

## Pre-Publish Security Checks

Before publishing a new version, run comprehensive security checks:

```bash
# Full quality gate with security scanning
make pre-publish

# Quick checks (for rapid iteration)
make pre-publish-quick
```

The `pre-publish` target includes:
1. Code quality checks (linting, formatting)
2. Type checking with mypy
3. Full test suite with 85% coverage requirement
4. Security vulnerability scanning (Safety + pip-audit)
5. Secret detection scan

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

### 1. Do NOT open a public issue

Security vulnerabilities should not be disclosed publicly until a fix is available.

### 2. Report privately

**Email:** [security contact - update with project maintainer email]

**Include:**
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

### 3. Expected Response Time

- **Initial Response:** Within 48 hours
- **Status Update:** Within 7 days
- **Fix Timeline:** Depends on severity
  - Critical: Within 7 days
  - High: Within 30 days
  - Medium: Within 90 days
  - Low: Next planned release

### 4. Security Advisory Process

Once a vulnerability is confirmed:
1. We will work on a fix in a private branch
2. A security advisory will be created
3. A CVE may be requested for significant vulnerabilities
4. The fix will be released with a security advisory
5. Public disclosure will occur after the fix is available

## Security Best Practices

### For Contributors

1. **Never commit secrets**
   - Use environment variables
   - Use `.env` files (never commit these)
   - Use secret management tools

2. **Run security checks before committing**
   ```bash
   make security-check
   make pre-publish
   ```

3. **Keep dependencies updated**
   - Review and merge Dependabot PRs
   - Run `pip list --outdated` regularly

4. **Follow secure coding practices**
   - Validate all user input
   - Use parameterized queries
   - Avoid eval() and exec()
   - Use secure random number generation
   - Follow OWASP guidelines

### For Maintainers

1. **Review security PRs promptly**
   - Prioritize Dependabot security updates
   - Test security patches thoroughly

2. **Monitor security advisories**
   - GitHub Security tab
   - PyPI advisory database
   - CVE databases

3. **Rotate secrets regularly**
   - API keys
   - Access tokens
   - Service credentials

4. **Enable branch protection**
   - Require security checks to pass
   - Require pull request reviews
   - Require signed commits (recommended)

## Security Tools Installation

Install all security scanning tools:

```bash
# Using Make
make security-install

# Or manually with pip
pip install safety pip-audit bandit detect-secrets
```

## Security Reports

Security reports are generated in `.security-reports/` directory:

- `safety-report.json` - Dependency vulnerabilities (Safety)
- `pip-audit-report.json` - Package vulnerabilities (pip-audit)
- `bandit-report.json` - Code security issues (Bandit)

**Note:** `.security-reports/` is git-ignored to prevent accidental commit of sensitive information.

## Additional Resources

- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [PyPA Security](https://www.pypa.io/en/latest/specifications/security/)

## Acknowledgments

We thank the security research community for responsible disclosure of vulnerabilities.

---

**Last Updated:** 2025-01-24
