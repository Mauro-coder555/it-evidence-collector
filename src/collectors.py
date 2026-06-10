"""Evidence collection orchestrator."""

from __future__ import annotations

from typing import Any, Callable

from src.analysis import analyze_evidence
from src.i18n import t
from src.network import collect_network_info
from src.processes import collect_processes
from src.services import collect_services
from src.system_info import collect_system_info

ProgressCallback = Callable[[int, str], None]


def _notify(progress_callback: ProgressCallback | None, percent: int, message: str) -> None:
    """Send progress updates to the UI if a callback is available."""
    if progress_callback:
        progress_callback(percent, message)


def collect_evidence(
    progress_callback: ProgressCallback | None = None,
    language: str = "en",
) -> dict[str, Any]:
    """Run all evidence collectors and return a combined payload."""
    evidence: dict[str, Any] = {
        "metadata": {
            "tool_name": "it-evidence-collector",
            "purpose": t(language, "metadata.purpose"),
            "safety_note": t(language, "metadata.safety_note"),
            "language": language,
        },
        "warnings": [],
    }

    _notify(progress_callback, 10, t(language, "progress.system"))
    try:
        evidence["system"] = collect_system_info()
    except Exception as exc:
        evidence["system"] = {"error": str(exc)}
        evidence["warnings"].append(f"{t(language, 'warning.system_failed')}: {exc}")

    _notify(progress_callback, 35, t(language, "progress.processes"))
    try:
        evidence["processes"] = collect_processes()
    except Exception as exc:
        evidence["processes"] = {"error": str(exc)}
        evidence["warnings"].append(f"{t(language, 'warning.processes_failed')}: {exc}")

    _notify(progress_callback, 60, t(language, "progress.network"))
    try:
        evidence["network"] = collect_network_info()
    except Exception as exc:
        evidence["network"] = {"error": str(exc)}
        evidence["warnings"].append(f"{t(language, 'warning.network_failed')}: {exc}")

    _notify(progress_callback, 80, t(language, "progress.services"))
    try:
        evidence["services"] = collect_services()
    except Exception as exc:
        evidence["services"] = {"error": str(exc)}
        evidence["warnings"].append(f"{t(language, 'warning.services_failed')}: {exc}")

    _notify(progress_callback, 90, t(language, "progress.analyzing"))
    try:
        evidence["analysis"] = analyze_evidence(evidence)
    except Exception as exc:
        evidence["analysis"] = {
            "overall_status": "review",
            "checks": [],
            "findings": [f"{t(language, 'warning.analysis_failed')}: {exc}"],
        }
        evidence["warnings"].append(f"{t(language, 'warning.analysis_failed')}: {exc}")

    _notify(progress_callback, 95, t(language, "progress.finalizing"))

    return evidence