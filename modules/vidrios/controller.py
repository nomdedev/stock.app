from PyQt6.QtWidgets import QTableWidgetItem
from modules.auditoria.model import AuditoriaModel
from core.logger import Logger

class VidriosController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.auditoria_model = AuditoriaModel(db_connection)
        # --- INTEGRACIÓN Y TRAZABILIDAD DE PEDIDOS POR OBRA (DOCUMENTACIÓN) ---
        #
        # Este controlador implementa la lógica para:
        # - Registrar y actualizar pedidos de vidrios por obra.
        # - Consultar el estado de pedidos de vidrios por obra y usuario.
        # - Registrar auditoría de cada acción relevante.
        # - Permitir la integración con otros módulos (Inventario, Herrajes, Producción, Contabilidad, Logística).
        #
        # Checklist de integración y pendientes:
        # [x] Registrar pedido de vidrios por obra y usuario.
        # [x] Actualizar estado de pedido de vidrios.
        # [x] Consultar pedidos por usuario y por obra.
        # [x] Registrar auditoría de cada acción.
        # [ ] Integrar consulta de estado de pedidos de otros módulos (inventario, herrajes) en la vista de obras.
        # [ ] Impedir pedidos a obras inexistentes (validar contra módulo Obras).
        # [ ] Unificar lógica de pedidos en Inventario y Herrajes (backend y controlador).
        # [ ] Exponer métodos para Producción y Logística para saber cuándo una obra está lista para fabricar/entregar.
        # [ ] Integrar con Contabilidad para registrar y actualizar pagos de pedidos.
        # [ ] Documentar excepciones y justificaciones en docs/estandares_visuales.md y docs/flujo_obras_material_vidrios.md.
        # [ ] Implementar tests automáticos de integración y feedback visual.
        #
        # Ver también: docs/flujo_obras_material_vidrios.md y docs/checklist_mejoras_uiux_por_modulo.md

    def some_method(self):
        # Example method
        pass

    def actualizar_por_obra(self, datos_obra):
        Logger().info(f"[LOG ACCIÓN] Ejecutando acción 'actualizar_por_obra' en módulo 'vidrios' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido') if self.usuario_actual else 'desconocido'}")
        """
        Método para refrescar la vista de vidrios cuando se agrega una nueva obra.
        Se puede usar para actualizar la lista de vidrios, pedidos pendientes, etc.
        """
        self.refrescar_vidrios()
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(f"Vidrios actualizados automáticamente por la obra '{datos_obra.get('nombre','')}'.", tipo='info')
        Logger().info("[LOG ACCIÓN] Acción 'actualizar_por_obra' en módulo 'vidrios' finalizada con éxito.")

    def refrescar_vidrios(self):
        Logger().info(f"[LOG ACCIÓN] Ejecutando acción 'refrescar_vidrios' en módulo 'vidrios' por usuario: {getattr(self.usuario_actual, 'username', 'desconocido') if self.usuario_actual else 'desconocido'}")
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
            Logger().info("[LOG ACCIÓN] Acción 'refrescar_vidrios' en módulo 'vidrios' finalizada con éxito.")
        except Exception as e:
            Logger().error(f"[LOG ACCIÓN] Error en acción 'refrescar_vidrios' en módulo 'vidrios': {e}")
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Error al refrescar vidrios: {e}", tipo='error')

    def cargar_resumen_obras(self):
        obras = self.model.obtener_obras_con_estado_pedido()
        self.view.mostrar_resumen_obras(obras)

    def cargar_pedidos_usuario(self, usuario):
        pedidos = self.model.obtener_pedidos_por_usuario(usuario)
        self.view.mostrar_pedidos_usuario(pedidos)

    def mostrar_detalle_pedido(self, id_obra, id_vidrio):
        detalle = self.model.obtener_detalle_pedido(id_obra, id_vidrio)
        self.view.mostrar_detalle_pedido(detalle)

    def actualizar_estado_pedido(self, id_obra, nuevo_estado):
        self.model.actualizar_estado_pedido(id_obra, nuevo_estado)
        self.auditoria_model.registrar_evento(
            usuario_id=getattr(self.usuario_actual, 'id', self.usuario_actual),
            modulo="Vidrios",
            tipo_evento="Actualizar estado pedido",
            detalle=f"Actualizó estado de pedido de obra {id_obra} a {nuevo_estado}",
            ip_origen="127.0.0.1"
        )
        self.cargar_resumen_obras()

    def validar_obra_existente(self, id_obra, obras_model):
        """
        Valida que la obra exista en el sistema antes de permitir registrar un pedido.
        Retorna True si existe, False si no.
        """
        if not id_obra:
            return False
        try:
            # El modelo de obras debe tener un método obtener_obra_por_id
            obra = obras_model.obtener_obra_por_id(id_obra)
            return obra is not None
        except Exception as e:
            Logger().error(f"[ERROR] No se pudo validar existencia de obra: {e}")
            return False

    def guardar_pedido_vidrios(self, datos, obras_model=None):
        """
        Guarda el pedido de vidrios solo si la obra existe (validación cruzada).
        Si obras_model es None, no valida (para compatibilidad).
        """
        id_obra = datos.get('id_obra') if isinstance(datos, dict) else None
        if obras_model is not None and not self.validar_obra_existente(id_obra, obras_model):
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"No se puede registrar el pedido: la obra {id_obra} no existe.", tipo='error')
            return
        self.model.guardar_pedido_vidrios(datos)
        self.auditoria_model.registrar_evento(
            usuario_id=self.usuario_actual,
            modulo="Vidrios",
            tipo_evento="Guardar pedido vidrios",
            detalle=f"Guardó pedido de vidrios: {datos}",
            ip_origen="127.0.0.1"
        )
        self.cargar_pedidos_usuario(self.usuario_actual)

    def reservar_vidrio(self, usuario, id_obra, id_vidrio, cantidad):
        """
        Reserva vidrio para una obra, validando que la obra exista antes de registrar el pedido.
        """
        from modules.obras.model import ObrasModel
        obras_model = ObrasModel(self.model.db)
        if not obras_model.existe_obra_por_id(id_obra):
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje("No existe una obra con ese ID. No se puede reservar vidrio.", tipo='error')
            self.auditoria_model.registrar_evento(
                usuario, "Vidrios", "reserva_vidrio", f"Intento de reserva a obra inexistente: {id_obra}", "error"
            )
            return False
        return self.model.reservar_vidrio(usuario, id_obra, id_vidrio, cantidad)

# Nota: Para integración en tiempo real, conectar así desde el controlador principal:
# self.obras_view.obra_agregada.connect(self.vidrios_controller.actualizar_por_obra)
# Esto permitirá que al agregar una obra, la tabla de vidrios se refresque automáticamente.