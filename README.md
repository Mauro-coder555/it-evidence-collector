# IT Evidence Collector

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-green)
![Windows](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Markdown](https://img.shields.io/badge/Reports-Markdown-purple)
![Status](https://img.shields.io/badge/Status-MVP-orange)
![Safety](https://img.shields.io/badge/Safety-Read%20Only-brightgreen)

**IT Evidence Collector** es una aplicación de escritorio local para Windows pensada para soporte técnico, troubleshooting e investigación inicial.

La herramienta recolecta información básica del equipo en modo solo lectura y genera un reporte Markdown con un resumen rápido, hallazgos principales y detalle técnico.

No es una herramienta forense avanzada. No reemplaza un EDR, SIEM, antivirus ni un proceso formal de análisis.

---

## Índice

- [Qué hace](#qué-hace)
- [Para qué sirve](#para-qué-sirve)
- [Información que recolecta](#información-que-recolecta)
- [Diagnóstico de crashes de Windows](#diagnóstico-de-crashes-de-windows)
- [Seguridad](#seguridad)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Instalación](#instalación)
- [Uso](#uso)
- [Reportes generados](#reportes-generados)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Mejoras futuras](#mejoras-futuras)

---

## Qué hace

La app permite ejecutar una recolección local de evidencia del equipo y generar un reporte con información útil para soporte.

El reporte incluye un resumen inicial para ver rápido el estado general de la PC.

Ejemplos de alertas que puede mostrar:

- Memoria alta
- Disco con poco espacio libre
- Muchos procesos activos
- Procesos con alto consumo de CPU o memoria
- Servicios escuchando en puertos relevantes
- PostgreSQL, SMB, RDP u otros puertos expuestos
- Eventos recientes de crash o BugCheck en Windows
- Reinicios inesperados registrados por Kernel-Power

---

## Para qué sirve

Sirve como una primera revisión técnica antes de escalar un caso.

Casos de uso posibles:

- Soporte IT remoto
- Troubleshooting de equipos lentos
- Revisión inicial después de pantallazos azules o reinicios
- Diagnóstico básico de red y servicios
- Evidencia inicial para adjuntar a un ticket
- Comparar el estado de una PC antes y después de una intervención

---

## Información que recolecta

La herramienta recolecta:

- Sistema operativo
- Hostname
- Usuario actual
- Fecha y hora de recolección
- Uptime
- CPU
- Memoria RAM
- Uso de disco
- Procesos activos
- Procesos con mayor uso de memoria
- Procesos con mayor uso de CPU
- Interfaces de red
- IP local
- Puertos TCP en escucha
- Servicios de Windows
- Salida de comandos seguros como `ipconfig /all`, `route print` y `netstat -ano`
- Eventos de crash de Windows
- Eventos BugCheck
- Eventos Kernel-Power
- Eventos WHEA
- Eventos Display
- Archivos minidump si existen

---

## Diagnóstico de crashes de Windows

La app incluye una sección para detectar señales relacionadas con pantallazos azules, reinicios inesperados y errores de sistema.

Busca información como:

- BugCheck events
- Kernel-Power events
- WHEA hardware events
- Display driver events
- Critical and error events recientes
- Archivos `.dmp` en `C:\Windows\Minidump`

Esto ayuda a detectar casos como:

- `DRIVER_IRQL_NOT_LESS_OR_EQUAL`
- `IRQL_NOT_LESS_OR_EQUAL`
- reinicios inesperados
- errores de driver
- posibles errores de hardware

La herramienta no analiza archivos dump en profundidad. Solo detecta su existencia y resume eventos relevantes.

---

## Seguridad

La herramienta es de solo lectura.

No realiza acciones destructivas.

No hace lo siguiente:

- No borra archivos
- No mata procesos
- No modifica servicios
- No cambia configuraciones del sistema
- No instala persistencia
- No recolecta contraseñas
- No recolecta tokens
- No recolecta cookies
- No recolecta claves privadas

---

## Tecnologías utilizadas

- **Python** para la lógica principal
- **Tkinter** para la interfaz gráfica
- **psutil** para métricas del sistema, procesos y red
- **PowerShell** para servicios y eventos de Windows
- **Markdown** para generar reportes simples y portables

---

## Instalación

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno virtual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

---

## Uso

Con el entorno virtual activo:

```powershell
python main.py
```

Luego:

1. Seleccionar idioma
2. Ejecutar la recolección
3. Esperar a que finalice
4. Abrir la carpeta de reportes desde la app
5. Revisar el archivo Markdown generado

---

## Reportes generados

Los reportes se guardan dentro de la carpeta:

```text
reports/
```

Ejemplos:

```text
reports/evidence-report-en-YYYYMMDD-HHMMSS.md
reports/evidence-report-es-YYYYMMDD-HHMMSS.md
```

El reporte incluye:

- Estado rápido del equipo
- Hallazgos principales
- Próximos pasos sugeridos
- Diagnóstico de crashes de Windows
- Información del sistema
- Recursos
- Procesos
- Red
- Servicios
- Salidas de comandos seguros
- Advertencias de recolección

---

## Estructura del proyecto

```text
it-evidence-collector/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── reports/
│   └── .gitkeep
│
└── src/
    ├── __init__.py
    ├── analysis.py
    ├── collectors.py
    ├── i18n.py
    ├── network.py
    ├── processes.py
    ├── report.py
    ├── services.py
    ├── system_info.py
    ├── ui.py
    └── windows_events.py
```

---

## Mejoras futuras

Ideas para próximas versiones:

- Corregir encoding de comandos clásicos de Windows
- Buscar también `C:\Windows\MEMORY.DMP`
- Buscar dumps en `C:\Windows\LiveKernelReports`
- Marcar el proceso propio de la herramienta para que no aparezca como falso top CPU
- Agregar estado de Windows Defender
- Agregar estado de BitLocker
- Agregar últimos errores del Event Viewer por categoría
- Exportar también en HTML
- Agregar botón para copiar resumen ejecutivo
- Empaquetar como `.exe` con PyInstaller
- Agregar firma o hash del reporte generado

---

## Estado del proyecto

MVP funcional para diagnóstico inicial de soporte IT en Windows.

