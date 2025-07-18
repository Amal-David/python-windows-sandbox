"""
Windows Sandbox Manager - A modern, secure Python library for Windows Sandbox management.
"""

from .core.manager import SandboxManager
from .core.sandbox import Sandbox
from .config.models import SandboxConfig
from .exceptions import (
    SandboxError,
    SandboxCreationError,
    SandboxNotFoundError,
    ConfigurationError,
    SecurityError,
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "SandboxManager",
    "Sandbox",
    "SandboxConfig",
    "SandboxError",
    "SandboxCreationError",
    "SandboxNotFoundError",
    "ConfigurationError",
    "SecurityError",
]
