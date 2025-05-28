# Contributing to Gnosis Evolve

Thank you for your interest in contributing to Gnosis Evolve! This guide will help you get started.

## Ways to Contribute

### 1. Tool Development
Create new MCP tools to extend Claude's capabilities:
- **Utility tools** - File operations, data processing, etc.
- **Integration tools** - APIs, databases, cloud services
- **Creative tools** - Content generation, art, music
- **Domain-specific tools** - Finance, science, education

### 2. Core Development
Improve the core Gnosis Evolve system:
- **Performance optimizations**
- **Bug fixes**
- **New features**
- **Platform support**

### 3. Documentation
Help improve project documentation:
- **User guides**
- **API documentation**
- **Tutorials and examples**
- **Translation to other languages**

### 4. Testing and Bug Reports
Help make Gnosis Evolve more stable:
- **Test new features**
- **Report bugs**
- **Verify fixes**
- **Performance testing**

## Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   # Clone your fork
   git clone https://github.com/yourusername/gnosis-evolve.git
   cd gnosis-evolve
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r requirements-dev.txt
   ```

3. **Install in development mode**
   ```bash
   # Windows
   .\evolve.ps1 -DevSetup
   
   # macOS
   ./evolve.sh --dev-setup
   ```

### Creating Your First Tool

1. **Choose a tool category**
   - `tools/` - Core tools
   - `contrib_tools/core/` - Community core tools
   - `contrib_tools/web/` - Web-related tools
   - `contrib_tools/finance/` - Financial tools
   - `contrib_tools/docker/` - Docker tools

2. **Use the tool template**
   ```python
   #!/usr/bin/env python3
   \"\"\"
   Tool Name - Brief description
   
   Detailed description of what the tool does.
   \"\"\"
   
   import sys
   import os
   import logging
   from typing import Dict, Any
   from mcp.server.fastmcp import FastMCP
   
   # Setup logging
   current_dir = os.path.dirname(os.path.abspath(__file__))
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s',
       handlers=[logging.FileHandler(os.path.join(current_dir, "../logs", "your_tool.log"))]
   )
   logger = logging.getLogger("your_tool")
   
   # Create MCP server
   mcp = FastMCP("your-tool-server")
   
   @mcp.tool()
   async def your_function(param: str) -> Dict[str, Any]:
       \"\"\"
       Function description.
       
       Args:
           param: Parameter description
           
       Returns:
           Dictionary with results
       \"\"\"
       try:
           # Your tool logic here
           result = process_data(param)
           logger.info(f"Successfully processed: {param}")
           return {"success": True, "result": result}
       except Exception as e:
           logger.error(f"Error processing {param}: {str(e)}")
           return {"success": False, "error": str(e)}
   
   if __name__ == "__main__":
       mcp.run()
   ```

3. **Test your tool**
   ```bash
   # Test locally
   python your_tool.py
   
   # Install via Claude
   "Please install my new tool with this code..."
   ```

## Contribution Guidelines

### Code Standards

1. **Python Style**
   - Follow PEP 8
   - Use type hints
   - Include docstrings for all functions
   - Maximum line length: 88 characters

2. **Error Handling**
   ```python
   try:
       # Main logic
       result = do_something()
       return {"success": True, "result": result}
   except SpecificException as e:
       logger.error(f"Specific error: {str(e)}")
       return {"success": False, "error": "Specific error message"}
   except Exception as e:
       logger.exception("Unexpected error")
       return {"success": False, "error": "An unexpected error occurred"}
   ```

3. **Logging**
   ```python
   # Good logging practices
   logger.info(f"Processing request: {request_id}")
   logger.warning(f"Unusual condition: {condition}")
   logger.error(f"Operation failed: {error_details}")
   logger.debug(f"Debug info: {debug_data}")
   ```

4. **Function Signatures**
   ```python
   @mcp.tool()
   async def function_name(
       required_param: str,
       optional_param: int = 10,
       flag: bool = False
   ) -> Dict[str, Any]:
       \"\"\"Clear docstring with Args and Returns sections.\"\"\"
   ```

### Testing

1. **Unit Tests**
   ```python
   # Create tests in tests/ directory
   import pytest
   from your_tool import your_function
   
   def test_your_function():
       result = your_function("test_input")
       assert result["success"] is True
       assert "result" in result
   ```

2. **Integration Tests**
   ```python
   # Test tool with Claude
   def test_tool_integration():
       # Install tool
       # Test via Claude conversation
       # Verify expected behavior
   ```

3. **Manual Testing Checklist**
   - [ ] Tool installs without errors
   - [ ] Functions work as expected
   - [ ] Error handling works properly
   - [ ] Logging outputs are helpful
   - [ ] No security vulnerabilities

### Documentation

1. **Tool Documentation**
   ```markdown
   # Tool Name
   
   ## Description
   Brief description of the tool's purpose.
   
   ## Functions
   
   ### function_name(param1, param2)
   Description of what the function does.
   
   **Parameters:**
   - `param1` (str): Description
   - `param2` (int, optional): Description (default: 10)
   
   **Returns:**
   Dictionary with result data.
   
   **Example:**
   ```
   "Use tool_name to process this data"
   ```
   
   ## Installation
   Ask Claude: "Please install the tool_name tool"
   
   ## Examples
   Provide usage examples and expected outputs.
   ```

2. **Code Comments**
   ```python
   # Explain complex logic
   def complex_function():
       # Step 1: Validate input data
       if not validate_input(data):
           return error_response()
       
       # Step 2: Process data with algorithm X
       processed = apply_algorithm_x(data)
       
       # Step 3: Format results for Claude
       return format_response(processed)
   ```

## Pull Request Process

### Before Submitting

1. **Check existing issues and PRs**
   - Avoid duplicate work
   - Reference related issues
   - Follow existing patterns

2. **Test thoroughly**
   - Run all tests
   - Test manually with Claude
   - Check for regressions

3. **Update documentation**
   - Update README if needed
   - Add/update tool documentation
   - Include usage examples

### PR Submission

1. **Create a clear title**
   ```
   Add weather forecast tool with multiple providers
   Fix file permission issue in file_writer
   Update documentation for tool development
   ```

2. **Write a good description**
   ```markdown
   ## What this PR does
   Brief summary of changes.
   
   ## Why
   Explanation of the problem or feature need.
   
   ## How
   Technical details of the implementation.
   
   ## Testing
   How you tested the changes.
   
   ## Screenshots/Examples
   If applicable, show the tool in action.
   ```

3. **Link to issues**
   ```
   Fixes #123
   Closes #456
   Related to #789
   ```

### Review Process

1. **Automated checks**
   - Code formatting
   - Tests pass
   - Security scans
   - Documentation builds

2. **Manual review**
   - Code quality
   - Security considerations
   - Performance impact
   - User experience

3. **Feedback and iteration**
   - Address review comments
   - Make requested changes
   - Re-test after changes

## Community Guidelines

### Communication

1. **Be respectful and inclusive**
   - Welcome newcomers
   - Help others learn
   - Assume good intentions
   - Use clear, professional language

2. **Use appropriate channels**
   - **GitHub Issues**: Bug reports, feature requests
   - **GitHub Discussions**: General questions, ideas
   - **Discord**: Real-time chat, community support
   - **Pull Requests**: Code contributions

### Behavior Standards

1. **What we encourage**
   - Helpful and constructive feedback
   - Sharing knowledge and experience
   - Collaboration over competition
   - Learning from mistakes

2. **What we don't tolerate**
   - Harassment or discrimination
   - Spam or self-promotion
   - Sharing malicious code
   - Violating others' privacy

## Recognition

### Contributors

All contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation
- Community showcases

### Tool Authors

Tool creators get:
- Credit in tool documentation
- Recognition in community showcases
- Invitation to join the maintainer team (for significant contributions)

## Getting Help

### For Contributors

1. **Discord Community**
   - Join: https://discord.gg/AQnAn9XgFJ
   - Channel: `#contributors`
   - Get help with development questions

