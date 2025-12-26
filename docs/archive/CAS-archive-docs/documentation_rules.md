### `documentation_rules.md`

# Documentation Rules & Guidelines

**Author:** thatlq1812
**Created:** 2025-12-18
**Last Updated:** 2025-12-19
**Version:** 1.0.1
**Status:** Active

---

## Purpose

This document establishes binding rules for creating, maintaining, and formatting technical documentation within the project. All contributors must adhere to these RULES to ensure clarity, consistency, and professional quality suitable for both human readers and AI agents.

---

## 1. Core Principles

### 1.1 Professional Tone

To maintain professional RULES suitable for enterprise software and technical auditing:

- **NO Emojis or Icons**: Do not use emojis in documentation files, commit messages, or code comments.
- **Objective Language**: Use clear, direct, and objective language.
- **No Casual Expressions**: Avoid slang, humor, or overly casual tone.

### 1.2 Language RULES

- **Written Content**: American English (en-US) only.
- **Spelling**: Use standard American technical spelling.
  - Correct: color, optimize, analyze
  - Incorrect: colour, optimise, analyse

### 1.3 Single Source of Truth

- **No Ephemeral Reports**: Do not commit temporary task reports.
- **Integration**: Integrate findings into permanent documentation structure.
- **Update, Don't Duplicate**: Update existing docs rather than creating new ones.

---

## 2. Directory Structure & Naming

Documentation is organized to serve specific audiences: Onboarding, Maintenance, and External Overview.

### 2.1 Folder Structure

```text
/
├── README.md                          # Project overview and quick start only
├── docs/                              # All documentation lives here
│   ├── documentation_rules.md         # This file
│   ├── CHANGELOG.md                   # Version history and changes
│   ├── architecture/                  # System design, diagrams, ADRs
│   ├── guides/                        # How-to, setup, deployment guides
│   ├── api/                           # API specifications
│   ├── database/                      # Schema, migrations, data flows
│   ├── assets/                        # Images, diagrams, media files
│   └── ...
└── ...

```

**Rationale:**

* Keep root directory clean with only README.md
* Centralize all documentation in `docs/` directory
* Easier to maintain and locate documentation

### 2.2 README Update Rules

**Decision Matrix:**

| Document Type | Filename Pattern | Update README? |
| --- | --- | --- |
| **Core Documentation** | `setup_guide.md` | **YES** - Add link |
| **Internal Notes** | `_meeting_notes.md` | **NO** - Use `_` prefix |
| **Temporary Analysis** | `_temp_analysis.md` | **NO** - Use `_` prefix |
| **Drafts** | `_draft_proposal.md` | **NO** - Use `_` prefix |

### 2.3 Naming Conventions

**Files:**

* Use `snake_case.md` for all documentation files.
* Correct: `setup_guide.md`, `api_authentication.md`
* Incorrect: `SetupGuide.md`, `api-auth.md`

**Images:**

* Store in `docs/assets/` directory.
* Use descriptive names with snake_case.
* Correct: `docs/assets/auth_flow_diagram.png`

### 2.4 Diagram & Image Standards

**Diagram as Code:**
* Prioritize using MermaidJS or PlantUML within markdown blocks over static images (PNG/JPG). This enables version control and easier updates.

* Example:

```markdown
graph TD;
    Client-->API_Gateway;
    API_Gateway-->Auth_Service;
```

**Accessibility:**
* All images and diagrams MUST include descriptive Alt Text to support accessibility and searchability.
```
Correct: ![User Login Flow Diagram](docs/assets/login_flow.png)

Incorrect: ![image](docs/assets/login_flow.png)
```

---

## 3. Document Metadata Header

All major documentation files in the `docs/` directory must begin with a metadata block to establish validity and ownership.

### 3.1 Required Metadata Template
#### 3.1.1 Document Title
```markdown
# [Document Title]

**Author:** [Username or Name]
**Created:** [YYYY-MM-DD]
**Last Updated:** [YYYY-MM-DD]
**Version:** [x.y.z]
**Status:** [Draft | Active | Deprecated]

---

```

