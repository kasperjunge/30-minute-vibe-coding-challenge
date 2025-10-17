# Clarify Design
Clarifies technical design and architecture based on requirements.

## Initial Setup
Respond with:
```
I'm ready to help clarify the technical design.

I'll read your requirements from spec/requirements.md to understand what needs to be built.

Please describe your tech stack and design preferences.
```

Wait for user input.

## Workflow
1. **Read** `spec/requirements.md` FULLY
2. **Receive user's tech preferences**
3. **Ask clarifying questions** (3-5 at a time) about:
   - Specific technologies and versions
   - Architecture patterns and structure
   - Data storage and management
   - UI/interface approach
   - Integration points and dependencies
   - Testing approach and preferences
4. **Continue asking** until no more questions remain
5. **Generate design document** at `spec/design.md`

## Guidelines
- Each bullet with a clarifying question should be numbered
- Be specific: name actual technologies with versions, not placeholders
- Align with requirements: every design decision should trace back to requirements
- If user doesn't mention UI approach and requirements need one, ask or suggest
- If user has no testing preferences, create appropriate strategy based on tech stack
- Include concrete file/folder structures
- Match complexity to project scope - don't over-engineer
- Design for both happy path and error cases

## Chat Output Format
After completing design:
```
I've created a design document at spec/design.md.

The design includes:
- Complete tech stack with rationale
- Component breakdown with responsibilities
- Data model and UI structure
- Key user flows and interactions
- File structure and development approach

Please review and let me know if you'd like any adjustments.
```

## File Output Format
Create `spec/design.md`:

```markdown
# Design: [Project Name]

## Design Overview
[2-3 sentences describing the technical approach and key architectural decisions]

## Tech Stack

### Languages & Frameworks
- **Language**: [e.g., JavaScript/TypeScript]
- **Framework**: [e.g., React 18]
- **Build Tool**: [e.g., Vite]
- **Styling**: [e.g., Tailwind CSS]

### Data & State
- **Data Storage**: [e.g., localStorage, PostgreSQL, MongoDB]
- **State Management**: [e.g., React Context, Redux, Zustand]
- **Data Format**: [e.g., JSON, structured data model]

### Dependencies
- [Library 1]: [Purpose]
- [Library 2]: [Purpose]

**Rationale**: [Why this tech stack? How does it fit the requirements?]

## System Architecture

### High-Level Architecture
```
[Diagram or description of system layers]

