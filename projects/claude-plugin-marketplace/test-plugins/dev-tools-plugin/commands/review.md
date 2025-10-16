---
description: Perform a comprehensive code review
---

# Code Review Command

Perform an in-depth code review of specified files or directories.

## Usage

```
/review [path] [--depth=full|quick]
```

## Parameters

- `path`: File or directory to review (defaults to current workspace)
- `--depth`: Review depth - `full` for comprehensive or `quick` for fast scan (default: quick)

## What it checks

- Code style and formatting
- Best practices adherence
- Potential bugs and security issues
- Performance considerations
- Documentation completeness
- Test coverage gaps

## Examples

```
/review src/main.py --depth=full
/review . --depth=quick
```

## Output

Provides a structured review with:
- Priority issues (high, medium, low)
- Specific file locations and line numbers
- Suggested fixes
- Overall code quality score

