# Create Requirements
Quick requirements generation with AI-driven creation and review cycle.

## Initial Setup
Respond with:
```
I'm ready to help create your project requirements.

Please provide a brief description of what you want to build (1-3 paragraphs is fine).
```

Wait for user input.

## Workflow
1. **Receive user's brief project description**
2. **Generate complete requirements document** immediately at `spec/requirements.md`
3. **Present the requirements** to user with summary
4. **Ask**: "Does this look good, or would you like me to make adjustments?"
5. **If adjustments needed**: make changes and repeat step 3-4
6. **Guide toward completion** (AI should signal when things look complete)

## Guidelines
- Make reasonable assumptions based on best practices
- Focus on WHAT users need, not HOW to build it
- Be specific with acceptance criteria (testable)
- Include common edge cases proactively
- Use aggressive "Out of Scope" section
- AI should guide conversation toward wrap-up after 2-3 adjustment rounds
- Stay user-focused: every feature should map to a clear user need
- Avoid vague terms like "user-friendly" or "fast"

## Chat Output Format
After generating requirements.md:
```
I've created a requirements document at spec/requirements.md based on your description.

Key decisions I made:
- [Decision 1 - e.g., "Focused on single-user experience (multi-user out of scope)"]
- [Decision 2 - e.g., "Prioritized core task management over advanced features"]
- [Decision 3 - e.g., "Included data export as key requirement based on user control needs"]

The document includes:
- [X] user stories with acceptance criteria
- [X] functional requirements
- Non-functional requirements
- Clear scope boundaries

Does this look good, or would you like me to make adjustments?
```

After adjustments (if needed):
```
I've updated spec/requirements.md with your feedback.

Changes made:
- [Change 1]
- [Change 2]

Does this look good now, or would you like further adjustments?
```

## File Output Format
Create `spec/requirements.md`:

```markdown
# Requirements: [Project Name]

## Project Overview
[2-3 sentences describing what this project is and why it exists]

## Target Users
[Who will use this? What's their context and needs?]

## User Stories

### Story 1: [User Goal]
**As a** [type of user]  
**I want to** [action]  
**So that** [benefit/value]

**Acceptance Criteria:**
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

**Edge Cases:**
- [What happens when X?]
- [What happens when Y?]

### Story 2: [Another User Goal]
[Same structure as Story 1]

[Continue for all major user stories]

## Functional Requirements

### FR1: [Requirement Name]
**Description**: [What the system must do]  
**Priority**: High/Medium/Low  
**Acceptance**: [How to verify this works]

### FR2: [Another Requirement]
[Same structure]

## Non-Functional Requirements

### Performance
- [e.g., "Page load time under 2 seconds"]
- [e.g., "Support up to 1000 items"]

### Usability
- [e.g., "Interface should be intuitive for first-time users"]
- [e.g., "Key actions accessible within 2 clicks"]

### Accessibility
- [Any accessibility requirements if applicable]

## Out of Scope
[Explicitly list what we're NOT building to prevent scope creep]
- [Feature/functionality 1]
- [Feature/functionality 2]

## Success Criteria
[How do we know this project succeeded?]
- [ ] [Measurable success criterion 1]
- [ ] [Measurable success criterion 2]

## Open Questions
[Any remaining uncertainties - resolve these before design phase]
- [Question 1]
- [Question 2]
```

