# medBillDozer Documentation Index

**Complete documentation for users and developers**

Last Updated: January 21, 2026

---

## 📚 Documentation Overview

This folder contains comprehensive documentation for medBillDozer, organized by audience and purpose.

### Total Documentation

- **2,500+ lines** of documentation
- **6 markdown files** covering all aspects
- **1 JSON manifest** for machine-readable metadata

---

## 👥 For End Users

### 🚀 [Quick Start Guide](QUICKSTART.md) (6.5 KB)

**Perfect for**: First-time users who want to get started immediately

**Contents**:
- 5-minute installation guide
- Basic usage tutorial (3 steps)
- Demo document walkthrough
- AI provider selection guide
- Common troubleshooting

**Start here if**: You want to analyze a bill right now!

---

### 📖 [User Guide](USER_GUIDE.md) (22 KB)

**Perfect for**: Users who want comprehensive instructions and best practices

**Contents**:
- Complete feature overview
- Detailed usage instructions
- Understanding analysis results
- Privacy & data security
- All 5 demo documents explained
- Tips & best practices
- Troubleshooting guide
- Important disclaimers

**Start here if**: You want to become a power user!

---

### 🤖 [Assistant Guide](ASSISTANT.md) (8 KB)

**Perfect for**: Users who want to use the AI-powered help system

**Contents**:
- How to use the documentation assistant
- Quick help button guide
- Example questions and answers
- AI provider comparison
- Contextual help system
- Troubleshooting the assistant

**Start here if**: You need help while using the app!

---

## 🔧 For Developers

### 📦 [Modules Reference](MODULES.md) (31 KB)

**Perfect for**: Developers who want to understand the codebase architecture

**Contents**:
- All 25 modules documented
- Module descriptions and purposes
- Function signatures and docstrings
- Constants and configuration
- Dependency relationships
- Organized by semantic category:
  - Application (1 module)
  - Core Business Logic (4 modules)
  - Fact Extractors (5 modules)
  - LLM Providers (4 modules)
  - Prompt Builders (5 modules)
  - UI Components (4 modules)
  - Utilities (2 modules)

**Start here if**: You want to contribute code or understand internals!

---

### 🔌 [API Reference](API.md) (880 B)

**Perfect for**: Developers integrating with medBillDozer or extending functionality

**Contents**:
- Public interface documentation
- Provider interface contracts
- Key classes and methods
- Usage patterns

**Start here if**: You're building on top of medBillDozer!

---

### 📊 [Dependencies](DEPENDENCIES.md) (1.8 KB)

**Perfect for**: Developers managing the dependency tree

**Contents**:
- Complete import graph
- Module-to-module dependencies
- External package usage
- Dependency visualization

**Start here if**: You need to refactor or audit dependencies!

---

### 📋 [Manifest](manifest.json) (6.6 KB)

**Perfect for**: Automated tools and CI/CD pipelines

**Contents**:
- Machine-readable project metadata
- All modules with functions and classes
- Structured dependency information
- Constants and configurations

**Start here if**: You're building automation!

---

## 📂 Project Documentation (Root Level)

### 📝 [Project README](../README.md)

**Perfect for**: GitHub visitors and first-time explorers

**Contents**:
- Project overview
- Feature highlights
- Quick installation
- Links to detailed docs
- Demo information
- Disclaimer

---

### 📖 [Documentation System Guide](../DOCUMENTATION.md)

**Perfect for**: Contributors maintaining the documentation

**Contents**:
- How the auto-documentation works
- Using the doc generator
- Pre-commit hook setup
- Makefile commands
- Best practices

---

## 🗂️ Documentation by Topic

### Getting Started

