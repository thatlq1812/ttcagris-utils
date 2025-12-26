# [PROC] Process Title

| Version | Date | Author | Description |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | @Author Name | Initial document |

**Status**: Active | Draft | Deprecated

---

## 1. Purpose

Brief statement of what this process aims to achieve and why it exists.

**Example:**
> This process defines how engineering team manages and tracks work items throughout the sprint lifecycle, ensuring transparency and accountability.

---

## 2. Scope

### 2.1 Applies To

- Backend Team
- Frontend Team
- Mobile Team
- QA Team

### 2.2 Does Not Apply To

- External contractors (separate process)
- Emergency hotfixes (see Emergency Process)

---

## 3. Definitions and Terminology

| Term | Definition |
| --- | --- |
| Sprint | One-week development cycle |
| Epic | Large body of work broken into tasks |
| Task | Unit of work that can be completed in sprint |
| Sub-task | Component of task managed at individual level |
| Assignee | Person responsible for completing task |
| Owner | Person accountable for process or document |

---

## 4. Roles and Responsibilities

### 4.1 Engineering Manager

- Creates epics and tasks
- Assigns work to team members
- Tracks overall sprint progress
- Resolves blockers

### 4.2 Team Members

- Creates sub-tasks as needed
- Updates task status regularly
- Attends daily standups
- Delivers work on time

### 4.3 QA Team

- Reviews completed tasks
- Performs testing
- Reports bugs
- Signs off on releases

---

## 5. Process Steps

### 5.1 Sprint Planning (Start of Sprint)

**When**: First day of sprint
**Duration**: 1-2 hours
**Participants**: Engineering Manager, Tech Leads, Team Members

**Steps**:
1. Engineering Manager presents tasks for sprint
2. Team reviews and estimates effort
3. Tasks assigned based on capacity
4. Team commits to sprint goal

**Output**: 
- Sprint backlog finalized
- All tasks assigned
- Sprint goal documented

### 5.2 Daily Development

#### 5.2.1 Task Status Management

**Task States**:
- **TODO**: Task not yet started
- **In Progress**: Actively being worked on
- **In Review**: Code complete, awaiting review
- **Done**: Fully complete and verified

**Rules**:
- Only task assignee can change task status
- Must update status at least once per day
- Add comments when blocked

#### 5.2.2 Daily Standup

**When**: Every morning 9:30 AM
**Duration**: 15 minutes max
**Format**: Each person shares:
- What I completed yesterday
- What I'm working on today
- Any blockers

### 5.3 Code Review Process

**Before submitting for review**:
1. Self-review code
2. Run all tests locally
3. Update documentation
4. Fill out PR template

**Review criteria**:
- Code follows style guide
- Tests included and passing
- No security vulnerabilities
- Documentation updated

**Review SLA**: 24 hours

### 5.4 QA Handoff

**When**: Task status changed to "In Review"

**QA Requirements**:
- Build deployed to TEST environment
- Test data prepared
- API documentation updated
- Test scenarios documented

**QA Process**:
1. Verify against acceptance criteria
2. Execute test scenarios
3. Report bugs if found
4. Sign off when passed

### 5.5 Task Completion

**Definition of Done**:
- [ ] Code merged to main branch
- [ ] Build successful on DEV environment
- [ ] Release branch created
- [ ] Deployed to TEST environment
- [ ] Technical documentation created
- [ ] Test data ready on TEST
- [ ] QA sign-off received

**Only assignee can mark task as Done**.

### 5.6 Sprint Retrospective (End of Sprint)

**When**: Last day of sprint
**Duration**: 1 hour
**Participants**: All team members

**Agenda**:
1. What went well?
2. What could be improved?
3. Action items for next sprint

---

## 6. Workflows

### 6.1 Standard Task Flow

```
TODO → In Progress → In Review → Done
```

### 6.2 Task with Bugs Found

```
In Review → (Bug Found) → In Progress → In Review → Done
```

### 6.3 Blocked Task

```
In Progress → Blocked → (Blocker Resolved) → In Progress → Done
```

---

## 7. Tools and Systems

### 7.1 Project Management

- **Tool**: Jira
- **Space**: Tech Board
- **Access**: All team members

### 7.2 Code Repository

- **Tool**: Azure DevOps / GitHub
- **Branching Strategy**: Git Flow
- **Naming Convention**: `feat/TASK-ID-description`

### 7.3 Communication

- **Daily Updates**: Microsoft Teams channel
- **Build Notifications**: Teams channel [AgriOS]_QC_Builds
- **Urgent Issues**: Direct message or phone

