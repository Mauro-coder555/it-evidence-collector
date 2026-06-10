"""Windows crash diagnostics collection utilities."""

from __future__ import annotations

import json
import platform
import re
import subprocess
from pathlib import Path
from typing import Any


def _run_powershell_json(command: str, timeout: int = 35) -> dict[str, Any]:
    """Run a safe read-only PowerShell command and return its output."""
    full_command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        command,
    ]

    try:
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            encoding="utf-8",
            errors="replace",
        )

        return {
            "command": " ".join(full_command),
            "return_code": result.returncode,
            "stdout": result.stdout.strip() or "not available",
            "stderr": result.stderr.strip() or "not available",
        }
    except FileNotFoundError:
        return {
            "command": " ".join(full_command),
            "return_code": "not available",
            "stdout": "not available",
            "stderr": "PowerShell not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(full_command),
            "return_code": "not available",
            "stdout": "not available",
            "stderr": "command timed out",
        }
    except Exception as exc:
        return {
            "command": " ".join(full_command),
            "return_code": "not available",
            "stdout": "not available",
            "stderr": str(exc),
        }


def _parse_json_output(raw_json: str) -> list[dict[str, Any]]:
    """Parse PowerShell JSON output into a list."""
    if not raw_json or raw_json == "not available":
        return []

    parsed = json.loads(raw_json)

    if isinstance(parsed, dict):
        return [parsed]

    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]

    return []


def _normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Windows event dictionary."""
    return {
        "time_created": event.get("TimeCreated", "not available"),
        "event_id": event.get("Id", "not available"),
        "provider": event.get("ProviderName", "not available"),
        "level": event.get("LevelDisplayName", "not available"),
        "message": event.get("Message", "not available"),
    }


def _collect_events(command: str) -> dict[str, Any]:
    """Collect Windows events from a PowerShell command."""
    command_result = _run_powershell_json(command)
    events: list[dict[str, Any]] = []
    error = ""

    if command_result.get("return_code") == 0:
        try:
            raw_events = _parse_json_output(str(command_result.get("stdout", "")))
            events = [_normalize_event(event) for event in raw_events]
        except json.JSONDecodeError as exc:
            error = f"Could not parse event JSON output: {exc}"
        except Exception as exc:
            error = str(exc)
    else:
        stderr = str(command_result.get("stderr", "not available"))
        if stderr != "not available":
            error = stderr

    return {
        "events": events,
        "count": len(events),
        "raw_command": command_result,
        "error": error,
    }


def _extract_bugcheck_code(events: list[dict[str, Any]]) -> str:
    """Extract the first bugcheck code found in event messages."""
    for event in events:
        message = str(event.get("message", ""))
        match = re.search(r"0x[0-9a-fA-F]+", message)
        if match:
            return match.group(0)

    return "not available"


def _collect_minidumps(limit: int = 20) -> dict[str, Any]:
    """Collect basic metadata for Windows minidump files."""
    minidump_dir = Path("C:/Windows/Minidump")

    if not minidump_dir.exists():
        return {
            "directory": str(minidump_dir),
            "exists": False,
            "count": 0,
            "files": [],
            "error": "",
        }

    try:
        dump_files = sorted(
            minidump_dir.glob("*.dmp"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )

        files = []
        for dump_file in dump_files[:limit]:
            stat = dump_file.stat()
            files.append(
                {
                    "name": dump_file.name,
                    "path": str(dump_file),
                    "size_bytes": stat.st_size,
                    "modified_timestamp": stat.st_mtime,
                }
            )

        return {
            "directory": str(minidump_dir),
            "exists": True,
            "count": len(dump_files),
            "files": files,
            "error": "",
        }
    except PermissionError:
        return {
            "directory": str(minidump_dir),
            "exists": True,
            "count": 0,
            "files": [],
            "error": "requires admin permissions",
        }
    except Exception as exc:
        return {
            "directory": str(minidump_dir),
            "exists": True,
            "count": 0,
            "files": [],
            "error": str(exc),
        }


def collect_windows_crash_diagnostics() -> dict[str, Any]:
    """Collect Windows crash-related diagnostics."""
    if platform.system().lower() != "windows":
        return {
            "supported": False,
            "bugchecks": {"events": [], "count": 0, "last_bugcheck_code": "not available"},
            "kernel_power": {"events": [], "count": 0},
            "whea_errors": {"events": [], "count": 0},
            "display_errors": {"events": [], "count": 0},
            "recent_critical_errors": {"events": [], "count": 0},
            "minidumps": {
                "directory": "C:/Windows/Minidump",
                "exists": False,
                "count": 0,
                "files": [],
                "error": "Windows-only feature",
            },
            "errors": ["Windows crash diagnostics are only available on Windows."],
        }

    event_projection = (
        "Select-Object TimeCreated,Id,ProviderName,LevelDisplayName,Message | "
        "ConvertTo-Json -Depth 3"
    )

    bugcheck_command = (
        "$events = Get-WinEvent -FilterHashtable "
        "@{LogName='System'; Id=1001; StartTime=(Get-Date).AddDays(-30)} "
        "-MaxEvents 20 -ErrorAction SilentlyContinue; "
        "$events | " + event_projection
    )

    kernel_power_command = (
        "$events = Get-WinEvent -FilterHashtable "
        "@{LogName='System'; Id=41; StartTime=(Get-Date).AddDays(-30)} "
        "-MaxEvents 20 -ErrorAction SilentlyContinue; "
        "$events | " + event_projection
    )

    whea_command = (
        "$events = Get-WinEvent -FilterHashtable "
        "@{LogName='System'; ProviderName='Microsoft-Windows-WHEA-Logger'; "
        "StartTime=(Get-Date).AddDays(-30)} "
        "-MaxEvents 20 -ErrorAction SilentlyContinue; "
        "$events | " + event_projection
    )

    display_command = (
        "$events = Get-WinEvent -FilterHashtable "
        "@{LogName='System'; ProviderName='Display'; StartTime=(Get-Date).AddDays(-30)} "
        "-MaxEvents 20 -ErrorAction SilentlyContinue; "
        "$events | " + event_projection
    )

    critical_errors_command = (
        "$events = Get-WinEvent -FilterHashtable "
        "@{LogName='System'; Level=1,2; StartTime=(Get-Date).AddDays(-7)} "
        "-MaxEvents 30 -ErrorAction SilentlyContinue; "
        "$events | " + event_projection
    )

    bugchecks = _collect_events(bugcheck_command)
    bugchecks["last_bugcheck_code"] = _extract_bugcheck_code(bugchecks.get("events", []))

    kernel_power = _collect_events(kernel_power_command)
    whea_errors = _collect_events(whea_command)
    display_errors = _collect_events(display_command)
    recent_critical_errors = _collect_events(critical_errors_command)
    minidumps = _collect_minidumps()

    errors = []
    for section_name, section in {
        "bugchecks": bugchecks,
        "kernel_power": kernel_power,
        "whea_errors": whea_errors,
        "display_errors": display_errors,
        "recent_critical_errors": recent_critical_errors,
    }.items():
        if section.get("error"):
            errors.append(f"{section_name}: {section['error']}")

    if minidumps.get("error"):
        errors.append(f"minidumps: {minidumps['error']}")

    return {
        "supported": True,
        "bugchecks": bugchecks,
        "kernel_power": kernel_power,
        "whea_errors": whea_errors,
        "display_errors": display_errors,
        "recent_critical_errors": recent_critical_errors,
        "minidumps": minidumps,
        "errors": errors,
    }