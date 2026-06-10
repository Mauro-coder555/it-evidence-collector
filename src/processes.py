"""Process collection utilities."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import psutil


def _safe_process_value(value: Any) -> Any:
    """Return a normalized process value."""
    if value is None:
        return "not available"
    return value


def _format_bytes(value: int | float | None) -> str:
    """Format a byte value using a human-readable unit."""
    if value is None:
        return "not available"

    value_float = float(value)
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if value_float < 1024:
            return f"{value_float:.2f} {unit}"
        value_float /= 1024

    return f"{value_float:.2f} PB"


def _format_process_time(timestamp: float | None) -> str:
    """Format a process creation timestamp."""
    if timestamp is None or timestamp <= 0:
        return "not available"

    try:
        return datetime.fromtimestamp(timestamp).isoformat(timespec="seconds")
    except Exception:
        return "not available"


def _prime_cpu_measurement() -> None:
    """Prime process CPU measurement so later readings are meaningful."""
    for process in psutil.process_iter():
        try:
            process.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def collect_processes(limit: int = 25) -> dict[str, Any]:
    """Collect active processes and top resource consumers."""
    processes: list[dict[str, Any]] = []
    errors: list[str] = []

    _prime_cpu_measurement()
    time.sleep(1)

    for process in psutil.process_iter(
        attrs=[
            "pid",
            "name",
            "username",
            "status",
            "create_time",
            "memory_info",
            "memory_percent",
        ]
    ):
        try:
            info = process.info
            memory_info = info.get("memory_info")
            cpu_percent = process.cpu_percent(interval=None)

            processes.append(
                {
                    "pid": _safe_process_value(info.get("pid")),
                    "name": _safe_process_value(info.get("name")),
                    "username": _safe_process_value(info.get("username")),
                    "status": _safe_process_value(info.get("status")),
                    "created_at": _format_process_time(info.get("create_time")),
                    "cpu_percent": round(float(cpu_percent or 0), 2),
                    "memory_percent": round(float(info.get("memory_percent") or 0), 2),
                    "rss_memory": _format_bytes(memory_info.rss if memory_info else None),
                    "rss_memory_bytes": memory_info.rss if memory_info else 0,
                }
            )
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            errors.append(f"Access denied while reading process PID {process.pid}")
        except Exception as exc:
            errors.append(f"Error while reading process PID {process.pid}: {exc}")

    top_by_memory = sorted(
        processes,
        key=lambda item: item.get("rss_memory_bytes", 0),
        reverse=True,
    )[:limit]

    top_by_cpu = sorted(
        processes,
        key=lambda item: item.get("cpu_percent", 0),
        reverse=True,
    )[:limit]

    all_processes_sample = processes[:limit]

    for item in processes:
        item.pop("rss_memory_bytes", None)

    for item in top_by_memory:
        item.pop("rss_memory_bytes", None)

    for item in top_by_cpu:
        item.pop("rss_memory_bytes", None)

    for item in all_processes_sample:
        item.pop("rss_memory_bytes", None)

    return {
        "total_processes": len(processes),
        "top_by_memory": top_by_memory,
        "top_by_cpu": top_by_cpu,
        "all_processes_sample": all_processes_sample,
        "errors": errors,
    }