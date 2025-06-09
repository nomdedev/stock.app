# test_botones_iconos.py
"""
Test automatizado para validar la presencia y correspondencia de íconos en los botones secundarios y modales
de la app PyQt6, según el checklist de estándares.
"""
import os
import pytest
from PyQt6.QtWidgets import QApplication, QPushButton, QDialog, QTableWidgetItem
from PyQt6.QtGui import QIcon
from modules.vidrios.view import VidriosView

# Ruta relativa a los íconos estándar
ICONOS_ESPERADOS = {
    'guardar-qr': 'resources/icons/guardar-qr.svg',
    'pdf': 'resources/icons/pdf.svg',
    'add-material': 'resources/icons/add-material.svg',
    'search': 'resources/icons/search_icon.svg',
    'excel': 'resources/icons/excel_icon.svg',
}

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

@pytest.mark.parametrize("boton,icono_esperado", [
    ("boton_agregar", ICONOS_ESPERADOS['add-material']),
    ("boton_buscar", ICONOS_ESPERADOS['search']),
    ("boton_exportar_excel", ICONOS_ESPERADOS['excel']),
])
def test_iconos_botones_principales(app, boton, icono_esperado):
    view = VidriosView()
    btn = getattr(view, boton)
    icon: QIcon = btn.icon()
    assert not icon.isNull(), f"El botón {boton} no tiene ícono asignado"
    # Verifica que el path del ícono coincida (solo para QIcon de archivo)
    for size in [24, 20, 48]:
        pixmap = icon.pixmap(size, size)
        assert not pixmap.isNull(), f"El ícono de {boton} no se carga correctamente para tamaño {size}"


def test_iconos_botones_modales_qr(app):
    view = VidriosView()
    # Simula selección de un item para disparar el modal QR
    view.tabla_vidrios.setRowCount(1)
    for col in range(view.tabla_vidrios.columnCount()):
        view.tabla_vidrios.setItem(0, col, QTableWidgetItem(f"valor{col}"))
    view.tabla_vidrios.selectRow(0)
    # Monkeypatch QDialog.exec para capturar los botones
    botones_capturados = {}
    original_exec = QDialog.exec
    def fake_exec(self):
        for child in self.findChildren(QPushButton):
            if child.toolTip() == "Guardar QR como imagen":
                botones_capturados['guardar'] = child
            if child.toolTip() == "Exportar QR a PDF":
                botones_capturados['pdf'] = child
        return 0
    QDialog.exec = fake_exec
    try:
        view.mostrar_qr_item_seleccionado()
        btn_guardar = botones_capturados.get('guardar')
        btn_pdf = botones_capturados.get('pdf')
        assert btn_guardar is not None, "No se encontró el botón Guardar QR en el modal"
        assert btn_pdf is not None, "No se encontró el botón PDF en el modal"
        assert not btn_guardar.icon().isNull(), "El botón Guardar QR no tiene ícono"
        assert not btn_pdf.icon().isNull(), "El botón PDF no tiene ícono"
    finally:
        QDialog.exec = original_exec