---

## 8. Naming Conventions

### 8.1 Epic Naming

Format: `[Dev] Epic Title`

**Example:**
- `[Dev] User Authentication System`
- `[Dev] Product Review & Rating`

### 8.2 Task Naming

Format: `[Platform] Task Description`

**Platforms**: API, Mobile, Portal, DevOps

**Examples:**
- `[API] Implement login endpoint`
- `[Mobile] Design profile screen`
- `[Portal] Add user management page`

### 8.3 Git Branch Naming

Format: `type/TASK-ID-short-description`

**Types**: feat, fix, refactor, docs, test

**Examples:**
- `feat/AGRIOS-123-user-login`
- `fix/AGRIOS-456-null-pointer-bug`
- `refactor/AGRIOS-789-optimize-query`

---

## 9. Build Submission Process

### 9.1 When to Submit Build

After task status changed to "In Review" and all Definition of Done items checked.

### 9.2 Where to Submit

- **Channel**: [AgriOS]_QC_Builds on Microsoft Teams
- **Thread**:
  - Backend: [BUILD]BE-QC
  - Mobile: [BUILD]Mobile App - QC
  - Web: [BUILD]WEB - QC

### 9.3 Required Information

```markdown
**Feature Name**: [Task title]
**Jira Task**: AGRIOS-XXX
**Scope**:
- What's new: ...
- What changed: ...
- Impact areas: ...

**Documentation**: [Link to API doc / Figma]
**Test Info**:
- API Collection: [Postman link]
- Test Account: username / password
- Test Data: [Description]

**Deployment**:
- Environment: TEST
- Version: v1.2.3
- Deploy Time: DD MMM YYYY HH:MM
```

---

## 10. Exception Handling

### 10.1 Bugs During Sprint

- Bugs found during sprint are NOT tracked in Tech Board
- Managed in QC space
- Developer self-manages fixes
- No impact on sprint velocity

### 10.2 Ad-hoc Tasks

- Tasks unrelated to sprint go to Tech Operation Board
- Do NOT create in Tech Board
- Examples: Infrastructure issues, urgent support

### 10.3 Task Status Reversal

- Once task is "Done", cannot revert to other states
- If changes needed, create new task
- Link to original task for context

---

## 11. Communication Guidelines

### 11.1 Task Communication

- **All task discussions** must be commented in Jira
- Include all stakeholders in comments
- Tag relevant people with @mention

### 11.2 Private Messages

- Private messages are for reference only
- NOT official source of truth
- Decisions must be documented in Jira

### 11.3 Decision Making

- Decisions require confirmation from stakeholders
- Document in task comments
- Include rationale and alternatives considered

---

## 12. Metrics and Reporting

### 12.1 Sprint Metrics

- **Velocity**: Story points completed per sprint
- **Completion Rate**: % of committed tasks completed
- **Cycle Time**: Average time from TODO to Done

### 12.2 Quality Metrics

- **Bug Rate**: Bugs per completed task
- **Reopen Rate**: % of tasks reopened after Done
- **Code Review Time**: Average review turnaround

---

## 13. Continuous Improvement

### 13.1 Process Review Schedule

- Monthly review of process effectiveness
- Gather feedback from team
- Update process based on learnings

### 13.2 Feedback Mechanism

- Submit process improvement suggestions to Engineering Manager
- Discuss in retrospectives
- Vote on significant changes

---

## 14. Compliance and Audit

### 14.1 Documentation Requirements

All process steps must be documented according to:
- [documentation_rules.md](../documentation_rules.md)
- [confluence_rules.md](../confluence_rules.md)

### 14.2 Audit Trail

- All task status changes logged automatically
- Decision rationale documented in comments
- Code review approvals tracked in Git

---

## 15. Related Documents

- [PROC] Code Review Process
- [PROC] Release Management Process
- [PROC] Incident Response Process
- [ORG] Team Structure and Roles

---

## 16. Revision History

| Version | Date | Author | Changes |
| --- | --- | --- | --- |
| 1.0.0 | DD MMM YYYY | @Name | Initial document |
| 1.1.0 | DD MMM YYYY | @Name | Added exception handling |
| 1.2.0 | DD MMM YYYY | @Name | Updated build submission format |

---

## 17. Approval

**Reviewed By**:
- [ ] Engineering Manager: @Name
- [ ] Tech Lead: @Name
- [ ] QA Lead: @Name

**Approved By**: @Engineering Manager
**Approval Date**: DD MMM YYYY
**Effective Date**: DD MMM YYYY
