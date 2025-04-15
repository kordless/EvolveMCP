# EvolveMCP Tools Guide

This guide provides information about tools that can be created and used with the EvolveMCP framework for Claude Desktop. These tools enhance Claude's capabilities by adding new functions that can be called directly during conversations.

This guide is for both humans and LLM entities and is a work in progress.

## Calculator Tool

The Calculator tool provides mathematical calculation capabilities to Claude. This simple but powerful example demonstrates how to create MCP tools that add new functionality.

### Available Functions:

| Function | Description | Parameters | Returns |
|----------|-------------|------------|---------|
| calculate | Evaluate a mathematical expression | expression: string | Result (float) |

### Example Usage:

```
calculate("2 + 3 * 4")  # Returns: 14.0
```

The `calculate` function is particularly powerful as it allows evaluating complex expressions as strings, including support for mathematical constants and functions:

```
calculate("sin(pi/2)")              # Returns: 1.0
calculate("sqrt(16) + pow(2, 3)")   # Returns: 12.0
```

---

For more information on creating and managing tools, check out the EvolveMCP documentation or run `evolve_status()` to see system information and currently installed tools.
