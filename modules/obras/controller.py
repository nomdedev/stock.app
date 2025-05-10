from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QComboBox
from PyQt6 import QtCore
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

permiso_auditoria_obras = PermisoAuditoria('obras')

class ObrasController:
    def __init__(self, model, view, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel()
        self.auditoria_model = AuditoriaModel()
        # Conexión de señales de los botones principales
        self.view.boton_agregar.clicked.connect(self.agregar_obra)
        self.view.boton_ver_cronograma.clicked.connect(self.ver_cronograma)
        self.view.boton_asignar_material.clicked.connect(self.asignar_materiales)
        self.view.boton_cambiar_estado.clicked.connect(self.cambiar_estado_obra)
        self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_cronograma_seleccionada("excel"))
        # self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_cronograma_seleccionada("pdf"))
        self.cargar_datos_obras()  # Cargar datos al iniciar

    def cargar_datos_obras(self):
        """Carga los datos de la tabla de obras en la vista."""
        try:
            datos = self.model.obtener_datos_obras()
            self.view.tabla_obras.setRowCount(len(datos))
            for row_idx, row_data in enumerate(datos):
                for col_idx, value in enumerate(row_data):
                    self.view.tabla_obras.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            # Ajustar el ancho de las columnas al contenido
            self.view.tabla_obras.resizeColumnsToContents()
            self.poblar_kanban()
        except Exception as e:
            self.view.label.setText(f"Error al cargar datos: {e}")

    def cargar_datos_cronograma(self, id_obra):
        """Carga los datos del cronograma de una obra en la pestaña de cronograma."""
        try:
            cronograma = self.model.obtener_cronograma_por_obra(id_obra)
            self.view.tabla_cronograma.setRowCount(len(cronograma))
            for row_idx, row_data in enumerate(cronograma):
                for col_idx, value in enumerate(row_data):
                    self.view.tabla_cronograma.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            # Ajustar el ancho de las columnas al contenido
            self.view.tabla_cronograma.resizeColumnsToContents()
        except Exception as e:
            self.view.label.setText(f"Error al cargar cronograma: {e}")

    def actualizar_calendario(self):
        """Actualiza el calendario con las fechas del cronograma."""
        try:
            cronograma = self.model.obtener_todas_las_fechas()
            for fecha in cronograma:
                # Aquí puedes agregar lógica para resaltar fechas en el calendario
                print(f"Fecha programada: {fecha}")
        except Exception as e:
            self.view.label.setText(f"Error al actualizar calendario: {e}")

    @permiso_auditoria_obras('agregar')
    def agregar_obra(self):
        """Abre un diálogo para cargar los datos clave de la obra y la registra."""
        try:
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Agregar nueva obra")
            layout = QVBoxLayout(dialog)
            label = QLabel("Ingrese los datos de la nueva obra:")
            layout.addWidget(label)

            nombre_input = QLineEdit()
            cliente_input = QLineEdit()
            estado_input = QComboBox()
            estado_input.addItems(["Medición", "Fabricación", "Entrega"])

            layout.addWidget(QLabel("Nombre:"))
            layout.addWidget(nombre_input)
            layout.addWidget(QLabel("Cliente:"))
            layout.addWidget(cliente_input)
            layout.addWidget(QLabel("Estado:"))
            layout.addWidget(estado_input)

            btn_guardar = QPushButton("Guardar")
            btn_cancelar = QPushButton("Cancelar")
            btn_guardar.clicked.connect(dialog.accept)
            btn_cancelar.clicked.connect(dialog.reject)
            layout.addWidget(btn_guardar)
            layout.addWidget(btn_cancelar)

            dialog.setLayout(layout)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                nombre = nombre_input.text()
                cliente = cliente_input.text()
                estado = estado_input.currentText()
                if not (nombre and cliente and estado):
                    self.view.label.setText("Por favor, complete todos los campos.")
                    return
                if self.model.verificar_obra_existente(nombre, cliente):
                    QMessageBox.warning(
                        self.view,
                        "Obra Existente",
                        "Ya existe una obra con el mismo nombre y cliente."
                    )
                    return
                fecha_actual = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
                self.model.agregar_obra((nombre, cliente, estado, fecha_actual))
                self.view.label.setText("Obra agregada exitosamente.")
                self.cargar_datos_obras()
        except Exception as e:
            print(f"Error al agregar obra: {e}")
            self.view.label.setText("Error al agregar la obra.")

    @permiso_auditoria_obras('ver_cronograma')
    def ver_cronograma(self):
        fila_seleccionada = self.view.tabla_obras.currentRow()
        if fila_seleccionada != -1:
            id_obra = self.view.tabla_obras.item(fila_seleccionada, 0).text()
            cronograma = self.model.obtener_cronograma_por_obra(id_obra)
            # Crear ventana emergente
            dialog = QDialog(self.view)
            dialog.setWindowTitle(f"Cronograma de Obra {id_obra}")
            layout = QVBoxLayout(dialog)
            label = QLabel(f"Cronograma de la obra seleccionada (ID: {id_obra})")
            layout.addWidget(label)
            tabla = QTableWidget()
            tabla.setColumnCount(6)
            tabla.setHorizontalHeaderLabels(["Etapa", "Fecha Programada", "Fecha Realizada", "Observaciones", "Responsable", "Estado"])
            tabla.setRowCount(len(cronograma))
            for row, etapa in enumerate(cronograma):
                for col, value in enumerate(etapa):
                    tabla.setItem(row, col, QTableWidgetItem(str(value)))
            layout.addWidget(tabla)
            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.clicked.connect(dialog.accept)
            layout.addWidget(btn_cerrar)
            dialog.exec()
        else:
            self.view.label.setText("Seleccione una obra para ver su cronograma.")

    @permiso_auditoria_obras('asignar_materiales')
    def asignar_materiales(self):
        fila_seleccionada = self.view.tabla_obras.currentRow()
        if fila_seleccionada != -1:
            id_obra = self.view.tabla_obras.item(fila_seleccionada, 0).text()
            # Diálogo para seleccionar material y cantidad
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Asignar material a obra")
            layout = QVBoxLayout(dialog)
            label = QLabel(f"Asignar material a la obra ID: {id_obra}")
            layout.addWidget(label)
            # Inputs
            id_item_input = QLineEdit()
            id_item_input.setPlaceholderText("ID de material")
            cantidad_necesaria_input = QLineEdit()
            cantidad_necesaria_input.setPlaceholderText("Cantidad necesaria")
            cantidad_reservada_input = QLineEdit()
            cantidad_reservada_input.setPlaceholderText("Cantidad reservada")
            estado_input = QComboBox()
            estado_input.addItems(["pendiente", "reservado", "entregado"])
            layout.addWidget(QLabel("ID de material:"))
            layout.addWidget(id_item_input)
            layout.addWidget(QLabel("Cantidad necesaria:"))
            layout.addWidget(cantidad_necesaria_input)
            layout.addWidget(QLabel("Cantidad reservada:"))
            layout.addWidget(cantidad_reservada_input)
            layout.addWidget(QLabel("Estado:"))
            layout.addWidget(estado_input)
            btn_guardar = QPushButton("Guardar")
            btn_cancelar = QPushButton("Cancelar")
            btn_guardar.clicked.connect(dialog.accept)
            btn_cancelar.clicked.connect(dialog.reject)
            layout.addWidget(btn_guardar)
            layout.addWidget(btn_cancelar)
            dialog.setLayout(layout)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                id_item = id_item_input.text()
                cantidad_necesaria = cantidad_necesaria_input.text()
                cantidad_reservada = cantidad_reservada_input.text()
                estado = estado_input.currentText()
                if not (id_item and cantidad_necesaria and cantidad_reservada and estado):
                    self.view.label.setText("Por favor, complete todos los campos de material.")
                    return
                self.model.asignar_material_a_obra((id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado))
                self.view.label.setText(f"Material asignado a la obra {id_obra}.")
        else:
            self.view.label.setText("Seleccione una obra para asignar materiales.")

    @permiso_auditoria_obras('exportar_cronograma')
    def exportar_cronograma(self, id_obra, formato):
        mensaje = self.model.exportar_cronograma(formato, id_obra)
        self.view.label.setText(mensaje)

    @permiso_auditoria_obras('exportar_cronograma_seleccionada')
    def exportar_cronograma_seleccionada(self, formato):
        fila_seleccionada = self.view.tabla_obras.currentRow()
        if fila_seleccionada != -1:
            id_obra = self.view.tabla_obras.item(fila_seleccionada, 0).text()
            self.exportar_cronograma(id_obra, formato)
        else:
            self.view.label.setText("Seleccione una obra para exportar su cronograma.")

    @permiso_auditoria_obras('sincronizar_materiales_con_inventario')
    def sincronizar_materiales_con_inventario(self, id_obra):
        """Sincroniza los materiales de una obra con el inventario."""
        try:
            materiales = self.model.obtener_materiales_por_obra(id_obra)
            for material in materiales:
                id_item = material[1]  # Suponiendo que el ID del ítem está en la columna 1
                cantidad_reservada = material[3]  # Suponiendo que la cantidad reservada está en la columna 3
                self.inventario_model.actualizar_stock(id_item, -cantidad_reservada)  # Reducir stock
            self.view.label.setText(f"Materiales de la obra {id_obra} sincronizados con el inventario.")
        except Exception as e:
            print(f"Error al sincronizar materiales con inventario: {e}")
            self.view.label.setText("Error al sincronizar materiales con el inventario.")

    @permiso_auditoria_obras('cambiar_estado')
    def cambiar_estado_obra(self, nuevo_estado=None):
        """Permite cambiar el estado de la obra seleccionada, validando el flujo y registrando auditoría."""
        fila = self.view.tabla_obras.currentRow()
        if fila == -1:
            self.view.label.setText("Seleccione una obra para cambiar su estado.")
            return
        id_obra = self.view.tabla_obras.item(fila, 0).text()
        estado_actual = self.view.tabla_obras.item(fila, 3).text()
        # Estados permitidos
        estados = ["medida", "pedido cargado", "en producción", "colocada", "finalizada"]
        try:
            idx = estados.index(estado_actual)
        except ValueError:
            self.view.label.setText("Estado actual no válido.")
            return
        # Si no se pasa nuevo_estado, abrir modal para elegir
        if not nuevo_estado:
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Cambiar estado de obra")
            layout = QVBoxLayout(dialog)
            label = QLabel("Seleccione el nuevo estado:")
            layout.addWidget(label)
            combo = QComboBox()
            for i, est in enumerate(estados):
                combo.addItem(est)
                if est == estado_actual:
                    combo.setCurrentIndex(i)
            layout.addWidget(combo)
            btn_guardar = QPushButton("Cambiar")
            btn_guardar.clicked.connect(dialog.accept)
            layout.addWidget(btn_guardar)
            dialog.setLayout(layout)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                nuevo_estado = combo.currentText()
            else:
                return
        # Validar transición
        if nuevo_estado not in estados or estados.index(nuevo_estado) <= idx:
            self.view.label.setText("Transición de estado no permitida.")
            return
        # Acciones en cadena
        if nuevo_estado == "pedido cargado":
            if hasattr(self, 'pedidos_controller'):
                if not self.pedidos_controller.existe_pedido_para_obra(id_obra):
                    self.pedidos_controller.generar_pedido_para_obra(id_obra)
            self.auditoria_model.registrar_evento(self.usuario_actual or "sistema", "obras", f"estado cambiado a {nuevo_estado}")
        elif nuevo_estado == "en producción":
            if hasattr(self, 'produccion_controller'):
                self.produccion_controller.iniciar_produccion_obra(id_obra)
            if hasattr(self, 'inventario_model'):
                self.model.reservar_materiales_para_obra(id_obra)
            self.auditoria_model.registrar_evento(self.usuario_actual or "sistema", "obras", f"estado cambiado a {nuevo_estado}")
        elif nuevo_estado == "colocada":
            if hasattr(self, 'logistica_controller'):
                self.logistica_controller.registrar_colocacion(id_obra)
            self.auditoria_model.registrar_evento(self.usuario_actual or "sistema", "obras", f"estado cambiado a {nuevo_estado}")
        elif nuevo_estado == "finalizada":
            # Bloquear edición, confirmar cobro, etc.
            self.auditoria_model.registrar_evento(self.usuario_actual or "sistema", "obras", f"estado cambiado a {nuevo_estado}")
        # Actualizar en modelo
        self.model.actualizar_estado_obra(id_obra, nuevo_estado)
        self.cargar_datos_obras()
        self.view.label.setText(f"Estado de la obra actualizado a {nuevo_estado}.")

    def poblar_kanban(self):
        # Limpia el layout
        while self.view.kanban_layout.count():
            item = self.view.kanban_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        # Obtener datos de obras
        datos = self.model.obtener_datos_obras()
        for row in datos:
            id_obra, nombre, cliente, estado, fecha_medicion = row
            from datetime import datetime, timedelta
            try:
                fecha_med = datetime.strptime(str(fecha_medicion), "%Y-%m-%d")
            except Exception:
                fecha_med = datetime.now()
            fecha_entrega = fecha_med + timedelta(days=90)
            tarjeta = QLabel(f"Obra: {nombre}\nCliente: {cliente}\nEstado: {estado}\nMedición: {fecha_med.date()}\nEntrega: {fecha_entrega.date()}")
            tarjeta.setStyleSheet("background: #e0e7ef; border-radius: 8px; padding: 12px; margin: 8px; font-size: 13px;")
            self.view.kanban_layout.addWidget(tarjeta)
