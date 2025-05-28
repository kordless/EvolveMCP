# Security Guidelines

Important security considerations for using Gnosis Evolve safely.

## Overview

Gnosis Evolve allows Claude to execute Python code on your system through MCP (Model Context Protocol) tools. While this provides powerful capabilities, it also requires careful security considerations.

## Security Model

### What Claude Can Do

With Gnosis Evolve, Claude can:
- **Execute Python code** through MCP tools
- **Read and write files** in accessible directories
- **Make network requests** through tools that support it
- **Install new Python packages** when creating tools
- **Run system commands** through some tools (like docker tools)

### What Claude Cannot Do

Claude is limited by:
- **Tool boundaries** - Only functions exposed through MCP tools
- **Python environment** - Cannot execute arbitrary system commands outside Python
- **File system permissions** - Limited by your user account permissions
- **Network restrictions** - Limited by your firewall and network settings

## Risk Assessment

### Low Risk Activities

These activities are generally safe:
- **File exploration** using file_explorer and evolve_filesystem
- **Basic calculations** using math_and_stats
- **Random number generation** using random_generator
- **Reading configuration files** and logs
- **Creating simple text files**

### Medium Risk Activities

Exercise caution with:
- **Installing new tools** - Review code before installation
- **File editing operations** - Backup important files first
- **Network requests** - Be aware of external API calls
- **Processing user data** - Sensitive information handling

### High Risk Activities

Require careful consideration:
- **Docker operations** - Container management can affect system
- **System file modifications** - Could impact system stability
- **Installing unknown packages** - Potential for malicious code
- **Executing user-provided code** - Always review first

## Best Practices

### For General Use

1. **Review Generated Code**
   ```
   "Show me the code before installing this tool"
   "What exactly will this tool do?"
   "Explain the security implications of this operation"
   ```

2. **Use in Appropriate Environments**
   - **Development machines**: Full functionality
   - **Personal computers**: Use with caution
   - **Production servers**: Not recommended without restrictions
   - **Shared systems**: Requires administrator approval

3. **Backup Important Data**
   ```bash
   # Before major operations
   "Create a backup of this project before making changes"
   "Show me what files will be modified"
   ```

4. **Monitor Tool Activity**
   ```bash
   # Check logs regularly
   .\evolve.ps1 -ViewLogs    # Windows
   ./evolve.sh --view-logs   # macOS
   ```

### For File Operations

1. **Understand File Permissions**
   - Tools inherit your user permissions
   - Cannot access files you cannot access
   - Can modify any file you can modify

2. **Use Version Control**
   ```bash
   # Work in Git repositories when possible
   git status
   git add .
   git commit -m "Before using Gnosis Evolve tools"
   ```

3. **Validate File Changes**
   ```
   "Show me exactly what changes you're about to make"
   "Use a diff to show the modifications"
   "Create a backup before applying these changes"
   ```

### For Tool Development

1. **Code Review Process**
   ```python
   # Always review tool code for:
   # - Unnecessary file system access
   # - Network requests to unknown hosts
   # - Execution of system commands
   # - Handling of sensitive data
   ```

2. **Principle of Least Privilege**
   - Tools should only access what they need
   - Validate all inputs
   - Handle errors gracefully
   - Log security-relevant operations

3. **Secure Coding Practices**
   ```python
   # Input validation
   if not isinstance(user_input, str) or len(user_input) > 1000:
       return {"error": "Invalid input"}
   
   # Path validation
   if not os.path.abspath(file_path).startswith(allowed_directory):
       return {"error": "Access denied"}
   
   # Command injection prevention
   # Never use: os.system(user_input)
   # Use: subprocess.run([command, arg1, arg2], shell=False)
   ```

## Environment Hardening

### Development Environment

1. **Use Virtual Environments**
   ```bash
   # Isolate Python dependencies
   python -m venv gnosis_env
   source gnosis_env/bin/activate  # macOS/Linux
   gnosis_env\Scripts\activate     # Windows
   ```

