"""System information collection utilities."""

from __future__ import annotations

import getpass
import platform
import socket
from datetime import datetime
from typing import Any

import psutil


def _format_bytes(value: int | float) -> str:
    """Format a byte value using a human-readable unit."""
    value_float = float(value)
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if value_float < 1024:
            return f"{value_float:.2f} {unit}"
        value_float /= 1024

    return f"{value_float:.2f} PB"


def _safe_call(label: str, func: Any, default: str = "not available") -> Any:
    """Run a callable and return a safe value when it fails."""
    try:
        return func()
    except PermissionError:
        return f"{default}: requires admin permissions for {label}"
    except Exception as exc:
        return f"{default}: {exc}"


def get_basic_system_info() -> dict[str, Any]:
    """Collect basic operating system and host information."""
    boot_time = _safe_call(
        "boot time",
        lambda: datetime.fromtimestamp(psutil.boot_time()).isoformat(timespec="seconds"),
    )

    uptime = "not available"
    if isinstance(boot_time, str) and not boot_time.startswith("not available"):
        try:
            boot_dt = datetime.fromisoformat(boot_time)
            uptime_delta = datetime.now() - boot_dt
            uptime = str(uptime_delta).split(".")[0]
        except Exception:
            uptime = "not available"

    return {
        "collection_time": datetime.now().isoformat(timespec="seconds"),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": _safe_call("hostname", socket.gethostname),
        "current_user": _safe_call("current user", getpass.getuser),
        "python_version": platform.python_version(),
        "boot_time": boot_time,
        "uptime": uptime,
    }


def get_resource_usage() -> dict[str, Any]:
    """Collect CPU, memory, and disk usage information."""
    cpu_info = {
        "physical_cores": _safe_call("physical CPU cores", lambda: psutil.cpu_count(logical=False)),
        "logical_cores": _safe_call("logical CPU cores", lambda: psutil.cpu_count(logical=True)),
        "cpu_usage_percent": _safe_call(
            "CPU usage",
            lambda: psutil.cpu_percent(interval=1),
        ),
    }

    memory = _safe_call("memory usage", psutil.virtual_memory)
    if not isinstance(memory, str):
        memory_info = {
            "total": _format_bytes(memory.total),
            "available": _format_bytes(memory.available),
            "used": _format_bytes(memory.used),
            "usage_percent": memory.percent,
        }
    else:
        memory_info = {
            "total": memory,
            "available": memory,
            "used": memory,
            "usage_percent": memory,
        }

    disk_info = []
    partitions = _safe_call("disk partitions", psutil.disk_partitions)

    if isinstance(partitions, str):
        disk_info.append({"device": "not available", "error": partitions})
    else:
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype or "not available",
                        "total": _format_bytes(usage.total),
                        "used": _format_bytes(usage.used),
                        "free": _format_bytes(usage.free),
                        "usage_percent": usage.percent,
                    }
                )
            except PermissionError:
                disk_info.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype or "not available",
                        "error": "requires admin permissions",
                    }
                )
            except Exception as exc:
                disk_info.append(
                    {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype or "not available",
                        "error": str(exc),
                    }
                )

    return {
        "cpu": cpu_info,
        "memory": memory_info,
        "disks": disk_info,
    }


def collect_system_info() -> dict[str, Any]:
    """Collect all system information sections."""
    return {
        "basic": get_basic_system_info(),
        "resources": get_resource_usage(),
    }