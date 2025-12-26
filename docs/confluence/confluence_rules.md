# Confluence Documentation Rules & Guidelines

***Created:*** 2025-12-26
***Last Updated:*** 2025-12-26
***Version:*** 1.0.0
***Status:*** Active

---

## 1. Introduction

### 1.1 Purpose

This document establishes binding rules for creating, maintaining, and formatting documentation on **Confluence**. These rules ensure consistency across all project documentation, facilitate collaboration between teams, and serve as a single source of truth for business and technical specifications.

**Difference from `documentation_rules.md`:**
- **Confluence Documentation**: Business requirements, processes, specifications. For PO, QA, Manager, Dev. (This document)
- **Repository Documentation**: Technical documentation in code repos (README, setup guides, API specs). For Dev/DevOps only. (See `documentation_rules.md`)

### 1.2 Scope

This document applies to:
- Software Requirements Specifications (SRS)
- Business Requirements Documents
- Technical Design Documents
- Process Documentation
- Meeting Notes and Decision Records

### 1.3 Target Audience

- Product Owner (PO)
- Backend Developer
- Frontend / Mobile Developer
- QC / Tester
- Technical Writer
- External Partners (for public documentation)

---

## 2. Core Principles

### 2.1 Professional Tone

- **NO Emojis or Icons**: Do not use emojis in any documentation.
- **Objective Language**: Use clear, direct, and professional language.
- **No Casual Expressions**: Avoid slang, humor, or overly casual tone.
- **Complete Documentation**: Do NOT use "To be continue..." or "TBD". Use `[WIP]` tag in title if document is work in progress.

### 2.2 Language Rules

- **Primary Language**: Vietnamese for internal documents.
- **Technical Terms**: **Keep English** for:
  - Technical terms: API, Cache, Latency, P90, gRPC, JWT, RBAC
  - Service/component names: App Gateway, Portal Gateway, User Service
  - Requirement IDs: FR-01, BR-001, NFR-P01
  - Technology names: PostgreSQL, Redis, Kubernetes
- **Consistency**: Maintain consistent language throughout the document.

**Correct Example:**
> "Hệ thống phải đảm bảo P90 Latency ≤ 200ms cho API List Products."

**Incorrect Example:**
> "Hệ thống phải đảm bảo độ trễ P90 nhỏ hơn hoặc bằng 200 mili giây cho giao diện lấy danh sách sản phẩm."

### 2.3 Single Source of Truth

- Each topic should have ONE authoritative document.
- Link to existing documents rather than duplicating content.
- Keep documents up-to-date with version history.

---

## 3. Document Structure

### 3.1 Version History Table

All formal documents MUST begin with a version history table:

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | Author Name | Initial document |
| 1.1.0 | DD MMM YYYY | Author Name | Added section X |

### 3.2 Standard Document Sections

Every document SHOULD include these sections in order:

1. **Version History Table**
2. **Introduction**
   - Purpose/Objective
   - Scope
   - Target Audience
3. **Main Content** (organized by numbered sections)
4. **Explicit Non-Goals** (what this document does NOT cover)
5. **Acceptance Criteria** (for requirements documents)

### 3.3 Section Numbering

Use hierarchical numbering for all sections:

```
1. Main Section
  1.1 Sub-section
    1.1.1 Sub-sub-section
```

---

## 4. Requirements Documentation (SRS)

### 4.1 Document Types

| Document Type | Prefix | Purpose |
| --- | --- | --- |
| Software Requirements Specification | [SRS] | Technical requirements |
| Business Requirements Document | [BRD] | Business requirements |
| Technical Design Document | [TDD] | System design |
| Architecture Decision Record | [ADR] | Design decisions |

### 4.2 Requirement ID Conventions

Use standardized prefixes for requirement IDs:

| Category | Prefix | Example | Description |
| --- | --- | --- | --- |
| **Functional Requirements** | FR- | FR-01, FR-02 | Core functionality |
| **Business Requirements** | BR- | BR-001, BR-002 | Business rules |
| **Non-Functional Requirements** | NFR- | NFR-P01, NFR-S01 | Performance, Security |
| **Technical Constraints** | TC- | TC-001, TC-002 | Technical limitations |
| **Metrics** | M- | M-01, M-02 | Measurable indicators |

**Prefix Patterns by Domain:**
- General: `FR-01`, `BR-001`
- App Gateway: `FR-A01`, `FR-A02`
- Portal: `FR-P01`, `FR-P02`
- Third Party: `FR-T01`, `FR-T02`

### 4.3 Requirement Structure

Each requirement MUST include:

```markdown
#### FR-01: Requirement Title

- **Description**: Clear description of the requirement
- **Rationale**: Why this requirement exists
- **Acceptance Criteria**: How to verify completion
- **Priority**: High / Medium / Low
```

### 4.4 Non-Functional Requirements Categories

