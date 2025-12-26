# Documentation Templates

**Version**: 1.0.0  
**Last Updated**: 26 Dec 2024  
**Owner**: Documentation Team

This directory contains standardized templates for creating consistent documentation across the AgriOS project. All templates follow rules defined in [confluence_rules.md](../confluence_rules.md) and [documentation_rules.md](../documentation_rules.md).

---

## Available Templates

### 1. Software Requirements Specification (SRS)

**File**: [srs_template.md](srs_template.md)  
**Purpose**: Document functional and non-functional requirements for software features.

**Use When**:
- Starting a new feature or module
- Defining system requirements
- Creating acceptance criteria for development

**Key Sections**:
- Business Requirements (BR-XXX)
- Functional Requirements (FR-XXX with domains: App, Portal, Third Party)
- Non-Functional Requirements (NFR-P/S/U/R/M)
- Technical Constraints (TC-XXX)
- Acceptance Criteria
- Glossary

**Naming Convention**: `[SRS] Feature Name - Brief Description.md`

---

### 2. Architecture Decision Record (ADR)

**File**: [adr_template.md](adr_template.md)  
**Purpose**: Document significant architectural decisions and their rationale.

**Use When**:
- Choosing between technology options
- Making design decisions with long-term impact
- Documenting trade-offs and alternatives

**Key Sections**:
- Context and problem statement
- Decision with rationale
- Alternatives considered (with pros/cons)
- Consequences (positive/negative)
- Implementation plan
- Success metrics

**Naming Convention**: `[ADR] ADR-XXX - Decision Title.md`

---

### 3. Meeting Notes

**File**: [meeting_notes_template.md](meeting_notes_template.md)  
**Purpose**: Standardized format for documenting team meetings.

**Use When**:
- Sprint planning meetings
- Retrospectives
- Technical discussions
- Stakeholder meetings

**Key Sections**:
- Attendees with roles
- Previous action items review
- Discussion topics with decisions
- New action items with owners/deadlines
- Blockers and risks
- Next meeting planning

**Naming Convention**: `[MEET] YYYY-MM-DD - Meeting Topic.md`

---

### 4. Request for Comments (RFC)

**File**: [rfc_template.md](rfc_template.md)  
**Purpose**: Propose significant changes and gather team feedback.

**Use When**:
- Proposing new features or processes
- Suggesting major refactorings
- Seeking team consensus on approach

**Key Sections**:
- Summary and motivation
- Detailed design with architecture
- Implementation phases
- Alternative approaches
- Impact analysis (technical, operational, team, timeline)
- Risks and mitigation
- Success metrics
- Open questions
- Feedback section

**Naming Convention**: `[RFC] RFC-XXX - Proposal Title.md`

---

### 5. Process Documentation

**File**: [process_template.md](process_template.md)  
**Purpose**: Document team processes, workflows, and procedures.

**Use When**:
- Establishing new team processes
- Documenting existing workflows
- Creating onboarding guides

**Key Sections**:
- Roles and responsibilities
- Detailed process steps
- Workflows and diagrams
- Tools and systems used
- Naming conventions (Epic, Task, Branch, Commit)
- Exception handling
- Communication guidelines
- Metrics and reporting
- Continuous improvement

**Naming Convention**: `[PROC] Process Name.md`

---

### 6. Technical Design Document (TDD)

**File**: [tdd_template.md](tdd_template.md)  
**Purpose**: Detailed technical design for implementing features.

**Use When**:
- Implementing complex features
- Designing new components or services
- Planning significant refactoring

**Key Sections**:
- System architecture diagrams
- Component design
- Data model and database schema
- API design (REST/gRPC)
- Security design
- Performance considerations
- Error handling
- Testing strategy
- Monitoring and observability
- Deployment plan

**Naming Convention**: `[TDD] Component Name - Feature.md`

---

### 7. README for Repositories

**File**: [readme_template.md](readme_template.md)  
**Purpose**: Standard README for code repositories.

**Use When**:
- Creating a new repository
- Improving existing repository documentation

**Key Sections**:
- Overview and purpose
- Quick start guide
- Configuration management
- Project structure
- API documentation
- Development workflows
- Database and migrations
- Deployment instructions
- Monitoring and health checks
- Troubleshooting guide
- Contributing guidelines

**Naming Convention**: `README.md` (always in repository root)

---

## How to Use Templates

### Step 1: Choose the Right Template

Refer to the "Use When" section for each template to determine which one fits your needs.

### Step 2: Copy Template

```bash
# Copy template to your working directory
cp docs/confluence/templates/[template_name].md docs/confluence/[new_document_name].md
```

### Step 3: Fill in Content

1. Update the version table with your information
2. Replace placeholder text (marked with `[brackets]`)
3. Remove sections that don't apply (mark with N/A if required by rules)
4. Follow naming conventions for IDs (FR-XXX, BR-XXX, NFR-XXX, etc.)

### Step 4: Validate

Check against compliance checklist in [confluence_rules.md](../confluence_rules.md):

