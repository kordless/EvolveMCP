# 🧠 EvolveMCP: Claude Desktop Tool Manager

EvolveMCP is a simple PowerShell utility that helps you extend Claude Desktop with custom tools.

## What is EvolveMCP?

EvolveMCP makes it easy to:
- Manage Claude Desktop processes (restart, view logs)
- Create and install custom tools for Claude
- Set up MCP servers without complex configuration

## Quick Start

### Requirements
- Windows
- PowerShell
- Claude Desktop installed
- Python installed

### Installation

#### Option 1: Using Git
```powershell
# Clone repository
git clone https://github.com/kordless/EvolveMCP.git
cd EvolveMCP

# Run setup
.\evolve.ps1 -Setup
```

#### Option 2: From Release
1. Download and unzip the latest release
2. Open PowerShell in the extracted folder
3. Run `.\evolve.ps1 -Setup`

### Creating Your First Tool

After setup and Claude restart:

1. Ask Claude to evolve a calculator tool:
```
evolve calculator
```

```
I'd be happy to help you set up a calculator tool using the evolve system. Let me do that for you.View result from evolve_wizard from evolve-server (local){

# Calculator Tool Created Successfully

I've created a calculator tool file at:
C:\Users\kord\Code\mcptest\calc.py

## The tool has been registered with Claude!

The calculator has been:
1. Created in the same directory as your evolve.py file
2. Added to Claude's configuration automatically

## To use the calculator tool:

1. **Restart Claude**:
   Run this command in PowerShell:
   """
   ./evolve.ps1 -Restart
   """
   
2. **After Claude restarts**:
   You can use the calculator functions:
   - `add(5, 3)` → 8.0
   - `subtract(10, 4)` → 6.0
   - `multiply(2.5, 3)` → 7.5
   - `calculate("2 + 3 * 4")` → 14.0
   - calculate the square root of pi
   - what is the distance to the moon (average) to the power of 3?
   - calculate the volume inside a regular ice cream cone scoop (in liters)

The calculator provides basic math operations as an example of how custom tools work.
Great! I've successfully created a calculator tool for you. The tool has been created and registered with Claude.
To start using the calculator, you'll need to restart Claude. Here's what to do:

Run this command in PowerShell:
./evolve.ps1 -Restart

After Claude restarts, you'll be able to use the calculator functions like:

add(5, 3) → 8.0
subtract(10, 4) → 6.0
multiply(2.5, 3) → 7.5
calculate("2 + 3 * 4") → 14.0



You can also ask natural language math questions like:

Calculate the square root of pi
What is the distance to the moon (average) to the power of 3?
Calculate the volume inside a regular ice cream cone scoop (in liters)

Would you like me to explain how the calculator tool works, or do you want to restart Claude now and try it out?
```

2. Restart Claude as instructed

3. Use your new tool (in Claude Desktop):
```
calculate the square root of pi
```

### Common Commands for the Evolve Configuration Tool

```powershell
# Show menu with all options
.\evolve.ps1

# Restart Claude
.\evolve.ps1 -Restart

# View logs
.\evolve.ps1 -ViewLogs

# List all tools
.\evolve.ps1 -ListTools
```

## Need Help?

If you encounter issues, check the logs with `.\evolve.ps1 -ViewLogs` or open an issue on GitHub.
