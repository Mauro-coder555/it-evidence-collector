"""Evidence analysis helpers for generating support-friendly summaries."""

from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    """Convert a value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int = 0) -> int:
    """Convert a value to int safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _status_rank(status: str) -> int:
    """Return a numeric severity rank."""
    ranks = {
        "ok": 0,
        "review": 1,
        "warning": 2,
        "error": 3,
    }
    return ranks.get(status, 0)


def _worst_status(statuses: list[str]) -> str:
    """Return the worst status from a list."""
    if not statuses:
        return "ok"

    return sorted(statuses, key=_status_rank, reverse=True)[0]


def _find_primary_network_interface(interfaces: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Find the most likely active non-loopback network interface."""
    for interface in interfaces:
        if not interface.get("is_up"):
            continue

        name = str(interface.get("name", "")).lower()
        if "loopback" in name:
            continue

        addresses = interface.get("addresses", [])
        for address in addresses:
            if address.get("family") == "IPv4":
                ip_address = str(address.get("address", ""))
                if ip_address and not ip_address.startswith("127."):
                    return interface

    return None


def _find_ipv4(interface: dict[str, Any] | None) -> str:
    """Return the first IPv4 address for an interface."""
    if not interface:
        return "not available"

    for address in interface.get("addresses", []):
        if address.get("family") == "IPv4":
            return str(address.get("address", "not available"))

    return "not available"


def _build_resource_checks(evidence: dict[str, Any]) -> list[dict[str, str]]:
    """Build CPU, memory, and disk checks."""
    checks: list[dict[str, str]] = []

    resources = evidence.get("system", {}).get("resources", {})
    cpu = resources.get("cpu", {})
    memory = resources.get("memory", {})
    disks = resources.get("disks", [])

    cpu_usage = _as_float(cpu.get("cpu_usage_percent"))
    if cpu_usage >= 90:
        cpu_status = "warning"
        cpu_detail = f"{cpu_usage}% usage. CPU usage is very high."
    elif cpu_usage >= 75:
        cpu_status = "review"
        cpu_detail = f"{cpu_usage}% usage. CPU usage is elevated."
    else:
        cpu_status = "ok"
        cpu_detail = f"{cpu_usage}% usage."

    checks.append({"area": "cpu", "status": cpu_status, "detail": cpu_detail})

    memory_usage = _as_float(memory.get("usage_percent"))
    if memory_usage >= 90:
        memory_status = "warning"
        memory_detail = f"{memory_usage}% used. Memory usage is very high."
    elif memory_usage >= 80:
        memory_status = "warning"
        memory_detail = f"{memory_usage}% used. Memory usage is high."
    elif memory_usage >= 70:
        memory_status = "review"
        memory_detail = f"{memory_usage}% used. Memory usage is elevated."
    else:
        memory_status = "ok"
        memory_detail = f"{memory_usage}% used."

    checks.append({"area": "memory", "status": memory_status, "detail": memory_detail})

    if not disks:
        checks.append(
            {
                "area": "disk",
                "status": "review",
                "detail": "No disk usage data available.",
            }
        )
        return checks

    for disk in disks:
        device = str(disk.get("device", "disk"))
        usage_percent = _as_float(disk.get("usage_percent"))

        if disk.get("error"):
            status = "review"
            detail = f"{device}: disk data is incomplete: {disk.get('error')}"
        elif usage_percent >= 80:
            status = "warning"
            detail = f"{device}: {usage_percent}% used, {disk.get('free', 'not available')} free."
        elif usage_percent >= 70:
            status = "review"
            detail = f"{device}: {usage_percent}% used, {disk.get('free', 'not available')} free."
        else:
            status = "ok"
            detail = f"{device}: {usage_percent}% used, {disk.get('free', 'not available')} free."

        checks.append({"area": "disk", "status": status, "detail": detail})

    return checks


def _build_process_checks(evidence: dict[str, Any]) -> list[dict[str, str]]:
    """Build process-related checks."""
    checks: list[dict[str, str]] = []

    processes = evidence.get("processes", {})
    total_processes = _as_int(processes.get("total_processes"))

    if total_processes >= 350:
        status = "review"
        detail = f"{total_processes} active processes. This is high and may deserve review."
    elif total_processes >= 250:
        status = "review"
        detail = f"{total_processes} active processes. This is moderately high."
    else:
        status = "ok"
        detail = f"{total_processes} active processes."

    checks.append({"area": "processes", "status": status, "detail": detail})

    top_memory = processes.get("top_by_memory", [])
    if top_memory:
        top = top_memory[0]
        checks.append(
            {
                "area": "top_memory_process",
                "status": "review",
                "detail": (
                    f"Top memory process: {top.get('name', 'not available')} "
                    f"PID {top.get('pid', 'not available')} using "
                    f"{top.get('rss_memory', 'not available')}."
                ),
            }
        )

    top_cpu = processes.get("top_by_cpu", [])
    if top_cpu:
        top = top_cpu[0]
        top_cpu_usage = _as_float(top.get("cpu_percent"))

        if top_cpu_usage >= 50:
            status = "warning"
        elif top_cpu_usage >= 20:
            status = "review"
        else:
            status = "ok"

        checks.append(
            {
                "area": "top_cpu_process",
                "status": status,
                "detail": (
                    f"Top CPU process: {top.get('name', 'not available')} "
                    f"PID {top.get('pid', 'not available')} using "
                    f"{top.get('cpu_percent', 'not available')}% CPU."
                ),
            }
        )

    return checks


def _build_network_checks(evidence: dict[str, Any]) -> list[dict[str, str]]:
    """Build network-related checks."""
    checks: list[dict[str, str]] = []

    network = evidence.get("network", {})
    interfaces = network.get("interfaces", [])
    listening_ports = network.get("listening_ports", {})
    connections = listening_ports.get("connections", [])

    primary_interface = _find_primary_network_interface(interfaces)
    primary_ip = _find_ipv4(primary_interface)

    if primary_interface:
        checks.append(
            {
                "area": "network",
                "status": "ok",
                "detail": (
                    f"Active interface: {primary_interface.get('name', 'not available')}, "
                    f"IPv4: {primary_ip}."
                ),
            }
        )
    else:
        checks.append(
            {
                "area": "network",
                "status": "warning",
                "detail": "No active non-loopback IPv4 network interface detected.",
            }
        )

    total_listening = _as_int(listening_ports.get("total_listening_connections"))
    checks.append(
        {
            "area": "listening_ports",
            "status": "review" if total_listening >= 25 else "ok",
            "detail": f"{total_listening} listening ports found.",
        }
    )

    public_bindings = []
    notable_ports = {
        445: "SMB / Windows file sharing",
        3389: "Remote Desktop",
        5432: "PostgreSQL",
        3306: "MySQL",
        1433: "SQL Server",
        6379: "Redis",
        9200: "Elasticsearch",
        11434: "Ollama",
    }

    for connection in connections:
        local_address = str(connection.get("local_address", ""))
        local_port = _as_int(connection.get("local_port"))

        if local_address in {"0.0.0.0", "::"}:
            public_bindings.append(connection)

        if local_port in notable_ports:
            bind_status = "review"
            if local_address in {"0.0.0.0", "::"} and local_port not in {445}:
                bind_status = "warning"

            checks.append(
                {
                    "area": "notable_port",
                    "status": bind_status,
                    "detail": (
                        f"{notable_ports[local_port]} listening on "
                        f"{local_address}:{local_port} "
                        f"({connection.get('process_name', 'not available')}, "
                        f"PID {connection.get('pid', 'not available')})."
                    ),
                }
            )

    if public_bindings:
        checks.append(
            {
                "area": "public_bindings",
                "status": "review",
                "detail": f"{len(public_bindings)} services are listening on all interfaces.",
            }
        )

    return checks


def _build_service_checks(evidence: dict[str, Any]) -> list[dict[str, str]]:
    """Build Windows service-related checks."""
    services = evidence.get("services", {})

    if not services.get("supported", False):
        return [
            {
                "area": "services",
                "status": "review",
                "detail": "Windows services are not available on this operating system.",
            }
        ]

    total_services = _as_int(services.get("total_services"))
    collection_error = services.get("error")

    if collection_error:
        return [
            {
                "area": "services",
                "status": "error",
                "detail": f"Service collection failed: {collection_error}",
            }
        ]

    if total_services <= 0:
        return [
            {
                "area": "services",
                "status": "error",
                "detail": "No Windows services were collected. Service collection may be broken.",
            }
        ]

    running = _as_int(services.get("summary", {}).get("Running"))
    stopped = _as_int(services.get("summary", {}).get("Stopped"))

    return [
        {
            "area": "services",
            "status": "ok",
            "detail": f"{total_services} services collected. Running: {running}, stopped: {stopped}.",
        }
    ]


def _build_crash_checks(evidence: dict[str, Any]) -> list[dict[str, str]]:
    """Build Windows crash diagnostics checks."""
    crash = evidence.get("crash_diagnostics", {})

    if not crash:
        return [
            {
                "area": "crash_diagnostics",
                "status": "review",
                "detail": "Windows crash diagnostics were not collected.",
            }
        ]

    if not crash.get("supported", False):
        return [
            {
                "area": "crash_diagnostics",
                "status": "review",
                "detail": "Windows crash diagnostics are not supported on this OS.",
            }
        ]

    checks: list[dict[str, str]] = []

    bugchecks = crash.get("bugchecks", {})
    bugcheck_count = _as_int(bugchecks.get("count"))
    last_bugcheck_code = bugchecks.get("last_bugcheck_code", "not available")

    if bugcheck_count > 0:
        checks.append(
            {
                "area": "bugcheck",
                "status": "warning",
                "detail": (
                    f"{bugcheck_count} BugCheck event(s) found in the last 30 days. "
                    f"Last detected code: {last_bugcheck_code}."
                ),
            }
        )
    else:
        checks.append(
            {
                "area": "bugcheck",
                "status": "ok",
                "detail": "No BugCheck events found in the last 30 days.",
            }
        )

    kernel_power = crash.get("kernel_power", {})
    kernel_power_count = _as_int(kernel_power.get("count"))
    if kernel_power_count > 0:
        checks.append(
            {
                "area": "kernel_power",
                "status": "review",
                "detail": f"{kernel_power_count} Kernel-Power event(s) found in the last 30 days.",
            }
        )

    whea_errors = crash.get("whea_errors", {})
    whea_count = _as_int(whea_errors.get("count"))
    if whea_count > 0:
        checks.append(
            {
                "area": "hardware_errors",
                "status": "warning",
                "detail": f"{whea_count} WHEA hardware error event(s) found in the last 30 days.",
            }
        )

    display_errors = crash.get("display_errors", {})
    display_count = _as_int(display_errors.get("count"))
    if display_count > 0:
        checks.append(
            {
                "area": "display_errors",
                "status": "review",
                "detail": f"{display_count} display driver related event(s) found in the last 30 days.",
            }
        )

    minidumps = crash.get("minidumps", {})
    minidump_count = _as_int(minidumps.get("count"))
    if minidump_count > 0:
        checks.append(
            {
                "area": "minidumps",
                "status": "review",
                "detail": f"{minidump_count} minidump file(s) found in {minidumps.get('directory')}.",
            }
        )

    errors = crash.get("errors", [])
    if errors:
        checks.append(
            {
                "area": "crash_collection_errors",
                "status": "review",
                "detail": f"{len(errors)} crash diagnostics collection issue(s) reported.",
            }
        )

    return checks


def build_findings(checks: list[dict[str, str]]) -> list[str]:
    """Build human-readable findings from checks."""
    findings: list[str] = []

    for check in checks:
        status = check.get("status", "ok")
        detail = check.get("detail", "")

        if status in {"warning", "error", "review"} and detail:
            findings.append(detail)

    if not findings:
        findings.append("No immediate issues were detected by the basic checks.")

    return findings


def build_recommendations(checks: list[dict[str, str]]) -> list[str]:
    """Build suggested next steps from checks."""
    recommendations: list[str] = []
    areas = {check.get("area"): check for check in checks}

    if "disk" in areas and areas["disk"].get("status") in {"review", "warning"}:
        recommendations.append("Review disk usage and free up space if possible.")

    if "memory" in areas and areas["memory"].get("status") in {"review", "warning"}:
        recommendations.append("Review high memory usage and top memory-consuming processes.")

    if "top_cpu_process" in areas and areas["top_cpu_process"].get("status") in {"review", "warning"}:
        recommendations.append("Review the top CPU process and confirm whether it is expected.")

    if "bugcheck" in areas and areas["bugcheck"].get("status") == "warning":
        recommendations.append("Review recent BugCheck events and analyze available minidump files.")

    if "kernel_power" in areas:
        recommendations.append("Check whether the device had unexpected restarts or power interruptions.")

    if "hardware_errors" in areas:
        recommendations.append("Review WHEA hardware errors. Consider checking drivers, BIOS, memory, and hardware health.")

    if "display_errors" in areas:
        recommendations.append("Review display driver events and consider updating or rolling back graphics drivers.")

    if "minidumps" in areas:
        recommendations.append("Analyze minidump files with WinDbg or another approved internal tool.")

    if "notable_port" in areas or "public_bindings" in areas:
        recommendations.append("Review services listening on all interfaces and confirm they are expected.")

    if not recommendations:
        recommendations.append("No immediate action suggested by the basic checks.")

    return recommendations


def analyze_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Analyze collected evidence and return a support-friendly summary."""
    checks: list[dict[str, str]] = []
    checks.extend(_build_resource_checks(evidence))
    checks.extend(_build_process_checks(evidence))
    checks.extend(_build_network_checks(evidence))
    checks.extend(_build_service_checks(evidence))
    checks.extend(_build_crash_checks(evidence))

    overall_status = _worst_status([check.get("status", "ok") for check in checks])

    return {
        "overall_status": overall_status,
        "checks": checks,
        "findings": build_findings(checks),
        "recommendations": build_recommendations(checks),
    }