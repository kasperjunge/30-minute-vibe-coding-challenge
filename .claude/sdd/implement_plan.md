# Implement Plan
Implements the project based on the approved implementation plan with rigorous testing.

## Initial Setup
Respond with:
```
I'm ready to implement the plan.

I'll read your plan from spec/plan.md, requirements from spec/requirements.md, and design from spec/design.md to guide the implementation.
```

Then proceed to read documents and start implementing.

## Workflow
1. **Read all spec documents** (`plan.md`, `requirements.md`, `design.md`) FULLY
2. **Check for existing checkmarks** `[x]` in plan.md to find where to start
3. **Create todo list** (if supported) to track progress
4. **For EACH TASK** (not phase):
   - Implement the task
   - Write tests (if not written)
   - Run tests
   - If tests fail: fix and retry (max 3 attempts)
   - If tests fail 3 times: **STOP** and report
   - Manual verification (if required)
   - Update checkboxes in plan.md
   - Report progress
   - Proceed to next task
5. **After phase complete**: 
   - **STOP** - do not continue to next phase
   - Summarize phase completion with all verification results
   - List any manual verification items needed
   - **Wait for user to review and verify before proceeding to next phase**

## Guidelines
**CRITICAL**: Test EVERY SINGLE TASK before moving to next (no exceptions!)

**CRITICAL**: STOP at the end of EVERY PHASE for human review and verification (no exceptions!)

- Follow plan's INTENT while adapting to reality
- Complete each task FULLY before moving to next
- Update checkboxes in plan.md as you complete items
- Each checkbox represents: code complete + tests passing
- Run tests at natural stopping points
- If tests fail 3 times: STOP, report, wait for user
- If codebase doesn't match expectations: STOP, present options
- Trust completed work, pick up from first unchecked item
- Stay aligned with requirements.md and design.md
- **Never proceed to the next phase without explicit user approval**

## Chat Output Format

### After Each Task:
```
Task [X.Y] Complete: [Task Name]

Changes Made:
- [Specific change 1 with file:line]
- [Specific change 2 with file:line]

Tests Written:
- [Test 1 description]
- [Test 2 description]

Test Results:
✓ All tests passing: `[command]`
✓ [X] tests passed

Manual Verification (if applicable):
- [What needs manual checking]

Proceeding to Task [X.Y+1]...
```

### After Each Phase:
```
Phase [N] Complete: [Phase Name]

Tasks Completed:
- Task [N.1]: [Name] ✓ Code ✓ Tests
- Task [N.2]: [Name] ✓ Code ✓ Tests  
- Task [N.3]: [Name] ✓ Code ✓ Tests

All Tests Passing:
✓ Unit tests: [X] passed
✓ Integration tests: [X] passed
✓ All verification steps completed

Manual Verification Needed (if any):
- [ ] [Manual check 1]
- [ ] [Manual check 2]

Phase Summary:
[Brief summary of what this phase accomplished]

Ready to proceed to Phase [N+1]?
```

### If Tests Fail 3 Times:
```
TESTING FAILURE - Need Guidance

Task: [Task number and name]

Issue: Tests have failed 3 times

Test Output:
[Last test failure output]

Attempts Made:
1. [What you tried first]
2. [What you tried second]
3. [What you tried third]

Analysis: [Why you think it's failing]

Options:
1. [Suggested fix approach]
2. Skip tests for this task and continue (not recommended)
3. Revise the plan for this task

How should I proceed?
```

### When Complete:
```
Implementation Complete!

Summary:
- [Number] phases completed
- All tasks from spec/plan.md implemented
- Verification results: [summary]

The project is ready for final review and testing.

Please test the application and verify it meets all requirements from spec/requirements.md.
```

## File Output Format
No new file is created. The command updates `spec/plan.md` by checking off items with `[x]` as they are completed:

```markdown
### Tasks

#### 2.1 Define Data Models
**File**: `src/types/index.ts`
...

**Test Requirements**:
- [x] Write tests to verify type definitions are correct
- [x] Test type safety with valid and invalid data
- [x] Tests pass: `npm run typecheck`

**Success Criteria**:
- [x] All code changes completed
- [x] Types compile without errors
- [x] All entities from design.md are defined
- [x] Type tests written and passing
```