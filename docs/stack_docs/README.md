# Stack Documentation

## What is this?

This folder contains practical documentation for all the technologies and services used in SeedGPT. Think of it as a **toolkit reference** for both humans and AI agents working on the project.

## Why does this exist?

- **Quick Reference**: Find syntax, examples, and best practices without leaving the project
- **AI Context**: Helps AI agents understand the exact tools and versions we use
- **Onboarding**: New developers can quickly understand the tech stack
- **Consistency**: Everyone (human or AI) uses the same patterns and conventions

## What's inside?

Each file documents one technology with:
- Key features and capabilities
- Code examples and common patterns
- Best practices specific to our project
- Version information we're using
- Links to official documentation

## Technologies Covered

### Core Services
- **anthropic-claude.md** - AI model for code generation
- **stripe.md** - Payment processing
- **google-cloud.md** - Cloud hosting (Cloud Run, Cloud SQL)
- **github-api.md** - Repository automation (PyGithub)
- **github-actions.md** - CI/CD workflows

### Backend
- **fastapi.md** - Python web framework
- **postgresql.md** - Database
- **sqlalchemy.md** - Database ORM

### Frontend
- **react.md** - UI library
- **vite.md** - Build tool
- **tailwindcss.md** - CSS framework

### Infrastructure
- **docker.md** - Containerization

## How to use this

**For Humans:**
- Browse files to learn about specific technologies
- Copy-paste examples when implementing features
- Reference best practices when making decisions

**For AI Agents:**
- Use as context when generating code
- Follow patterns and conventions documented here
- Reference version information for compatibility

---

**Keep this updated**: When upgrading dependencies or changing patterns, update the relevant documentation file.
