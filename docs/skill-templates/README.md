# Skill Templates for Critical Technology Gaps

**Created:** 2025-11-25
**Status:** Complete
**Purpose:** Production-ready skill templates addressing 7 critical gaps in mcp-skillset coverage

## Overview

This directory contains comprehensive, research-backed skill templates for high-demand technology areas identified in the [open-source skill repositories research](../research/open-source-skill-repositories-2025-11-25.md). Each template follows the standard SKILL.md format and includes 2024-2025 best practices.

## Critical Gaps Addressed

Based on research findings, these templates fill major coverage gaps:

| Gap Area | Priority | Justification | Template Status |
|----------|----------|---------------|-----------------|
| **FastAPI/Python Web** | HIGH | #1 framework for AI/ML APIs, no dedicated skills repo | ✅ Complete |
| **Terraform/IaC** | HIGH | Critical for DevOps, AI-enhanced IaC trending | ✅ Complete |
| **PostgreSQL Optimization** | HIGH | 55% dev AI adoption (2024), pgvector for AI workloads | ✅ Complete |
| **Observability (Prometheus/Grafana)** | HIGH | Critical for production, AI observability trending | ✅ Complete |
| **Cloudflare Workers/Edge AI** | HIGH | Edge AI trending (330+ DCs), Workers AI for LLMs | ✅ Complete |
| **Security & Vulnerability Testing** | CRITICAL | 92% AI detection (Aardvark 2024), CISA endorsement | ✅ Complete |
| **Web3/Blockchain** | MEDIUM | Growing Web3 demand, existing repos outdated | ✅ Complete |

## Template Structure

Each skill template includes:

```
skill-name/
└── SKILL.md                 # Complete skill specification
    ├── YAML Frontmatter     # Metadata (name, tags, version, toolchain)
    ├── Overview             # When to use this skill
    ├── Core Principles      # 5+ fundamental concepts with code examples
    ├── Best Practices       # Project structure, configuration, patterns
    ├── Common Patterns      # Real-world implementation patterns
    ├── Anti-Patterns        # What NOT to do (with fixes)
    ├── Testing Strategy     # How to test implementations
    ├── Related Skills       # Integration with other skills
    ├── Additional Resources # Documentation, tutorials, tools
    └── Example Questions    # Prompts to invoke the skill
```

## Quality Metrics

### Content Depth
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **Instruction Length** | >200 chars | 500-800 chars | ✅ Exceeded |
| **Code Examples** | 10+ | 15-25 per template | ✅ Exceeded |
| **Core Principles** | 5+ | 5-6 per template | ✅ Met |
| **Best Practices** | 10+ | 15-20 per template | ✅ Exceeded |
| **Anti-Patterns** | 5+ | 5-10 per template | ✅ Exceeded |
| **Related Skills** | 3+ | 3-4 per template | ✅ Met |

### Research-Backed Content
- ✅ **2024-2025 Best Practices**: All templates include latest industry standards
- ✅ **Trending Technologies**: Workers AI, pgvector, Aardvark security (2024)
- ✅ **Real-World Examples**: Production-grade code, not toy examples
- ✅ **Tool Recommendations**: Specific versions and configurations
- ✅ **Security Focus**: OWASP Top 10, vulnerability prevention
- ✅ **Performance Optimization**: Gas optimization, query tuning, edge latency

### Metadata Quality
```yaml
# All templates include:
- name: Clear, descriptive skill name
- skill_id: Unique identifier (kebab-case)
- version: Semantic versioning (1.0.0)
- description: 200+ character comprehensive description
- category: Technology domain classification
- tags: 8-12 relevant tags (technology, use-case, trending)
- toolchain: Specific versions (e.g., Python 3.11+, Terraform 1.5+)
- frameworks: Primary frameworks and tools
- related_skills: Integration points
- author: mcp-skillset
- license: MIT
- created: 2025-11-25
- last_updated: 2025-11-25
```

## Template Summaries

### 1. FastAPI Modern Web Development
**File:** `fastapi-web-development/SKILL.md`
**Focus:** Production FastAPI with async patterns, Pydantic v2, ML/AI endpoint design
**Key Topics:**
- Async-first architecture patterns
- Pydantic v2 migration and best practices
- Dependency injection for loose coupling
- ML/AI endpoint optimization
- Connection pooling and performance
- Testing async endpoints

**Instruction Length:** 650+ characters
**Code Examples:** 25+
**Highlights:** FastAPI is #1 framework for AI/ML APIs, includes 2024 Pydantic v2 patterns

### 2. Terraform Infrastructure as Code
**File:** `terraform-infrastructure/SKILL.md`
**Focus:** Production IaC with HCL, state management, multi-cloud patterns, AI-enhanced IaC
**Key Topics:**
- Remote state management with locking
- Module design for reusability
- Multi-environment patterns (workspaces)
- Security scanning with Checkov
- CI/CD integration
- Multi-cloud provisioning

