import pytest
from PyQt6.QtWidgets import QApplication
from modules.obras.view import ObrasView, AltaObraDialog, EditObraDialog
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture(scope="module")
def app():
    import sys
    return QApplication.instance() or QApplication(sys.argv)

class DummyController:
    def __init__(self):
        self.obras = []
        self.mensajes = []
    def alta_obra(self, datos):
        # Simula validación y alta
        if not datos["nombre"] or not datos["cliente"]:
            self.mensajes.append(("Nombre y cliente no pueden estar vacíos.", "error"))
            raise ValueError("Nombre y cliente no pueden estar vacíos.")
        if len(datos["nombre"]) > 100:
            self.mensajes.append(("Nombre muy largo (máx 100 caracteres)", "error"))
            raise ValueError("Nombre muy largo (máx 100 caracteres)")
        if len(datos["cliente"]) > 100:
            self.mensajes.append(("Cliente muy largo (máx 100 caracteres)", "error"))
            raise ValueError("Cliente muy largo (máx 100 caracteres)")
        if not all(c.isalnum() or c.isspace() for c in datos["nombre"]):
            self.mensajes.append(("Nombre solo puede contener letras, números y espacios", "error"))
            raise ValueError("Nombre solo puede contener letras, números y espacios")
        if not all(c.isalnum() or c.isspace() for c in datos["cliente"]):
            self.mensajes.append(("Cliente solo puede contener letras, números y espacios", "error"))
            raise ValueError("Cliente solo puede contener letras, números y espacios")
        fecha_med = datetime.strptime(datos["fecha_medicion"], "%Y-%m-%d")
        fecha_ent = datetime.strptime(datos["fecha_entrega"], "%Y-%m-%d")
        if fecha_ent < fecha_med:
            self.mensajes.append(("La fecha de entrega no puede ser anterior a la fecha de medición", "error"))
            raise ValueError("La fecha de entrega no puede ser anterior a la fecha de medición")
        self.obras.append(datos)
        self.mensajes.append(("Obra agregada exitosamente", "exito"))
        return len(self.obras)
    def editar_obra(self, index, datos):
        # Simula edición de obra
        if index < 0 or index >= len(self.obras):
            self.mensajes.append(("Índice de obra no válido", "error"))
            raise IndexError("Índice de obra no válido")
        self.obras[index] = datos
        self.mensajes.append(("Obra editada exitosamente", "exito"))
    def eliminar_obra(self, index):
        # Simula eliminación de obra
        if index < 0 or index >= len(self.obras):
            self.mensajes.append(("Índice de obra no válido", "error"))
            raise IndexError("Índice de obra no válido")
        self.obras.pop(index)
        self.mensajes.append(("Obra eliminada exitosamente", "exito"))

@pytest.mark.parametrize("nombre,cliente,fecha_med,fecha_ent,espera_exito", [
    ("ObraTest", "ClienteTest", "2025-06-10", "2025-06-15", True),
    ("", "ClienteTest", "2025-06-10", "2025-06-15", False),
    ("ObraTest", "", "2025-06-10", "2025-06-15", False),
    ("ObraTest", "ClienteTest", "2025-06-10", "2025-06-05", False),
    ("A"*101, "ClienteTest", "2025-06-10", "2025-06-15", False),
    ("ObraTest", "B"*101, "2025-06-10", "2025-06-15", False),
    ("Obra@123", "ClienteTest", "2025-06-10", "2025-06-15", False),
    ("ObraTest", "Cliente#1", "2025-06-10", "2025-06-15", False),
])
def test_formulario_alta_obra_interaccion(app, nombre, cliente, fecha_med, fecha_ent, espera_exito):
    view = ObrasView()
    controller = DummyController()
    view.set_controller(controller)
    dialog = AltaObraDialog(view)
    dialog.nombre_input.setText(nombre)
    dialog.cliente_input.setText(cliente)
    dialog.fecha_medicion_input.setDate(datetime.strptime(fecha_med, "%Y-%m-%d").date())
    dialog.fecha_entrega_input.setDate(datetime.strptime(fecha_ent, "%Y-%m-%d").date())
    # Simula click en guardar
    try:
        dialog.guardar_obra()
        if espera_exito:
            assert controller.mensajes[-1][1] == "exito"
        else:
            assert False, "Se esperaba error pero no ocurrió"
    except Exception:
        if espera_exito:
            assert False, "Se esperaba éxito pero ocurrió error"
        else:
            assert controller.mensajes[-1][1] == "error"

# Test de edición de obra (formulario EditObraDialog)
def test_formulario_editar_obra_interaccion(app):
    view = ObrasView()
    controller = DummyController()
    # Cargar una obra inicial
    datos_obra = {"nombre": "Obra1", "cliente": "Cliente1", "fecha_medicion": "2025-06-10", "fecha_entrega": "2025-06-15"}
    controller.obras.append(datos_obra.copy())
    view.set_controller(controller)
    dialog = EditObraDialog(view, datos_obra)
    # Modificar datos
    dialog.nombre_input.setText("ObraEditada")
    dialog.cliente_input.setText("ClienteEditado")
    dialog.fecha_medicion_input.setDate(datetime.strptime("2025-06-12", "%Y-%m-%d").date())
    dialog.fecha_entrega_input.setDate(datetime.strptime("2025-06-20", "%Y-%m-%d").date())
    # Simula click en guardar
    dialog.guardar_obra()
    # Simula llamada a controller
    controller.editar_obra(0, {
        "nombre": dialog.nombre_input.text(),
        "cliente": dialog.cliente_input.text(),
        "fecha_medicion": dialog.fecha_medicion_input.date().toString("yyyy-MM-dd"),
        "fecha_entrega": dialog.fecha_entrega_input.date().toString("yyyy-MM-dd")
    })
    assert controller.mensajes[-1][1] == "exito"
    assert controller.obras[0]["nombre"] == "ObraEditada"
    assert controller.obras[0]["cliente"] == "ClienteEditado"

# Test de eliminación de obra (simulación de interacción)
def test_formulario_eliminar_obra_interaccion(app):
    view = ObrasView()
    controller = DummyController()
    # Cargar una obra inicial
    datos_obra = {"nombre": "Obra1", "cliente": "Cliente1", "fecha_medicion": "2025-06-10", "fecha_entrega": "2025-06-15"}
    controller.obras.append(datos_obra.copy())
    view.set_controller(controller)
    # Simula eliminación
    controller.eliminar_obra(0)
    assert controller.mensajes[-1][1] == "exito"
    assert len(controller.obras) == 0
