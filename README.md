# IT Evidence Collector

**IT Evidence Collector** es una aplicación de escritorio simple y local para Windows, pensada para soporte técnico, troubleshooting e investigación inicial ante incidentes o comportamientos extraños en una computadora.

El objetivo del proyecto es construir un MVP práctico, chico y mantenible. No busca ser una herramienta forense avanzada.

## Qué hace

La herramienta permite iniciar una recolección básica de evidencia del sistema desde una interfaz visual simple y generar automáticamente un reporte en formato Markdown dentro de la carpeta `reports/`.

Información que recolecta:

- Sistema operativo
- Hostname
- Usuario actual
- Fecha y hora de recolección
- Uptime
- Uso de CPU
- Uso de RAM
- Uso de disco
- Procesos activos
- Procesos más pesados por memoria y CPU
- Interfaces de red
- Puertos abiertos en escucha
- Salida de comandos seguros como `ipconfig /all`, `route print` y `netstat -ano`
- Servicios de Windows mediante `sc query state= all`

## Seguridad

Esta herramienta está pensada únicamente para uso defensivo, diagnóstico interno y soporte técnico.

No realiza acciones destructivas.

No hace lo siguiente:

- No borra archivos
- No mata procesos
- No modifica servicios
- No cambia configuraciones del sistema
- No instala persistencia
- No ejecuta funciones ocultas
- No recolecta contraseñas
- No recolecta tokens
- No recolecta cookies
- No recolecta claves privadas

Si algún dato no puede recolectarse por permisos, el reporte debería mostrarlo como `not available` o indicar que requiere permisos de administrador.

## Limitaciones

Esta herramienta no reemplaza:

- Una solución EDR
- Un SIEM
- Un antivirus
- Un proceso forense formal
- Una investigación de seguridad avanzada

Es una herramienta simple para una primera revisión técnica.

## Requisitos

- Windows
- Python 3.10 o superior recomendado
- Entorno virtual de Python
- Dependencias de `requirements.txt`

## Instalación

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt