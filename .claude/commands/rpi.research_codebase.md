# Research Codebase
Documents and explains the codebase as it exists - no suggestions, improvements, or critiques.

## Initial Setup
Respond with:
```
I'm ready to research the codebase. Please provide your task, research question or area of interest, and I'll analyze it thoroughly by exploring relevant components and connections.
```

Wait for user's research query.

## Workflow
1. **Read any directly mentioned files** FULLY first (tickets, docs, config files)
2. **Analyze and decompose** the research question into composable research areas
3. **Conduct comprehensive research**:
   - Use parallel agents/tasks if supported to research different aspects concurrently
   - Location finding: WHERE files and components live
   - Code analysis: HOW specific code works
   - Pattern discovery: Examples of existing patterns
   - Testing patterns: How similar code is tested
   - Integration points: Where components connect
4. **Wait for all research to complete** before proceeding
5. **Synthesize findings** - compile all findings, connect across components, include file paths and line numbers
6. **Create directory**: `mkdir -p context-engineering`
7. **Generate research document** at `context-engineering/YYYY-MM-DD-description.md`
8. **Handle follow-up questions**: Append to same document with new section `## Follow-up Research [description]`

## Guidelines
**CRITICAL**: Your ONLY job is to document and explain the codebase as it exists

- DO NOT suggest improvements, changes, or enhancements unless explicitly asked
- DO NOT perform root cause analysis unless explicitly asked
- DO NOT critique implementation or identify problems
- DO NOT recommend refactoring, optimization, or architectural changes
- ONLY describe what exists, where it exists, how it works, and how components interact
- You are creating a technical map/documentation of the existing system
- Be specific: include file paths, function names, line numbers (`path/to/file.ext:123`)
- If unsure, note it as a question rather than stating as fact
- Document what IS, not what SHOULD BE
- Show how components connect and trace data flow
- Use parallel agents when possible to minimize context usage
- Always run fresh research - never rely solely on existing docs
- Read mentioned files FULLY before starting research
- Use web search only if tool supports it AND user explicitly asks for external info

## Chat Output Format
Present concise summary after completing research:
```
I've completed the research and documented my findings in context-engineering/YYYY-MM-DD-description.md.

Key findings:
- [Major discovery 1]
- [Major discovery 2]
- [Major discovery 3]

The document includes specific file references and code patterns you should follow.
```

## File Output Format
Create `context-engineering/YYYY-MM-DD-description.md`:

```markdown
# Research: [User's Question/Topic]

## Research Question
[Original user query]

## Summary
[High-level documentation of what was found, answering the user's question by describing what exists]

## Detailed Findings

### [Component/Area 1]
- Description of what exists (`file.ext:line`)
- How it connects to other components
- Current implementation details (without evaluation)

### [Component/Area 2]
[Similar structure for each component researched]

#### Key Files
- `path/to/file.ext` - [Responsibility]
  - Key function: `functionName()` at line 123
  - Key class: `ClassName` at line 45

#### Information Flow
Describe how data/requests flow through this component:
- Entry point: `file.ext:functionName()` at line X
- Processing: `another.ext:processFunction()` at line Y
- Output: `output.ext:resultFunction()` at line Z

#### Existing Patterns

**Error Handling**
[Patterns observed with code examples]
- Example: `path/to/file.ext:50-60`

**Testing Patterns**
[How this code is tested]
- Test location: `path/to/test.ext`
- Framework: [name]
- Example test: `path/to/test.ext:50-100`

**Naming Conventions**
[Patterns observed in the codebase]

**Code Organization**
[How code is structured]

#### Integration Points
How this component integrates with others:
- Connects to: `ComponentName` via `functionName()` in `file.ext:100`
- Implements: `InterfaceName` in `file.ext:50`
- Dependencies: [list]

## Code References
- `path/to/file.ext:123` - Description of what's there
- `another/file.ext:45-67` - Description of the code block

## Architecture Documentation
[Current patterns, conventions, and design implementations found in the codebase]

## Open Questions
[Any areas that need further investigation]
```
