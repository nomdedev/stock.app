# Documentación de test agregada el 12/06/2025:
# Este test cubre el alta de obra desde la UI y su reflejo inmediato en la tabla de obras.
# - Simula el flujo real de usuario: abre el diálogo, completa campos obligatorios, guarda y verifica la tabla.
# - Valida feedback visual.
# - Cumple con el checklist de UI/UX y QA documentado en docs/checklists/checklist_mejoras_ui_general.md y README.md.
# - Si el flujo de alta cambia, actualizar este test y la documentación.
# Última revisión: 12/06/2025.
# [COMPLETADO 12/06/2025] Este test valida el alta de obra y reflejo en tabla, cumpliendo el checklist de UI/UX y QA.
# Verificado y documentado en README.md y docs/checklists/checklist_mejoras_ui_general.md.

import pytest
from PyQt6.QtWidgets import QApplication
from modules.obras.view import ObrasView

def test_alta_obra_y_reflejo_en_tabla(qtbot):
    """
    Test de UI: simula el alta de una obra desde el formulario y verifica que se refleja en la tabla de obras.
    """
    app = QApplication.instance() or QApplication([])
    view = ObrasView(usuario_actual="testuser", db_connection=None)
    qtbot.addWidget(view)

    # Simula abrir el diálogo de alta y completar los campos obligatorios
    dialogo = view.mostrar_dialogo_alta()
    assert dialogo is not None, "No se pudo obtener el diálogo de alta de obra. Ajusta mostrar_dialogo_alta para test."

    # Completar solo los campos obligatorios
    if hasattr(dialogo, 'nombre_input'):
        dialogo.nombre_input.setText("Obra Test UI")
    if hasattr(dialogo, 'cliente_input'):
        dialogo.cliente_input.setText("Cliente UI")

    # Buscar el botón guardar de forma robusta
    from PyQt6.QtWidgets import QPushButton
    boton_guardar = getattr(dialogo, 'boton_guardar', None) or dialogo.findChild(QPushButton, "boton_guardar")
    assert boton_guardar is not None, "No se encontró el botón guardar en el diálogo"
    qtbot.mouseClick(boton_guardar, 1)

    # Verificar que la obra aparece en la tabla
    tabla = view.tabla_obras
    nombres = []
    clientes = []
    for row in range(tabla.rowCount()):
        item_nombre = tabla.item(row, 0)
        item_cliente = tabla.item(row, 1)
        if item_nombre is not None:
            nombres.append(item_nombre.text())
        if item_cliente is not None:
            clientes.append(item_cliente.text())
    assert "Obra Test UI" in nombres, f"La obra no se reflejó en la tabla: {nombres}"
    assert "Cliente UI" in clientes, f"El cliente no se reflejó en la tabla: {clientes}"

    # Opcional: verificar feedback visual
    assert view.label_feedback.isVisible() or view.label_feedback.text() != ""
