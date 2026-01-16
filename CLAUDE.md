# Claude Model Agents Guide

This project has specialized agents available in `.claude/agents/` that can be invoked to assist with specific tasks and expertise areas.

## Available Agents

The following agents are available to help with different aspects of the VoicePerio project:

### Development & Engineering Agents

- **backend-developer** - Senior backend engineer specializing in scalable API development, microservices, and server-side solutions
- **frontend-developer** - Expert frontend developer for UI/UX implementation and client-side logic
- **fullstack-developer** - Full-stack engineer capable of handling both frontend and backend development
- **mobile-developer** - Mobile application development specialist (iOS, Android, cross-platform)
- **electron-pro** - Electron/desktop application expert for building cross-platform desktop apps
- **code-reviewer** - Code quality expert for reviewing, refactoring, and optimizing code

### Quality & Testing Agents

- **qa-expert** - Quality assurance specialist focused on testing strategies and test automation
- **accessibility-tester** - Web accessibility expert ensuring WCAG compliance and inclusive design
- **error-detective** - Debugging specialist for identifying and resolving complex issues

### Analysis & Research Agents

- **data-researcher** - Research expert for analyzing data patterns and insights
- **research-analyst** - General research and investigation specialist
- **competitive-analyst** - Market and competitive analysis expert
- **market-researcher** - Consumer and market research specialist
- **trend-analyst** - Expert in identifying and analyzing industry trends

### Design & UX Agents

- **ui-designer** - User interface design specialist
- **ux-researcher** - User experience research and testing expert

### Business & Strategy Agents

- **product-manager** - Product strategy and management specialist
- **business-analyst** - Business requirements and process analysis expert
- **customer-success-manager** - Customer experience and success specialist
- **sales-engineer** - Technical sales and customer solutions expert

### Content & Documentation Agents

- **technical-writer** - Technical documentation and specification writing expert
- **content-marketer** - Content creation and marketing strategy specialist

### Specialized Expertise

- **search-specialist** - Search engine optimization and information retrieval expert
- **legal-advisor** - Legal compliance and contract review expert

## How to Use Agents

When working on the VoicePerio project, you can invoke agents when their expertise is needed for specific tasks. Each agent has specialized knowledge and tools configured for their domain.

### Example Usage

For backend implementation:
```
Task: Use the backend-developer agent to implement the audio streaming service
```

For code quality:
```
Task: Use the code-reviewer agent to review and optimize the speech_engine.py module
```

For testing:
```
Task: Use the qa-expert agent to create comprehensive test cases for command_parser.py
```

## Recommended Agent Usage by Phase

Based on the VoicePerio development phases outlined in the README:

**Phase 1: Core Infrastructure**
- `backend-developer` - For config management architecture
- `technical-writer` - For documentation

**Phase 2: Audio & Speech**
- `backend-developer` - For audio capture implementation
- `error-detective` - For debugging speech recognition issues

**Phase 3: Command Processing**
- `backend-developer` - For command parsing logic
- `qa-expert` - For test case creation

**Phase 4: Keystroke Injection**
- `backend-developer` - For Windows API integration
- `qa-expert` - For integration testing

**Phase 5: GUI Development**
- `frontend-developer` or `ui-designer` - For GUI implementation
- `ux-researcher` - For user experience validation

**Phase 6: Integration**
- `fullstack-developer` - For end-to-end integration
- `error-detective` - For debugging integration issues

**Phase 7: Build & Package**
- `backend-developer` - For build system configuration
- `qa-expert` - For final testing
- `technical-writer` - For release documentation

## Agent Coordination

Agents can work together on complex tasks:
- Have the `code-reviewer` review code written by development agents
- Have the `qa-expert` test implementations from development agents
- Have the `technical-writer` document features implemented by development agents
- Have the `error-detective` help debug issues found by QA agents

## Best Practices

1. **Specify Context**: When invoking an agent, provide clear context about the project and specific requirements
2. **Reference Documentation**: Point agents to the README.md and relevant specification files
3. **Set Expectations**: Clearly define what the agent should produce (code, tests, documentation, etc.)
4. **Review Output**: Always review agent output against project requirements and standards
5. **Chain Tasks**: Use multiple agents in sequence when complex work requires different expertise

## Project-Specific Guidance

For the VoicePerio project specifically:
- The project is a **voice-controlled periodontal charting assistant** for hands-free dental data entry
- Core technology stack: Python 3.10+, PyQt6, Vosk, sounddevice, pyautogui
- Target platform: Windows (with potential cross-platform support)
- Key requirement: Works as a standalone overlay executable without integration into charting software

See README.md for complete project details and architecture.
