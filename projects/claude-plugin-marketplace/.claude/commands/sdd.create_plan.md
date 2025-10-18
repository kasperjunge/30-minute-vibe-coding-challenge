# Create Implementation Plan
Creates detailed implementation plan based on requirements and design specifications.

## Initial Setup
Respond with:
```
I'm ready to create an implementation plan.

I'll read your requirements from spec/requirements.md and design from spec/design.md to create a detailed plan.
```

Then proceed to read documents and generate plan.

## Workflow
1. **Read** `spec/requirements.md` FULLY
2. **Read** `spec/design.md` FULLY
3. **Generate implementation plan** at `spec/plan.md` with:
   - 3-5 phases, each with specific tasks
   - Every task has: file paths, code structure, test requirements, verification steps, success criteria
   - Map tasks to user stories from requirements
   - Clear scope boundaries

## Guidelines
- Be specific: every task needs concrete file paths and line numbers
- Every task MUST have:
  - Test Requirements section
  - Verification Steps section
  - Success criteria (what tests to run, what to verify)
- Break work into 3-5 discrete phases
- Each phase should be independently verifiable
- Order matters - explain why phases come in sequence
- Map tasks to specific user stories from requirements.md
- Include "What We're NOT Doing" section to prevent scope creep
- Plan should be detailed enough to execute mechanically

## Chat Output Format
After completing plan:
```
I've created a detailed implementation plan at spec/plan.md.

The plan includes:
- [X] phases with specific tasks
- File paths and code structures from design.md
- Acceptance criteria from requirements.md
- Clear verification checklist

Please review and let me know if you'd like any adjustments.
```

## File Output Format
Create `spec/plan.md`:

```markdown
# Implementation Plan: [Project Name]

## Overview
[1-2 sentence summary of what we're building based on requirements and design]

## Current State
- Empty project / Starting from scratch
- Target tech stack: [From design.md]

## Desired End State
[Clear description of what "done" looks like, referencing requirements]

**Success Criteria:**
- [ ] All user stories from requirements.md are implemented
- [ ] All acceptance criteria are met
- [ ] Application matches design specifications
- [ ] Code is tested and runs without errors

## What We're NOT Doing
[Explicitly list out-of-scope items from requirements.md]

## Implementation Approach
[High-level strategy: which phases, why this order, key dependencies]

---

## Phase 1: Project Setup & Foundation

### Overview
Set up the development environment and project structure according to design specifications.

### Tasks

#### 1.1 Initialize Project
**Action**:
- Create project using [tool, e.g., "Vite", "Create React App"]
- Install dependencies listed in design.md
- Set up file structure from design.md

**Files Created**:
- `package.json` / `requirements.txt` / [dependency file]
- `src/` directory structure
- Configuration files (tsconfig.json, vite.config.js, etc.)

**Success Criteria**:
- [ ] Project builds without errors: `[build command]`
- [ ] Dev server starts: `[dev command]`
- [ ] All dependencies installed correctly

#### 1.2 Setup Development Tools
**Action**:
- Configure linting and formatting
- Set up testing framework
- Add scripts to package.json

**Success Criteria**:
- [ ] Linter runs: `[lint command]`
- [ ] Formatter works: `[format command]`
- [ ] Test runner works: `[test command]`

---

## Phase 2: Data Layer

### Overview
Implement data models, storage, and state management as defined in design.md.

### Tasks

#### 2.1 Define Data Models
**File**: `src/types/index.ts` (or equivalent)
**Action**:
- Implement [Entity1] interface from design.md
- Implement [Entity2] interface from design.md
- Add type exports

**Code Structure**:
```typescript
interface Entity1 {
  id: string;
  field1: string;
  // ... from design
}
```

**Test Requirements**:
- [ ] Write tests to verify type definitions are correct
- [ ] Test type safety with valid and invalid data
- [ ] Tests pass: `npm run typecheck` or equivalent

**Verification Steps**:
1. Run type checker: `[typecheck command]`
2. Verify no type errors in output
3. Expected: Clean compilation, all types defined

**Success Criteria**:
- [ ] All code changes completed
- [ ] Types compile without errors
- [ ] All entities from design.md are defined
- [ ] Type tests written and passing

#### 2.2 Implement Storage Layer
**File**: `src/utils/storage.ts` (or equivalent)
**Action**:
- Create [storage approach from design.md]
- Implement CRUD operations for each entity
- Add error handling

**Functions to Implement**:
- `create[Entity](data: Entity): Promise<Entity>`
- `read[Entity](id: string): Promise<Entity>`
- `update[Entity](id: string, data: Partial<Entity>): Promise<Entity>`
- `delete[Entity](id: string): Promise<void>`

**Test Requirements**:
- [ ] Write unit tests for each CRUD operation
- [ ] Test error handling (invalid data, not found, etc.)
- [ ] Test data persistence and retrieval
- [ ] Tests pass: `[test command]`

**Verification Steps**:
1. Run tests: `[test command]`
2. Verify all CRUD operations tested
3. Expected: All tests passing, 100% coverage on storage functions

**Success Criteria**:
- [ ] All code changes completed
- [ ] All CRUD operations implemented
- [ ] Unit tests written for all operations
- [ ] All tests passing
- [ ] Error cases handled and tested

---

## Phase 3: Core Components

### Overview
Build the UI components defined in design.md, focusing on core functionality first.

### Tasks

#### 3.1 Create [ComponentName] Component
**File**: `src/components/[ComponentName].tsx` (from design.md)
**Action**:
- Implement component as specified in design.md
- Add props/interface from design
- Implement event handlers
- Add basic styling

**Component Structure** (from design.md):
```typescript
interface ComponentProps {
  // Props from design.md
}

