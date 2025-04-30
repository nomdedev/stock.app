from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QComboBox, QSizePolicy
from PyQt6.QtCore import QTimer
from core.ui_components import CustomButton

class UsuariosView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Usuarios")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setFixedWidth(500)
        self.apellido_input = QLineEdit()
        self.apellido_input.setFixedWidth(500)
        self.usuario_input = QLineEdit()
        self.usuario_input.setFixedWidth(500)
        self.password_input = QLineEdit()
        self.password_input.setFixedWidth(500)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.email_input = QLineEdit()
        self.email_input.setFixedWidth(500)
        self.rol_input = QComboBox()
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Apellido:", self.apellido_input)
        self.form_layout.addRow("Usuario:", self.usuario_input)
        self.form_layout.addRow("Contraseña:", self.password_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Rol:", self.rol_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar = CustomButton("Agregar Usuario")
        self.boton_agregar.setFixedWidth(100)
        self.boton_agregar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_agregar)

        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(10)
        self.tabla_usuarios.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Email", "Usuario", "Rol", "Estado",
            "Editar", "Suspender/Reactivar", "Resetear Contraseña"
        ])
        self.tabla_usuarios.horizontalHeader().setStretchLastSection(True)
        self.tabla_usuarios.horizontalHeader().setSectionsMovable(True)
        self.tabla_usuarios.horizontalHeader().setStyleSheet("")
        self.tabla_usuarios.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                font-size: 14px;
                background: #f8f9fc;
                selection-background-color: #2563eb;
                selection-color: #fff;
            }
            QHeaderView::section {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                padding: 6px;
                border-radius: 12px;
            }
        """)
        self.tabla_usuarios.setFixedSize(800, 400)
        self.layout.addWidget(self.tabla_usuarios)

        self.boton_nuevo_usuario = CustomButton("Nuevo Usuario")
        self.layout.addWidget(self.boton_nuevo_usuario)

        self.boton_favorito = CustomButton("Marcar como Favorito")
        if self.controller is None:
            raise AttributeError("El controlador no está inicializado correctamente.")
        self.boton_favorito.clicked.connect(self.controller.marcar_como_favorito)
        self.layout.addWidget(self.boton_favorito)

        # Botón para gestionar roles y permisos
        self.boton_gestion_roles = CustomButton("Gestionar Roles y Permisos")
        self.boton_gestion_roles.setFixedWidth(100)
        self.boton_gestion_roles.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_gestion_roles)

        # Tabla de roles y permisos
        self.tabla_roles_permisos = QTableWidget()
        self.tabla_roles_permisos.setColumnCount(6)
        self.tabla_roles_permisos.setHorizontalHeaderLabels(["Rol", "Módulo", "Ver", "Editar", "Aprobar", "Eliminar"])
        self.tabla_roles_permisos.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_roles_permisos)

        # Botón para guardar permisos
        self.boton_guardar_permisos = CustomButton("Guardar Permisos")
        self.boton_guardar_permisos.setFixedWidth(100)
        self.boton_guardar_permisos.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_guardar_permisos)

        # Botón para exportar logs
        self.boton_exportar_logs = CustomButton("Exportar Logs")
        self.boton_exportar_logs.setFixedWidth(100)
        self.boton_exportar_logs.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_exportar_logs)

        self.toast_label = QLabel("")
        self.toast_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        self.toast_label.setVisible(False)
        self.layout.addWidget(self.toast_label)

        self.setLayout(self.layout)

        self.inicializar_botones()

    def mostrar_toast(self, mensaje):
        self.toast_label.setText(mensaje)
        self.toast_label.setVisible(True)
        QTimer.singleShot(3000, lambda: self.toast_label.setVisible(False))

    def inicializar_botones(self):
        self.boton_suspender = CustomButton("Suspender Cuenta")
        self.layout.addWidget(self.boton_suspender)

        self.boton_reactivar = CustomButton("Reactivar Cuenta")
        self.layout.addWidget(self.boton_reactivar)

        self.label_rol_origen = QLabel("Rol Origen:")
        self.layout.addWidget(self.label_rol_origen)
        self.input_rol_origen = QLineEdit()
        self.layout.addWidget(self.input_rol_origen)

        self.label_rol_destino = QLabel("Rol Destino:")
        self.layout.addWidget(self.label_rol_destino)
        self.input_rol_destino = QLineEdit()
        self.layout.addWidget(self.input_rol_destino)

        self.boton_clonar_permisos = CustomButton("Clonar Permisos")
        self.layout.addWidget(self.boton_clonar_permisos)

class Usuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Usuarios")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
