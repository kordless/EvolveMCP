# 🧠 EvolveMCP: Claude Manager & MCP Bootstrapper

A PowerShell utility for managing Claude Desktop and bootstrapping MCP servers with minimal hassle and maximum AI magic.

---

## 🌟 What It Is

**EvolveMCP** is a lightweight PowerShell tool that simplifies the chaos of working with **Claude Desktop** and **Model Context Protocol (MCP)**. Think of it as your AI sidekick that:

- Manages Claude Desktop processes (kill, restart, monitor)
- Boots up an MCP server with a single click
- Automatically configures Claude for tool usage
- Evolves into something better over time with AI-generated extensions

If MCP feels like a rat's nest on Windows (and let’s face it, it is), this tool makes it suck less.

---

## 💡 The Vision: Let the AI Build Itself

**EvolveMCP** isn’t just a manager—it’s a bootstrapper for AI-generated tool chains.

The idea is simple:

> Use AI to write tools for AI, then evolve those tools with AI again.

This feedback loop means the more you use it, the smarter it becomes:

- Learns the kinds of tools you use
- Writes new ones to fit your style
- Automates boring setup tasks
- Tracks its own growth and can recompile itself with new ideas

It’s a system that evolves while you build.

---

## ✨ Key Features

- 🔄 **Claude Manager**: Kill and restart Claude Desktop
- 📋 **MCP Log Viewer**: Browse Claude logs (zero config)
- 🚀 **MCP Bootstrapper**: Spins up your `evolve.py` tool using Python
- ⚙️ **Auto Config**: Rewrites `claude_desktop_config.json` for you
- 🧠 **Evolve Function**: A pattern-learning bootstrap mechanism for iterative tool creation

---

## 🚀 Get Started

First, clone the repo:

```powershell
git clone https://github.com/kordless/EvolveMCP.git
cd EvolveMCP
```

Then just run the main script:

```powershell
.\evolve.ps1
```

---

## 🧰 Menu Walkthrough

Once it’s running, you’ll get:

```
🧰 ===== CLAUDE MANAGER MENU ===== 🧰
1. 📜 View MCP Logs
2. 💪 Kill Claude Desktop
3. 🚀 Setup Evolve Server
4. 🔄 Restart Claude
5. 🚪 Exit
```

Here’s what each one does:

| Option | Description |
|--------|-------------|
| **📜 View MCP Logs** | Opens Claude log files from the correct directory |
| **💪 Kill Claude Desktop** | Force quits all Claude Desktop processes |
| **🚀 Setup Evolve Server** | Boots a Python MCP server, builds config, and links it in |
| **🔄 Restart Claude** | Restarts Claude after changes |
| **🚪 Exit** | Close the tool |

---

## ⚙️ What Setup Actually Does

The `Setup Evolve Server` option automates a whole messy chain:

- ✅ Creates and configures `evolve.py` server
- 🔗 Links it in your Claude `claude_desktop_config.json`
- 💾 Stores config to correct AppData path
- 🔄 Restarts Claude to activate MCP tools
- 🧪 Ready for evolution

---

## 📋 Requirements

Before running, make sure you have:

- ✅ Windows with PowerShell
- ✅ [Claude Desktop](https://claude.ai/download)
- ✅ Python installed (`python` in your path)
- ✅ MCP Server installed:
  ```bash
  pip install mcp-server
  ```

---

## 🧠 Evolve: A Bootstrapping Brain

Evolve isn’t just one script—it’s a concept.

- Learns from your usage patterns
- Can generate new tools or upgrade its own codebase
- Supports basic/advanced/debug modes
- Will eventually support memory and cross-session state

It's the first draft of a system that builds itself.

---

## 📺 Future Ideas

- 🧬 Support for versioned tools
- 📂 Plugin-style auto-discovery
- 🔗 Local function registry to map AI toolchains
- 🧠 Semantic memory integration (Qdrant + Ollama)

---

## 💼 Asset Preview (Evolve Logo Placeholder)

![EvolveMCP Asset](https://raw.githubusercontent.com/kordless/EvolveMCP/main/assets/evolve-logo.png)

> Add an `assets/` folder with `evolve-logo.png` to make this real.

---

## 🏴‍☠️ This Ain’t Your Daddy’s Algorithm

EvolveMCP is part of a future where tools build themselves. If Claude is your AI assistant, this makes it your command center.