#### 3.1.2 Service Title
```markdown
# [Service Title]

**Created:** [YYYY-MM-DD]
**Last Updated:** [YYYY-MM-DD]
**Updated By:** [Username or Name]
**Version:** [x.y.z]
**Status:** [Draft | Active | Deprecated]

---

```

### 3.2 Metadata Field Guidelines

* **Version**: Follow Semantic Versioning (`MAJOR.MINOR.PATCH`).
  * **PATCH** (e.g., `1.0.0` -> `1.0.1`): Fixes, typo corrections, formatting changes (No content logic change).
  * **MINOR** (e.g., `1.0.0` -> `1.1.0`): Adding new sections, clarifications, or updates that do not invalidate previous info.
  * **MAJOR** (e.g., `1.0.0` -> `2.0.0`): Complete rewrites, breaking changes, or deprecating major sections.

* **Status**:
  * `Draft`: Work in progress.
  * `Active`: Current and maintained.
  * `Deprecated`: Historical reference only.

---

## 4. Content Structure

Every technical guide must follow this logical flow:

### 4.1 Overview

* Explain what this document covers and why it is necessary.
* Identify target audience.

### 4.2 Prerequisites

* List software versions, dependencies, access rights, and environment variables.

### 4.3 Implementation Steps

* Use numbered lists (`1.`, `2.`) for sequential procedures.
* Explain *what* each command does, not just the command itself.

### 4.4 Verification (CRITICAL)

* Explain how to verify successful completion.
* Provide expected outputs or log samples.

### 4.5 Troubleshooting

* List common errors and solutions.

---

## 5. Technical Formatting Rules

### 5.1 Code Blocks

Always specify the language for syntax highlighting.

```go
func main() {
    fmt.Println("Hello, World!")
}
```

### 5.2 Variables and Placeholders

* Use angle brackets or CAPS: `<PORT>` or `YOUR_PORT`.
* Example: `go run main.go --port <PORT>`

---

## 6. Maintenance & Review

### 6.1 Pull Request Policy

* **Documentation is Code**: Updates must be in the same PR as code changes.
* **Rejection Criteria**: Reviewers must reject PRs if:
* Documentation contains emojis.
* Metadata header is missing.
* Verification steps are missing.
* Code blocks lack language specification.



### 6.2 Update Guidelines

* Update the **Last Updated** field.
* Increment **Version** appropriately.
* Document significant changes in CHANGELOG.md.

### 6.3 Deprecation Process

1. Do not delete immediately if it has historical value.
2. Update **Status** field to `Deprecated`.
3. Add deprecation notice at the top:
> **DEPRECATED**: This document is no longer maintained. See [new_link] for details.

---

## 7. AI Agent Guidelines

This section provides specific guidance for AI agents working with documentation.

### 7.1 When Creating Documentation

* Always include metadata header.
* Follow content structure template (Overview -> Verification).
* Use specified naming conventions.
* Never use emojis.

### 7.2 When Updating Documentation

* Update metadata (Last Updated, Version).
* Maintain consistent formatting.

---

## 8. Examples

### 8.1 Complete Document Example

```markdown
# Service Deployment Guide

**Author:** thatlq1812
**Created:** 2025-12-18
**Last Updated:** 2025-12-18
**Version:** 1.0.0
**Status:** Active

---

## Overview
This guide covers deploying the notification service to production.

## Prerequisites
- Kubernetes cluster access (v1.28+)

## Implementation Steps
1. **Apply deployment manifest:**
   ```bash
   kubectl apply -f k8s/deployment.yaml

```

## Verification

Verify deployment is running:

```bash
kubectl get pods -l app=noti-service
# Expected output: 1/1 Running
```

---

## Compliance

All documentation in this repository must comply with these RULES. Non-compliant documentation should be updated or removed during code review.