2. **GitHub Discussions**
   - Ask questions about contributing
   - Propose new features
   - Share ideas

3. **Documentation**
   - [Tool Development Guide](TOOL_DEVELOPMENT.md)
   - [Security Guidelines](SECURITY.md)
   - [Installation Guide](INSTALLATION.md)

### Mentorship Program

We offer mentorship for new contributors:
- **Pair programming sessions**
- **Code review guidance**
- **Architecture discussions**
- **Career development advice**

Contact us on Discord if you're interested!

## Release Process

### Versioning

We use semantic versioning (SemVer):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

### Release Cycle

1. **Development** - Ongoing work in `main` branch
2. **Feature freeze** - Prepare for release
3. **Testing** - Extensive testing period
4. **Release** - Tag and distribute
5. **Post-release** - Bug fixes and patches

## Legal

### License

By contributing, you agree that your contributions will be licensed under the same license as the project (Gnosis AI-Sovereign License v1.1).

### Contributor License Agreement

For significant contributions, we may ask you to sign a CLA to ensure the project can continue to be developed and distributed.

## Thank You!

Your contributions make Gnosis Evolve better for everyone. Whether you're fixing a typo, adding a feature, or helping other users, every contribution matters.

Questions? Join our [Discord community](https://discord.gg/AQnAn9XgFJ) - we'd love to help you get started! 🚀