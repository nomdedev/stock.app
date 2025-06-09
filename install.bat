@echo off
python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt
if %errorlevel% neq 0 (
    echo Error durante la instalación de dependencias.
    pause
    exit /b %errorlevel%
)
echo Instalación y actualización de dependencias completada.
pause