1. **[Quick Start](QUICKSTART.md)** - Get running in 5 minutes
2. **[User Guide § Getting Started](USER_GUIDE.md#getting-started)** - Detailed setup

### Using the Application

1. **[Quick Start § Basic Usage](QUICKSTART.md#basic-usage-3-steps)** - 3-step tutorial
2. **[User Guide § Using the Application](USER_GUIDE.md#using-the-application)** - Complete workflow
3. **[User Guide § Understanding Results](USER_GUIDE.md#understanding-results)** - Interpreting analysis

### Privacy & Security

1. **[Quick Start § Privacy & Security](QUICKSTART.md#privacy--security)** - Quick overview
2. **[User Guide § Privacy & Data Security](USER_GUIDE.md#privacy--data-security)** - Comprehensive details
3. **[Project README § Privacy](../README.md#privacy--security)** - At-a-glance summary

### Troubleshooting

1. **[Quick Start § Troubleshooting](QUICKSTART.md#troubleshooting)** - Common quick fixes
2. **[User Guide § Troubleshooting](USER_GUIDE.md#troubleshooting)** - Detailed problem solving

### Development

1. **[Modules Reference](MODULES.md)** - Complete codebase overview
2. **[API Reference](API.md)** - Public interfaces
3. **[Dependencies](DEPENDENCIES.md)** - Import relationships
4. **[Documentation System](../DOCUMENTATION.md)** - Maintaining docs

---

## 📊 Documentation Statistics

### By Audience

| Audience | Files | Lines | Size |
|----------|-------|-------|------|
| End Users | 2 files | ~1,100 lines | 28.5 KB |
| Developers | 4 files | ~1,400 lines | 40 KB |

### By Category

| Category | Primary File | Lines |
|----------|--------------|-------|
| Getting Started | QUICKSTART.md | 250 |
| User Instructions | USER_GUIDE.md | 850 |
| Code Reference | MODULES.md | 1,305 |
| API Docs | API.md | 47 |
| Dependencies | DEPENDENCIES.md | 71 |

---

## 🔄 Keeping Documentation Updated

All code documentation (MODULES.md, API.md, DEPENDENCIES.md) is **automatically generated** from the codebase using:

```bash
make docs
```

This runs on every commit via pre-commit hook, ensuring documentation stays synchronized with code.

### What's Auto-Generated?

✅ Module descriptions (from module docstrings)  
✅ Function signatures (from code)  
✅ Function documentation (from docstrings)  
✅ Class hierarchies (from AST analysis)  
✅ Dependencies (from import statements)  
✅ Constants (from code inspection)  

### What's Manual?

📝 User guides (QUICKSTART.md, USER_GUIDE.md)  
📝 This index file  
📝 Project README  

---

## 🎯 Quick Navigation

### I want to...

**→ Start using medBillDozer right now**  
Read: [QUICKSTART.md](QUICKSTART.md)

**→ Analyze my medical bill**  
Read: [USER_GUIDE.md § Using the Application](USER_GUIDE.md#using-the-application)

**→ Understand what an analysis result means**  
Read: [USER_GUIDE.md § Understanding Results](USER_GUIDE.md#understanding-results)

**→ Know if my data is private**  
Read: [USER_GUIDE.md § Privacy & Data Security](USER_GUIDE.md#privacy--data-security)

**→ Fix an error or issue**  
Read: [QUICKSTART.md § Troubleshooting](QUICKSTART.md#troubleshooting)

**→ Contribute to the codebase**  
Read: [MODULES.md](MODULES.md) and [DOCUMENTATION.md](../DOCUMENTATION.md)

**→ Understand a specific module**  
Read: [MODULES.md](MODULES.md) and search for the module name

**→ See all dependencies**  
Read: [DEPENDENCIES.md](DEPENDENCIES.md)

**→ Build on top of medBillDozer**  
Read: [API.md](API.md)

---

## 📞 Getting Help

### Documentation Issues

If you find errors or gaps in the documentation:
1. Open a GitHub issue
2. Tag with `documentation` label
3. Specify which file and section

### Usage Questions

For questions about using medBillDozer:
1. Check the relevant documentation first
2. Search existing GitHub issues
3. Open a new issue if needed

### Code Questions

For questions about the code:
1. Review [MODULES.md](MODULES.md) for the relevant module
2. Check function docstrings in the source
3. Open a GitHub discussion for clarification

---

## 📜 License

All documentation is provided under the same license as the medBillDozer project.

See [LICENSE](../LICENSE) for details.

---

**Happy documenting!** 📚
