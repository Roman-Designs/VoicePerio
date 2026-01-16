# Important: Read This Before Working on VoicePerio

## 📖 Required Reading

**Before starting any work on this project, you MUST read:**

1. **CLAUDE.md** - Learn about available agents and how to use them
2. **README.md** - Understand the complete project vision, requirements, and architecture

## Why This Matters

This project has specialized agents available that can help you work more effectively. Understanding which agents to use for specific tasks will:

- ✓ Speed up development by delegating to specialists
- ✓ Improve code quality through expert review
- ✓ Reduce debugging time with error detection specialists
- ✓ Ensure comprehensive testing and documentation
- ✓ Keep the project aligned with its goals and standards

## Quick Start

### 1. Read CLAUDE.md First
Open `CLAUDE.md` to see:
- Complete list of 24 specialized agents
- What each agent does
- How to invoke agents for specific tasks
- Recommended agents for each development phase

### 2. Read README.md Second
Open `README.md` to understand:
- What VoicePerio is and why it exists
- How the application works
- Complete technical architecture
- Project structure and file organization
- Development phases and roadmap
- Voice commands and features
- Dependencies and setup requirements

### 3. Check Current Development Phase
Look at `PROJECT_SETUP_SUMMARY.md` and `SETUP_CHECKLIST.txt` to see:
- What's already been completed
- What needs to be done next
- Which phase of development is active

## Agent Selection Guide

### For Implementation Work
👉 **Use: backend-developer, frontend-developer, or fullstack-developer**
- Implementing new features
- Writing core functionality
- Building user interfaces
- Integrating components

### For Code Quality & Testing
👉 **Use: code-reviewer, qa-expert, or error-detective**
- Reviewing code before merging
- Creating test cases
- Debugging issues
- Optimizing performance

### For Documentation
👉 **Use: technical-writer**
- Writing API documentation
- Creating user guides
- Documenting architecture decisions
- Writing specification documents

### For Complex Problems
👉 **Use multiple agents in sequence**
- Developer builds feature
- Code-reviewer reviews it
- QA-expert tests it
- Technical-writer documents it

## Project Overview

**VoicePerio** is a voice-controlled periodontal charting assistant that allows dentists to dictate pocket depths and perio indicators while keeping their hands on the probe and eyes on the patient.

### Key Facts
- **Type**: Standalone Windows overlay application
- **Language**: Python 3.10+
- **Architecture**: Voice → Commands → Keystrokes
- **Tech Stack**: Vosk, sounddevice, PyQt6, pyautogui, pywin32
- **Status**: Phase 1 (Core Infrastructure) - COMPLETE

### Current Phase
**Phase 2: Audio & Speech Recognition**
- Next task: Implement audio_capture.py
- Download Vosk model
- Implement speech_engine.py
- Test speech recognition

## Common Workflows

### Adding a New Feature
1. Use `backend-developer` to implement core logic
2. Use `code-reviewer` to review implementation
3. Use `qa-expert` to create and run tests
4. Use `technical-writer` to document changes

### Debugging an Issue
1. Use `error-detective` to identify root cause
2. Use `backend-developer` to implement fix
3. Use `qa-expert` to verify fix works
4. Use `code-reviewer` to ensure quality

### Preparing for Release
1. Use `qa-expert` to run final tests
2. Use `code-reviewer` to ensure code quality
3. Use `technical-writer` to finalize documentation
4. Use `backend-developer` to optimize build

## Important Reminders

⚠️ **Always check the current phase** - Don't work on Phase 3 features if Phase 2 isn't complete

⚠️ **Follow the architecture** - Respect the modular structure and component boundaries

⚠️ **Reference the spec** - When unsure about behavior, check README.md and command definitions

⚠️ **Test thoroughly** - Use qa-expert to create comprehensive test cases

⚠️ **Document changes** - Keep README.md, code comments, and docstrings up-to-date

## File Organization

```
VoicePerio/
├── CLAUDE.md              ← Agent reference guide
├── AGENTS.md              ← This file (you are here)
├── README.md              ← Project documentation (READ FIRST)
├── PROJECT_SETUP_SUMMARY.md  ← Setup status
├── SETUP_CHECKLIST.txt    ← Completion checklist
├── src/voiceperio/        ← Main application code
├── tests/                 ← Test files
└── ... (other files)
```

## Before You Start

**Checklist:**
- [ ] I have read CLAUDE.md
- [ ] I have read README.md
- [ ] I understand the current development phase
- [ ] I know which agent(s) to use for this task
- [ ] I have the project requirements in mind

## Questions?

- **About the project**: See README.md
- **About agents**: See CLAUDE.md
- **About what to do next**: See PROJECT_SETUP_SUMMARY.md
- **About implementation details**: Check the relevant module docstrings

---

**Happy coding! 🚀**

Remember: This project has expert agents ready to help. Use them to build something great!
