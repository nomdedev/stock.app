from PyQt6.QtWidgets import QTableWidgetItem
from core.database import DataAccessLayer
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', UsuariosModel())
                auditoria_model = getattr(controller, 'auditoria_model', AuditoriaModel())
                usuario = getattr(controller, 'usuario_actual', None)
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                resultado = func(controller, *args, **kwargs)
                auditoria_model.registrar_evento(usuario, self.modulo, accion)
                return resultado
            return wrapper
        return decorador

permiso_auditoria_compras = PermisoAuditoria('compras')

class PedidosController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel()
        self.auditoria_model = AuditoriaModel()
        self.dal = DataAccessLayer(db_connection)
        self.view.boton_crear.clicked.connect(self.crear_pedido)
        self.view.boton_ver_detalles.clicked.connect(self.ver_detalles_pedido)
        self.view.boton_cargar_presupuesto.clicked.connect(self.cargar_presupuesto)

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
                return

            self.model.crear_pedido(tuple(campos.values()))
            self.view.label.setText("Pedido creado exitosamente.")
        except Exception as e:
            print(f"Error al crear pedido: {e}")
            self.view.label.setText("Error al crear el pedido.")

    @permiso_auditoria_compras('actualizar')
    def actualizar_pedido(self, id_pedido, datos, fecha_actualizacion):
        try:
            self.dal.actualizar_registro("pedidos", id_pedido, datos, fecha_actualizacion)
            self.view.label.setText("Pedido actualizado exitosamente.")
        except Exception as e:
            self.view.label.setText(f"Error: {str(e)}")

    @permiso_auditoria_compras('ver_detalles')
    def ver_detalles_pedido(self):
        fila_seleccionada = self.view.tabla_pedidos.currentRow()
        if fila_seleccionada == -1:
            return

        id_pedido = self.view.tabla_pedidos.item(fila_seleccionada, 0).text()
        detalles = self.model.obtener_detalle_pedido(id_pedido)
        self.view.tabla_detalle_pedido.setRowCount(len(detalles))
        for row, detalle in enumerate(detalles):
            for col, value in enumerate(detalle):
                self.view.tabla_detalle_pedido.setItem(row, col, QTableWidgetItem(str(value)))
        self.view.tabla_detalle_pedido.resizeColumnsToContents()

    @permiso_auditoria_compras('cargar_presupuesto')
    def cargar_presupuesto(self):
        try:
            fila_seleccionada = self.view.tabla_pedidos.currentRow()
            if fila_seleccionada == -1:
                self.view.label.setText("Seleccione un pedido para cargar el presupuesto.")
                return

            id_pedido = self.view.tabla_pedidos.item(fila_seleccionada, 0).text()
            presupuesto = self.view.obtener_datos_presupuesto()

            if not presupuesto:
                self.view.label.setText("Error: Datos incompletos para cargar el presupuesto.")
                return

            self.model.agregar_presupuesto((id_pedido, *presupuesto.values()))
            self.view.label.setText(f"Presupuesto cargado para el pedido {id_pedido}.")
        except Exception as e:
            print(f"Error al cargar presupuesto: {e}")
            self.view.label.setText("Error al cargar el presupuesto.")

    @permiso_auditoria_compras('comparar_presupuestos')
    def comparar_presupuestos(self, id_pedido):
        presupuestos = self.model.obtener_presupuestos_por_pedido(id_pedido)
        if presupuestos:
            comparacion = sorted(presupuestos, key=lambda x: x[5])
            self.view.mostrar_comparacion_presupuestos(comparacion)
        else:
            self.view.label.setText("No hay presupuestos para comparar.")

    @permiso_auditoria_compras('sincronizar_inventario')
    def sincronizar_pedido_con_inventario(self, id_pedido):
        try:
            detalles_pedido = self.model.obtener_detalle_pedido(id_pedido)
            for detalle in detalles_pedido:
                id_item = detalle[1]
                cantidad = detalle[2]
                self.inventario_model.actualizar_stock(id_item, -cantidad)
            self.view.label.setText(f"Pedido {id_pedido} sincronizado con el inventario.")
        except Exception as e:
            print(f"Error al sincronizar pedido con inventario: {e}")
            self.view.label.setText("Error al sincronizar el pedido con el inventario.")

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
        except Exception as e:
            print(f"Error al cargar pedidos: {e}")
            self.view.label.setText("Error al cargar los pedidos.")
