# Documentation Rules & Guidelines

***Created:*** 2025-12-18

***Last Updated:*** 2025-12-26

***Version:*** 2.0.0

***Status:*** Active

---

## Purpose

This document establishes binding rules for creating, maintaining, and formatting technical documentation within code repositories. All contributors must adhere to these rules to ensure clarity, consistency, and professional quality suitable for both human readers and AI agents.

**Target Audience:**
- Backend Developer
- Frontend / Mobile Developer
- DevOps Engineer
- Technical Writer
- AI Agents

**Scope:**
- Code repository documentation (README, guides, API docs)
- Technical specifications stored in Git

**Out of Scope:**
- Confluence/wiki documentation (see `confluence_rules.md`)
- SRS/requirements documents (see `confluence_rules.md`)

---

## 1. Core Principles

### 1.1 Professional Tone

To maintain professional standards suitable for enterprise software and technical auditing:

- **NO Emojis or Icons**: Do not use emojis in documentation files, commit messages, or code comments.
- **Objective Language**: Use clear, direct, and objective language.
- **No Casual Expressions**: Avoid slang, humor, or overly casual tone.
- **Complete Documentation**: Do not leave placeholders like "To be continue..." or "TBD". Use `[WIP]` prefix in title if work is in progress.

### 1.2 Language Rules

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

### 2.2 README Update Rules

| Document Type | Filename Pattern | Update README? |
| --- | --- | --- |
| **Core Documentation** | `setup_guide.md` | **YES** - Add link |
| **Internal Notes** | `_meeting_notes.md` | **NO** - Use `_` prefix |
| **Temporary Analysis** | `_temp_analysis.md` | **NO** - Use `_` prefix |
| **Drafts** | `_draft_proposal.md` | **NO** - Use `_` prefix |

### 2.3 Naming Conventions

**Files:**
- Use `snake_case.md` for all documentation files.
- Correct: `setup_guide.md`, `api_authentication.md`
- Incorrect: `SetupGuide.md`, `api-auth.md`

**Images:**
- Store in `docs/assets/` directory.
- Use descriptive names with snake_case.
- Correct: `docs/assets/auth_flow_diagram.png`

### 2.4 Diagram & Image Standards

**Diagram as Code:**
- Prioritize using MermaidJS or PlantUML within markdown blocks over static images (PNG/JPG).
- This enables version control and easier updates.

**Accessibility:**
- All images and diagrams MUST include descriptive Alt Text.

```markdown
Correct: ![User Login Flow Diagram](docs/assets/login_flow.png)
Incorrect: ![image](docs/assets/login_flow.png)
```

---

## 3. Document Metadata Header

All major documentation files must begin with a metadata block to establish validity and ownership.

### 3.1 Standard Document Header

```markdown
# [Document Title]

***Created:*** [YYYY-MM-DD]
***Last Updated:*** [YYYY-MM-DD]
***Version:*** [x.y.z]
***Status:*** [Draft | Active | Deprecated]

---
```

### 3.2 Metadata Field Guidelines

**Version**: Follow Semantic Versioning (`MAJOR.MINOR.PATCH`).
- **PATCH** (e.g., `1.0.0` -> `1.0.1`): Fixes, typo corrections, formatting changes.
- **MINOR** (e.g., `1.0.0` -> `1.1.0`): Adding new sections, clarifications.
- **MAJOR** (e.g., `1.0.0` -> `2.0.0`): Complete rewrites, breaking changes.

**Status**:
- `Draft`: Work in progress.
- `Active`: Current and maintained.
- `Deprecated`: Historical reference only.

---

## 4. Content Structure

Every technical document must follow a logical flow appropriate to its type.

### 4.1 General Technical Document Structure

1. **Overview/Purpose**: What this document covers and why.
2. **Target Audience**: Who should read this document.
3. **Prerequisites**: Software versions, dependencies, access rights.
4. **Main Content**: Organized by numbered sections.
5. **Verification**: How to verify successful completion.
6. **Troubleshooting**: Common errors and solutions.

### 4.2 Section Numbering

Use hierarchical numbering for all sections:

```markdown
## 1. Main Section
### 1.1 Sub-section
#### 1.1.1 Sub-sub-section
```

---

## 5. Technical Formatting Rules

### 5.1 Code Blocks

Always specify the language for syntax highlighting:

```go
func main() {
    fmt.Println("Hello, World!")
}
```

### 5.2 Variables and Placeholders

Use angle brackets or CAPS for placeholders:
- `<PORT>` or `YOUR_PORT`
- Example: `go run main.go --port <PORT>`

### 5.3 Tables

Use tables for structured data with clear headers.

### 5.4 Lists

- Use bullet points for unordered items.
- Use numbered lists for sequential procedures.
- Keep list items parallel in structure.

---

## 6. Maintenance & Review

### 6.1 Pull Request Policy

- **Documentation is Code**: Updates must be in the same PR as code changes.
- **Rejection Criteria**: Reviewers must reject PRs if:
  - Documentation contains emojis.
  - Metadata header is missing.
  - Verification steps are missing.
  - Code blocks lack language specification.

### 6.2 Update Guidelines

- Update the **Last Updated** field.
- Increment **Version** appropriately.
- Document significant changes in CHANGELOG.md.

### 6.3 Deprecation Process

1. Do not delete immediately if it has historical value.
2. Update **Status** field to `Deprecated`.
3. Add deprecation notice at the top:

> **DEPRECATED**: This document is no longer maintained. See [new_link] for details.

---

## 7. AI Agent Guidelines

### 7.1 When Creating Documentation

- Always include metadata header.
- Follow content structure template.
- Use specified naming conventions.
- Never use emojis.

### 7.2 When Updating Documentation

- Update metadata (Last Updated, Version).
- Maintain consistent formatting.
- Preserve existing structure.

---

## 8. Explicit Non-Goals

To maintain focus, this document does NOT cover:

- Confluence-specific formatting rules (see `confluence_rules.md`).
- SRS/requirements document templates (see `confluence_rules.md`).
- Code style guidelines (see language-specific linter configs).
- Git commit message conventions (see repository contributing guide).

---

## 9. Compliance

All documentation in this repository must comply with these rules. Non-compliant documentation should be updated or removed during code review.

---

## Related Documents

- [confluence_rules.md](confluence_rules.md) - Confluence documentation rules (English)