
# claude_cleanup.py
# Script to properly terminate Claude processes including system tray icons

import os
import sys
import time
import psutil
import subprocess
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("claude_cleanup.log")]
)
logger = logging.getLogger("claude-cleanup")

def find_claude_processes() -> List[Dict[str, Any]]:
    """
    Finds all Claude-related processes running on the system.
    
    Returns:
        List of dictionaries with process information
    """
    claude_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'create_time']):
        try:
            # Get process info
            proc_info = proc.info
            name = proc_info.get('name', '').lower()
            cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
            exe = proc_info.get('exe', '').lower() if proc_info.get('exe') else ''
            
            # Check if this is a Claude-related process
            if ('claude' in name or 'claude' in cmdline or 'claude' in exe or
                'anthropic' in name or 'anthropic' in cmdline or 'anthropic' in exe):
                
                # Get additional info about this process
                try:
                    with proc.oneshot():
                        cpu_percent = proc.cpu_percent(interval=0.1)
                        memory_info = proc.memory_info()
                        status = proc.status()
                        parent_pid = proc.ppid()
                        parent_name = psutil.Process(parent_pid).name() if parent_pid else "None"
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    cpu_percent = 0
                    memory_info = None
                    status = "unknown"
                    parent_pid = None
                    parent_name = "unknown"
                
                # Add to results
                claude_processes.append({
                    'pid': proc_info['pid'],
                    'name': name,
                    'exe': exe,
                    'cmdline': cmdline,
                    'cpu_percent': cpu_percent,
                    'memory_mb': memory_info.rss / (1024 * 1024) if memory_info else 0,
                    'status': status,
                    'parent_pid': parent_pid,
                    'parent_name': parent_name,
                    'create_time': proc_info['create_time']
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return claude_processes

def find_system_tray_processes() -> List[Dict[str, Any]]:
    """
    Finds potential system tray processes that might be related to Claude.
    
    Returns:
        List of dictionaries with process information
    """
    tray_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            # Get process info
            proc_info = proc.info
            name = proc_info.get('name', '').lower()
            cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
            exe = proc_info.get('exe', '').lower() if proc_info.get('exe') else ''
            
            # Check if this is a system tray related process
            if ('systray' in name or 'tray' in name or 'notif' in name or
                'systray' in cmdline or 'tray' in cmdline or 'notif' in cmdline or
                'explorernot' in exe or 'shell' in exe):
                
                # Get additional info about this process
                try:
                    with proc.oneshot():
                        status = proc.status()
                        parent_pid = proc.ppid()
                        parent_name = psutil.Process(parent_pid).name() if parent_pid else "None"
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    status = "unknown"
                    parent_pid = None
                    parent_name = "unknown"
                
                # Add to results
                tray_processes.append({
                    'pid': proc_info['pid'],
                    'name': name,
                    'exe': exe,
                    'cmdline': cmdline,
                    'status': status,
                    'parent_pid': parent_pid,
                    'parent_name': parent_name
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return tray_processes

def terminate_claude_processes(force: bool = False, timeout: int = 5) -> Dict[str, Any]:
    """
    Terminates all Claude-related processes found on the system.
    
    Args:
        force: Whether to force termination using SIGKILL (Windows: taskkill /F)
        timeout: Seconds to wait for graceful termination before force-killing
    
    Returns:
        Dictionary with information about terminated processes
    """
    # Find Claude processes
    processes = find_claude_processes()
    
    if not processes:
        logger.info("No Claude processes found running")
        return {
            "status": "success",
            "message": "No Claude processes found running",
            "processes": []
        }
    
    logger.info(f"Found {len(processes)} Claude-related processes")
    for proc in processes:
        logger.info(f"Process: PID={proc['pid']}, Name={proc['name']}, Exe={proc['exe']}")
    
    # First attempt graceful termination on all processes
    terminated = []
    for proc in processes:
        try:
            pid = proc['pid']
            process = psutil.Process(pid)
            logger.info(f"Attempting to terminate process {pid} ({proc['name']})")
            process.terminate()
            terminated.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.error(f"Error terminating process {proc['pid']}: {str(e)}")
    
    # Wait for processes to terminate
    if terminated:
        logger.info(f"Waiting {timeout} seconds for graceful termination")
        _, alive = psutil.wait_procs([psutil.Process(p['pid']) for p in terminated 
                                    if psutil.pid_exists(p['pid'])], 
                                    timeout=timeout)
        
        # Force kill remaining processes if requested
        if alive and force:
            logger.info(f"{len(alive)} processes still alive after timeout, force killing")
            for process in alive:
                try:
                    logger.info(f"Force killing process {process.pid}")
                    process.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    logger.error(f"Error force killing process {process.pid}: {str(e)}")
    
    # Check if any system tray processes might need cleanup
    tray_processes = find_system_tray_processes()
    potential_issue_processes = []
    
    for proc in tray_processes:
        # Try to identify if any of these might be related to Claude
        # This is more speculative and would need manual review
        if proc['parent_pid'] is None or not psutil.pid_exists(proc['parent_pid']):
            # Orphaned process potentially
            potential_issue_processes.append(proc)
    
    # Final confirmation
    still_running = [p for p in processes if psutil.pid_exists(p['pid'])]
    
    # Try using Windows-specific taskkill as a last resort for stubborn processes
    if still_running and sys.platform == 'win32' and force:
        for proc in still_running:
            try:
                logger.info(f"Using taskkill to force kill PID {proc['pid']}")
                subprocess.run(['taskkill', '/F', '/PID', str(proc['pid'])], capture_output=True, text=True)
            except Exception as e:
                logger.error(f"Error with taskkill: {str(e)}")
    
    # Check for system tray cleaners and run them if needed
    if sys.platform == 'win32' and (still_running or potential_issue_processes):
        try:
            logger.info("Attempting to refresh system tray")
            # This will attempt to restart Windows Explorer, which can fix stuck icons
            subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], capture_output=True, text=True)
            time.sleep(1)  # Wait a moment
            subprocess.Popen(['explorer.exe'])
            logger.info("Windows Explorer has been restarted to clear tray icons")
        except Exception as e:
            logger.error(f"Error refreshing system tray: {str(e)}")
    
    # Final check
    final_check = find_claude_processes()
    
    return {
        "status": "success" if not final_check else "partial",
        "message": f"Successfully terminated {len(processes) - len(final_check)} Claude processes" 
                   if not final_check else f"Terminated some processes, but {len(final_check)} still running",
        "processes_found": len(processes),
        "processes_terminated": len(processes) - len(final_check),
        "processes_remaining": final_check,
        "potential_tray_issues": potential_issue_processes,
        "tray_refresh_attempted": bool(still_running or potential_issue_processes),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def list_claude_processes() -> Dict[str, Any]:
    """
    Lists all Claude-related processes without terminating them.
    
    Returns:
        Dictionary with information about running Claude processes
    """
    processes = find_claude_processes()
    
    return {
        "status": "success",
        "count": len(processes),
        "processes": processes,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude process cleanup utility")
    parser.add_argument('--list', action='store_true', help='Only list processes without terminating')
    parser.add_argument('--force', action='store_true', help='Force termination after timeout (default: False)')
    parser.add_argument('--timeout', type=int, default=5, help='Seconds to wait for graceful termination (default: 5)')
    
    args = parser.parse_args()
    
    if args.list:
        result = list_claude_processes()
        print(f"Found {result['count']} Claude-related processes:")
        for proc in result['processes']:
            print(f"PID: {proc['pid']}, Name: {proc['name']}, Memory: {proc['memory_mb']:.2f} MB")
    else:
        result = terminate_claude_processes(force=args.force, timeout=args.timeout)
        print(result['message'])
        
        if result['status'] == 'partial':
            print("\nProcesses still running:")
            for proc in result['processes_remaining']:
                print(f"PID: {proc['pid']}, Name: {proc['name']}")
        
        if result['tray_refresh_attempted']:
            print("\nSystem tray refresh was attempted to clean up icon resources")
            
    print(f"\nSee claude_cleanup.log for detailed information")
