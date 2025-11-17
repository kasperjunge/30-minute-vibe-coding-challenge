# Research-Plan-Implement Plugin

A comprehensive development workflow plugin for Claude Code that follows a three-phase approach: **Research** your codebase, **Plan** your implementation, and **Implement** with verification.

## Attribution

This plugin is based on advanced context engineering methodologies developed by [Dexter Horthy](https://github.com/humanlayer) at HumanLayer. The original prompts and workflow patterns are adapted from the [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) framework.

**Credits:**
- Original methodology: Dexter Horthy @ HumanLayer
- Adaptation & plugin packaging: Kasper Junge
- Further reading: [ACE for Coding Agents Blog Post](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md)

## Overview

This plugin enhances your development workflow with:

- **Specialized Research Agents**: Deep codebase analysis, pattern finding, and web research
- **Interactive Planning**: Research-driven implementation planning with parallel sub-agents
- **Structured Execution**: Phase-by-phase implementation with automated and manual verification

## Agents

### Codebase Research Agents

- **`codebase-analyzer`**: Analyzes implementation details, traces data flow, and documents technical workings with precise file:line references
- **`codebase-locator`**: Finds files, directories, and components relevant to features or tasks
- **`codebase-pattern-finder`**: Discovers similar implementations and existing patterns to model after
- **`web-search-researcher`**: Performs web research for documentation, best practices, and technical solutions

## Commands

The plugin provides three core commands that map to the Research → Plan → Implement workflow:

- **`/humanlayer.research_codebase`**: Comprehensive codebase research using parallel sub-agents
- **`/humanlayer.create_plan`**: Interactive implementation planning with codebase research
- **`/humanlayer.implement_plan`**: Executes approved plans with verification and testing

## Usage

### Research Workflow

1. Start with codebase research:
   ```
   /humanlayer.research_codebase
   ```
   Answer the prompt with your research question

2. For targeted analysis, use specialized agents:
   ```
   @codebase-analyzer analyze how authentication works in the API
   @codebase-locator find all files related to user management
   @codebase-pattern-finder show me pagination patterns in the codebase
   ```

### Planning Workflow

Create an implementation plan with integrated research:
```
/humanlayer.create_plan tasks/username/001-2025-01-15-feature-name/requirements.md
```

Or start with an interactive prompt:
```
/humanlayer.create_plan
```

### Implementation Workflow

Execute an approved plan:
```
/humanlayer.implement_plan tasks/username/001-2025-01-15-feature-name/plan.md
```

## Key Features

### Documentation-First Philosophy

All research agents follow a strict documentation-first approach:
- Document what EXISTS, not what SHOULD BE
- No unsolicited improvements or critiques
- Precise file:line references
- Focus on understanding, not evaluation

### Task Organization

The plugin uses a structured task directory system:
```
tasks/
└── username/
    └── NNN-YYYY-MM-DD-description/
        ├── research.md      (from /humanlayer.research_codebase)
        ├── requirements.md  (optional: your requirements)
        └── plan.md          (from /humanlayer.create_plan)
```

### Verification & Testing

Implementation plans include:
- Automated verification steps (tests, linting, builds)
- Manual verification steps (UI/UX, performance)
- Phase-by-phase success criteria
- Pause points for human validation

## Best Practices

1. **Start with Research**: Use `/humanlayer.research_codebase` before planning
2. **Be Specific**: The more detailed your prompts, the better the results
3. **Verify Continuously**: Check off success criteria as you go
4. **Document Decisions**: Keep research and plans in task directories
5. **Iterate**: Plans can be refined based on discoveries

## Requirements

- Claude Code installed
- Git repository (for metadata and task organization)
- Basic understanding of your project's tech stack

## References

- [Advanced Context Engineering for Coding Agents](https://github.com/humanlayer/advanced-context-engineering-for-coding-agents/blob/main/ace-fca.md) - Original methodology by Dexter Horthy
- [HumanLayer on GitHub](https://github.com/humanlayer) - Source of the ACE framework
