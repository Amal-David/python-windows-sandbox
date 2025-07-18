# Windows Sandbox Manager

Python library for managing Windows Sandbox instances programmatically. Useful for running untrusted code, testing applications, or executing AI agents in isolated environments.

## Installation

```bash
pip install windows-sandbox-manager
```

## Usage

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig

async def main():
    # Create sandbox manager
    manager = SandboxManager()
    
    # Create sandbox configuration
    config = SandboxConfig(
        name="my-sandbox",
        memory_mb=4096,
        cpu_cores=2,
        networking=True
    )
    
    # Create and start sandbox
    sandbox = await manager.create_sandbox(config)
    
    # Execute commands
    result = await sandbox.execute("python --version")
    print(f"Output: {result.stdout}")
    
    # Cleanup
    await sandbox.shutdown()

asyncio.run(main())
```

### CLI

```bash
wsb create sandbox.yaml
wsb list
wsb exec <sandbox-id> "python script.py"
wsb shutdown <sandbox-id>
```

## Configuration

```yaml
name: "dev-sandbox"
memory_mb: 4096
cpu_cores: 2
networking: true

folders:
  - host: "C:\\Projects\\MyApp"
    guest: "C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp"
    readonly: false

startup_commands:
  - "python --version"
```

## AI Agent Execution

Windows Sandbox provides a secure environment for running AI agents that need to execute untrusted code or interact with the file system without risking the host machine.

### Example: Running an AI Code Agent

```python
import asyncio
from windows_sandbox_manager import SandboxManager, SandboxConfig, FolderMapping
from pathlib import Path

async def run_ai_agent():
    config = SandboxConfig(
        name="ai-agent-sandbox",
        memory_mb=8192,
        cpu_cores=4,
        networking=True,
        folders=[
            FolderMapping(
                host=Path("C:/agent_workspace"),
                guest=Path("C:/Users/WDAGUtilityAccount/Desktop/workspace"),
                readonly=False
            )
        ],
        startup_commands=[
            "python -m pip install requests openai",
            "python -c \"print('AI Agent environment ready')\""
        ]
    )
    
    async with SandboxManager() as manager:
        sandbox = await manager.create_sandbox(config)
        
        # Execute AI agent code safely
        agent_code = '''
import os
import requests

# AI agent can safely write files, make network requests, etc.
with open("output.txt", "w") as f:
    f.write("AI agent executed safely in sandbox")

# Network access is isolated
response = requests.get("https://api.github.com")
print(f"API Status: {response.status_code}")
'''
        
        # Write agent code to sandbox
        result = await sandbox.execute(f'echo "{agent_code}" > agent.py')
        
        # Run the agent (now uses real PowerShell Direct communication)
        result = await sandbox.execute("python agent.py")
        print(f"Agent output: {result.stdout}")
        print(f"Exit code: {result.returncode}")
        
        # Monitor resource usage
        stats = await sandbox.get_resource_stats()
        print(f"Memory usage: {stats.memory_mb}MB")
        print(f"CPU usage: {stats.cpu_percent}%")
        
        # Check results
        result = await sandbox.execute("type output.txt")
        print(f"Agent created file: {result.stdout}")

asyncio.run(run_ai_agent())
```

### Use Cases for AI Agents

- **Code Generation & Execution**: Let AI agents write and test code without affecting your system
- **File System Operations**: Allow agents to create, modify, and organize files safely
- **Web Scraping**: Run web scraping agents with network isolation
- **Data Processing**: Process untrusted data files in a contained environment
- **Testing & Validation**: Test AI-generated scripts before running on production systems

## Features

- **Real Sandbox Execution**: Execute commands directly in Windows Sandbox VMs using PowerShell Direct
- **Resource Monitoring**: Monitor CPU, memory, and disk usage of sandbox processes in real-time
- **Async API**: Full async/await support for non-blocking sandbox operations
- **Secure Isolation**: Complete isolation from host system for running untrusted code
- **Folder Mapping**: Share folders between host and sandbox with configurable permissions
- **CLI Interface**: Command-line tools for managing sandboxes

## Requirements

- Windows 10 Pro/Enterprise/Education (version 1903+)
- Windows Sandbox feature enabled
- Python 3.9+
- PowerShell 5.0+ (for sandbox communication)

## Development

```bash
git clone https://github.com/Amal-David/python-windows-sandbox.git
cd python-windows-sandbox
pip install -e ".[dev]"
pytest
```

## License

MIT