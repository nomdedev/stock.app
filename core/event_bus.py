from PyQt6.QtCore import QObject, pyqtSignal

class EventBus(QObject):
    """
    Bus de eventos centralizado para señales entre módulos principales (Obras, Inventario, Vidrios, etc).
    Permite desacoplar la lógica de actualización en tiempo real y facilita los tests de integración.
    """
    obra_agregada = pyqtSignal(dict)  # dict con datos de la obra/pedido
    pedido_actualizado = pyqtSignal(dict)
    stock_modificado = pyqtSignal(dict)
    vidrio_asignado = pyqtSignal(dict)
    # Agregar aquí otras señales relevantes para integración cruzada

# Instancia global para importar en cualquier módulo
# Ejemplo de uso: from core.event_bus import event_bus

event_bus = EventBus()
