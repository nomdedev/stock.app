import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QComboBox, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6 import QtCore
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            from functools import wraps
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                usuario = getattr(controller, 'usuario_actual', None)
                if usuario_model is None or auditoria_model is None:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText("Error interno: modelo de usuario o auditoría no disponible.")
                    return None
                # Permitir siempre a admin y supervisor
                if usuario and usuario.get('rol') in ('admin', 'supervisor'):
                    resultado = func(controller, *args, **kwargs)
                    auditoria_model.registrar_evento(usuario, self.modulo, accion)
                    return resultado
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
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.view.boton_agregar.clicked.connect(self.agregar_obra)
        self.view.gantt_on_bar_clicked = self.editar_fecha_entrega
        # Conexión del botón de verificación manual (si existe en la vista)
        if hasattr(self.view, 'boton_verificar_obra'):
            self.view.boton_verificar_obra.clicked.connect(self.verificar_obra_en_sql_dialog)
        self._insertar_obras_ejemplo_si_vacio()
        self.cargar_datos_obras()
        self.mostrar_gantt()
        self.actualizar_calendario()

    def _insertar_obras_ejemplo_si_vacio(self):
        datos = self.model.obtener_datos_obras()
        if not datos or len(datos) == 0:
            from datetime import date, timedelta
            hoy = date.today()
            ejemplos = [
                ("Edificio Central", "Constructora Sur", "Medición", (hoy-timedelta(days=10)).strftime("%Y-%m-%d"), (hoy+timedelta(days=30)).strftime("%Y-%m-%d")),
                ("Torre Norte", "Desarrollos Río", "Fabricación", (hoy-timedelta(days=20)).strftime("%Y-%m-%d"), (hoy+timedelta(days=15)).strftime("%Y-%m-%d")),
                ("Residencial Sur", "Grupo Delta", "Entrega", (hoy-timedelta(days=40)).strftime("%Y-%m-%d"), (hoy+timedelta(days=5)).strftime("%Y-%m-%d")),
            ]
            for nombre, cliente, estado, fecha, fecha_entrega in ejemplos:
                self.model.agregar_obra((nombre, cliente, estado, fecha, fecha_entrega))

    def cargar_datos_obras(self):
        try:
            datos = self.model.obtener_datos_obras()
        except Exception as e:
            self.view.label.setText(f"Error al cargar datos: {e}")

    def verificar_obra_en_sql(self, nombre, cliente):
        """Verifica si la obra existe en la base de datos SQL Server y muestra el resultado en el label."""
        try:
            datos = self.model.obtener_obra_por_nombre_cliente(nombre, cliente)
            if datos:
                self.view.label.setText(f"✔ Obra encontrada en SQL: {datos}")
            else:
                self.view.label.setText("✖ La obra NO se encuentra en la base de datos SQL.")
        except Exception as e:
            self.view.label.setText(f"Error al verificar obra en SQL: {e}")

    def verificar_obra_en_sql_dialog(self):
        """Abre un diálogo para ingresar nombre y cliente y verifica la existencia en SQL Server."""
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Verificar obra en SQL")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Nombre de la obra:"))
        nombre_input = QLineEdit()
        layout.addWidget(nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        cliente_input = QLineEdit()
        layout.addWidget(cliente_input)
        btn_verificar = QPushButton("Verificar")
        btn_cancelar = QPushButton("Cancelar")
        btn_verificar.clicked.connect(dialog.accept)
        btn_cancelar.clicked.connect(dialog.reject)
        layout.addWidget(btn_verificar)
        layout.addWidget(btn_cancelar)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nombre = nombre_input.text()
            cliente = cliente_input.text()
            if not (nombre and cliente):
                self.view.label.setText("Debe ingresar nombre y cliente.")
                return
            self.verificar_obra_en_sql(nombre, cliente)

    @permiso_auditoria_obras('agregar')
    def agregar_obra(self):
        """Abre un diálogo para cargar los datos clave de la obra y la registra."""
        try:
            usuario = self.usuario_actual
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Agregar nueva obra")
            layout = QVBoxLayout(dialog)
            label = QLabel("Ingrese los datos de la nueva obra:")
            label.setStyleSheet("font-weight: bold; font-size: 15px; margin-bottom: 8px;")
            layout.addWidget(label)

            # Usuario actual visible, destacado
            if usuario and 'username' in usuario:
                usuario_label = QLabel(f"<b>Usuario cargando: <span style='color:#2563eb'>{usuario['username']} ({usuario.get('rol','')})</span></b>")
                usuario_label.setStyleSheet("font-size: 13px; margin-bottom: 8px; background: #f1f5f9; border-radius: 8px; padding: 4px 8px;")
                layout.addWidget(usuario_label)

            nombre_input = QLineEdit()
            cliente_input = QLineEdit()
            estado_input = QComboBox()
            estado_input.addItems(["Medición", "Fabricación", "Entrega"])

            nombre_input.setPlaceholderText("Nombre de la obra")
            cliente_input.setPlaceholderText("Cliente")

            layout.addWidget(QLabel("Nombre:"))
            layout.addWidget(nombre_input)
            layout.addWidget(QLabel("Cliente:"))
            layout.addWidget(cliente_input)
            layout.addWidget(QLabel("Estado:"))
            layout.addWidget(estado_input)

            # Botones con estilo visual consistente
            btns_layout = QHBoxLayout()
            btn_guardar = QPushButton()
            btn_guardar.setIcon(QIcon("img/plus_icon.svg"))
            btn_guardar.setToolTip("Guardar obra")
            btn_guardar.setFixedSize(48, 48)
            btn_guardar.setStyleSheet("background-color: #2563eb; border-radius: 12px; border: none;")
            btn_guardar.clicked.connect(dialog.accept)
            btn_cancelar = QPushButton()
            btn_cancelar.setIcon(QIcon("img/reject.svg"))
            btn_cancelar.setToolTip("Cancelar")
            btn_cancelar.setFixedSize(48, 48)
            btn_cancelar.setStyleSheet("background-color: #e5e7eb; border-radius: 12px; border: none;")
            btn_cancelar.clicked.connect(dialog.reject)
            btns_layout.addWidget(btn_guardar)
            btns_layout.addWidget(btn_cancelar)
            layout.addLayout(btns_layout)

            dialog.setLayout(layout)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                nombre = nombre_input.text().strip()
                cliente = cliente_input.text().strip()
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
                self.actualizar_calendario()
                self.mostrar_gantt()
                # Verificación automática en SQL
                self.verificar_obra_en_sql(nombre, cliente)
        except Exception as e:
            print(f"Error al agregar obra: {e}")
            self.view.label.setText("Error al agregar la obra.")

    def editar_fecha_entrega(self, id_obra, fecha_actual):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Editar fecha de entrega")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Fecha actual: {fecha_actual}"))
        fecha_input = QLineEdit(fecha_actual)
        layout.addWidget(QLabel("Nueva fecha de entrega (YYYY-MM-DD):"))
        layout.addWidget(fecha_input)
        btn_guardar = QPushButton("Guardar")
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar.clicked.connect(dialog.accept)
        btn_cancelar.clicked.connect(dialog.reject)
        layout.addWidget(btn_guardar)
        layout.addWidget(btn_cancelar)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nueva_fecha = fecha_input.text()
            # Obtener datos actuales de la obra
            datos = self.model.obtener_obra_por_id(id_obra)
            if datos:
                nombre, cliente, estado = datos[1], datos[2], datos[3]
                self.model.actualizar_obra(id_obra, nombre, cliente, estado, nueva_fecha)
                self.mostrar_gantt()

    def mostrar_gantt(self):
        datos = self.model.obtener_datos_obras()
        if hasattr(self.view, 'cronograma_view'):
            self.view.cronograma_view.set_obras([
                {
                    'id': d[0],
                    'nombre': d[1],
                    'cliente': d[2],
                    'estado': d[3],
                    'fecha': d[4] if isinstance(d[4], (datetime.date, datetime.datetime)) else self._parse_fecha(d[4]),
                    'fecha_entrega': d[5] if isinstance(d[5], (datetime.date, datetime.datetime)) else self._parse_fecha(d[5]),
                }
                for d in datos if d[4] and d[5]
            ])

    @staticmethod
    def _parse_fecha(fecha_str):
        import datetime
        if not fecha_str:
            return None
        try:
            return datetime.datetime.strptime(str(fecha_str), "%Y-%m-%d").date()
        except Exception:
            return None

    def actualizar_calendario(self):
        """Actualiza el calendario con las fechas del cronograma."""
        try:
            cronograma = self.model.obtener_todas_las_fechas()
            for fecha in cronograma:
                # Aquí puedes agregar lógica para resaltar fechas en el calendario
                print(f"Fecha programada: {fecha}")
        except Exception as e:
            self.view.label.setText(f"Error al actualizar calendario: {e}")
