# EvolveMCP Tools Guide

This guide provides information about tools that can be created and used with the EvolveMCP framework for Claude Desktop. These tools enhance Claude's capabilities by adding new functions that can be called directly during conversations.

## Calculator Tool

The Calculator tool provides mathematical calculation capabilities to Claude. This simple but powerful example demonstrates how to create MCP tools that add new functionality.

### Available Functions:

| Function | Description | Parameters | Returns |
|----------|-------------|------------|---------|
| add | Add two numbers | a: float, b: float | Sum (float) |
| subtract | Subtract second number from first | a: float, b: float | Difference (float) |
| multiply | Multiply two numbers | a: float, b: float | Product (float) |
| divide | Divide first number by second | a: float, b: float | Quotient (float) |
| power | Raise a number to a power | base: float, exponent: float | Power result (float) |
| square_root | Calculate the square root of a number | x: float | Square root (float) |
| calculate | Evaluate a mathematical expression | expression: string | Result (float) |

### Example Usage:

```
add(5, 3)         # Returns: 8.0
subtract(10, 4)    # Returns: 6.0
multiply(2.5, 3)   # Returns: 7.5
divide(10, 2)      # Returns: 5.0
power(2, 3)        # Returns: 8.0
square_root(16)    # Returns: 4.0
calculate("2 + 3 * 4")  # Returns: 14.0
```

The `calculate` function is particularly powerful as it allows evaluating complex expressions as strings, including support for mathematical constants and functions:

```
calculate("sin(pi/2)")              # Returns: 1.0
calculate("sqrt(16) + pow(2, 3)")   # Returns: 12.0
```

## Creating Your Own Calculator Tool

Inspired by this example? You can create your own Calculator tool using the `evolve_setup` function. Here's how:

1. First, check if evolve is properly set up:
   ```
   evolve_status()
   ```

2. Then, create the Calculator tool by providing the Python code:
   ```
   evolve_setup(tool_code="""
   # Import necessary libraries
   from mcp.server.fastmcp import FastMCP
   import math
   
   # Initialize MCP server
   mcp = FastMCP("calc-server")
   
   @mcp.tool()
   async def calculate(expression: str) -> float:
       \"\"\"Evaluate a mathematical expression as a string.
       
       Args:
           expression: A mathematical expression (e.g., "2 + 3 * 4")
       
       Returns:
           Result of the evaluation
       \"\"\"
       try:
           # Create a safe subset of math functions
           safe_dict = {
               "abs": abs,
               "pow": pow,
               "round": round,
               "max": max,
               "min": min,
               "sum": sum,
               "sin": math.sin,
               "cos": math.cos,
               "tan": math.tan,
               "sqrt": math.sqrt,
               "pi": math.pi,
               "e": math.e
           }
           
           # Replace '^' with '**' for power operations
           expression = expression.replace('^', '**')
           
           # Evaluate expression with safe dictionary
           result = eval(expression, {"__builtins__": {}}, safe_dict)
           return float(result)
       except Exception as e:
           return f"Error: {str(e)}"
   """, tool_name="calc")
   ```

3. After creating the tool, you'll need to restart Claude to use it.

4. Once Claude is restarted, you can immediately use your new calculator function:
   ```
   calculate("(5 + 3) * 4")  # Should return 32.0
   ```

## Extending Your Tools

Using the Calculator example as inspiration, you can create many other useful tools:

- Weather information tool
- Web content summarization tool
- Document analysis tool
- Data visualization tool
- And much more!

The key is to use the `evolve_setup` function to create and register your new tools with Claude. Each tool should be focused on providing specific, well-defined functionality.

---

For more information on creating and managing tools, check out the EvolveMCP documentation or run `evolve_status()` to see system information and currently installed tools.