- [ ] Document has proper prefix ([SRS], [ADR], etc.)
- [ ] Version table is complete
- [ ] All required sections are present
- [ ] Requirement IDs follow conventions
- [ ] No "To be continue..." or "TBD" (use [WIP] prefix if incomplete)
- [ ] Language is consistent (American English for content, preserve technical terms)
- [ ] Cross-references use correct format
- [ ] Images have proper alt text and captions

### Step 5: Review and Publish

1. Request peer review
2. Address feedback
3. Get approval signatures (if required)
4. Publish to Confluence or commit to repository

---

## Template Customization

### When to Customize

- Templates are starting points, not rigid requirements
- Add sections specific to your project needs
- Remove sections that don't apply (document as N/A if mandatory)
- Adapt to team workflow and tooling

### What NOT to Change

- Document prefix conventions ([SRS], [ADR], etc.)
- Requirement ID format (FR-XXX, NFR-P, etc.)
- Version table structure
- Metadata headers

---

## Quick Reference

### Document Prefixes

| Prefix | Document Type | Template |
| --- | --- | --- |
| [SRS] | Software Requirements Specification | srs_template.md |
| [ADR] | Architecture Decision Record | adr_template.md |
| [MEET] | Meeting Notes | meeting_notes_template.md |
| [RFC] | Request for Comments | rfc_template.md |
| [PROC] | Process Documentation | process_template.md |
| [TDD] | Technical Design Document | tdd_template.md |
| [BRD] | Business Requirements Document | (Use SRS template) |
| [WIP] | Work In Progress | (Prefix for incomplete docs) |

### Requirement ID Patterns

| Pattern | Description | Example |
| --- | --- | --- |
| FR-XX | Functional Requirement | FR-01, FR-02 |
| FR-AXX | App-specific Requirement | FR-A01, FR-A02 |
| FR-PXX | Portal-specific Requirement | FR-P01, FR-P02 |
| FR-TXX | Third Party Integration | FR-T01, FR-T02 |
| BR-XXX | Business Requirement | BR-001, BR-002 |
| NFR-P | Performance Requirement | NFR-P01 |
| NFR-S | Security Requirement | NFR-S01 |
| NFR-U | Usability Requirement | NFR-U01 |
| NFR-R | Reliability Requirement | NFR-R01 |
| NFR-M | Maintainability Requirement | NFR-M01 |
| TC-XXX | Technical Constraint | TC-001, TC-002 |
| M-XX | Metric | M-01, M-02 |

---

## Common Mistakes to Avoid

### 1. Using "To be continue..." or "TBD"

**Wrong**:
```markdown
## Future Enhancements
To be continue...
```

**Right**:
```markdown
# [WIP] Future Enhancements
This document is a work in progress. The following sections will be completed:
- [ ] Performance optimization strategy
- [ ] Caching implementation
```

### 2. Incomplete Requirement IDs

**Wrong**:
```markdown
FR-1: User can login
FR-2: User can logout
```

**Right**:
```markdown
FR-01: User can login
FR-02: User can logout
```

### 3. Missing Acceptance Criteria

**Wrong**:
```markdown
**FR-01**: User authentication
```

**Right**:
```markdown
**FR-01**: User authentication

**Acceptance Criteria**:
- Given a registered user
- When user enters correct credentials
- Then system grants access and creates session
```

### 4. No Cross-References

**Wrong**:
```markdown
See the architecture document for details.
```

**Right**:
```markdown
See [ADR] ADR-001 - Microservices Architecture for details.
```

### 5. Missing Version Information

**Wrong**: No version table at the beginning of document

**Right**:
```markdown
| Version | Date | Author | Status |
| --- | --- | --- | --- |
| 1.0.0 | 26 Dec 2024 | @username | Draft |
```

---

## Template Maintenance

### Version Control

All templates follow Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to template structure
- **MINOR**: New sections or significant additions
- **PATCH**: Minor updates, typo fixes, clarifications

### Update Process

1. Propose changes via Pull Request
2. Discuss with Documentation Team
3. Update relevant rules files if needed
4. Update this README with changes
5. Communicate updates to all teams

### Feedback

Have suggestions for improving templates?
- Create an issue in Azure DevOps
- Contact Documentation Team
- Propose changes in Pull Request

---

## Related Documentation

- [confluence_rules.md](../confluence_rules.md) - Comprehensive documentation rules
- [documentation_rules.md](../documentation_rules.md) - Code repository documentation rules
- [copilot-instructions.md](../../copilot-instructions.md) - AI agent coding guidelines

---

## Changelog

### Version 1.0.0 (26 Dec 2024)

**Added**:
- Initial template collection with 7 templates
- Template usage guide
- Quick reference tables
- Common mistakes section
- Compliance checklist

**Templates Included**:
- SRS Template (10 sections)
- ADR Template (11 sections)
- Meeting Notes Template (8 sections)
- RFC Template (13 sections)
- Process Template (17 sections)
- TDD Template (18 sections)
- README Template (comprehensive repository guide)