| Category | Prefix | Description |
| --- | --- | --- |
| Performance | NFR-P | Response time, throughput |
| Security | NFR-S | Authentication, authorization |
| Usability | NFR-U | User experience |
| Reliability | NFR-R | Availability, fault tolerance |
| Maintainability | NFR-M | Code quality, documentation |

---

## 5. Content Formatting

### 5.1 Tables

Use tables for structured data:

| Column 1 | Column 2 | Column 3 |
| --- | --- | --- |
| Data | Data | Data |

**Table Guidelines:**
- Always include header row
- Use consistent alignment
- Keep cell content concise

### 5.2 Lists

**Bullet Points** - For unordered items:
- Item 1
- Item 2
- Item 3

**Numbered Lists** - For sequential procedures:
1. Step 1
2. Step 2
3. Step 3

### 5.3 Code Blocks

Use code blocks for technical content:

```json
{
  "example": "value"
}
```

### 5.4 Diagrams

- Use Confluence diagram tools or embed images
- Include alt text for accessibility
- Store source files (draw.io, Mermaid) for future editing

---

## 6. Scope and Non-Goals

### 6.1 Scope Section

Every document SHOULD clearly define what it covers:

```markdown
## Scope

This document applies to:
- Component A
- Feature B
- Service C

This document does NOT cover:
- Component X (see [Link to Document X])
- Feature Y (out of scope for MVP)
```

### 6.2 Explicit Non-Goals Section

Include an "Explicit Non-Goals" section to prevent scope creep:

```markdown
## Explicit Non-Goals

The following are intentionally NOT addressed in this document:
- Feature X (to be addressed in Phase 2)
- Integration with System Y (separate document required)
- Performance optimization beyond MVP requirements
```

---

## 7. Acceptance Criteria

### 7.1 Purpose

Acceptance criteria define how to verify that requirements are met.

### 7.2 Format

```markdown
## Acceptance Criteria

- [ ] Criterion 1: Description of what must be true
- [ ] Criterion 2: Description of what must be true
- [ ] Criterion 3: Description of what must be true
```

### 7.3 Examples from SRS

**Functional Criteria:**
- API returns correct response format
- Data validation works as specified
- Error handling follows defined patterns

**Technical Criteria:**
- Import to Postman succeeds
- All endpoints are documented
- Authentication is properly configured

---

## 8. Linking and References

### 8.1 Internal Links

- Use Confluence page links for internal references
- Format: `[Document Title](link)`
- Avoid hardcoded URLs that may break

### 8.2 External Links

- Clearly label external links
- Verify links are accessible to target audience
- Include access instructions if needed

### 8.3 Cross-References

- Reference related documents in Introduction section
- Use consistent naming conventions
- Maintain a document index for large projects

---

## 9. Maintenance

### 9.1 Version Control

- Increment version for every change
- Update version history table
- Use semantic versioning (MAJOR.MINOR.PATCH)

### 9.2 Review Process

- Assign document owner
- Schedule periodic reviews
- Track changes through version history

### 9.3 Deprecation

When deprecating a document:
1. Add **[DEPRECATED]** prefix to title
2. Add deprecation notice at top:

> **DEPRECATED**: This document is no longer maintained. See [new document] for current information.

3. Link to replacement document
4. Keep for historical reference

---

## 10. Templates

### 10.1 SRS Template

```markdown
# [SRS] Document Title

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | Name | Initial document |

## 1. Introduction
### 1.1 Purpose
### 1.2 Scope
### 1.3 Target Audience

## 2. System Overview
### 2.1 Architecture
### 2.2 Constraints

## 3. Functional Requirements
### 3.1 Feature Area 1
#### FR-01: Requirement Title

## 4. Non-Functional Requirements
### 4.1 Performance
#### NFR-P01: Requirement Title

## 5. Technical Constraints
### TC-001: Constraint Title

## 6. Explicit Non-Goals

## 7. Acceptance Criteria
```

### 10.2 Process Document Template

```markdown
# [PROC] Process Title

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | Name | Initial document |

## 1. Purpose

## 2. Scope

## 3. Definitions

## 4. Process Steps
### 4.1 Step 1
### 4.2 Step 2

## 5. Exceptions

## 6. Related Documents
```

### 10.3 Meeting Notes Template

```markdown
# [MEET] Meeting Title - DD MMM YYYY

**Time**: 10:00 - 11:00
**Location**: Meeting Room 3 / Microsoft Teams
**Attendees**:
- @Tran Dang Quang (Chair)
- @Diep Chi Cuong
- @Le Van Thiet

---

## 1. Discussion Topics

### 1.1 Topic 1
- Content...
- Decision: ...

## 2. Action Items

| # | Task | Assignee | Deadline | Status |
| --- | --- | --- | --- | --- |
| 1 | Implement feature X | @Diep Chi Cuong | 2025-12-30 | To Do |
| 2 | Review PR #123 | @Le Van Thiet | 2025-12-27 | In Progress |

## 3. Next Meeting

- **Date**: 02 Jan 2026
- **Topic**: Sprint Retrospective
```

### 10.4 RFC Template

