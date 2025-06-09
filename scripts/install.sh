#!/bin/bash
# Script de instalación para MPS Inventario App (Linux/Mac)
# Instala todas las dependencias necesarias usando requirements.txt

cd "$(dirname "$0")"
cd ..

# Crear entorno virtual (opcional, recomendado)
# python3 -m venv venv
# source venv/bin/activate

# Instalar dependencias con --user si no hay entorno virtual
python3 -m pip install --user --upgrade pip
python3 -m pip install --user --upgrade -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Instalación completada correctamente."
else
    echo "Hubo un error durante la instalación de dependencias."
fi
