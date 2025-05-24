from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QGuiApplication, QBrush
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal

from core.theme import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR


# --- DOCUMENTACIÓN: SplashScreen y errores de UpdateLayeredWindowIndirect ---
# Para evitar errores de Windows como "UpdateLayeredWindowIndirect failed... (El parámetro no es correcto)",
# se recomienda NO usar transparencia (WA_TranslucentBackground), ni QGraphicsDropShadowEffect, ni el flag FramelessWindowHint
# en la SplashScreen, especialmente en equipos con drivers de video antiguos o virtualizados.
# Si se requiere un diseño moderno, usar solo bordes redondeados y fondo sólido, sin efectos avanzados.
#
# Si se necesita sombra, implementarla solo en sistemas donde no se reporten errores, o dejarla opcional.
#
# Referencia: https://github.com/pyqt/examples/issues/12 y docs/estandares_visuales.md

class SplashScreen(QSplashScreen):
    splash_ready = pyqtSignal()  # Señal para indicar que la app está lista

    def __init__(self, pixmap_path=None, message="Cargando...", duration=2000):
        ancho, alto = 640, 400  # Más grande
        custom_img_path = "img/pantalla-carga.jpg"
        use_custom_img = QPixmap(custom_img_path).isNull() is False
        # Fondo blanco con bordes redondeados (sin transparencia ni sombra)
        pixmap = QPixmap(ancho, alto)
        pixmap.fill(QColor(PRIMARY_COLOR))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(PRIMARY_COLOR))
        painter.setPen(QColor(BORDER_COLOR))
        painter.drawRoundedRect(0, 0, ancho, alto, 12, 12)
        # Imagen redondeada centrada
        if use_custom_img:
            img = QPixmap(custom_img_path).scaled(360, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                  Qt.TransformationMode.SmoothTransformation)
            mask = QPixmap(360, 200)
            mask.fill(Qt.GlobalColor.transparent)
            mask_painter = QPainter(mask)
            mask_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            mask_painter.setBrush(QBrush(Qt.GlobalColor.white))
            mask_painter.setPen(Qt.PenStyle.NoPen)
            mask_painter.drawRoundedRect(0, 0, 360, 200, 18, 18)
            mask_painter.end()
            img.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent, Qt.MaskMode.MaskInColor))
            painter.drawPixmap((ancho - 360) // 2, 40, img)
        painter.end()
        super().__init__(pixmap)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # Desactivado para evitar errores en Windows
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Desactivado para evitar errores
        # Sombra elegante (desactivada por defecto)
        # shadow = QGraphicsDropShadowEffect(self)
        # shadow.setBlurRadius(40)
        # shadow.setColor(QColor(0, 0, 0, 60))
        # shadow.setOffset(0, 12)
        # self.setGraphicsEffect(shadow)
        # Logo central solo si no hay imagen personalizada
        if not use_custom_img:
            self.logo = QLabel(self)
            self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_pix = QPixmap("img/add-material.svg")
            logo_bg = QPixmap(96, 96)
            logo_bg.fill(Qt.GlobalColor.transparent)
            p = QPainter(logo_bg)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setBrush(QColor(SECONDARY_COLOR))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(0, 0, 96, 96)
            if not logo_pix.isNull():
                p.drawPixmap(16, 16, 64, 64, logo_pix.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                                                                Qt.TransformationMode.SmoothTransformation))
            p.end()
            self.logo.setPixmap(logo_bg)
            self.logo.setGeometry((ancho - 96) // 2, 60, 96, 96)
        # Mensaje y barra de carga minimalista
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 22px; font-weight: bold; background: transparent; font-family: 'Segoe UI', 'Arial', sans-serif;")
        self.label.setGeometry(0, alto - 110, ancho, 40)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(ancho // 4, alto - 60, ancho // 2, 18)
        self.progress.setRange(0, 0)  # Barra indeterminada
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar {{background: {SECONDARY_COLOR}; border-radius: 9px;}} QProgressBar::chunk {{background: {ACCENT_COLOR}; border-radius: 9px;}}")
        self.duration = duration
        # Animación de opacidad (opcional, no afecta a la ventana completa)
        self.setWindowOpacity(1.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(1.0)
        self.fade_in.setEndValue(1.0)
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(350)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(1.0)

    def mousePressEvent(self, event):
        # Ignorar cualquier clic del usuario en el splash
        pass

    def show_and_finish(self):
        self.show()
        self.fade_in.start()

        def cerrar_splash():
            self.fade_out.finished.connect(self.close)
            self.fade_out.start()

        QTimer.singleShot(self.duration, cerrar_splash)

    def close_when_ready(self, main_window):
        """Cierra el splash solo cuando la ventana principal esté visible y activa."""

        def check_ready():
            if main_window.isVisible() and main_window.isActiveWindow():
                self.fade_out.finished.connect(self.close)
                self.fade_out.start()
            else:
                QTimer.singleShot(100, check_ready)

        check_ready()
