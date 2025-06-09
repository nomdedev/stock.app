import os
import glob
import re
from PyQt6.QtGui import QIcon
from utils.icon_loader import get_icon

ICON_DIR = os.path.join(os.path.dirname(__file__), '../resources/icons')

# Lista de botones y el nombre de ícono esperado (según checklist)
BOTONES_ICONOS = [
    ("vidrios.boton_agregar", "add-material"),
    ("vidrios.boton_buscar", "search_icon"),
    ("vidrios.boton_exportar_excel", "excel_icon"),
    ("usuarios.boton_agregar", "agregar-user"),
    ("pedidos.boton_agregar", "add-material"),
    ("pedidos.btn_guardar", "guardar-qr"),
    ("pedidos.btn_pdf", "pdf"),
    ("pedidos.btn_confirmar", "finish-check"),
    ("pedidos.btn_cancelar", "close"),
    ("auditoria.boton_agregar", "add-material"),
    ("auditoria.boton_ver_logs", "search_icon"),
    ("auditoria.btn_guardar", "guardar-qr"),
    ("auditoria.btn_pdf", "pdf"),
    ("auditoria.btn_cerrar", "close"),
]

EXTS = [".svg", ".png"]

def icono_existe(nombre):
    for ext in EXTS:
        if os.path.isfile(os.path.join(ICON_DIR, nombre + ext)):
            return True
    return False

def test_botones_tienen_icono():
    faltantes = []
    for boton, icono in BOTONES_ICONOS:
        if not icono_existe(icono):
            faltantes.append((boton, icono))
    assert not faltantes, f"Faltan íconos para los siguientes botones: {faltantes}"

def test_get_icon_no_vacio():
    # Verifica que get_icon devuelva un QIcon válido para cada ícono esperado
    for _, icono in BOTONES_ICONOS:
        icon = get_icon(icono)
        assert not icon.isNull(), f"get_icon('{icono}') devuelve un QIcon vacío"
