#!/bin/bash
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error durante la instalación de dependencias."
    exit 1
fi
echo "Instalación y actualización de dependencias completada."