2. **Network Restrictions**
   ```bash
   # Consider firewall rules for Python
   # Block unnecessary outbound connections
   # Monitor network activity
   ```

3. **File System Permissions**
   ```bash
   # Create a dedicated workspace
   mkdir ~/gnosis_workspace
   cd ~/gnosis_workspace
   # Work primarily in this directory
   ```

### Production Environment

**❌ Not Recommended**: Using Gnosis Evolve in production environments without significant restrictions.

If you must use in production:

1. **Containerization**
   ```dockerfile
   # Run in isolated container
   FROM python:3.11-slim
   RUN useradd -m -s /bin/bash gnosis
   USER gnosis
   # ... rest of container setup
   ```

2. **Restricted User Account**
   ```bash
   # Create limited user account
   sudo useradd -m -s /bin/bash gnosis-user
   sudo usermod -L gnosis-user  # Lock password login
   ```

3. **Network Isolation**
   - Use VPNs or network segmentation
   - Restrict internet access
   - Monitor all network connections

## Monitoring and Auditing

### Log Analysis

1. **Regular Log Review**
   ```bash
   # Check for suspicious activity
   grep -i "error\|warning\|fail" logs/*.log
   grep -i "network\|http\|download" logs/*.log
   ```

2. **Tool Usage Tracking**
   ```bash
   # Monitor which tools are being used
   grep "tool.*called" logs/evolve.log
   ```

3. **File Access Monitoring**
   ```bash
   # Track file operations
   grep -i "file.*created\|file.*modified\|file.*deleted" logs/*.log
   ```

### System Monitoring

1. **Process Monitoring**
   ```bash
   # Monitor Python processes
   ps aux | grep python
   ps aux | grep claude
   ```

2. **Network Monitoring**
   ```bash
   # Monitor network connections
   netstat -an | grep python
   lsof -i | grep python
   ```

3. **File System Monitoring**
   ```bash
   # Use tools like auditd (Linux) or File Auditing (Windows)
   # to track file system changes
   ```

## Incident Response

### If Something Goes Wrong

1. **Immediate Actions**
   ```bash
   # Stop Claude Desktop
   # Windows
   .\evolve.ps1 -Stop
   
   # macOS
   ./evolve.sh --stop
   
   # Check running processes
   ps aux | grep -E "(claude|python|mcp)"
   
   # Kill if necessary
   pkill -f "claude\|evolve"
   ```

2. **Assess Damage**
   ```bash
   # Check recent file modifications
   find . -mtime -1 -type f
   
   # Check network connections
   netstat -an
   
   # Review logs
   tail -100 logs/*.log
   ```

3. **Recovery Steps**
   - Restore from backups if needed
   - Review what tools were active
   - Check for any persistent changes
   - Update security measures

### Reporting Security Issues

If you discover a security vulnerability:

1. **Do not create a public issue**
2. **Email**: security@gnosis-evolve.com (if available)
3. **Discord**: Contact moderators privately
4. **Include**: Detailed reproduction steps and impact assessment

## Security Checklist

### Before Installation
- [ ] Understand the risks involved
- [ ] Choose appropriate environment (development recommended)
- [ ] Backup important data
- [ ] Review system permissions

### During Use
- [ ] Review generated code before execution
- [ ] Monitor log files regularly
- [ ] Use version control for important projects
- [ ] Validate file changes before applying

### Tool Development
- [ ] Review all tool code thoroughly
- [ ] Test tools in isolated environment first
- [ ] Follow secure coding practices
- [ ] Document security considerations

### Regular Maintenance
- [ ] Update Gnosis Evolve regularly
- [ ] Review installed tools periodically
- [ ] Clean up unused tools
- [ ] Monitor system for unusual activity

## Conclusion

Gnosis Evolve provides powerful capabilities that require responsible use. By following these security guidelines, you can enjoy the benefits while minimizing risks.

**Remember**: When in doubt, ask Claude to explain what a tool will do before using it. Claude can help you understand the security implications of any operation.

For questions about security, join our [Discord community](https://discord.gg/AQnAn9XgFJ) or review our [documentation](README.md).

Stay safe! 🔒