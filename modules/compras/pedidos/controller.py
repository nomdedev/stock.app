from PyQt6.QtWidgets import QTableWidgetItem
from core.database import DataAccessLayer
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from core.logger import log_error

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                usuario = getattr(controller, 'usuario_actual', None)
                usuario_id = usuario['id'] if usuario and 'id' in usuario else None
                ip = usuario.get('ip', '') if usuario else ''
                if not usuario or not usuario_model or not auditoria_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                if not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    detalle = f"{accion} - denegado"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return None
                try:
                    resultado = func(controller, *args, **kwargs)
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    detalle = f"{accion} - error: {e}"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_compras = PermisoAuditoria('compras')

class ComprasPedidosController:
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None, inventario_model=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.auditoria_model = AuditoriaModel(db_connection)
        self.usuarios_model = usuarios_model
        self.dal = DataAccessLayer(db_connection)
        self.inventario_model = inventario_model
        self.view.boton_crear.clicked.connect(self.crear_pedido)
        self.view.boton_ver_detalles.clicked.connect(self.ver_detalles_pedido)
        self.view.boton_cargar_presupuesto.clicked.connect(self.cargar_presupuesto)

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'compras', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    @permiso_auditoria_compras('crear')
    def crear_pedido(self):
        try:
            campos = {
                "cliente": self.view.cliente_input.text(),
                "producto": self.view.producto_input.text(),
                "cantidad": self.view.cantidad_input.text(),
                "fecha": self.view.fecha_input.text()
            }

            if not all(campos.values()):
                self.view.label.setText("Por favor, complete todos los campos.")
                self._registrar_evento_auditoria('crear', 'campos incompletos', 'error')
                return

            self.model.crear_pedido(tuple(campos.values()))
            self.view.label.setText("Pedido creado exitosamente.")
            self._registrar_evento_auditoria('crear', 'pedido creado', 'éxito')
        except Exception as e:
            log_error(f"Error al crear pedido: {e}")
            self.view.label.setText("Error al crear el pedido.")
            self._registrar_evento_auditoria('crear', f"error: {e}", 'error')

    @permiso_auditoria_compras('actualizar')
    def actualizar_pedido(self, id_pedido, datos, fecha_actualizacion):
        try:
            self.dal.actualizar_registro("pedidos", id_pedido, datos, fecha_actualizacion)
            self.view.label.setText("Pedido actualizado exitosamente.")
            self._registrar_evento_auditoria('actualizar', f"pedido {id_pedido} actualizado", 'éxito')
        except Exception as e:
            log_error(f"Error al actualizar pedido: {e}")
            self.view.label.setText(f"Error: {str(e)}")
            self._registrar_evento_auditoria('actualizar', f"error: {e}", 'error')

    @permiso_auditoria_compras('ver_detalles')
    def ver_detalles_pedido(self):
        fila_seleccionada = self.view.tabla_pedidos.currentRow()
        if fila_seleccionada == -1:
            self.view.label.setText("Seleccione un pedido para ver detalles.")
            self._registrar_evento_auditoria('ver_detalles', 'sin selección', 'error')
            return

        id_pedido = self.view.tabla_pedidos.item(fila_seleccionada, 0).text()
        detalles = self.model.obtener_detalle_pedido(id_pedido)
        self.view.tabla_detalle_pedido.setRowCount(len(detalles))
        for row, detalle in enumerate(detalles):
            for col, value in enumerate(detalle):
                self.view.tabla_detalle_pedido.setItem(row, col, QTableWidgetItem(str(value)))
        self.view.tabla_detalle_pedido.resizeColumnsToContents()
        self._registrar_evento_auditoria('ver_detalles', f"pedido {id_pedido} detalles mostrados", 'éxito')

    @permiso_auditoria_compras('cargar_presupuesto')
    def cargar_presupuesto(self):
        try:
            fila_seleccionada = self.view.tabla_pedidos.currentRow()
            if fila_seleccionada == -1:
                self.view.label.setText("Seleccione un pedido para cargar el presupuesto.")
                self._registrar_evento_auditoria('cargar_presupuesto', 'sin selección', 'error')
                return

            id_pedido = self.view.tabla_pedidos.item(fila_seleccionada, 0).text()
            presupuesto = self.view.obtener_datos_presupuesto()

            if not presupuesto:
                self.view.label.setText("Error: Datos incompletos para cargar el presupuesto.")
                self._registrar_evento_auditoria('cargar_presupuesto', 'datos incompletos', 'error')
                return

            self.model.agregar_presupuesto((id_pedido, *presupuesto.values()))
            self.view.label.setText(f"Presupuesto cargado para el pedido {id_pedido}.")
            self._registrar_evento_auditoria('cargar_presupuesto', f"presupuesto cargado para pedido {id_pedido}", 'éxito')
        except Exception as e:
            log_error(f"Error al cargar presupuesto: {e}")
            self.view.label.setText("Error al cargar el presupuesto.")
            self._registrar_evento_auditoria('cargar_presupuesto', f"error: {e}", 'error')

    @permiso_auditoria_compras('comparar_presupuestos')
    def comparar_presupuestos(self, id_pedido):
        try:
            presupuestos = self.model.obtener_presupuestos_por_pedido(id_pedido)
            if presupuestos:
                comparacion = sorted(presupuestos, key=lambda x: x[5])
                self.view.mostrar_comparacion_presupuestos(comparacion)
                self._registrar_evento_auditoria('comparar_presupuestos', f"pedido {id_pedido} presupuestos comparados", 'éxito')
            else:
                self.view.label.setText("No hay presupuestos para comparar.")
                self._registrar_evento_auditoria('comparar_presupuestos', f"pedido {id_pedido} sin presupuestos", 'error')
        except Exception as e:
            log_error(f"Error al comparar presupuestos: {e}")
            self.view.label.setText("Error al comparar los presupuestos.")
            self._registrar_evento_auditoria('comparar_presupuestos', f"error: {e}", 'error')

    @permiso_auditoria_compras('sincronizar_inventario')
    def sincronizar_pedido_con_inventario(self, id_pedido):
        try:
            detalles_pedido = self.model.obtener_detalle_pedido(id_pedido)
            if not hasattr(self, 'inventario_model') or self.inventario_model is None:
                self.view.label.setText("Error: No se puede sincronizar, inventario_model no está definido.")
                self._registrar_evento_auditoria('sincronizar_inventario', 'inventario_model no definido', 'error')
                return
            for detalle in detalles_pedido:
                id_item = detalle[1]
                cantidad = detalle[2]
                self.inventario_model.actualizar_stock(id_item, -cantidad)
            self.view.label.setText(f"Pedido {id_pedido} sincronizado con el inventario.")
            self._registrar_evento_auditoria('sincronizar_inventario', f"pedido {id_pedido} sincronizado", 'éxito')
        except Exception as e:
            log_error(f"Error al sincronizar pedido con inventario: {e}")
            self.view.label.setText("Error al sincronizar el pedido con el inventario.")
            self._registrar_evento_auditoria('sincronizar_inventario', f"error: {e}", 'error')

    @permiso_auditoria_compras('cargar_pedidos')
    def cargar_pedidos(self):
        try:
            pedidos = self.model.obtener_todos_pedidos()
            self.view.tabla_pedidos.setRowCount(len(pedidos))
            for row, pedido in enumerate(pedidos):
                for col, value in enumerate(pedido):
                    self.view.tabla_pedidos.setItem(row, col, QTableWidgetItem(str(value)))
            self.view.tabla_pedidos.resizeColumnsToContents()
            self.view.label.setText("Pedidos cargados correctamente.")
            self._registrar_evento_auditoria('cargar_pedidos', 'todos los pedidos cargados', 'éxito')
        except Exception as e:
            log_error(f"Error al cargar pedidos: {e}")
            self.view.label.setText("Error al cargar los pedidos.")
            self._registrar_evento_auditoria('cargar_pedidos', f"error: {e}", 'error')
