from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap
from PyQt6.QtCore import Qt

class LoginView(QWidget):
    """
    Vista de inicio de sesión.
    El logo principal es ahora aún más grande y visible (mínimo 380x380 px). Para cambiar el tamaño, edita el valor en el método __init__ donde se usa pixmap.scaled(380, 380, ...).
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.setFixedSize(370, 620)
        # self.setStyleSheet("""
        #     QWidget {
        #         background: #e0e7ef;
        #     }
        #     QFrame#login_card {
        #         background: #f3f4f6;
        #         border-radius: 28px;
        #         padding: 0px;
        #     }
        #     QLabel#titulo {
        #         font-size: 2.2rem;
        #         font-weight: bold;
        #         color: #2563eb;
        #         margin-top: 18px;
        #         margin-bottom: 8px;
        #         letter-spacing: 1px;
        #     }
        #     QLabel#icono {
        #         margin-top: 32px;
        #         margin-bottom: 8px;
        #     }
        #     QLabel#subtitulo {
        #         color: #374151;
        #         font-size: 1.1rem;
        #         margin-bottom: 18px;
        #     }
        #     QLineEdit {
        #         background: #fff;
        #         color: #1e293b;
        #         border: 2px solid #d1d5db;
        #         border-radius: 14px;
        #         padding: 12px;
        #         font-size: 1.1rem;
        #         margin-bottom: 8px;
        #     }
        #     QLineEdit:focus {
        #         border: 2px solid #2563eb;
        #         background: #f3f4f6;
        #         color: #1e293b;
        #     }
        #     QLineEdit::placeholder {
        #         color: #bdbdbd;
        #         font-style: italic;
        #     }
        #     QPushButton {
        #         background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #60a5fa);
        #         color: #fff;
        #         border-radius: 14px;
        #         font-size: 1.1rem;
        #         font-weight: bold;
        #         padding: 14px;
        #         margin-top: 18px;
        #         margin-bottom: 8px;
        #         /* box-shadow eliminado: Qt no soporta esta propiedad en QSS. Usar QGraphicsDropShadowEffect en Python para sombras. */
        #     }
        #     QPushButton:hover {
        #         background: #1d4ed8;
        #     }
        #     QLabel#error {
        #         color: #ef4444;
        #         font-size: 1rem;
        #         margin-top: 8px;
        #     }
        # """)
        # Fondo general
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Card de login con sombra
        self.login_card = QFrame()
        self.login_card.setObjectName("login_card")  # Para QSS global
        self.login_card.setFixedSize(340, 540)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setColor(QColor(37, 99, 235, 60))
        shadow.setOffset(0, 8)
        self.login_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.login_card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(16)

        # Icono superior (logo de inicio de sesión, ahora aún más grande)
        self.icono = QLabel()
        self.icono.setObjectName("icono")  # Para QSS global
        # Buscar imagen en resources/icons si no existe en img/
        pixmap = QPixmap("resources/icons/MPS_inicio_sesion.png")
        # Mostrar la imagen aún más grande (por ejemplo, 500x500)
        # Para cambiar el tamaño, edita el valor de scaled aquí:
        self.icono.setPixmap(pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.icono.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.icono)

        # Eliminar el título "StockApp" (no agregar el QLabel de título)

        self.subtitulo = QLabel("Iniciar sesión")
        self.subtitulo.setObjectName("subtitulo")  # Para QSS global
        self.subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(13)
        self.subtitulo.setFont(font)
        card_layout.addWidget(self.subtitulo)

        self.usuario_input = QLineEdit()
        self.usuario_input.setObjectName("usuario_input")  # Para QSS global
        self.usuario_input.setPlaceholderText("Usuario")
        # self.usuario_input.setStyleSheet("""
        #     QLineEdit {
        #         background: #fff;
        #         color: #1e293b;
        #         border-radius: 14px;
        #         border: 1.5px solid #e3e3e3;
        #         padding: 12px;
        #         font-size: 1.1rem;
        #     }
        #     QLineEdit:focus {
        #         border: 2px solid #2563eb;
        #         background: #f3f4f6;
        #         color: #1e293b;
        #     }
        #     QLineEdit::placeholder {
        #         color: #bdbdbd;
        #         font-style: italic;
        #     }
        # """)
        card_layout.addWidget(self.usuario_input)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("password_input")  # Para QSS global
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        # self.password_input.setStyleSheet(self.usuario_input.styleSheet())  # Migrado a QSS global
        card_layout.addWidget(self.password_input)

        self.boton_login = QPushButton("Ingresar")
        self.boton_login.setObjectName("boton_login")  # Para QSS global
        # Aplicar sombra visual al botón usando QGraphicsDropShadowEffect (reemplazo de box-shadow)
        sombra_boton = QGraphicsDropShadowEffect(self)
        sombra_boton.setBlurRadius(16)
        sombra_boton.setColor(QColor(37, 99, 235, 60))
        sombra_boton.setOffset(0, 4)
        self.boton_login.setGraphicsEffect(sombra_boton)
        card_layout.addWidget(self.boton_login)

        self.label_error = QLabel("")
        self.label_error.setObjectName("error")  # Para QSS global
        self.label_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.label_error)

        main_layout.addStretch()
        main_layout.addWidget(self.login_card, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()

        self.set_tooltips_accesibilidad()

    def mostrar_feedback(self, mensaje, tipo="info"):
        """
        Muestra feedback visual accesible y moderno en el label_feedback (o label_error para login).
        tipo: 'info', 'exito', 'advertencia', 'error'.
        """
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        icono = iconos.get(tipo, "ℹ️ ")
        color = colores.get(tipo, "#2563eb")
        self.label_error.setText(f"{icono}{mensaje}")
        self.label_error.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 1rem; margin-top: 8px;")
        self.label_error.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        self.label_error.setAccessibleName(f"Feedback {tipo}")
        self.label_error.setToolTip(mensaje)
        self.label_error.setVisible(True)

    def mostrar_error(self, mensaje):
        self.mostrar_feedback(mensaje, tipo="error")

    def limpiar_error(self):
        self.label_error.setText("")
        self.label_error.setStyleSheet("")
        self.label_error.setAccessibleDescription("")
        self.label_error.setAccessibleName("")
        self.label_error.setToolTip("")
        self.label_error.setVisible(False)

    def set_tooltips_accesibilidad(self):
        self.usuario_input.setToolTip("Ingrese su nombre de usuario")
        self.usuario_input.setAccessibleName("Campo de usuario")
        self.usuario_input.setAccessibleDescription("Campo para ingresar el nombre de usuario")
        self.password_input.setToolTip("Ingrese su contraseña")
        self.password_input.setAccessibleName("Campo de contraseña")
        self.password_input.setAccessibleDescription("Campo para ingresar la contraseña")
        self.boton_login.setToolTip("Ingresar al sistema")
        self.boton_login.setAccessibleName("Botón de ingresar")
        self.boton_login.setAccessibleDescription("Botón para iniciar sesión")
