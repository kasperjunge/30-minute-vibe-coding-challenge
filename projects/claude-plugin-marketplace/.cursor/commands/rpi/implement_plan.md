# Implement Plan
Implements approved technical plan with phases, specific changes, and success criteria.

## Initial Setup
Respond with:
```
I'm ready to implement the plan. Please provide the path to your implementation plan (e.g., context-engineering/plan.md).

I'll read the plan, check for any existing progress, and begin implementation.
```

## Workflow
1. **Read the plan completely** - read entire plan, check for checkmarks `[x]`, read all mentioned files FULLY
2. **Create todo list** (if supported) to track progress
3. **Think deeply before starting** - understand how pieces fit together, relationships between components
4. **Determine starting point**:
   - If checkmarks exist: pick up from first unchecked item
   - If no checkmarks: start with Phase 1
5. **For each phase**:
   - Implement the specific changes listed
   - Follow plan's intent while adapting to actual code structure
   - Run verification at natural stopping points
   - Execute automated verification steps
   - Fix failures before proceeding
   - Update checkboxes `[x]` in plan file
   - Report progress
   - **STOP at end of phase for user review**
6. **If codebase doesn't match expectations**: STOP and present options
7. **When complete**: summarize all phases and manual verification needed

## Guidelines
- Follow plan's INTENT while adapting to reality
- Complete each phase FULLY before moving to next
- Update checkboxes in plan file as you complete items
- Run tests at natural stopping points - batch verification when it makes sense
- If codebase doesn't match expectations: STOP, present options, wait for guidance
- Trust completed work, pick up from first unchecked item
- Stay mechanical - you're executing the plan, not making new design decisions
- Major new decisions mean the plan was incomplete - ask rather than assume
- Keep forward momentum - balance following plan with adapting to reality
- If context fills up after a phase, that's OK - plan tracks progress
- Next session picks up from first unchecked item

## Chat Output Format

### After Each Phase:
```
Phase [N] Complete: [Phase Name]

Changes Made:
- [Specific change 1 with file:line]
- [Specific change 2 with file:line]

Verification Results:
✓ Tests passed: `[command]`
✓ Linting passed: `[command]`
✓ Build succeeded: `[command]`

Manual Verification Needed:
- [ ] [Manual check 1]
- [ ] [Manual check 2]

Deviations from Plan:
[Any changes from original plan and why]

Proceeding to Phase [N+1]?
```

### If Codebase Doesn't Match:
```
Issue in Phase [N]:

Expected: [what the plan says]
Found: [actual situation in the codebase]

Why this matters: [impact on implementation]

Options:
1. [Adapt the plan to current reality]
2. [Alternative approach]
3. [What else needs to be investigated]

How should I proceed?
```

### When Complete:
```
Implementation Complete!

Summary:
- [Number] phases completed
- All automated verification passing
- Manual verification items listed below

Manual Verification Needed:
[List all manual checks from all phases]

Next Steps:
1. Review the implemented code
2. Perform manual verification
3. Test edge cases
4. Consider the work ready for review
```

## File Output Format
No new file is created. The command updates the existing plan file (`context-engineering/plan.md`) by checking off items with `[x]` as they are completed:

```markdown
## Phase 1: [Phase Name]

### Changes Required

#### 1. [Component/File Name]
**File**: `path/to/file.ext`
**Changes**:
- [x] Add function `functionName()` at line ~[X]
- [x] Modify `existingFunction()` at line [Y]
- [x] Update import statements at line [Z]

### Success Criteria

#### Automated Verification:
- [x] Tests pass: `npm test`
- [x] Linting passes: `npm run lint`
- [x] Build succeeds: `npm run build`

#### Manual Verification:
- [ ] Feature works in UI when clicking button
- [ ] Handles empty input gracefully
```
