#!/usr/bin/env bash
# Gnosis: Evolve for Claude Desktop - Claude Manager & MCP Bootstrapper
# A bash utility for managing Claude Desktop and bootstrapping MCP servers on macOS

# Default values
VIEW_LOGS=false
KILL=false
SETUP=false
RESTART=false
MENU=false
LOG_NAME=""
LIST_TOOLS=false

# Define the specific logs directory path for macOS
LOGS_PATH="$HOME/Library/Logs/Claude/"
CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Function to print colored output
print_color() {
    local color=$1
    local message=$2
    
    case $color in
        "green") echo -e "\033[0;32m$message\033[0m" ;;
        "red") echo -e "\033[0;31m$message\033[0m" ;;
        "yellow") echo -e "\033[0;33m$message\033[0m" ;;
        "magenta") echo -e "\033[0;35m$message\033[0m" ;;
        "cyan") echo -e "\033[0;36m$message\033[0m" ;;
        "gray") echo -e "\033[0;37m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# Parse command-line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--view-logs)
                VIEW_LOGS=true
                shift
                ;;
            -k|--kill)
                KILL=true
                shift
                ;;
            -s|--setup)
                SETUP=true
                shift
                ;;
            -r|--restart)
                RESTART=true
                shift
                ;;
            -m|--menu)
                MENU=true
                shift
                ;;
            -l|--list-tools)
                LIST_TOOLS=true
                shift
                ;;
            -n|--log-name)
                LOG_NAME="$2"
                shift
                shift
                ;;
            *)
                print_color "red" "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

# Ensure logs directory exists
ensure_logs_directory() {
    if [ ! -d "$LOGS_PATH" ]; then
        try_create_dir=true
        
        if [ "$1" != "silent" ]; then
            print_color "red" "Logs directory not found at: $LOGS_PATH"
            read -p "Would you like to create the logs directory? (y/n) " create_dir
            if [ "$create_dir" != "y" ]; then
                try_create_dir=false
            fi
        fi
        
        if [ "$try_create_dir" = true ]; then
            mkdir -p "$LOGS_PATH" 2>/dev/null
            if [ $? -eq 0 ]; then
                print_color "green" "Created logs directory at: $LOGS_PATH"
            else
                print_color "red" "Failed to create logs directory"
                return 1
            fi
        fi
    fi
    
    return 0
}

