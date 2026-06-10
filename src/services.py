"""Windows service collection utilities."""

from __future__ import annotations

import json
import platform
import subprocess
from typing import Any


def _run_powershell_json(command: str, timeout: int = 30) -> dict[str, Any]:
    """Run a safe PowerShell read-only command that returns JSON."""
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


def _normalize_service_json(raw_json: str) -> list[dict[str, Any]]:
    """Parse and normalize PowerShell service JSON output."""
    if not raw_json or raw_json == "not available":
        return []

    parsed = json.loads(raw_json)

    if isinstance(parsed, dict):
        parsed = [parsed]

    services: list[dict[str, Any]] = []

    for item in parsed:
        if not isinstance(item, dict):
            continue

        services.append(
            {
                "service_name": item.get("Name", "not available"),
                "display_name": item.get("DisplayName", "not available"),
                "status": item.get("Status", "not available"),
                "start_type": item.get("StartType", "not available"),
            }
        )

    return services


def collect_services(limit: int = 150) -> dict[str, Any]:
    """Collect Windows service state information."""
    if platform.system().lower() != "windows":
        return {
            "supported": False,
            "services": [],
            "summary": {},
            "raw_command": {
                "command": "Get-Service",
                "stdout": "not available",
                "stderr": "Windows services are only available on Windows",
            },
        }

    powershell_command = (
        "Get-Service | "
        "Select-Object Name,DisplayName,Status,StartType | "
        "ConvertTo-Json -Depth 2"
    )

    command_result = _run_powershell_json(powershell_command)
    services: list[dict[str, Any]] = []
    error = ""

    if command_result.get("return_code") == 0 and command_result.get("stdout") != "not available":
        try:
            services = _normalize_service_json(str(command_result["stdout"]))
        except json.JSONDecodeError as exc:
            error = f"Could not parse PowerShell JSON output: {exc}"
        except Exception as exc:
            error = str(exc)
    else:
        error = str(command_result.get("stderr", "not available"))

    summary: dict[str, int] = {}
    for service in services:
        status = str(service.get("status", "not available"))
        summary[status] = summary.get(status, 0) + 1

    services = sorted(
        services,
        key=lambda item: (
            str(item.get("status", "")),
            str(item.get("service_name", "")).lower(),
        ),
    )

    return {
        "supported": True,
        "total_services": len(services),
        "summary": summary,
        "services": services[:limit],
        "raw_command": command_result,
        "error": error,
    }