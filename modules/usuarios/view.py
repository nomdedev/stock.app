from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QComboBox, QSizePolicy, QPushButton
from PyQt6.QtCore import QTimer
from core.ui_components import CustomButton

class UsuariosView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.layout = QVBoxLayout(self)

        # Ajustar estilo general de la vista
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0; /* Fondo gris claro */
                color: #000000; /* Texto negro */
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333; /* Gris oscuro */
            }
            QTableWidget {
                border: 1px solid #000000; /* Bordes negros */
                background-color: #ffffff; /* Fondo blanco */
                font-size: 12px;
                gridline-color: #000000; /* Líneas de cuadrícula negras */
            }
            QTableWidget::item {
                background-color: #ffffff; /* Fondo blanco */
            }
            QTableWidget::item:selected {
                background-color: #d1d5db; /* Gris más oscuro */
                color: #000000; /* Texto negro */
            }
            QHeaderView::section {
                background-color: #dbeafe; /* Azul crema */
                color: #000000; /* Texto negro */
                font-weight: bold; /* Letras en negrita */
                border: 1px solid #000000; /* Bordes negros */
            }
        """)

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

        # Tabla principal de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(7)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Email", "Usuario", "Rol", "Estado"])
        self.layout.addWidget(self.tabla_usuarios)

        # Ajustar el ancho de las columnas al contenido
        self.tabla_usuarios.resizeColumnsToContents()

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

        # Tabla de permisos por rol
        self.tabla_roles_permisos = QTableWidget()
        self.tabla_roles_permisos.setColumnCount(6)
        self.tabla_roles_permisos.setHorizontalHeaderLabels(["Rol", "Módulo", "Ver", "Editar", "Aprobar", "Eliminar"])
        self.layout.addWidget(self.tabla_roles_permisos)

        # Ajustar el ancho de las columnas al contenido
        self.tabla_roles_permisos.resizeColumnsToContents()

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

        # Botón de ejemplo
        self.boton_ejemplo = QPushButton("Ejemplo Usuarios")
        self.boton_ejemplo.setFixedHeight(40)  # Altura fija
        self.boton_ejemplo.setFixedWidth(150)  # Ancho fijo
        self.boton_ejemplo.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                text-align: center; /* Centrar texto */
                border: none;
                font-size: 14px; /* Tamaño de letra */
                font-weight: bold; /* Negrita */
                border-radius: 8px; /* Bordes redondeados */
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        self.layout.addWidget(self.boton_ejemplo)

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