```markdown
# [RFC] Proposal Title

| Version | Date | Author | Status |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | Name | Draft |

## 1. Summary

Brief description of the proposal (2-3 sentences).

## 2. Motivation

Why is this change/improvement needed?

## 3. Detailed Proposal

### 3.1 Proposed Solution
### 3.2 Alternative Approaches Considered
### 3.3 Why This Solution

## 4. Impact

### 4.1 Technical Impact
- Which services are affected?
- Breaking changes?

### 4.2 Timeline
- Estimated effort: X person-days
- Milestone: Q1 2026

## 5. Risks

- Risk 1: Description + mitigation
- Risk 2: ...

## 6. Open Questions

- [ ] Question 1?
- [ ] Question 2?

## 7. Feedback and Discussion

(Team comments here)
```

---

## 11. Compliance Checklist

Before publishing any document, verify:

### 11.1 Metadata & Structure
- [ ] Version history table is present and complete
- [ ] Title has correct prefix ([SRS], [PROC], etc.)
- [ ] All sections use hierarchical numbering (1, 1.1, 1.1.1)
- [ ] Has "Introduction" section with Purpose/Scope/Audience
- [ ] Has "Explicit Non-Goals" section

### 11.2 Requirements (for SRS/BRD)
- [ ] Requirement IDs follow naming conventions (FR-, BR-, NFR-, etc.)
- [ ] Each requirement has: Definition, Rationale, Acceptance Criteria
- [ ] Clear categorization: Functional, Non-Functional, Technical Constraints
- [ ] Has "Acceptance Criteria" section

### 11.3 Content Quality
- [ ] No emojis or casual language
- [ ] NO "To be continue..." (use [WIP] if incomplete)
- [ ] Vietnamese has proper diacritics
- [ ] Technical terms kept in English
- [ ] Consistent language throughout

### 11.4 Links & References
- [ ] All internal links working (no hardcoded URLs)
- [ ] Images display correctly (no broken `media/image1.tmp` links)
- [ ] Linked to Jira Epic (if SRS)
- [ ] Has "Related Documents" section with valid links

### 11.5 Ownership & Status
- [ ] Document owner assigned
- [ ] Status is clear (Draft/In Review/Approved)
- [ ] Labels properly tagged (status, team, priority)

---

## 12. Maintenance & Review

### 12.1 Version Management

- **Increment version** for every meaningful change
- **Update version history table** with clear descriptions
- Use **Semantic Versioning** (MAJOR.MINOR.PATCH):
  - **PATCH** (1.0.0 → 1.0.1): Typo fixes, formatting
  - **MINOR** (1.0.0 → 1.1.0): New sections, content updates
  - **MAJOR** (1.0.0 → 2.0.0): Major changes, breaking changes

### 12.2 Review Process

- **Assign Document Owner**: Each document must have 1 owner
- **Periodic Reviews**:
  - SRS: Review when new requirements or every 6 months
  - PROC: Review every 3 months or when process changes
  - ORG: Review when team structure changes
- **Track Changes**: Use Confluence Page History

### 12.3 Deprecation Process

When deprecating a document:

1. **Add prefix** `[DEPRECATED]` to title:
   ```
   [DEPRECATED][SRS] Mobile App QoS Tracking – MVP
   ```

2. **Add notice** at top:
   > **DOCUMENT DEPRECATED**
   > 
   > This document is no longer maintained. See [SRS] Mobile App QoS Tracking v2.0 for current information.
   > 
   > **Deprecation Reason**: Replaced by new version with improved architecture.
   > 
   > **Deprecation Date**: 26 Dec 2025

3. **Link** to replacement document

4. **Move** to `Archive` folder but **DO NOT DELETE** (keep for historical reference)

5. **Update label** to `status:deprecated`

---

## 13. Real-World Examples

### 13.1 Good Example

See: `[SRS] Mobile App Quality of Service (QoS) Tracking – MVP`

**Strengths:**
- Complete version history table
- Standard requirement IDs (M-01, FR-01, NFR-P01)
- Clear categorization: Functional, Non-Functional, Technical
- Has "Explicit Non-Goals" section
- Has "Acceptance Criteria"
- Vietnamese with diacritics, technical terms in English

### 13.2 Needs Improvement

**Document**: `Quy trình Quản lý Công việc.md`

**Issues:**
- Has "To be continue..." instead of [WIP]
- Broken image links (`media/image1.tmp`, `media/image2.tmp`)
- Missing "Explicit Non-Goals" section

**How to Fix:**
1. Replace "To be continue..." with `[WIP]` in title
2. Re-upload images directly to Confluence
3. Add final section: "Explicit Non-Goals"

---

## 14. Contact & Support

- **Document Owner of `confluence_rules.md`**: Ask Technical Writer Team
- **Questions about SRS/Requirements**: Ask Product Owner
- **Questions about Technical Templates**: Ask Tech Lead

---

## Related Documents

- [documentation_rules.md](documentation_rules.md) - Code repository documentation rules (English)