Example:
┌─────────────────────────────┐
│   Presentation Layer        │ ← UI Components
├─────────────────────────────┤
│   Business Logic Layer      │ ← State Management
├─────────────────────────────┤
│   Data Layer                │ ← Storage/API
└─────────────────────────────┘
```

### Component Breakdown

#### Component: [Name]
**Purpose**: [What this component does]  
**Location**: `src/components/ComponentName.tsx`  
**Responsibilities**:
- [Responsibility 1]
- [Responsibility 2]

**Props/Interface**:
```typescript
interface ComponentProps {
  prop1: string;
  prop2: number;
  onAction: () => void;
}
```

**State**:
- [State item 1]: [Purpose]
- [State item 2]: [Purpose]

## Data Model

### Entity: [EntityName]
```typescript
interface EntityName {
  id: string;
  field1: string;
  field2: number;
  field3: Date;
}
```

**Purpose**: [What this represents]  
**Relationships**: [How it relates to other entities]

## User Interface Design

### Screen: [ScreenName]
**Purpose**: [What user accomplishes here]  
**Layout**:
```
┌─────────────────────────┐
│  Header                 │
├─────────────────────────┤
│  Main Content           │
│  - Element 1            │
│  - Element 2            │
├─────────────────────────┤
│  Footer/Actions         │
└─────────────────────────┘
```

**Key Elements**:
- [Element 1]: [Purpose and behavior]
- [Element 2]: [Purpose and behavior]

**User Interactions**:
- [Action 1] → [Result]
- [Action 2] → [Result]

## Key Interactions & Flows

### Flow: [FlowName]
**Scenario**: [User story this implements]

1. User [action]
2. System [response]
3. System [next step]
4. User sees [result]

**Error Handling**:
- If [error condition] → [behavior]
- If [error condition] → [behavior]

## File Structure
```
project-root/
├── src/
│   ├── components/
│   │   ├── ComponentA.tsx
│   │   └── ComponentB.tsx
│   ├── hooks/
│   │   └── useCustomHook.ts
│   ├── utils/
│   │   └── helpers.ts
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   └── main.tsx
├── spec/
│   ├── requirements.md
│   └── design.md
├── package.json
└── README.md
```

## Design Decisions & Tradeoffs

### Decision: [DecisionName]
**Choice**: [What we decided]  
**Alternatives Considered**: [What else we could do]  
**Rationale**: [Why we chose this]  
**Tradeoffs**: [What we gain/lose]

## Non-Functional Considerations

### Performance
- [Performance approach, e.g., "Lazy load components"]
- [Optimization strategy, e.g., "Memoize expensive calculations"]

### Scalability
- [How design handles growth]
- [What needs to change if requirements scale]

### Accessibility
- [Accessibility approach, e.g., "ARIA labels on all interactive elements"]
- [Keyboard navigation strategy]

### Error Handling
- [Error handling strategy]
- [User feedback approach]

## Testing Strategy

**Philosophy**: Every task must be verified before moving to the next. Testing is incremental and continuous.

### Testing Tools & Framework
- **Testing Framework**: [e.g., Jest, pytest, Vitest, etc.]
- **Testing Library**: [e.g., React Testing Library, unittest, etc.]
- **Test Runner Command**: `[e.g., npm test, pytest, etc.]`
- **Coverage Tool** (if applicable): [e.g., Jest coverage, coverage.py]

### Verification Approach for Each Task Type

#### Code/Logic Tasks
- **Verification Method**: Automated tests
- **When to Test**: [After each task / TDD / as you go]
- **What to Test**: 
  - Function behavior with valid inputs
  - Edge cases and error handling
  - Integration with other components

#### UI/Component Tasks
- **Verification Method**: [Automated tests + manual verification / manual only]
- **Automated Tests**: Component rendering, props, interactions
- **Manual Verification**: Visual appearance, responsiveness, UX flow

#### Configuration/Setup Tasks
- **Verification Method**: [e.g., "Run build command", "Run dev server"]
- **Success Criteria**: No errors, expected output

### Test Writing Approach
[Describe when tests should be written:]
- **Test-Driven Development (TDD)**: Write tests before implementation
- **Test-After**: Implement feature, then write tests
- **Incremental**: Write tests as you implement

### Critical Testing Rules
1. Every task must have clear verification steps
2. Tests must pass before moving to next task
3. If tests fail repeatedly (3+ times), stop and reassess
4. Document any tasks that cannot be automated (manual verification)

### Unit Tests
- **What**: Test individual components/functions in isolation
- **Where**: `src/__tests__/` or alongside source files
- **Key areas**: [List critical functions to test]
- **Run Command**: `[command to run unit tests]`

### Integration Tests
- **What**: Test component interactions and data flow
- **Key flows**: [List important user flows to test]
- **Run Command**: `[command to run integration tests]`

### Manual Testing Scenarios
- **What**: UI/UX verification that requires human judgment
- **Key scenarios**: [List scenarios to manually verify]
- **When**: After completing each phase with UI changes

## Development Approach

### Phase Breakdown
[High-level phases - detailed breakdown happens in plan.md]
1. **Phase 1**: [e.g., "Setup & Core Structure"]
2. **Phase 2**: [e.g., "Data Layer"]
3. **Phase 3**: [e.g., "UI Components"]
4. **Phase 4**: [e.g., "Integration & Polish"]

### Development Standards
- [Coding conventions]
- [Naming conventions]
- [Documentation requirements]

## Open Questions
[Any remaining technical uncertainties - resolve before planning]
- [Question 1]
- [Question 2]

## References
- Requirements: `spec/requirements.md`
- [Any relevant documentation or resources]
```