# View MCP Logs Function
view_mcp_logs() {
    local filter_name="$1"
    
    # Check if logs directory exists
    if [ -d "$LOGS_PATH" ]; then
        print_color "green" "Found logs directory at: $LOGS_PATH"
        
        # Get log files in this exact directory
        local log_filter="*.log"
        if [ -n "$filter_name" ]; then
            log_filter="*${filter_name}*.log"
        fi
        
        log_files=($(ls -1 "$LOGS_PATH"/$log_filter 2>/dev/null))
        
        if [ ${#log_files[@]} -gt 0 ]; then
            print_color "green" "Found ${#log_files[@]} log files:"
            
            # Display files with number options for selection
            for i in "${!log_files[@]}"; do
                index=$((i+1))
                file_name=$(basename "${log_files[$i]}")
                print_color "cyan" "  $index. $file_name"
            done
            
            # If only one file and we're filtering, automatically select it
            if [ ${#log_files[@]} -eq 1 ] && [ -n "$filter_name" ]; then
                selected_log="${log_files[0]}"
                print_color "yellow" "\nReading log file: $(basename "$selected_log")"
                print_color "yellow" "Last 20 lines:"
                tail -20 "$selected_log"
                
                # Option to monitor the log file
                read -p "Would you like to monitor this log file in real-time? (y/n) " monitor_option
                if [ "$monitor_option" = "y" ]; then
                    print_color "magenta" "Monitoring log file. Press Ctrl+C to stop."
                    tail -20 -f "$selected_log"
                fi
                return
            fi
            
            # Let user select a log file
            read -p "Select a log file to view (1-${#log_files[@]}) " selected_option
            
            if [[ "$selected_option" =~ ^[0-9]+$ ]] && [ "$selected_option" -ge 1 ] && [ "$selected_option" -le ${#log_files[@]} ]; then
                selected_index=$((selected_option-1))
                selected_log="${log_files[$selected_index]}"
                print_color "yellow" "\nReading selected log file: $(basename "$selected_log")"
                print_color "yellow" "Last 20 lines:"
                tail -20 "$selected_log"
                
                # Option to monitor the log file
                read -p "Would you like to monitor this log file in real-time? (y/n) " monitor_option
                if [ "$monitor_option" = "y" ]; then
                    print_color "magenta" "Monitoring log file. Press Ctrl+C to stop."
                    tail -20 -f "$selected_log"
                fi
            else
                print_color "red" "Invalid selection."
            fi
        else
            print_color "red" "No log files found in $LOGS_PATH matching '$log_filter'"
            print_color "yellow" "The directory exists but contains no matching log files."
        fi
    else
        print_color "red" "Logs directory not found at: $LOGS_PATH"
        
        # Option to create the logs directory
        read -p "Would you like to create the logs directory? (y/n) " create_dir
        if [ "$create_dir" = "y" ]; then
            ensure_logs_directory
        fi
    fi
}

# Function to find Claude executable
find_claude_executable() {
    print_color "yellow" "Searching for Claude executable..."
    
    local claude_exe_paths=(
        "/Applications/Claude.app/Contents/MacOS/Claude"
        "$HOME/Applications/Claude.app/Contents/MacOS/Claude"
    )
    
    local claude_exe=""
    for path in "${claude_exe_paths[@]}"; do
        if [ -f "$path" ]; then
            claude_exe="$path"
            print_color "green" "Found Claude executable: $claude_exe"
            break
        fi
    done
    
    # If not found in standard locations, try to find with mdfind
    if [ -z "$claude_exe" ]; then
        print_color "yellow" "Searching for Claude app using Spotlight..."
        local mdfind_results=$(mdfind "kMDItemCFBundleIdentifier == 'com.anthropic.claude'" -onlyin /Applications)
        
        if [ -n "$mdfind_results" ]; then
            local app_path=$(echo "$mdfind_results" | head -1)
            if [ -d "$app_path" ]; then
                claude_exe="$app_path/Contents/MacOS/Claude"
                if [ -f "$claude_exe" ]; then
                    print_color "green" "Found Claude executable: $claude_exe"
                fi
            fi
        fi
    fi
    
    echo "$claude_exe"
}

# Function to start Claude executable
start_claude_executable() {
    local executable_path="$1"
    local wait_time=${2:-5}
    
    if [ -n "$executable_path" ]; then
        local action_verb="Starting"
        if pgrep -i "Claude" >/dev/null; then
            action_verb="Restarting"
        fi
        
        print_color "green" "$action_verb Claude from: $executable_path"
        
        # Fixed the try-catch block with proper bash error handling
        {
            open -a "Claude"
            
            # Verify Claude started successfully
            sleep $wait_time
            if pgrep -i "Claude" >/dev/null; then
                print_color "green" "Claude has been successfully started."
                return 0
            else
                print_color "red" "Failed to detect Claude processes after start."
                return 1
            fi
        } || {
            print_color "red" "Error starting Claude: $?"
            return 1
        }
    else
        print_color "red" "Could not find Claude app to start. Please start manually."
        return 1
    fi
}

# Function to find and manage Claude processes
manage_claude_process() {
    local kill_process=false
    local restart_process=false
    local wait_time=5
    
    if [ "$1" = "--kill" ]; then
        kill_process=true
    fi
    
    if [ "$1" = "--restart" ]; then
        restart_process=true
    fi
    
    if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
        wait_time=$2
    fi
    
    print_color "yellow" "Searching for Claude processes..."
    local claude_pids=($(pgrep -i "Claude"))
    
    if [ ${#claude_pids[@]} -gt 0 ]; then
        print_color "green" "Found Claude processes:"
        for pid in "${claude_pids[@]}"; do
            process_name=$(ps -p $pid -o comm= | xargs basename)
            print_color "cyan" "  - $process_name (PID: $pid)"
        done
        
        if [ "$kill_process" = true ] || [ "$restart_process" = true ]; then
            print_color "yellow" "Stopping Claude processes..."
            for pid in "${claude_pids[@]}"; do
                process_name=$(ps -p $pid -o comm= | xargs basename)
                kill $pid 2>/dev/null
                if [ $? -eq 0 ]; then
                    print_color "red" "  - Stopped $process_name (PID: $pid)"
                else
                    print_color "red" "  - Failed to stop $process_name (PID: $pid)"
                    # Try force kill if regular kill failed
                    kill -9 $pid 2>/dev/null
                    if [ $? -eq 0 ]; then
                        print_color "red" "  - Force stopped $process_name (PID: $pid)"
                    else
                        print_color "red" "  - Failed to force stop $process_name (PID: $pid)"
                    fi
                fi
            done
            
            # Verify all processes are actually stopped
            print_color "yellow" "Waiting for processes to fully terminate... ($wait_time seconds)"
            sleep 2
            
            local remaining_attempts=3
            local all_processes_stopped=false
            
            while [ "$all_processes_stopped" = false ] && [ $remaining_attempts -gt 0 ]; do
                local running_pids=($(pgrep -i "Claude"))
                
                if [ ${#running_pids[@]} -gt 0 ]; then
                    print_color "yellow" "Some Claude processes are still running. Attempting to stop again..."
                    for pid in "${running_pids[@]}"; do
                        process_name=$(ps -p $pid -o comm= | xargs basename)
                        kill -9 $pid 2>/dev/null
                        if [ $? -eq 0 ]; then
                            print_color "red" "  - Force stopped $process_name (PID: $pid)"
                        else
                            print_color "red" "  - Failed to force stop $process_name (PID: $pid)"
                        fi
                    done
                    
                    sleep $wait_time
                    remaining_attempts=$((remaining_attempts-1))
                else
                    all_processes_stopped=true
                    print_color "green" "All Claude processes have been terminated."
                fi
            done
            
            # Final check for any stubborn processes
            local stubborn_pids=($(pgrep -i "Claude"))
            if [ ${#stubborn_pids[@]} -gt 0 ]; then
                print_color "yellow" "Warning: Some Claude processes could not be terminated. Restart may not work properly."
                for pid in "${stubborn_pids[@]}"; do
                    process_name=$(ps -p $pid -o comm= | xargs basename)
                    print_color "yellow" "  - Still running: $process_name (PID: $pid)"
                done
            fi
            
            if [ "$restart_process" = true ]; then
                local claude_exe=$(find_claude_executable)
                if [ -n "$claude_exe" ]; then
                    start_claude_executable "$claude_exe" $wait_time
                    return $?
                else
                    # Try using "open" command even if we couldn't find the executable path
                    print_color "yellow" "Trying to restart Claude with 'open' command..."
                    open -a "Claude"
                    sleep $wait_time
                    if pgrep -i "Claude" >/dev/null; then
                        print_color "green" "Claude has been successfully restarted."
                        return 0
                    else
                        print_color "red" "Failed to restart Claude."
                        return 1
                    fi
                fi
            fi
        fi
    else
        print_color "yellow" "No Claude processes found running."
        
        if [ "$restart_process" = true ]; then
            local claude_exe=$(find_claude_executable)
            if [ -n "$claude_exe" ]; then
                start_claude_executable "$claude_exe" $wait_time
                return $?
            else
                # Try using "open" command even if we couldn't find the executable path
                print_color "yellow" "Trying to start Claude with 'open' command..."
                open -a "Claude"
                sleep $wait_time
                if pgrep -i "Claude" >/dev/null; then
                    print_color "green" "Claude has been successfully started."
                    return 0
                else
                    print_color "red" "Failed to start Claude."
                    return 1
                fi
            fi
        fi
    fi
}

# Quick restart function that can be called directly
restart_claude() {
    local wait_time=${1:-5}
    
    print_color "magenta" "Restarting Claude..."
    manage_claude_process "--restart" $wait_time
    local result=$?
    
    if [ $result -eq 0 ]; then
        print_color "green" "Claude restart completed successfully."
    else
        print_color "red" "Claude restart failed. Please try again or restart manually."
    fi
}

# Function to read Claude's configuration file
read_claude_config() {
    if [ -f "$CONFIG_PATH" ]; then
        cat "$CONFIG_PATH"
        return 0
    else
        print_color "red" "Claude configuration file not found at: $CONFIG_PATH"
        return 1
    fi
}

# Function to write Claude's configuration file
write_claude_config() {
    local config="$1"
    
    local config_dir=$(dirname "$CONFIG_PATH")
    if [ ! -d "$config_dir" ]; then
        mkdir -p "$config_dir" 2>/dev/null
        if [ $? -ne 0 ]; then
            print_color "red" "Error creating configuration directory: $config_dir"
            return 1
        fi
    fi
    
    echo "$config" > "$CONFIG_PATH"
    if [ $? -eq 0 ]; then
        print_color "green" "Updated Claude configuration at $CONFIG_PATH"
        return 0
    else
        print_color "red" "Error updating Claude configuration"
        return 1
    fi
}

# List all configured MCP tools - requires jq
list_mcp_tools() {
    if ! command -v jq >/dev/null 2>&1; then
        print_color "red" "jq is required for listing MCP tools but is not installed."
        print_color "yellow" "Please install jq with: brew install jq"
        return 1
    fi
    
    if [ ! -f "$CONFIG_PATH" ]; then
        print_color "red" "Claude configuration file not found at: $CONFIG_PATH"
        return 1
    fi
    
    # Check if mcpServers exists and has properties
    local server_count=$(jq '.mcpServers | length' "$CONFIG_PATH" 2>/dev/null)
    if [ $? -ne 0 ] || [ "$server_count" = "0" ] || [ "$server_count" = "null" ]; then
        print_color "yellow" "No MCP servers are configured."
        return 0
    fi
    
    print_color "green" "Configured MCP Servers:"
    
    local server_names=($(jq -r '.mcpServers | keys[]' "$CONFIG_PATH"))
    
    for server_name in "${server_names[@]}"; do
        # Get server command
        local server_command=$(jq -r ".mcpServers[\"$server_name\"].command" "$CONFIG_PATH")
        
        # Get server args if any
        local has_args=$(jq ".mcpServers[\"$server_name\"] | has(\"args\")" "$CONFIG_PATH")
        local args_string=""
        local script_path=""
        
        if [ "$has_args" = "true" ]; then
            args_string=$(jq -r ".mcpServers[\"$server_name\"].args | join(\" \")" "$CONFIG_PATH")
            script_path=$(jq -r ".mcpServers[\"$server_name\"].args[0]" "$CONFIG_PATH")
        fi
        
        # Determine if Gnosis tool
        local is_evolve_tool=false
        if [ -n "$script_path" ]; then
            local file_name=$(basename "$script_path")
            if [[ "$file_name" == mcp_tool.* ]]; then
                is_evolve_tool=true
            fi
        fi
        
        # Display server info with different colors for evolve tools
        if [ "$is_evolve_tool" = true ]; then
            print_color "magenta" "  $server_name" -n
            print_color "yellow" " (Gnosis Tool)"
        else
            print_color "cyan" "  $server_name"
        fi
        
        print_color "gray" "    - Command: $server_command"
        
        if [ -n "$args_string" ]; then
            print_color "gray" "    - Args: $args_string"
        fi
        
        # Check if the server script exists
        if [ -n "$script_path" ]; then
            if [ -f "$script_path" ]; then
                if [ "$is_evolve_tool" = true ]; then
                    # For Gnosis tools, read metadata from file
                    if [ -r "$script_path" ]; then
                        local version=$(head -6 "$script_path" | grep "# Version:" | sed 's/# Version://' | xargs)
                        local created=$(head -6 "$script_path" | grep "# Created:" | sed 's/# Created://' | xargs)
                        
                        print_color "green" "    - Status: Script exists (Gnosis tool active)"
                        if [ -n "$version" ]; then 
                            print_color "gray" "    - Version: $version"
                        fi
                        if [ -n "$created" ]; then
                            print_color "gray" "    - Created: $created"
                        fi
                    else
                        print_color "green" "    - Status: Script exists"
                    fi
                else
                    print_color "green" "    - Status: Script exists"
                fi
            else
                print_color "red" "    - Status: Script not found at $script_path"
            fi
        fi
        
        echo ""
    done
}

# Setup Gnosis Server for the first time
setup_evolve_server() {
    print_color "yellow" "Setting up Gnosis: Evolve MCP Server"
    
    # Get the current directory to save evolve.py with absolute path
    local current_dir=$(pwd)
    local evolve_script_path="$current_dir/evolve.py"
    
    # Check if evolve.py already exists in the current directory
    if [ -f "$evolve_script_path" ]; then
        print_color "green" "Found evolve.py at: $evolve_script_path"
    else
        print_color "red" "evolve.py not found at: $evolve_script_path"
        print_color "yellow" "Please make sure evolve.py is in the current directory before continuing."
        return 1
    fi
    
    # Create a backup of the existing config
    local backup_path="${CONFIG_PATH}.backup"
    if [ -f "$CONFIG_PATH" ]; then
        cp "$CONFIG_PATH" "$backup_path" 2>/dev/null
        if [ $? -eq 0 ]; then
            print_color "green" "Created configuration backup at: $backup_path"
        else
            print_color "yellow" "Warning: Failed to create backup of configuration file"
        fi
    fi
    
    # Check if jq is installed for JSON handling
    if ! command -v jq >/dev/null 2>&1; then
        print_color "red" "jq is required for configuration but is not installed."
        print_color "yellow" "Please install jq with: brew install jq"
        return 1
    fi
    
    # Check if other MCP servers exist
    local has_other_servers=false
    
    if [ -f "$CONFIG_PATH" ]; then
        local server_count=$(jq '.mcpServers | length' "$CONFIG_PATH" 2>/dev/null)
        if [ $? -eq 0 ] && [ "$server_count" != "0" ] && [ "$server_count" != "null" ]; then
            # Check for servers other than evolve-server
            local other_server_count=$(jq '.mcpServers | keys[] | select(. != "evolve-server") | length' "$CONFIG_PATH" 2>/dev/null | wc -l)
            if [ "$other_server_count" -gt 0 ]; then
                has_other_servers=true
                print_color "yellow" "The following MCP servers are currently configured:"
                
                jq -r '.mcpServers | keys[] | select(. != "evolve-server")' "$CONFIG_PATH" | while read -r server; do
                    print_color "cyan" "  - $server"
                done
                
                print_color "yellow" "Setting up evolve will REMOVE all other MCP servers from the configuration."
                print_color "yellow" "   All tools will need to be reconfigured through evolve_setup."
                
                read -p "Are you sure you want to continue? (y/n) " confirmation
                if [ "$confirmation" != "y" ]; then
                    print_color "red" "Setup aborted."
                    return 1
                fi
            fi
        fi
    fi
    
    # Create a new configuration with only evolve-server
    local new_config=$(cat <<EOF
{
  "mcpServers": {
    "evolve-server": {
      "command": "python3",
      "args": ["$evolve_script_path"]
    }
  }
}
EOF
)
    
    # Write the configuration
    local config_dir=$(dirname "$CONFIG_PATH")
    if [ ! -d "$config_dir" ]; then
        mkdir -p "$config_dir" 2>/dev/null
        if [ $? -ne 0 ]; then
            print_color "red" "Error creating configuration directory: $config_dir"
            
            # Offer to restore backup
            if [ -f "$backup_path" ]; then
                read -p "Would you like to restore the backup configuration? (y/n) " restore_backup
                if [ "$restore_backup" = "y" ]; then
                    cp "$backup_path" "$CONFIG_PATH" 2>/dev/null
                    if [ $? -eq 0 ]; then
                        print_color "green" "Restored configuration from backup."
                    else
                        print_color "red" "Failed to restore backup."
                    fi
                fi
            fi
            
            return 1
        fi
    fi
    
    # Save the new configuration
    echo "$new_config" > "$CONFIG_PATH"
    if [ $? -eq 0 ]; then
        if [ "$has_other_servers" = true ]; then
            print_color "green" "Removed all previous MCP servers and configured evolve-server."
        else
            print_color "green" "Configured evolve-server."
        fi
        
        print_color "green" "Config uses absolute path to Gnosis: Evolve script: $evolve_script_path"
        print_color "green" "Gnosis: Evolve MCP server setup completed successfully!"
        
        read -p "Would you like to restart Claude now? (y/n) " restart_option
        if [ "$restart_option" = "y" ]; then
            restart_claude
        else
            print_color "yellow" "Remember to restart Claude for the changes to take effect."
        fi
        
        return 0
    else
        print_color "red" "Failed to update Claude configuration"
        
        # Offer to restore backup
        if [ -f "$backup_path" ]; then
            read -p "Would you like to restore the backup configuration? (y/n) " restore_backup
            if [ "$restore_backup" = "y" ]; then
                cp "$backup_path" "$CONFIG_PATH" 2>/dev/null
                if [ $? -eq 0 ]; then
                    print_color "green" "Restored configuration from backup."
                else
                    print_color "red" "Failed to restore backup."
                fi
            fi
        fi
        
        return 1
    fi
}

# Main menu function
show_claude_manager_menu() {
    # Menu for script actions
    print_color "magenta" "\n===== CLAUDE MANAGER MENU ====="
    print_color "cyan" "1. View MCP Logs"
    print_color "cyan" "2. Kill Claude Desktop"
    print_color "cyan" "3. Setup Gnosis: Evolve Server"
    print_color "cyan" "4. Restart Claude"
    print_color "cyan" "5. List Current MCP Servers"
    print_color "cyan" "6. Exit"

    read -p "Select an option (1-6): " choice

    case $choice in
        "1")
            # View MCP Logs
            view_mcp_logs
            
            # Return to menu after viewing logs
            read -p "Return to menu? (y/n) " return_to_menu
            if [ "$return_to_menu" = "y" ]; then
                show_claude_manager_menu
            fi
            ;;
        "2")
            # Kill Claude Desktop
            manage_claude_process "--kill"
            
            # Return to menu after killing processes
            read -p "Return to menu? (y/n) " return_to_menu
            if [ "$return_to_menu" = "y" ]; then
                show_claude_manager_menu
            fi
            ;;
        "3")
            # Setup Evolve Server
            setup_evolve_server
            
            # Return to menu after setup
            read -p "Return to menu? (y/n) " return_to_menu
            if [ "$return_to_menu" = "y" ]; then
                show_claude_manager_menu
            fi
            ;;
        "4")
            # Restart Claude
            restart_claude
            
            # Return to menu after restart
            read -p "Return to menu? (y/n) " return_to_menu
            if [ "$return_to_menu" = "y" ]; then
                show_claude_manager_menu
            fi
            ;;
        "5")
            # List MCP Tools
            list_mcp_tools
            
            # Return to menu after listing tools
            read -p "Return to menu? (y/n) " return_to_menu
            if [ "$return_to_menu" = "y" ]; then
                show_claude_manager_menu
            fi
            ;;
        "6")
            print_color "yellow" "Exiting..."
            exit 0
            ;;
        *)
            print_color "red" "Invalid option. Please select a valid option."
            show_claude_manager_menu
            ;;
    esac
}

# Main execution starts here
parse_args "$@"

# Process command-line parameters
if [ "$VIEW_LOGS" = true ]; then
    view_mcp_logs "$LOG_NAME"
    exit 0
fi

if [ "$KILL" = true ]; then
    manage_claude_process "--kill"
    exit 0
fi

if [ "$SETUP" = true ]; then
    setup_evolve_server
    exit 0
fi

if [ "$RESTART" = true ]; then
    restart_claude
    exit 0
fi

if [ "$LIST_TOOLS" = true ]; then
    list_mcp_tools
    exit 0
fi

# If no parameters specified or MENU is true, show the menu
if [ "$MENU" = true ] || [ $# -eq 0 ]; then
    # Start the script by showing the menu
    print_color "yellow" "Gnosis: Evolve - Claude Manager Tool"
    print_color "yellow" "Logs Path: $LOGS_PATH"
    print_color "yellow" "Config Path: $CONFIG_PATH"
    show_claude_manager_menu
fi