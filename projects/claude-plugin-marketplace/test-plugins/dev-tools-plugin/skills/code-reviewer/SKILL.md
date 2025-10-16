---
description: Automated code review skill for identifying issues and suggesting improvements
tags: ["code-quality", "review", "best-practices"]
---

# Code Reviewer Skill

Analyzes code for quality, security, and best practice adherence.

## Purpose

This skill enables Claude to automatically review code during development, identifying:
- Code quality issues
- Security vulnerabilities
- Performance bottlenecks
- Best practice violations
- Documentation gaps

## When Invoked

Claude automatically uses this skill when:
- Reviewing code changes
- Analyzing pull requests
- Evaluating file modifications
- Checking code before commits

## Analysis Areas

### Code Quality
- Readability and maintainability
- Naming conventions
- Code duplication
- Complexity metrics

### Security
- Input validation
- Authentication/authorization
- Data sanitization
- Secure configurations

### Performance
- Algorithm efficiency
- Resource usage
- Caching opportunities
- Query optimization

### Best Practices
- Language-specific idioms
- Framework conventions
- Design patterns
- Error handling

## Output Format

Provides structured feedback with:
- Severity levels (critical, high, medium, low)
- Line-specific references
- Explanation of issues
- Concrete fix suggestions
- Links to documentation

## Example Usage

When Claude sees code like:

```python
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
```

The skill identifies:
- **CRITICAL**: SQL injection vulnerability
- **HIGH**: Plain text password comparison
- **MEDIUM**: No error handling
- Suggests: Use parameterized queries, hash passwords, add try-catch

