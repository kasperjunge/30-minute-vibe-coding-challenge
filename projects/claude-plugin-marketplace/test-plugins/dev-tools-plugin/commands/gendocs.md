---
description: Generate documentation for code
---

# Generate Documentation Command

Automatically generate comprehensive documentation for your codebase.

## Usage

```
/gendocs [path] [--format=markdown|html]
```

## Parameters

- `path`: File or directory to document (defaults to current workspace)
- `--format`: Output format - `markdown` or `html` (default: markdown)

## Features

- Extracts function/class signatures
- Generates usage examples
- Creates API references
- Builds table of contents
- Includes type annotations

## Examples

```
/gendocs src/api --format=markdown
/gendocs lib/utils.py
```

## Output Location

Documentation is saved to `docs/` directory in your workspace.

