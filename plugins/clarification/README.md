# Clarification Plugin

A lightweight Claude Code plugin for clarifying tasks and requirements through structured questions.

## What It Does

The Clarification plugin helps you thoroughly understand any task before jumping into implementation. It guides you through a systematic questioning process to uncover:

- Core objectives and desired outcomes
- Key scenarios and edge cases
- Success criteria and acceptance criteria
- Scope boundaries and constraints
- Dependencies and context

## Commands

### `/clarify_task`

Starts an interactive clarification session where Claude will ask focused questions to fully understand your task before proceeding with implementation.

**Usage:**
```
/clarify_task
```

Claude will guide you through a series of questions, and at the end, provide a clear summary of the clarified requirements.

## When to Use This Plugin

Use this plugin when:
- Starting a new feature or project
- Requirements are unclear or ambiguous
- You want to ensure all edge cases are considered
- You need to document understanding before implementation
- You're about to start coding and want to validate assumptions

## Installation

This plugin is part of the 30 Minute Vibe Coding Challenge marketplace.

To install:
```
/plugin install clarification@30-minute-vibe-coding-challenge
```

## Example

```
You: /clarify_task
Claude: I'm ready to help clarify your task. Please describe what you want to accomplish.

You: I need to add user authentication to my app

Claude: Great! Let me ask some clarifying questions about the authentication feature:

1. What type of authentication do you need? (email/password, OAuth, magic links, etc.)
2. Do you already have a user database, or is this a new system?
3. Should users be able to reset their passwords?
4. Are there different user roles or permissions to consider?
5. What should happen if someone tries to access a protected route without being logged in?

[... conversation continues ...]

Claude: I now have a clear understanding of your task:

**Objective**: Add email/password authentication with JWT tokens to existing Express app

**Key Requirements**:
- Login and registration endpoints
- Password hashing with bcrypt
- JWT token generation and validation
- Protected route middleware
- Password reset via email

**Success Criteria**:
- Users can register with email/password
- Users can log in and receive a JWT token
- Protected routes only accessible with valid token
- Passwords are securely hashed
- Password reset flow works end-to-end

**Out of Scope**:
- OAuth providers (future enhancement)
- Two-factor authentication
- Role-based access control

Ready to proceed?
```
