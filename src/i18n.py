"""Simple internationalization helpers for the IT Evidence Collector app."""

from __future__ import annotations


DEFAULT_LANGUAGE = "en"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "app.title": "IT Evidence Collector",
        "app.description": (
            "Local defensive diagnostic tool for IT support. "
            "It collects read-only system evidence and generates a Markdown report."
        ),
        "app.safety": (
            "Safety: this tool does not delete files, kill processes, modify services, "
            "change system settings, or collect credentials."
        ),
        "label.language": "Language:",
        "button.start": "Start evidence collection",
        "button.open_reports": "Open reports folder",
        "label.activity_log": "Activity log:",
        "status.ready": "Ready.",
        "status.starting": "Starting evidence collection...",
        "status.collection_running": "Evidence collection is already running.",
        "status.generating_report": "Generating Markdown report...",
        "status.completed": "Report generated",
        "status.failed": "Evidence collection failed.",
        "dialog.already_running.title": "Collection already running",
        "dialog.completed.title": "Collection completed",
        "dialog.completed.message": "Evidence report generated successfully:",
        "dialog.failed.title": "Collection failed",
        "dialog.failed.message": "Evidence collection failed:",
        "dialog.open_reports_failed.title": "Could not open reports folder",
        "dialog.open_reports_failed.message": "Could not open reports folder:",
        "log.starting": "Starting evidence collection...",
        "log.completed": "Report generated successfully:",
        "log.error": "Error:",
        "progress.system": "Collecting system information...",
        "progress.processes": "Collecting process information...",
        "progress.network": "Collecting network information...",
        "progress.services": "Collecting Windows service information...",
        "progress.analyzing": "Analyzing collected evidence...",
        "progress.finalizing": "Finalizing evidence collection...",
        "metadata.purpose": "Defensive IT support and diagnostic evidence collection",
        "metadata.safety_note": (
            "This tool only collects read-only diagnostic information. "
            "It does not modify system configuration, kill processes, delete files, "
            "change services, or collect passwords, tokens, cookies, or private keys."
        ),
        "warning.system_failed": "System information collection failed",
        "warning.processes_failed": "Process collection failed",
        "warning.network_failed": "Network collection failed",
        "warning.services_failed": "Service collection failed",
        "warning.analysis_failed": "Evidence analysis failed",
        "report.title": "IT Evidence Collector Report",
        "report.purpose": "Purpose",
        "report.purpose_text": (
            "This report was generated for defensive IT support, troubleshooting, "
            "and initial diagnostic investigation."
        ),
        "report.safety_note": "Safety Note",
        "report.not_replacement": (
            "This tool does not replace an EDR, SIEM, antivirus, or formal forensic process."
        ),
        "report.quick_status": "Quick Computer Status",
        "report.overall_status": "Overall status",
        "report.key_findings": "Key Findings",
        "report.no_findings": "No immediate issues were detected by the basic checks.",
        "report.collection_summary": "Collection Summary",
        "report.resource_usage": "Resource Usage",
        "report.cpu": "CPU",
        "report.memory": "Memory",
        "report.disks": "Disks",
        "report.processes": "Processes",
        "report.total_processes": "Total processes collected",
        "report.top_by_memory": "Top Processes by Memory",
        "report.top_by_cpu": "Top Processes by CPU",
        "report.process_errors": "Process Collection Errors",
        "report.no_process_errors": "No process collection errors reported.",
        "report.network_summary": "Network Summary",
        "report.network_interfaces": "Network Interfaces",
        "report.listening_ports": "Listening Ports",
        "report.windows_services": "Windows Services",
        "report.safe_command_outputs": "Safe Command Outputs",
        "report.collection_warnings": "Collection Warnings",
        "report.no_collection_warnings": "No collection warnings reported.",
        "report.no_process_data": "No process data available.",
        "report.no_disk_data": "No disk data available.",
        "report.no_interface_data": "No network interface data available.",
        "report.no_address_data": "No address data available.",
        "report.no_listening_ports": "No listening port data available.",
        "report.no_service_data": "No service data available.",
        "report.services_not_available": "Windows services are not available on this operating system.",
        "report.total_listening_connections": "Total listening connections found",
        "report.total_services": "Total services found",
        "report.service_state_summary": "Service State Summary",
        "report.service_sample": "Service Sample",
        "report.errors": "Errors",
        "report.command": "Command",
        "report.return_code": "Return code",
        "report.stdout": "stdout",
        "report.stderr": "stderr",
        "table.area": "Area",
        "table.status": "Status",
        "table.detail": "Detail",
        "table.field": "Field",
        "table.value": "Value",
        "table.pid": "PID",
        "table.name": "Name",
        "table.user": "User",
        "table.cpu_percent": "CPU %",
        "table.memory_percent": "Memory %",
        "table.rss_memory": "RSS Memory",
        "table.created_at": "Created At",
        "table.device": "Device",
        "table.mountpoint": "Mountpoint",
        "table.filesystem": "Filesystem",
        "table.total": "Total",
        "table.used": "Used",
        "table.free": "Free",
        "table.usage_percent": "Usage %",
        "table.error": "Error",
        "table.family": "Family",
        "table.address": "Address",
        "table.netmask": "Netmask",
        "table.broadcast": "Broadcast",
        "table.protocol": "Protocol",
        "table.local_address": "Local Address",
        "table.local_port": "Local Port",
        "table.process": "Process",
        "table.service_name": "Service Name",
        "table.display_name": "Display Name",
        "table.start_type": "Start Type",
    },
    "es": {
        "app.title": "Recolector de Evidencia IT",
        "app.description": (
            "Herramienta local de diagnóstico defensivo para soporte IT. "
            "Recolecta evidencia del sistema en modo solo lectura y genera un reporte Markdown."
        ),
        "app.safety": (
            "Seguridad: esta herramienta no borra archivos, no mata procesos, no modifica servicios, "
            "no cambia configuraciones del sistema ni recolecta credenciales."
        ),
        "label.language": "Idioma:",
        "button.start": "Iniciar recolección de evidencia",
        "button.open_reports": "Abrir carpeta de reportes",
        "label.activity_log": "Registro de actividad:",
        "status.ready": "Listo.",
        "status.starting": "Iniciando recolección de evidencia...",
        "status.collection_running": "La recolección de evidencia ya está en ejecución.",
        "status.generating_report": "Generando reporte Markdown...",
        "status.completed": "Reporte generado",
        "status.failed": "La recolección de evidencia falló.",
        "dialog.already_running.title": "Recolección en ejecución",
        "dialog.completed.title": "Recolección completada",
        "dialog.completed.message": "Reporte de evidencia generado correctamente:",
        "dialog.failed.title": "La recolección falló",
        "dialog.failed.message": "La recolección de evidencia falló:",
        "dialog.open_reports_failed.title": "No se pudo abrir la carpeta de reportes",
        "dialog.open_reports_failed.message": "No se pudo abrir la carpeta de reportes:",
        "log.starting": "Iniciando recolección de evidencia...",
        "log.completed": "Reporte generado correctamente:",
        "log.error": "Error:",
        "progress.system": "Recolectando información del sistema...",
        "progress.processes": "Recolectando información de procesos...",
        "progress.network": "Recolectando información de red...",
        "progress.services": "Recolectando información de servicios de Windows...",
        "progress.analyzing": "Analizando evidencia recolectada...",
        "progress.finalizing": "Finalizando recolección de evidencia...",
        "metadata.purpose": "Recolección de evidencia defensiva para soporte IT y diagnóstico",
        "metadata.safety_note": (
            "Esta herramienta solo recolecta información de diagnóstico en modo lectura. "
            "No modifica la configuración del sistema, no mata procesos, no borra archivos, "
            "no cambia servicios y no recolecta contraseñas, tokens, cookies ni claves privadas."
        ),
        "warning.system_failed": "Falló la recolección de información del sistema",
        "warning.processes_failed": "Falló la recolección de procesos",
        "warning.network_failed": "Falló la recolección de red",
        "warning.services_failed": "Falló la recolección de servicios",
        "warning.analysis_failed": "Falló el análisis de evidencia",
        "report.title": "Reporte de Evidencia IT",
        "report.purpose": "Propósito",
        "report.purpose_text": (
            "Este reporte fue generado para soporte IT defensivo, troubleshooting "
            "e investigación diagnóstica inicial."
        ),
        "report.safety_note": "Nota de seguridad",
        "report.not_replacement": (
            "Esta herramienta no reemplaza un EDR, SIEM, antivirus ni un proceso forense formal."
        ),
        "report.quick_status": "Estado rápido del equipo",
        "report.overall_status": "Estado general",
        "report.key_findings": "Hallazgos principales",
        "report.no_findings": "No se detectaron problemas inmediatos con los chequeos básicos.",
        "report.collection_summary": "Resumen de recolección",
        "report.resource_usage": "Uso de recursos",
        "report.cpu": "CPU",
        "report.memory": "Memoria",
        "report.disks": "Discos",
        "report.processes": "Procesos",
        "report.total_processes": "Total de procesos recolectados",
        "report.top_by_memory": "Procesos con mayor uso de memoria",
        "report.top_by_cpu": "Procesos con mayor uso de CPU",
        "report.process_errors": "Errores de recolección de procesos",
        "report.no_process_errors": "No se reportaron errores de recolección de procesos.",
        "report.network_summary": "Resumen de red",
        "report.network_interfaces": "Interfaces de red",
        "report.listening_ports": "Puertos en escucha",
        "report.windows_services": "Servicios de Windows",
        "report.safe_command_outputs": "Salidas de comandos seguros",
        "report.collection_warnings": "Advertencias de recolección",
        "report.no_collection_warnings": "No se reportaron advertencias de recolección.",
        "report.no_process_data": "No hay datos de procesos disponibles.",
        "report.no_disk_data": "No hay datos de discos disponibles.",
        "report.no_interface_data": "No hay datos de interfaces de red disponibles.",
        "report.no_address_data": "No hay datos de direcciones disponibles.",
        "report.no_listening_ports": "No hay datos de puertos en escucha disponibles.",
        "report.no_service_data": "No hay datos de servicios disponibles.",
        "report.services_not_available": "Los servicios de Windows no están disponibles en este sistema operativo.",
        "report.total_listening_connections": "Total de conexiones en escucha encontradas",
        "report.total_services": "Total de servicios encontrados",
        "report.service_state_summary": "Resumen de estados de servicios",
        "report.service_sample": "Muestra de servicios",
        "report.errors": "Errores",
        "report.command": "Comando",
        "report.return_code": "Código de retorno",
        "report.stdout": "stdout",
        "report.stderr": "stderr",
        "table.area": "Área",
        "table.status": "Estado",
        "table.detail": "Detalle",
        "table.field": "Campo",
        "table.value": "Valor",
        "table.pid": "PID",
        "table.name": "Nombre",
        "table.user": "Usuario",
        "table.cpu_percent": "CPU %",
        "table.memory_percent": "Memoria %",
        "table.rss_memory": "Memoria RSS",
        "table.created_at": "Creado en",
        "table.device": "Dispositivo",
        "table.mountpoint": "Punto de montaje",
        "table.filesystem": "Sistema de archivos",
        "table.total": "Total",
        "table.used": "Usado",
        "table.free": "Libre",
        "table.usage_percent": "Uso %",
        "table.error": "Error",
        "table.family": "Familia",
        "table.address": "Dirección",
        "table.netmask": "Máscara de red",
        "table.broadcast": "Broadcast",
        "table.protocol": "Protocolo",
        "table.local_address": "Dirección local",
        "table.local_port": "Puerto local",
        "table.process": "Proceso",
        "table.service_name": "Nombre del servicio",
        "table.display_name": "Nombre visible",
        "table.start_type": "Tipo de inicio",
    },
}


def normalize_language(language: str | None) -> str:
    """Return a supported language code."""
    if not language:
        return DEFAULT_LANGUAGE

    normalized = language.lower().strip()
    if normalized not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE

    return normalized


def t(language: str | None, key: str) -> str:
    """Translate a key using the selected language."""
    language_code = normalize_language(language)
    return TRANSLATIONS.get(language_code, TRANSLATIONS[DEFAULT_LANGUAGE]).get(
        key,
        TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key),
    )