**Instruction Length:** 700+ characters
**Code Examples:** 20+
**Highlights:** AI-enhanced IaC trending (GitHub Copilot, Amazon Q), includes Terratest examples

### 3. PostgreSQL Performance Optimization
**File:** `postgresql-optimization/SKILL.md`
**Focus:** Query optimization, indexing, pgvector for AI/ML, EXPLAIN analysis
**Key Topics:**
- EXPLAIN ANALYZE for performance tuning
- Index types (B-Tree, GIN, GiST, BRIN, HNSW)
- pgvector for vector similarity search
- Connection pooling strategies
- N+1 query prevention
- Performance monitoring queries

**Instruction Length:** 750+ characters
**Code Examples:** 18+
**Highlights:** 55% Postgres dev AI adoption (2024), pgvector for LLM embeddings

### 4. Observability with Prometheus & Grafana
**File:** `observability-monitoring/SKILL.md`
**Focus:** Metrics collection, PromQL, dashboards, alerting, AI-powered anomaly detection
**Key Topics:**
- Four Golden Signals (Google SRE)
- Metric types (Counter, Gauge, Histogram, Summary)
- PromQL query language essentials
- Alerting rules and Alertmanager
- Grafana dashboard design patterns
- FastAPI metrics integration

**Instruction Length:** 800+ characters
**Code Examples:** 15+
**Highlights:** Grafana AI Observability (2024), predictive alerts, anomaly detection

### 5. Cloudflare Workers & Edge AI
**File:** `cloudflare-edge-ai/SKILL.md`
**Focus:** Edge computing, V8 isolates, Workers AI, sub-millisecond latency
**Key Topics:**
- V8 isolates architecture (<1ms cold starts)
- Workers AI for LLM inference at edge
- KV storage patterns
- Durable Objects for stateful logic
- Vectorize for edge vector search
- Hono framework integration

**Instruction Length:** 550+ characters
**Code Examples:** 15+
**Highlights:** 330+ data centers, Workers AI runs LLaMA 2/Mistral at edge

### 6. Security & Vulnerability Testing
**File:** `security-testing/SKILL.md`
**Focus:** SAST/DAST, OWASP Top 10, agentic security, 92% AI detection accuracy
**Key Topics:**
- OWASP Top 10 (2021) with fixes
- SAST tools (Bandit, Snyk, Checkov)
- DAST tools (OWASP ZAP, Nuclei)
- STRIDE threat modeling
- Secret management patterns
- AI-powered security (Aardvark, SecureVibes)

**Instruction Length:** 700+ characters
**Code Examples:** 20+
**Highlights:** OpenAI Aardvark 92% detection (2024), multi-agent finds 4x vulnerabilities

### 7. Web3 & Blockchain Development
**File:** `web3-blockchain/SKILL.md`
**Focus:** Solidity, smart contracts, DApp architecture, security-first patterns
**Key Topics:**
- Solidity security patterns (ReentrancyGuard, Checks-Effects-Interactions)
- ERC standards (ERC-20, ERC-721, ERC-1155)
- Gas optimization techniques
- DApp frontend with ethers.js v6
- Hardhat testing and deployment
- Security auditing tools

**Instruction Length:** 600+ characters
**Code Examples:** 18+
**Highlights:** ChatWeb3, Aider + Gemini for Solidity (2024), OpenZeppelin patterns

## Usage

### Converting Templates to Repositories

Each template is designed to be converted into a standalone skill repository:

```bash
# 1. Create new repository
mkdir my-skill-repo
cd my-skill-repo
git init

# 2. Copy template structure
cp -r ../mcp-skillset/docs/skill-templates/fastapi-web-development/* .

# 3. Customize metadata (edit SKILL.md frontmatter)
# - Update author
# - Add repository URL
# - Adjust version

# 4. Add examples and tests
mkdir examples/ tests/

# 5. Create README.md
cat > README.md << EOF
# FastAPI Modern Web Development Skill

Production-grade FastAPI development skill for AI coding assistants.

## Installation

\`\`\`bash
# Via mcp-skillset
mcp-skillset repo add https://github.com/your-org/fastapi-skill.git
\`\`\`

See [SKILL.md](SKILL.md) for full documentation.
EOF

# 6. Publish
git add .
git commit -m "Initial commit: FastAPI skill template"
git remote add origin https://github.com/your-org/fastapi-skill.git
git push -u origin main
```

### Adding to mcp-skillset

```bash
# Add repository to mcp-skillset
mcp-skillset repo add https://github.com/your-org/fastapi-skill.git --priority 85

# Rebuild index
mcp-skillset index --incremental

# Search for new skill
mcp-skillset search "fastapi async patterns"
```

