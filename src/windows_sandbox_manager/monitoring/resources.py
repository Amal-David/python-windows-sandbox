"""
Resource monitoring for sandbox instances.
"""

import asyncio
import psutil
from datetime import datetime
from typing import Optional


class ResourceStats:
    """Resource usage statistics."""

    def __init__(self, memory_mb: int, cpu_percent: float, disk_mb: int):
        self.memory_mb = memory_mb
        self.cpu_percent = cpu_percent
        self.disk_mb = disk_mb
        self.timestamp = datetime.utcnow()


class ResourceMonitor:
    """
    Monitors resource usage for sandbox instances.
    """

    def __init__(self, sandbox_id: str, interval: int = 30):
        self.sandbox_id = sandbox_id
        self.interval = interval
        self._monitoring = False
        self._task: Optional[asyncio.Task] = None
        self._latest_stats: Optional[ResourceStats] = None

    async def start(self) -> None:
        """Start resource monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop(self) -> None:
        """Stop resource monitoring."""
        self._monitoring = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def get_stats(self) -> ResourceStats:
        """Get latest resource statistics."""
        if self._latest_stats is None:
            # Return placeholder stats if monitoring not started
            return ResourceStats(memory_mb=0, cpu_percent=0.0, disk_mb=0)
        return self._latest_stats

    async def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                stats = await self._collect_stats()
                self._latest_stats = stats
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error but continue monitoring
                await asyncio.sleep(self.interval)

    async def _collect_stats(self) -> ResourceStats:
        """Collect current resource statistics for sandbox process."""
        try:
            # Find sandbox processes by name (WindowsSandbox.exe)
            sandbox_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    if proc.info['name'] and 'sandbox' in proc.info['name'].lower():
                        sandbox_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not sandbox_processes:
                # No sandbox processes found, return zero stats
                return ResourceStats(memory_mb=0, cpu_percent=0.0, disk_mb=0)
            
            # Aggregate stats from all sandbox processes
            total_memory_bytes = 0
            total_cpu_percent = 0.0
            total_disk_mb = 0
            
            for proc in sandbox_processes:
                try:
                    # Memory usage
                    memory_info = proc.memory_info()
                    total_memory_bytes += memory_info.rss
                    
                    # CPU usage (get current reading)
                    cpu_percent = proc.cpu_percent()
                    total_cpu_percent += cpu_percent
                    
                    # Disk usage estimation (based on process working set)
                    total_disk_mb += memory_info.vms // (1024 * 1024)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            memory_mb = total_memory_bytes // (1024 * 1024)
            
            return ResourceStats(
                memory_mb=int(memory_mb),
                cpu_percent=round(total_cpu_percent, 2),
                disk_mb=int(total_disk_mb)
            )
            
        except Exception:
            # If monitoring fails, return zero stats rather than crashing
            return ResourceStats(memory_mb=0, cpu_percent=0.0, disk_mb=0)
