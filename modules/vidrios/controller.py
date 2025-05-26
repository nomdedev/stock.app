from PyQt6.QtWidgets import QTableWidgetItem
from modules.auditoria.model import AuditoriaModel

class VidriosController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.auditoria_model = AuditoriaModel(db_connection)
        # ...existing code...

    def some_method(self):
        # Example method
        pass

    def actualizar_por_obra(self, datos_obra):
        print(f"[LOG ACCIÓN] Ejecutando acción 'actualizar_por_obra' en módulo 'vidrios' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido') if self.usuario_actual else 'desconocido'}")
        """
        Método para refrescar la vista de vidrios cuando se agrega una nueva obra.
        Se puede usar para actualizar la lista de vidrios, pedidos pendientes, etc.
        """
        self.refrescar_vidrios()
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(f"Vidrios actualizados automáticamente por la obra '{datos_obra.get('nombre','')}'.", tipo='info')
        print("[LOG ACCIÓN] Acción 'actualizar_por_obra' en módulo 'vidrios' finalizada con éxito.")

    def refrescar_vidrios(self):
        print(f"[LOG ACCIÓN] Ejecutando acción 'refrescar_vidrios' en módulo 'vidrios' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido') if self.usuario_actual else 'desconocido'}")
        """
        Refresca la tabla de vidrios desde la base de datos.
        """
        try:
            vidrios = self.model.obtener_vidrios()
            if hasattr(self.view, 'tabla_vidrios') and hasattr(self.view, 'vidrios_headers'):
                self.view.tabla_vidrios.setRowCount(len(vidrios))
                for fila, vidrio in enumerate(vidrios):
                    for columna, header in enumerate(self.view.vidrios_headers):
                        valor = vidrio.get(header, "") if isinstance(vidrio, dict) else vidrio[columna]
                        self.view.tabla_vidrios.setItem(fila, columna, QTableWidgetItem(str(valor)))
            print("[LOG ACCIÓN] Acción 'refrescar_vidrios' en módulo 'vidrios' finalizada con éxito.")
        except Exception as e:
            print(f"[LOG ACCIÓN] Error en acción 'refrescar_vidrios' en módulo 'vidrios': {e}")
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Error al refrescar vidrios: {e}", tipo='error')

# Nota: Para integración en tiempo real, conectar así desde el controlador principal:
# self.obras_view.obra_agregada.connect(self.vidrios_controller.actualizar_por_obra)
# Esto permitirá que al agregar una obra, la tabla de vidrios se refresque automáticamente.