@echo off
REM Script de instalación para MPS Inventario App
REM Instala todas las dependencias necesarias usando requirements.txt

cd /d %~dp0

REM Crear entorno virtual (opcional, recomendado)
REM python -m venv venv
REM call venv\Scripts\activate

REM Instalar dependencias con --user si no hay entorno virtual
pip install --user --upgrade pip
pip install --user --upgrade -r ..\requirements.txt

REM Mensaje final
if %errorlevel%==0 (
    echo Instalación completada correctamente.
) else (
    echo Hubo un error durante la instalación de dependencias.
)
pause
