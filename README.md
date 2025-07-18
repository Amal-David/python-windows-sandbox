# Windows Sandbox Manager

Python library for managing Windows Sandbox instances programmatically.

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

## Requirements

- Windows 10 Pro/Enterprise/Education (version 1903+)
- Windows Sandbox feature enabled
- Python 3.9+

## Development

```bash
git clone https://github.com/Amal-David/python-windows-sandbox.git
cd python-windows-sandbox
pip install -e ".[dev]"
pytest
```

## License

MIT