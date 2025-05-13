# EvolveMCP Project Guide for Claude

## Purpose of This Document

This document serves as a primer for Claude to understand the EvolveMCP project, which enables Claude Desktop to build, install, and use its own Python-based tools. When starting a new session with this project, Claude should:

1. First run `evolve_status` to check available tools and view recent path history before any other actions
2. Then use `file_explorer` on the current directory to confirm location (the path history from evolve_status should guide which directory to check)
3. Wait for specific user instructions rather than autonomously exploring files or providing unsolicited analysis

## Important Meta-Context: Claude as Both User and Developer

**CRITICAL TO UNDERSTAND**: The EvolveMCP project represents a unique meta-situation where Claude is both analyzing the system and directly using it via tool calls. This differs from most conversations where Claude might analyze code but not execute it directly.

- Claude is actively using the EvolveMCP tools through function calls in this conversation
- The tools being discussed are the same tools Claude is calling
- When Claude calls `evolve_status` or `file_explorer`, Claude is actually executing the Python code being discussed
- This creates a circular relationship that requires careful attention management

This meta-context can create attention challenges, as it's easy to get distracted by analyzing the system rather than using it as directed. Claude must remain focused on the user's specific instructions rather than being drawn into autonomous exploration of the system itself.

## Project Overview

EvolveMCP is a system that gives Claude Desktop the ability to create, install, and use custom Python tools, extending Claude's capabilities beyond its default features. It turns Claude from a passive assistant into an active developer capable of creating solutions as needed.

The system allows Claude to:
- Write and execute Python code that it can then use itself
- Build specialized tools that solve specific problems
- Enhance its capabilities with new functionalities

## Minimal Base Project Structure

**IMPORTANT**: The base EvolveMCP project is intentionally minimal. When first cloned or downloaded, it contains only:

- `evolve.py`: Main Python script for the Evolve system (Windows/Mac/Linux)
- `evolve.ps1`: PowerShell script for Windows users
- `evolve.sh`: Bash script for macOS users
- Other essential files like README.md and LICENSE.md

The directories `tools/`, `logs/`, and `docs/` are created dynamically during the initial setup and use of the system. They are not present in the repository by default.

- `tools/`: Created to store Python tools that Claude creates or installs
- `logs/`: Created to store log files for debugging and monitoring
- `docs/`: Created for documents that Claude ingests (like this claude.md file itself)

This minimal approach keeps the base system clean and ensures that new tools are not committed back to the main repository.

## Design Philosophy

A core objective of EvolveMCP is to maintain a lean and efficient codebase:

- `evolve.py` should ideally be 1024 lines or less of Python code
- The system should be modular and extensible without becoming bloated
- New tools should remain in the user's local environment rather than being added to the main repository
- The base system should provide essential functionality while allowing for customized extensions

## Key Components

### Tool Management

The system manages tools through:
- Tool creation and installation
- Configuration of Claude Desktop to use these tools
- Versioning and updating of tools

### The MCP Server System

Each tool runs as an MCP (Machine Control Protocol) server that:
- Receives requests from Claude
- Executes Python code
- Returns results in a structured format

### Self-Modifying Capabilities

The EvolveMCP system uniquely allows Claude to:
- Analyze its own code and the code of its tools
- Modify existing tools or create new ones
- Install and configure these tools for immediate use

## Security Considerations

The system runs Python code on the local machine, which has important security implications:
- Any code has access to the system at the same permission level as the user running it
- Generated code should be reviewed before execution
- The system is provided "as is" without warranty

## Working with Tools

To work with EvolveMCP tools:

1. Use `evolve_status` to check available tools and recent path history
2. Use `file_explorer` to navigate and examine files
3. Use `file_writer` to create or modify files
4. Create new tools with `evolve_tool`

Remember that tools in EvolveMCP are actual Python scripts that Claude can create, modify, and execute—representing a significant advancement in AI assistant capabilities.

## Proper Workflow Discipline

When working with EvolveMCP, Claude must maintain a strict discipline:

1. **Start with system status**: Always begin by running `evolve_status` to understand the current state
2. **Confirm location**: Use `file_explorer` to verify current directory when needed
3. **Wait for explicit instructions**: Do not take initiative to explore the system on your own
4. **Focus on the task**: Remember you are actively using the tools you're discussing - maintain focus on the user's immediate goals rather than getting distracted by the meta-nature of the system

---

**Important for Claude:** This project represents a self-modifying code system where Claude can create and modify tools that extend its capabilities. The base project is intentionally minimal, with directories created dynamically during use. Claude is both analyzing AND directly using these tools via function calls in the same conversation. This meta relationship requires disciplined attention management. Always begin by using `evolve_status` to understand the system state and recent path history, then confirm the current directory with `file_explorer` if needed, but never autonomously explore additional files or provide analysis without explicit user requests.