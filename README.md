# Windows Sandbox Manager

A modern, secure, and scalable Python library for creating and managing Windows Sandbox instances with enterprise-grade features and performance.

## Features

- **🔒 Security First**: Input validation, privilege separation, and comprehensive audit logging
- **⚡ Async by Default**: Non-blocking operations for better concurrency and performance
- **🔧 Type Safe**: Full type hints with runtime validation using Pydantic
- **📊 Observable**: Structured logging, metrics collection, and health monitoring
- **🔌 Extensible**: Plugin architecture for custom functionality
- **☁️ Cloud Ready**: Built for scaling and container environments

## Quick Start

### Installation

```bash
pip install windows-sandbox-manager
```

### Basic Usage

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

### CLI Usage

```bash
# Create sandbox from config
wsb create sandbox.yaml

# List running sandboxes  
wsb list

# Execute command in sandbox
wsb exec <sandbox-id> "python script.py"

# Monitor resources
wsb monitor <sandbox-id>

# Shutdown sandbox
wsb shutdown <sandbox-id>
```

## Configuration

Create a YAML configuration file:

```yaml
# sandbox.yaml
name: "development-sandbox"
memory_mb: 4096
cpu_cores: 2
networking: true
gpu_acceleration: false

folders:
  - host: "C:\\Projects\\MyApp"
    guest: "C:\\Users\\WDAGUtilityAccount\\Desktop\\MyApp"
    readonly: false

environment:
  PYTHON_PATH: "C:\\Python39"
  DEBUG: "true"

startup_commands:
  - "python --version"
  - "pip install -r requirements.txt"

security:
  isolation_level: "high"
  network_restrictions:
    allow: ["*.github.com"]
    deny: ["*"]

monitoring:
  metrics_enabled: true
  log_level: "info"
  health_check_interval: 30
```

## Requirements

- Windows 10 Pro/Enterprise/Education (version 1903 or later)
- Windows Sandbox feature enabled
- Python 3.9 or later

## Architecture

The library is built with a modular architecture:

- **Core Engine**: Async sandbox lifecycle management
- **Configuration System**: Type-safe configuration with Pydantic
- **Security Framework**: Input validation and privilege management
- **Communication Layer**: High-performance gRPC communication
- **Monitoring System**: Resource tracking and health checks
- **Plugin System**: Extensible functionality framework

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Inspiration

This project was inspired by existing Windows Sandbox automation tools and aims to provide a modern, production-ready alternative with enterprise features.

---

For detailed documentation, examples, and API reference, visit our [documentation site](https://windows-sandbox-manager.readthedocs.io).