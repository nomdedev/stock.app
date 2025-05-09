from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QComboBox, QSizePolicy, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import QTimer, QSize
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QColor
import os
from core.ui_components import CustomButton

class UsuariosView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.layout = QVBoxLayout(self)

        # Cargar el stylesheet visual moderno para Usuarios
        try:
            with open("styles/inventario_styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar inventario_styles.qss: {e}")

        self.label_titulo = QLabel("Gestión de Usuarios")
        self.layout.addWidget(self.label_titulo)

        # Botón principal de acción estándar
        self.boton_accion = QPushButton()
        icon_path = os.path.join(os.path.dirname(__file__), '../../utils/users.svg')
        self.boton_accion.setIcon(QIcon(icon_path))
        self.boton_accion.setToolTip("Agregar usuario")
        self.boton_accion.setFixedSize(48, 48)
        self.boton_accion.setIconSize(QSize(32, 32))
        self.boton_accion.setObjectName("boton_accion")
        self.layout.addWidget(self.boton_accion)

        # Sombra visual profesional para el botón principal
        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 160))
            widget.setGraphicsEffect(sombra)
        aplicar_sombra(self.boton_accion)

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

        # Tabla principal de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(7)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Email", "Usuario", "Rol", "Estado"])
        self.layout.addWidget(self.tabla_usuarios)

        # Ajustar el ancho de las columnas al contenido
        self.tabla_usuarios.resizeColumnsToContents()

        self.inicializar_botones()

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

    def inicializar_botones(self):
        # Layout horizontal para los botones principales
        botones_layout = QHBoxLayout()
        # Botón Suspender (icono)
        self.boton_suspender = QPushButton()
        self.boton_suspender.setIcon(QtGui.QIcon('img/usuarios.svg'))
        self.boton_suspender.setIconSize(QSize(24, 24))
        self.boton_suspender.setToolTip('Suspender cuenta de usuario')
        self.boton_suspender.setText("")
        self.boton_suspender.setFixedSize(48, 48)
        self.boton_suspender.setStyleSheet("")
        botones_layout.addWidget(self.boton_suspender)
        # Botón Reactivar (icono)
        self.boton_reactivar = QPushButton()
        self.boton_reactivar.setIcon(QtGui.QIcon('img/sync.svg'))
        self.boton_reactivar.setIconSize(QSize(24, 24))
        self.boton_reactivar.setToolTip('Reactivar cuenta de usuario')
        self.boton_reactivar.setText("")
        self.boton_reactivar.setFixedSize(48, 48)
        self.boton_reactivar.setStyleSheet("")
        botones_layout.addWidget(self.boton_reactivar)
        # Botón Clonar Permisos (icono)
        self.boton_clonar_permisos = QPushButton()
        self.boton_clonar_permisos.setIcon(QtGui.QIcon('img/copy_icon.svg'))
        self.boton_clonar_permisos.setIconSize(QSize(24, 24))
        self.boton_clonar_permisos.setToolTip('Clonar permisos entre roles')
        self.boton_clonar_permisos.setText("")
        self.boton_clonar_permisos.setFixedSize(48, 48)
        self.boton_clonar_permisos.setStyleSheet("")
        botones_layout.addWidget(self.boton_clonar_permisos)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)
        # Inputs para clonado de permisos
        self.label_rol_origen = QLabel("Rol Origen:")
        self.layout.addWidget(self.label_rol_origen)
        self.input_rol_origen = QLineEdit()
        self.layout.addWidget(self.input_rol_origen)
        self.label_rol_destino = QLabel("Rol Destino:")
        self.layout.addWidget(self.label_rol_destino)
        self.input_rol_destino = QLineEdit()
        self.layout.addWidget(self.input_rol_destino)

    def mostrar_toast(self, mensaje):
        self.toast_label.setText(mensaje)
        self.toast_label.setVisible(True)
        QTimer.singleShot(3000, lambda: self.toast_label.setVisible(False))

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado

    @property
    def buscar_input(self):
        if not hasattr(self, '_buscar_input'):
            self._buscar_input = QLineEdit()
            self._buscar_input.setPlaceholderText('Buscar usuario...')
        return self._buscar_input

    @property
    def id_item_input(self):
        if not hasattr(self, '_id_item_input'):
            self._id_item_input = QLineEdit()
            self._id_item_input.setPlaceholderText('ID de usuario')
        return self._id_item_input

class Usuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Usuarios")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