function ComponentName({ prop1, prop2 }: ComponentProps) {
  // Implementation
}
```

**Implements User Story**: [Reference specific user story from requirements.md]

**Test Requirements**:
- [ ] Write component tests (rendering, props, interactions)
- [ ] Test event handlers trigger correctly
- [ ] Test edge cases (empty data, errors, etc.)
- [ ] Tests pass: `[test command]`

**Verification Steps**:
1. Run tests: `[test command]`
2. Manual check: Open app, verify component appears correctly
3. Expected: Tests passing, component renders and functions as designed

**Success Criteria**:
- [ ] All code changes completed
- [ ] Component implemented per design
- [ ] Component tests written and passing
- [ ] Manual verification confirms visual appearance
- [ ] Event handlers tested and working

---

## Phase 4: User Flows & Integration

### Overview
Connect components together to implement complete user flows from requirements.md.

### Tasks

#### 4.1 Implement [Flow Name] Flow
**User Story**: [Reference specific user story from requirements.md]
**Components Involved**: [List from design.md]

**Action**:
- Connect [Component A] to [Component B]
- Implement data flow as per design.md
- Add error handling for edge cases from requirements.md

**Flow Steps** (from design.md):
1. User [action]
2. System [response]
3. User sees [result]

**Acceptance Criteria** (from requirements.md):
- [ ] [Criterion 1 from requirements]
- [ ] [Criterion 2 from requirements]
- [ ] [Criterion 3 from requirements]

**Edge Cases**:
- [ ] [Edge case 1 from requirements] handles correctly
- [ ] [Edge case 2 from requirements] handles correctly

---

## Phase 5: Polish & Testing

### Overview
Add finishing touches, handle edge cases, and verify all acceptance criteria.

### Tasks

#### 5.1 UI/UX Polish
**Action**:
- Refine styling to match design vision
- Add loading states
- Add empty states
- Improve error messages

**Success Criteria**:
- [ ] UI matches design specifications
- [ ] All interactive elements are accessible
- [ ] Loading states are clear
- [ ] Empty states are helpful

#### 5.2 Error Handling
**Action**:
- Implement error boundaries (if applicable)
- Add user-friendly error messages
- Handle all edge cases from requirements.md

**Success Criteria**:
- [ ] No uncaught errors
- [ ] Users see helpful error messages
- [ ] Edge cases handled gracefully

#### 5.3 Final Testing
**Action**:
- Write unit tests for critical functions
- Manually test all user flows
- Test all acceptance criteria from requirements.md

**Success Criteria**:
- [ ] All automated tests pass: `[test command]`
- [ ] All user stories verified manually
- [ ] All acceptance criteria met

---

## Verification Checklist

### Requirements Completion
[For each user story from requirements.md]
- [ ] User Story 1: [Name]
  - [ ] Acceptance criterion 1
  - [ ] Acceptance criterion 2
- [ ] User Story 2: [Name]
  - [ ] Acceptance criterion 1
  - [ ] Acceptance criterion 2

### Design Implementation
- [ ] All components from design.md implemented
- [ ] Data model matches design.md
- [ ] File structure matches design.md
- [ ] Tech stack matches design.md

### Quality Checks
- [ ] Code builds without errors: `[build command]`
- [ ] Linter passes: `[lint command]`
- [ ] Tests pass: `[test command]`
- [ ] Application runs: `[dev/start command]`

### User Acceptance
- [ ] Manually test all user flows
- [ ] Verify all edge cases
- [ ] Check performance (if requirements specify)
- [ ] Verify accessibility (if requirements specify)

---

## Development Notes

### Suggested Order
1. Don't skip phases - each builds on the previous
2. Verify success criteria before moving to next task
3. Update this document if you discover issues in specs

### If You Get Stuck
- Review requirements.md for the "why"
- Review design.md for the "how"
- Ask questions if specs are unclear
- Update specs if you find gaps

## References
- Requirements: `spec/requirements.md`
- Design: `spec/design.md`
```