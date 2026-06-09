"""Windows service collection utilities."""

from __future__ import annotations

import platform
import subprocess
from typing import Any


def _run_command(command: list[str], timeout: int = 30) -> dict[str, Any]:
    """Run a safe read-only command and return its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            encoding="utf-8",
            errors="replace",
        )

        return {
            "command": " ".join(command),
            "return_code": result.returncode,
            "stdout": result.stdout.strip() or "not available",
            "stderr": result.stderr.strip() or "not available",
        }
    except FileNotFoundError:
        return {
            "command": " ".join(command),
            "return_code": "not available",
            "stdout": "not available",
            "stderr": "command not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(command),
            "return_code": "not available",
            "stdout": "not available",
            "stderr": "command timed out",
        }
    except Exception as exc:
        return {
            "command": " ".join(command),
            "return_code": "not available",
            "stdout": "not available",
            "stderr": str(exc),
        }


def _parse_sc_query_output(output: str) -> list[dict[str, Any]]:
    """Parse a basic subset of sc query output."""
    services: list[dict[str, Any]] = []
    current_service: dict[str, Any] | None = None

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if line.startswith("SERVICE_NAME:"):
            if current_service:
                services.append(current_service)

            current_service = {
                "service_name": line.replace("SERVICE_NAME:", "").strip(),
                "display_name": "not available",
                "state": "not available",
            }

        elif current_service and line.startswith("DISPLAY_NAME:"):
            current_service["display_name"] = line.replace("DISPLAY_NAME:", "").strip()

        elif current_service and line.startswith("STATE"):
            parts = line.split(":", maxsplit=1)
            if len(parts) == 2:
                current_service["state"] = parts[1].strip()

    if current_service:
        services.append(current_service)

    return services


def collect_services(limit: int = 100) -> dict[str, Any]:
    """Collect Windows service state information."""
    if platform.system().lower() != "windows":
        return {
            "supported": False,
            "services": [],
            "summary": {},
            "raw_command": {
                "command": "sc query state= all",
                "stdout": "not available",
                "stderr": "Windows services are only available on Windows",
            },
        }

    command_result = _run_command(["sc", "query", "state=", "all"])
    services = []

    if command_result.get("stdout") and command_result["stdout"] != "not available":
        services = _parse_sc_query_output(command_result["stdout"])

    summary: dict[str, int] = {}
    for service in services:
        state = str(service.get("state", "not available"))
        summary[state] = summary.get(state, 0) + 1

    return {
        "supported": True,
        "total_services": len(services),
        "summary": summary,
        "services": services[:limit],
        "raw_command": command_result,
    }