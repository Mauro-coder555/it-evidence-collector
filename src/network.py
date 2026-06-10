"""Network collection utilities."""

from __future__ import annotations

import locale
import socket
import subprocess
from typing import Any

import psutil


def _decode_windows_output(data: bytes) -> str:
    """Decode Windows command output using safe fallbacks."""
    encodings = [
        "utf-8",
        locale.getpreferredencoding(False),
        "cp850",
        "cp437",
        "latin-1",
    ]

    for encoding in encodings:
        if not encoding:
            continue

        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue

    return data.decode("utf-8", errors="replace")


def _run_command(command: list[str], timeout: int = 20) -> dict[str, Any]:
    """Run a safe read-only command and return its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            check=False,
        )

        return {
            "command": " ".join(command),
            "return_code": result.returncode,
            "stdout": _decode_windows_output(result.stdout).strip() or "not available",
            "stderr": _decode_windows_output(result.stderr).strip() or "not available",
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


def collect_interfaces() -> list[dict[str, Any]]:
    """Collect network interface addresses and status."""
    interfaces: list[dict[str, Any]] = []

    try:
        addresses = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
    except Exception as exc:
        return [{"name": "not available", "error": str(exc)}]

    for name, address_list in addresses.items():
        interface_stats = stats.get(name)

        interface_data: dict[str, Any] = {
            "name": name,
            "is_up": interface_stats.isup if interface_stats else "not available",
            "speed_mbps": interface_stats.speed if interface_stats else "not available",
            "addresses": [],
        }

        for address in address_list:
            family = "unknown"

            if address.family == socket.AF_INET:
                family = "IPv4"
            elif address.family == socket.AF_INET6:
                family = "IPv6"
            elif hasattr(psutil, "AF_LINK") and address.family == psutil.AF_LINK:
                family = "MAC"

            interface_data["addresses"].append(
                {
                    "family": family,
                    "address": address.address,
                    "netmask": address.netmask or "not available",
                    "broadcast": address.broadcast or "not available",
                }
            )

        interfaces.append(interface_data)

    return interfaces


def collect_listening_ports(limit: int = 100) -> dict[str, Any]:
    """Collect listening TCP ports."""
    connections: list[dict[str, Any]] = []
    errors: list[str] = []

    try:
        net_connections = psutil.net_connections(kind="inet")
    except psutil.AccessDenied:
        return {
            "connections": [],
            "errors": ["requires admin permissions to read full network connections"],
        }
    except Exception as exc:
        return {
            "connections": [],
            "errors": [str(exc)],
        }

    for connection in net_connections:
        try:
            if connection.type != socket.SOCK_STREAM:
                continue

            if connection.status != psutil.CONN_LISTEN:
                continue

            process_name = "not available"
            if connection.pid:
                try:
                    process_name = psutil.Process(connection.pid).name()
                except Exception:
                    process_name = "not available"

            local_address = "not available"
            local_port = "not available"

            if connection.laddr:
                local_address = connection.laddr.ip
                local_port = connection.laddr.port

            connections.append(
                {
                    "protocol": "TCP",
                    "local_address": local_address,
                    "local_port": local_port,
                    "pid": connection.pid or "not available",
                    "process_name": process_name,
                    "status": connection.status,
                }
            )
        except Exception as exc:
            errors.append(str(exc))

    connections = sorted(
        connections,
        key=lambda item: (
            str(item.get("local_address", "")),
            int(item.get("local_port", 0)) if str(item.get("local_port", "")).isdigit() else 0,
        ),
    )

    return {
        "connections": connections[:limit],
        "total_listening_connections": len(connections),
        "errors": errors,
    }


def collect_network_info() -> dict[str, Any]:
    """Collect network diagnostic information."""
    return {
        "interfaces": collect_interfaces(),
        "listening_ports": collect_listening_ports(),
        "ipconfig": _run_command(["ipconfig", "/all"]),
        "route_print": _run_command(["route", "print"]),
        "netstat": _run_command(["netstat", "-ano"]),
    }