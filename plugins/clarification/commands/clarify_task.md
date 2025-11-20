# Clarify Task
Helps clarify any task, feature, or requirement by asking focused questions to uncover details, edge cases, and success criteria.

## Initial Setup
Respond with:
```
I'm ready to help clarify your task.

Please describe what you want to accomplish.
```

Wait for user input.

## Workflow
1. **Receive user's task description**
2. **Ask clarifying questions** (3-5 at a time) about:
   - Core objectives and desired outcomes
   - Key scenarios and use cases
   - Edge cases and error conditions
   - Constraints and limitations
   - Success criteria and acceptance criteria
   - Scope boundaries (what's in/out)
   - Priority and dependencies
3. **Continue asking** until no more questions remain
4. **Summarize clarified understanding** in a concise format

## Guidelines
- Each clarifying question should be numbered
- Focus on understanding WHAT needs to be done and WHY
- Ask about edge cases and error scenarios
- Identify explicit scope boundaries
- Uncover implicit assumptions
- Be specific: ask for measurable criteria when possible
- Avoid making assumptions - ask instead
- Prioritize questions that have the biggest impact on the approach

## Chat Output Format
After completing clarification:
```
I now have a clear understanding of your task:

**Objective**: [Clear statement of what needs to be accomplished]

**Key Requirements**:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

**Success Criteria**:
- [How we'll know this is done correctly]
- [Measurable outcome if applicable]

**Out of Scope**:
- [What we're explicitly NOT doing]

**Edge Cases to Consider**:
- [Edge case 1]
- [Edge case 2]

Ready to proceed?
```

## Example Questions to Ask

### Understanding the Core Need
- What problem are you trying to solve?
- What's the desired outcome?
- Who will benefit from this?
- What happens if we don't do this?

### Clarifying Scope
- What are the must-have features vs. nice-to-have?
- Are there any specific constraints (time, budget, technology)?
- What's explicitly out of scope?
- What's the minimum viable version?

### Edge Cases and Error Handling
- What should happen if [edge case scenario]?
- How should errors be handled?
- What are the failure modes?
- Are there any security considerations?

### Success Criteria
- How will you know this is successful?
- What does "done" look like?
- Are there any performance requirements?
- What should the user experience be?

### Dependencies and Context
- Does this depend on anything else?
- Does anything else depend on this?
- Is there existing code/infrastructure to consider?
- Are there any similar implementations to reference?
