@echo off
REM Script de build para Windows usando PyInstaller
REM Empaqueta la app incluyendo recursos críticos y config de ejemplo

REM Activar entorno virtual si existe
IF EXIST ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
)

REM Instalar PyInstaller si no está
pip show pyinstaller >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    pip install pyinstaller
)

REM Ejecutar PyInstaller con recursos incluidos
pyinstaller --name stock_app --onefile --noconfirm ^
  --add-data "core/config.example.py;core" ^
  --add-data "resources/icons;resources/icons" ^
  --add-data "resources/qss;resources/qss" ^
  --add-data "static;static" ^
  --add-data "templates;templates" ^
  --add-data "themes;themes" ^
  --add-data "config/theme_config.json;config" ^
  --add-data "config/columnas;config/columnas" ^
  --add-data "config/privado/.env;config/privado" ^
  main.py

REM Mover ejecutable a dist/
IF EXIST dist\stock_app.exe (
    echo Build exitoso: dist\stock_app.exe
) ELSE (
    echo Error en el build. Revisa el log de PyInstaller.
)