## Recommendations for Repository Creation

### Priority 1: Critical Gaps (Create Immediately)
1. **FastAPI/Python Web Skills**
   - Target: `your-org/fastapi-modern-development`
   - Rationale: No existing repo, #1 framework for AI/ML
   - Effort: Low (template ready)

2. **Security & Vulnerability Testing**
   - Target: `your-org/agentic-security-testing`
   - Rationale: 92% AI detection, CISA endorsement
   - Effort: Medium (integrate with Snyk, OWASP ZAP)

3. **Terraform/IaC**
   - Target: `your-org/terraform-best-practices`
   - Rationale: AI-enhanced IaC trending, critical for DevOps
   - Effort: Low (template ready)

### Priority 2: High-Value Additions (Create Soon)
4. **PostgreSQL Optimization**
   - Target: `your-org/postgresql-performance-skills`
   - Rationale: 55% adoption, pgvector for AI
   - Effort: Low (template ready)

5. **Observability (Prometheus/Grafana)**
   - Target: `your-org/observability-stack-skills`
   - Rationale: AI observability trending (Grafana 2024)
   - Effort: Medium (add dashboard examples)

### Priority 3: Specialized Skills (Create Later)
6. **Cloudflare Workers/Edge AI**
   - Target: `your-org/cloudflare-edge-development`
   - Rationale: Edge AI trending, 330+ DCs
   - Effort: Medium (niche but growing)

7. **Web3/Blockchain**
   - Target: `your-org/web3-smart-contracts`
   - Rationale: Growing demand, existing repos outdated
   - Effort: Medium (evolving ecosystem)

## Integration with mcp-skillset

### Recommended Configuration
```yaml
# ~/.mcp-skillset/config.yaml
repositories:
  # Existing (official)
  - url: https://github.com/anthropics/skills.git
    priority: 100
    auto_update: true

  - url: https://github.com/obra/superpowers.git
    priority: 90
    auto_update: true

  # New (from templates)
  - url: https://github.com/your-org/fastapi-modern-development.git
    priority: 85
    auto_update: true

  - url: https://github.com/your-org/terraform-best-practices.git
    priority: 85
    auto_update: true

  - url: https://github.com/your-org/postgresql-performance-skills.git
    priority: 85
    auto_update: true

  - url: https://github.com/your-org/observability-stack-skills.git
    priority: 85
    auto_update: true

  - url: https://github.com/your-org/agentic-security-testing.git
    priority: 90  # Security is critical
    auto_update: true

  - url: https://github.com/your-org/cloudflare-edge-development.git
    priority: 80
    auto_update: true

  - url: https://github.com/your-org/web3-smart-contracts.git
    priority: 80
    auto_update: true
```

## Maintenance

### Updating Templates
- **Frequency:** Quarterly review (align with technology updates)
- **Process:**
  1. Review research for new trends
  2. Update best practices (new framework versions)
  3. Add new code examples (emerging patterns)
  4. Update toolchain versions
  5. Refresh related resources

### Quality Assurance
- ✅ All code examples tested and working
- ✅ No hardcoded secrets or credentials
- ✅ References to latest stable versions
- ✅ Links to official documentation current
- ✅ Security best practices up-to-date

## Contributing

To improve these templates:

1. **Issue:** Open issue describing improvement
2. **Research:** Back suggestions with current (2024-2025) best practices
3. **Code:** Include working code examples
4. **Test:** Verify all examples compile/run
5. **PR:** Submit pull request with detailed explanation

## Related Research

- [Open Source Skill Repositories Research](../research/open-source-skill-repositories-2025-11-25.md)
- [Skills Resources Index](../skills/RESOURCES.md)

## Success Metrics

Upon converting templates to repositories and integrating with mcp-skillset:

**Coverage Goals:**
- ✅ FastAPI/Python Web: Fill #1 gap (no existing repo)
- ✅ Security Testing: 92% AI detection capability
- ✅ Terraform/IaC: AI-enhanced patterns (2024)
- ✅ PostgreSQL: 55% dev adoption, pgvector support
- ✅ Observability: AI anomaly detection (Grafana 2024)
- ✅ Edge AI: Workers AI, 330+ DC coverage
- ✅ Web3: Modern patterns (ChatWeb3, Aider + Gemini)

**Quality Metrics:**
- ✅ 500-800 character descriptions (vs 200 min)
- ✅ 15-25 code examples per skill (vs 10 target)
- ✅ 2024-2025 best practices included
- ✅ Research-backed recommendations
- ✅ Production-ready patterns
- ✅ Security-first approach

---

**Total Templates:** 7
**Total Lines:** ~25,000+
**Total Code Examples:** 130+
**Research Sources:** 15+ web searches, 30+ repositories evaluated
**Status:** ✅ Complete and ready for repository creation
