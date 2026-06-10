"""Markdown report generation utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from src.i18n import normalize_language, t


REPORTS_DIR = Path("reports")


def _safe_value(value: Any) -> str:
    """Convert a value into a safe Markdown string."""
    if value is None:
        return "not available"

    text = str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("|", "\\|")
    return text


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


def _localized_label(language: str, english: str, spanish: str) -> str:
    """Return a small localized label without requiring translation keys."""
    return spanish if normalize_language(language) == "es" else english


def _status_badge(status: Any) -> str:
    """Format a status value for Markdown."""
    normalized = str(status).lower().strip()

    if normalized == "ok":
        return "OK"
    if normalized == "review":
        return "REVIEW"
    if normalized == "warning":
        return "WARNING"
    if normalized == "error":
        return "ERROR"

    return _safe_value(status)


def _render_key_value_table(data: dict[str, Any], language: str) -> str:
    """Render a dictionary as a Markdown key-value table."""
    lines = [
        f"| {t(language, 'table.field')} | {t(language, 'table.value')} |",
        "|---|---|",
    ]

    for key, value in data.items():
        lines.append(f"| `{key}` | {_safe_value(value)} |")

    return "\n".join(lines)


def _render_quick_status(analysis: dict[str, Any], language: str) -> str:
    """Render the quick computer status section."""
    checks = analysis.get("checks", [])

    lines = [
        f"{t(language, 'report.overall_status')}: **{_status_badge(analysis.get('overall_status', 'ok'))}**",
        "",
        f"| {t(language, 'table.area')} | {t(language, 'table.status')} | {t(language, 'table.detail')} |",
        "|---|---|---|",
    ]

    for check in checks:
        lines.append(
            "| "
            f"{_safe_value(check.get('area'))} | "
            f"{_status_badge(check.get('status'))} | "
            f"{_safe_value(check.get('detail'))} |"
        )

    return "\n".join(lines)


def _render_key_findings(analysis: dict[str, Any], language: str) -> str:
    """Render key findings."""
    findings = analysis.get("findings", [])

    if not findings:
        return t(language, "report.no_findings")

    return "\n".join([f"- {_safe_value(finding)}" for finding in findings])


def _render_recommendations(analysis: dict[str, Any], language: str) -> str:
    """Render suggested next steps."""
    recommendations = analysis.get("recommendations", [])

    if not recommendations:
        return _localized_label(
            language,
            "No immediate action suggested by the basic checks.",
            "No se sugieren acciones inmediatas con los chequeos básicos.",
        )

    return "\n".join([f"- {_safe_value(recommendation)}" for recommendation in recommendations])


def _render_process_table(processes: list[dict[str, Any]], language: str) -> str:
    """Render process rows as a Markdown table."""
    if not processes:
        return t(language, "report.no_process_data")

    lines = [
        (
            f"| {t(language, 'table.pid')} "
            f"| {t(language, 'table.name')} "
            f"| {t(language, 'table.user')} "
            f"| {t(language, 'table.status')} "
            f"| {t(language, 'table.cpu_percent')} "
            f"| {t(language, 'table.memory_percent')} "
            f"| {t(language, 'table.rss_memory')} "
            f"| {t(language, 'table.created_at')} |"
        ),
        "|---:|---|---|---|---:|---:|---:|---|",
    ]

    for process in processes:
        lines.append(
            "| "
            f"{_safe_value(process.get('pid'))} | "
            f"{_safe_value(process.get('name'))} | "
            f"{_safe_value(process.get('username'))} | "
            f"{_safe_value(process.get('status'))} | "
            f"{_safe_value(process.get('cpu_percent'))} | "
            f"{_safe_value(process.get('memory_percent'))} | "
            f"{_safe_value(process.get('rss_memory'))} | "
            f"{_safe_value(process.get('created_at'))} |"
        )

    return "\n".join(lines)


def _render_disk_table(disks: list[dict[str, Any]], language: str) -> str:
    """Render disk usage as a Markdown table."""
    if not disks:
        return t(language, "report.no_disk_data")

    lines = [
        (
            f"| {t(language, 'table.device')} "
            f"| {t(language, 'table.mountpoint')} "
            f"| {t(language, 'table.filesystem')} "
            f"| {t(language, 'table.total')} "
            f"| {t(language, 'table.used')} "
            f"| {t(language, 'table.free')} "
            f"| {t(language, 'table.usage_percent')} "
            f"| {t(language, 'table.error')} |"
        ),
        "|---|---|---|---:|---:|---:|---:|---|",
    ]

    for disk in disks:
        lines.append(
            "| "
            f"{_safe_value(disk.get('device'))} | "
            f"{_safe_value(disk.get('mountpoint'))} | "
            f"{_safe_value(disk.get('filesystem'))} | "
            f"{_safe_value(disk.get('total'))} | "
            f"{_safe_value(disk.get('used'))} | "
            f"{_safe_value(disk.get('free'))} | "
            f"{_safe_value(disk.get('usage_percent'))} | "
            f"{_safe_value(disk.get('error', ''))} |"
        )

    return "\n".join(lines)


def _render_interfaces(interfaces: list[dict[str, Any]], language: str) -> str:
    """Render network interface information."""
    if not interfaces:
        return t(language, "report.no_interface_data")

    sections = []

    for interface in interfaces:
        section = [
            f"### {_safe_value(interface.get('name'))}",
            "",
            _render_key_value_table(
                {
                    "is_up": interface.get("is_up"),
                    "speed_mbps": interface.get("speed_mbps"),
                    "error": interface.get("error", ""),
                },
                language,
            ),
            "",
        ]

        addresses = interface.get("addresses", [])
        if addresses:
            section.extend(
                [
                    (
                        f"| {t(language, 'table.family')} "
                        f"| {t(language, 'table.address')} "
                        f"| {t(language, 'table.netmask')} "
                        f"| {t(language, 'table.broadcast')} |"
                    ),
                    "|---|---|---|---|",
                ]
            )

            for address in addresses:
                section.append(
                    "| "
                    f"{_safe_value(address.get('family'))} | "
                    f"{_safe_value(address.get('address'))} | "
                    f"{_safe_value(address.get('netmask'))} | "
                    f"{_safe_value(address.get('broadcast'))} |"
                )
        else:
            section.append(t(language, "report.no_address_data"))

        sections.append("\n".join(section))

    return "\n\n".join(sections)


def _render_listening_ports(data: dict[str, Any], language: str) -> str:
    """Render listening ports as a Markdown table."""
    connections = data.get("connections", [])

    if not connections:
        return t(language, "report.no_listening_ports")

    lines = [
        (
            f"{t(language, 'report.total_listening_connections')}: "
            f"**{_safe_value(data.get('total_listening_connections'))}**"
        ),
        "",
        (
            f"| {t(language, 'table.protocol')} "
            f"| {t(language, 'table.local_address')} "
            f"| {t(language, 'table.local_port')} "
            f"| {t(language, 'table.pid')} "
            f"| {t(language, 'table.process')} "
            f"| {t(language, 'table.status')} |"
        ),
        "|---|---|---:|---:|---|---|",
    ]

    for connection in connections:
        lines.append(
            "| "
            f"{_safe_value(connection.get('protocol'))} | "
            f"{_safe_value(connection.get('local_address'))} | "
            f"{_safe_value(connection.get('local_port'))} | "
            f"{_safe_value(connection.get('pid'))} | "
            f"{_safe_value(connection.get('process_name'))} | "
            f"{_safe_value(connection.get('status'))} |"
        )

    errors = data.get("errors", [])
    if errors:
        lines.extend(["", f"{t(language, 'report.errors')}:"])
        lines.extend([f"- {_safe_value(error)}" for error in errors])

    return "\n".join(lines)


def _render_services(data: dict[str, Any], language: str) -> str:
    """Render service information."""
    if not data.get("supported", False):
        return t(language, "report.services_not_available")

    services = data.get("services", [])
    summary = data.get("summary", {})
    error = data.get("error", "")

    lines = [
        (
            f"{t(language, 'report.total_services')}: "
            f"**{_safe_value(data.get('total_services'))}**"
        ),
        "",
    ]

    if error:
        lines.extend([f"{t(language, 'table.error')}: **{_safe_value(error)}**", ""])

    lines.extend(
        [
            f"### {t(language, 'report.service_state_summary')}",
            "",
            _render_key_value_table(summary, language),
            "",
            f"### {t(language, 'report.service_sample')}",
            "",
        ]
    )

    if not services:
        lines.append(t(language, "report.no_service_data"))
        return "\n".join(lines)

    lines.extend(
        [
            (
                f"| {t(language, 'table.service_name')} "
                f"| {t(language, 'table.display_name')} "
                f"| {t(language, 'table.status')} "
                f"| {t(language, 'table.start_type')} |"
            ),
            "|---|---|---|---|",
        ]
    )

    for service in services:
        lines.append(
            "| "
            f"{_safe_value(service.get('service_name'))} | "
            f"{_safe_value(service.get('display_name'))} | "
            f"{_safe_value(service.get('status'))} | "
            f"{_safe_value(service.get('start_type'))} |"
        )

    return "\n".join(lines)


def _render_event_table(events: list[dict[str, Any]], language: str) -> str:
    """Render Windows events as a Markdown table."""
    if not events:
        return _localized_label(
            language,
            "No events found.",
            "No se encontraron eventos.",
        )

    lines = [
        "| Time | Event ID | Provider | Level | Message |",
        "|---|---:|---|---|---|",
    ]

    for event in events:
        message = str(event.get("message", "not available"))
        short_message = message.replace("\n", " ").strip()
        if len(short_message) > 220:
            short_message = short_message[:220] + "..."

        lines.append(
            "| "
            f"{_safe_value(event.get('time_created'))} | "
            f"{_safe_value(event.get('event_id'))} | "
            f"{_safe_value(event.get('provider'))} | "
            f"{_safe_value(event.get('level'))} | "
            f"{_safe_value(short_message)} |"
        )

    return "\n".join(lines)


def _render_minidumps(minidumps: dict[str, Any], language: str) -> str:
    """Render Windows minidump metadata."""
    files = minidumps.get("files", [])

    lines = [
        _render_key_value_table(
            {
                "directory": minidumps.get("directory"),
                "exists": minidumps.get("exists"),
                "count": minidumps.get("count"),
                "error": minidumps.get("error", ""),
            },
            language,
        ),
        "",
    ]

    if not files:
        lines.append(
            _localized_label(
                language,
                "No minidump files found.",
                "No se encontraron archivos minidump.",
            )
        )
        return "\n".join(lines)

    lines.extend(
        [
            "| File | Size | Path |",
            "|---|---:|---|",
        ]
    )

    for dump_file in files:
        lines.append(
            "| "
            f"{_safe_value(dump_file.get('name'))} | "
            f"{_format_bytes(dump_file.get('size_bytes'))} | "
            f"{_safe_value(dump_file.get('path'))} |"
        )

    return "\n".join(lines)


def _render_crash_diagnostics(crash: dict[str, Any], language: str) -> str:
    """Render Windows crash diagnostics."""
    if not crash:
        return _localized_label(
            language,
            "Crash diagnostics were not collected.",
            "No se recolectó diagnóstico de crashes.",
        )

    if not crash.get("supported", False):
        return _localized_label(
            language,
            "Windows crash diagnostics are not available on this operating system.",
            "El diagnóstico de crashes de Windows no está disponible en este sistema operativo.",
        )

    bugchecks = crash.get("bugchecks", {})
    kernel_power = crash.get("kernel_power", {})
    whea_errors = crash.get("whea_errors", {})
    display_errors = crash.get("display_errors", {})
    recent_critical_errors = crash.get("recent_critical_errors", {})
    minidumps = crash.get("minidumps", {})

    content = [
        "### Summary",
        "",
        _render_key_value_table(
            {
                "bugcheck_events_last_30_days": bugchecks.get("count", 0),
                "last_bugcheck_code": bugchecks.get("last_bugcheck_code", "not available"),
                "kernel_power_events_last_30_days": kernel_power.get("count", 0),
                "whea_events_last_30_days": whea_errors.get("count", 0),
                "display_events_last_30_days": display_errors.get("count", 0),
                "recent_critical_or_error_events_last_7_days": recent_critical_errors.get("count", 0),
                "minidump_files": minidumps.get("count", 0),
            },
            language,
        ),
        "",
        "### BugCheck Events",
        "",
        _render_event_table(bugchecks.get("events", []), language),
        "",
        "### Kernel-Power Events",
        "",
        _render_event_table(kernel_power.get("events", []), language),
        "",
        "### WHEA Hardware Events",
        "",
        _render_event_table(whea_errors.get("events", []), language),
        "",
        "### Display Driver Events",
        "",
        _render_event_table(display_errors.get("events", []), language),
        "",
        "### Minidump Files",
        "",
        _render_minidumps(minidumps, language),
    ]

    errors = crash.get("errors", [])
    if errors:
        content.extend(["", "### Collection Issues", ""])
        content.extend([f"- {_safe_value(error)}" for error in errors])

    return "\n".join(content)


def _render_command_output(title: str, command_result: dict[str, Any], language: str) -> str:
    """Render command output safely in Markdown."""
    return "\n".join(
        [
            f"### {title}",
            "",
            f"{t(language, 'report.command')}: `{_safe_value(command_result.get('command'))}`",
            "",
            f"{t(language, 'report.return_code')}: `{_safe_value(command_result.get('return_code'))}`",
            "",
            f"#### {t(language, 'report.stdout')}",
            "",
            "```text",
            _safe_value(command_result.get("stdout")),
            "```",
            "",
            f"#### {t(language, 'report.stderr')}",
            "",
            "```text",
            _safe_value(command_result.get("stderr")),
            "```",
        ]
    )


def generate_markdown_report(evidence: dict[str, Any], language: str = "en") -> Path:
    """Generate a localized Markdown report and return its path."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    language_code = normalize_language(language)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = REPORTS_DIR / f"evidence-report-{language_code}-{timestamp}.md"

    system = evidence.get("system", {})
    system_basic = system.get("basic", {})
    resources = system.get("resources", {})
    processes = evidence.get("processes", {})
    network = evidence.get("network", {})
    services = evidence.get("services", {})
    crash_diagnostics = evidence.get("crash_diagnostics", {})
    analysis = evidence.get("analysis", {})

    crash_title = _localized_label(
        language_code,
        "Windows Crash Diagnostics",
        "Diagnóstico de crashes de Windows",
    )

    recommendations_title = _localized_label(
        language_code,
        "Suggested Next Steps",
        "Próximos pasos sugeridos",
    )

    content = [
        f"# {t(language_code, 'report.title')}",
        "",
        f"## {t(language_code, 'report.quick_status')}",
        "",
        _render_quick_status(analysis, language_code),
        "",
        f"## {t(language_code, 'report.key_findings')}",
        "",
        _render_key_findings(analysis, language_code),
        "",
        f"## {recommendations_title}",
        "",
        _render_recommendations(analysis, language_code),
        "",
        f"## {crash_title}",
        "",
        _render_crash_diagnostics(crash_diagnostics, language_code),
        "",
        f"## {t(language_code, 'report.purpose')}",
        "",
        t(language_code, "report.purpose_text"),
        "",
        f"## {t(language_code, 'report.safety_note')}",
        "",
        evidence.get("metadata", {}).get("safety_note", t(language_code, "metadata.safety_note")),
        "",
        f"> {t(language_code, 'report.not_replacement')}",
        "",
        f"## {t(language_code, 'report.collection_summary')}",
        "",
        _render_key_value_table(system_basic, language_code),
        "",
        f"## {t(language_code, 'report.resource_usage')}",
        "",
        f"### {t(language_code, 'report.cpu')}",
        "",
        _render_key_value_table(resources.get("cpu", {}), language_code),
        "",
        f"### {t(language_code, 'report.memory')}",
        "",
        _render_key_value_table(resources.get("memory", {}), language_code),
        "",
        f"### {t(language_code, 'report.disks')}",
        "",
        _render_disk_table(resources.get("disks", []), language_code),
        "",
        f"## {t(language_code, 'report.processes')}",
        "",
        (
            f"{t(language_code, 'report.total_processes')}: "
            f"**{_safe_value(processes.get('total_processes'))}**"
        ),
        "",
        f"### {t(language_code, 'report.top_by_memory')}",
        "",
        _render_process_table(processes.get("top_by_memory", []), language_code),
        "",
        f"### {t(language_code, 'report.top_by_cpu')}",
        "",
        _render_process_table(processes.get("top_by_cpu", []), language_code),
        "",
        f"### {t(language_code, 'report.process_errors')}",
        "",
    ]

    process_errors = processes.get("errors", [])
    if process_errors:
        content.extend([f"- {_safe_value(error)}" for error in process_errors])
    else:
        content.append(t(language_code, "report.no_process_errors"))

    content.extend(
        [
            "",
            f"## {t(language_code, 'report.network_interfaces')}",
            "",
            _render_interfaces(network.get("interfaces", []), language_code),
            "",
            f"## {t(language_code, 'report.listening_ports')}",
            "",
            _render_listening_ports(network.get("listening_ports", {}), language_code),
            "",
            f"## {t(language_code, 'report.windows_services')}",
            "",
            _render_services(services, language_code),
            "",
            f"## {t(language_code, 'report.safe_command_outputs')}",
            "",
            _render_command_output("ipconfig /all", network.get("ipconfig", {}), language_code),
            "",
            _render_command_output("route print", network.get("route_print", {}), language_code),
            "",
            _render_command_output("netstat -ano", network.get("netstat", {}), language_code),
            "",
            f"## {t(language_code, 'report.collection_warnings')}",
            "",
        ]
    )

    warnings = evidence.get("warnings", [])
    if warnings:
        content.extend([f"- {_safe_value(warning)}" for warning in warnings])
    else:
        content.append(t(language_code, "report.no_collection_warnings"))

    report_path.write_text("\n".join(content), encoding="utf-8")

    return report_path