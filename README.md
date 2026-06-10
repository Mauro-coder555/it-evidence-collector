# IT Evidence Collector

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![UI](https://img.shields.io/badge/UI-Tkinter-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Reports](https://img.shields.io/badge/Reports-Markdown-purple)
![Purpose](https://img.shields.io/badge/Purpose-Defensive%20IT-orange)
![Status](https://img.shields.io/badge/Status-MVP-yellow)

**IT Evidence Collector** es una aplicación de escritorio simple y local para Windows, pensada para equipos de soporte IT que necesitan recolectar evidencia básica de una computadora ante un incidente, comportamiento extraño o tarea de troubleshooting.

La herramienta genera un reporte en Markdown con información útil del sistema, consumo de recursos, procesos, red, puertos abiertos y servicios de Windows.

> Esta herramienta no reemplaza un EDR, SIEM, antivirus ni un proceso forense formal. Es un MVP defensivo para diagnóstico inicial y soporte técnico.

---

## Índice

- [Qué hace](#qué-hace)
- [Para qué sirve](#para-qué-sirve)
- [Características principales](#características-principales)
- [Información recolectada](#información-recolectada)
- [Seguridad y alcance](#seguridad-y-alcance)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Uso de la aplicación](#uso-de-la-aplicación)
- [Reportes generados](#reportes-generados)
- [Limitaciones actuales](#limitaciones-actuales)
- [Mejoras futuras](#mejoras-futuras)
- [Empaquetado futuro como .exe](#empaquetado-futuro-como-exe)
- [Comandos útiles de Git](#comandos-útiles-de-git)

---

## Qué hace

IT Evidence Collector permite abrir una interfaz visual simple, seleccionar idioma, iniciar una recolección de evidencia y generar automáticamente un reporte local en la carpeta `reports/`.

El objetivo es ayudar a una persona de soporte IT a responder preguntas como:

- ¿La computadora está con poco espacio en disco?
- ¿Hay consumo alto de memoria o CPU?
- ¿Qué procesos están consumiendo más recursos?
- ¿Qué IP tiene el equipo?
- ¿Qué puertos están escuchando?
- ¿Qué servicios de Windows están corriendo?
- ¿Hay algo obvio para revisar rápidamente?

---

## Para qué sirve

Este proyecto sirve para:

- Troubleshooting inicial.
- Soporte técnico interno.
- Diagnóstico rápido de una PC Windows.
- Recolección básica de evidencia ante incidentes.
- Documentar el estado de una computadora en un momento específico.
- Compartir un reporte simple con otro miembro del equipo de IT.

---

## Características principales

- Interfaz gráfica simple con Tkinter.
- Recolección local, sin enviar información a servidores externos.
- Reportes en Markdown.
- Soporte bilingüe para UI y reportes: inglés y español.
- Barra de progreso durante la recolección.
- Botón para abrir la carpeta de reportes.
- Resumen rápido del estado del equipo.
- Hallazgos principales al inicio del reporte.
- Recolección defensiva y de solo lectura.
- Pensada inicialmente para Windows.
- MVP chico, modular y mantenible.

---

## Información recolectada

La herramienta puede recolectar:

- Sistema operativo.
- Versión de Windows.
- Arquitectura.
- Hostname.
- Usuario actual.
- Fecha y hora de recolección.
- Uptime.
- Uso de CPU.
- Uso de RAM.
- Uso de disco.
- Procesos activos.
- Procesos con mayor consumo de memoria.
- Procesos con mayor consumo de CPU.
- Interfaces de red.
- IP local.
- Puertos TCP en escucha.
- Servicios de Windows.
- Estado y tipo de inicio de servicios.
- Salidas de comandos seguros como:
  - `ipconfig /all`
  - `route print`
  - `netstat -ano`

---

## Seguridad y alcance

Esta herramienta está diseñada para uso defensivo, soporte técnico y diagnóstico interno.

No realiza acciones destructivas.

No hace lo siguiente:

- No borra archivos.
- No mata procesos.
- No modifica servicios.
- No cambia configuraciones del sistema.
- No instala persistencia.
- No ejecuta acciones ocultas.
- No recolecta contraseñas.
- No recolecta tokens.
- No recolecta cookies.
- No recolecta claves privadas.
- No intenta evadir controles de seguridad.

Si algún dato no puede recolectarse por permisos, el reporte debería mostrarlo como `not available`, `access denied` o indicar que requiere permisos de administrador.

---

## Tecnologías utilizadas

| Herramienta | Uso |
|---|---|
| Python | Lenguaje principal del proyecto. |
| Tkinter | Interfaz gráfica local. |
| psutil | Recolección de CPU, memoria, disco, procesos y red. |
| subprocess | Ejecución de comandos seguros de Windows en modo lectura. |
| PowerShell | Recolección estructurada de servicios de Windows. |
| Markdown | Formato del reporte generado. |
| PyInstaller | Opción futura para empaquetar como `.exe`. |

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
    ├── system_info.py
    ├── processes.py
    ├── network.py
    ├── services.py
    ├── report.py
    ├── i18n.py
    └── ui.py
```

### Descripción rápida de módulos

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Punto de entrada de la aplicación. |
| `src/ui.py` | Interfaz gráfica con Tkinter. |
| `src/collectors.py` | Orquesta la recolección de evidencia. |
| `src/system_info.py` | Información básica del sistema y recursos. |
| `src/processes.py` | Procesos activos y consumo de CPU/RAM. |
| `src/network.py` | Interfaces de red, puertos y comandos de red. |
| `src/services.py` | Servicios de Windows usando PowerShell. |
| `src/analysis.py` | Genera resumen rápido y hallazgos principales. |
| `src/report.py` | Genera el reporte Markdown. |
| `src/i18n.py` | Traducciones para UI y reportes. |

---

## Instalación

Desde la raíz del proyecto, crear un entorno virtual:

```powershell
python -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, ejecutar:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

Actualizar `pip`:

```powershell
python -m pip install --upgrade pip
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

---

## Ejecución

Con el entorno virtual activo:

```powershell
python main.py
```

Esto abrirá la interfaz gráfica de la aplicación.

---

## Uso de la aplicación

1. Abrir la app con `python main.py`.
2. Seleccionar idioma: English o Español.
3. Presionar el botón de recolección.
4. Esperar a que finalice la barra de progreso.
5. Revisar el mensaje de reporte generado.
6. Abrir la carpeta `reports/` desde la app si se desea.

---

## Reportes generados

Los reportes se guardan dentro de:

```text
reports/
```

Ejemplos de nombres:

```text
reports/evidence-report-es-20260609-211305.md
reports/evidence-report-en-20260609-211305.md
```

El reporte incluye secciones como:

- Estado rápido del equipo.
- Hallazgos principales.
- Propósito y nota de seguridad.
- Información general del sistema.
- Uso de CPU, memoria y disco.
- Procesos con mayor consumo.
- Interfaces de red.
- Puertos en escucha.
- Servicios de Windows.
- Salidas crudas de comandos seguros.
- Advertencias de recolección.

---

## Limitaciones actuales

- Está pensado inicialmente para Windows.
- No es una herramienta forense avanzada.
- No reemplaza herramientas de monitoreo o seguridad corporativa.
- Algunos datos pueden requerir permisos elevados.
- Las salidas crudas de comandos de Windows pueden mostrar caracteres con encoding imperfecto según la configuración regional del sistema.
- El análisis automático usa reglas simples y conservadoras.

---

## Mejoras futuras

Ideas para futuras versiones:

- Agregar sección de próximos pasos sugeridos.
- Exportar también en HTML.
- Corregir decoding de salidas crudas de comandos Windows.
- Agregar recolección básica de Windows Event Logs.
- Agregar estado de Microsoft Defender.
- Agregar estado de BitLocker.
- Agregar listado resumido de programas instalados.
- Agregar hash del reporte generado.
- Permitir configurar qué módulos recolectar.
- Agregar modo CLI sin interfaz gráfica.
- Mejorar traducciones de hallazgos automáticos.
- Empaquetar como `.exe` con PyInstaller.

---

## Empaquetado futuro como .exe

Más adelante se puede empaquetar la aplicación con PyInstaller.

Instalar PyInstaller:

```powershell
pip install pyinstaller
```

Generar ejecutable:

```powershell
pyinstaller --onefile --windowed --name it-evidence-collector main.py
```

El ejecutable quedará en:

```text
dist/
```

Recomendación: validar primero el MVP ejecutándolo con Python antes de empaquetarlo.

---

## Comandos útiles de Git

Ver cambios:

```bash
git status
```

Agregar archivos:

```bash
git add .
```

Crear commit:

```bash
git commit -m "Update project documentation"
```

Commit sugerido para este README:

```bash
git commit -m "Add simple project README"
```
