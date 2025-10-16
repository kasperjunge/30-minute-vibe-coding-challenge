# Dev Tools Plugin

A comprehensive development toolkit for Claude Code that enhances code quality, testing, and documentation workflows.

## 🚀 Features

### Commands
- **`/review`** - Perform thorough code reviews with actionable feedback
- **`/gendocs`** - Auto-generate documentation from your codebase

### Agents
- **Test Specialist** - Expert agent for test creation and coverage improvement

### Skills
- **Code Reviewer** - Automated code analysis for quality and security

## 📦 Installation

Add the marketplace and install the plugin:

```bash
/plugin marketplace add https://marketplace.example.com/marketplace.json
/plugin install dev-tools
```

## 🔧 Usage

### Code Review

Review a single file:
```
/review src/auth.py --depth=full
```

Quick scan of entire project:
```
/review . --depth=quick
```

### Documentation Generation

Generate markdown docs:
```
/gendocs src/api --format=markdown
```

Generate HTML docs:
```
/gendocs lib --format=html
```

### Test Specialist Agent

The Test Specialist agent is automatically available. Ask Claude:
- "Write comprehensive tests for the user service"
- "Improve test coverage for the payment module to 85%"
- "Set up integration tests for the API endpoints"

### Code Reviewer Skill

The Code Reviewer skill works automatically when you:
- Ask Claude to review code
- Make file modifications
- Create pull requests

## 📊 What You Get

- **Better Code Quality**: Catch issues before they become problems
- **Comprehensive Tests**: Achieve high test coverage with expert guidance
- **Complete Documentation**: Auto-generated docs that stay up to date
- **Security Focus**: Identify vulnerabilities early
- **Best Practices**: Learn and apply language-specific conventions

## 🔍 Review Criteria

The plugin checks for:
- ✅ Code style and formatting
- ✅ Security vulnerabilities (SQL injection, XSS, etc.)
- ✅ Performance issues
- ✅ Error handling completeness
- ✅ Type safety
- ✅ Test coverage
- ✅ Documentation quality

## 📝 License

Apache-2.0

## 🤝 Contributing

Found a bug or have a feature request? Open an issue on our [GitHub repository](https://github.com/devtools/claude-plugin).

## 📖 Learn More

Visit our [documentation](https://devtools.example.com) for:
- Detailed usage guides
- Configuration options
- Best practices
- Example workflows
- FAQ

## Version History

### 2.1.0 (Latest)
- Added Code Reviewer skill
- Enhanced /review command with security checks
- Improved documentation generation

### 2.0.0
- Added Test Specialist agent
- Rewrote review engine
- Added HTML documentation format

### 1.0.0
- Initial release
- Basic /review and /gendocs commands

