from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QGuiApplication, QBrush
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, pyqtSignal
from PyQt6.QtSvg import QSvgRenderer

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

    def __init__(self, pixmap_path=None, message="Cargando...", duration=2000, theme=None, logo_path=None):
        ancho, alto = 640, 400
        self.logo_path = logo_path or pixmap_path or "resources/icons/pantalla-carga.jpg"
        self.theme = theme
        self._apply_theme_colors()
        pixmap = QPixmap(ancho, alto)
        pixmap.fill(QColor(self.bg_color))
        painter = QPainter(pixmap)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(self.bg_color))
            painter.setPen(QColor(self.border_color))
            painter.drawRoundedRect(0, 0, ancho, alto, 12, 12)
            # Renderizar logo (SVG o imagen)
            if self.logo_path.lower().endswith('.svg'):
                renderer = QSvgRenderer(self.logo_path)
                svg_pixmap = QPixmap(180, 180)
                svg_pixmap.fill(Qt.GlobalColor.transparent)
                svg_painter = QPainter(svg_pixmap)
                try:
                    renderer.render(svg_painter)
                finally:
                    svg_painter.end()
                painter.drawPixmap((ancho-180)//2, 50, svg_pixmap)
            else:
                img = QPixmap(self.logo_path)
                if not img.isNull():
                    img = img.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    painter.drawPixmap((ancho-180)//2, 50, img)
        finally:
            painter.end()
        super().__init__(pixmap)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        # Mensaje y barra de carga
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(
            f"color: {self.text_color}; font-size: 22px; font-weight: bold; background: transparent; font-family: 'Segoe UI', 'Arial', sans-serif;")
        self.label.setGeometry(0, alto - 110, ancho, 40)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(ancho // 4, alto - 60, ancho // 2, 18)
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(
            f"QProgressBar {{background: {self.secondary_color}; border-radius: 9px;}} QProgressBar::chunk {{background: {self.accent_color}; border-radius: 9px;}}")
        self.duration = duration
        self.setWindowOpacity(1.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(1.0)
        self.fade_in.setEndValue(1.0)
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(350)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(1.0)

    def _apply_theme_colors(self):
        # Permite adaptar los colores al tema activo
        # Si theme es None, usar los colores globales
        if self.theme == 'dark':
            self.bg_color = '#23272e'
            self.text_color = '#f0f0f0'
            self.border_color = '#444'
            self.secondary_color = '#2d313a'
            self.accent_color = '#4fc3f7'
        elif self.theme == 'light':
            self.bg_color = '#f8f8f8'
            self.text_color = '#23272e'
            self.border_color = '#bbb'
            self.secondary_color = '#e0e0e0'
            self.accent_color = '#1976d2'
        else:
            from core.theme import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR
            self.bg_color = PRIMARY_COLOR
            self.text_color = TEXT_COLOR
            self.border_color = BORDER_COLOR
            self.secondary_color = SECONDARY_COLOR
            self.accent_color = ACCENT_COLOR

    def set_image(self, logo_path):
        """Permite cambiar la imagen/logo en tiempo de ejecución y refresca el fondo si es necesario."""
        self.logo_path = logo_path
        ancho, alto = 640, 400
        pixmap = QPixmap(ancho, alto)
        pixmap.fill(QColor(self.bg_color))
        painter = QPainter(pixmap)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setBrush(QColor(self.bg_color))
            painter.setPen(QColor(self.border_color))
            painter.drawRoundedRect(0, 0, ancho, alto, 12, 12)
            if logo_path.lower().endswith('.svg'):
                renderer = QSvgRenderer(logo_path)
                svg_pixmap = QPixmap(180, 180)
                svg_pixmap.fill(Qt.GlobalColor.transparent)
                svg_painter = QPainter(svg_pixmap)
                try:
                    renderer.render(svg_painter)
                finally:
                    svg_painter.end()
                painter.drawPixmap((ancho-180)//2, 50, svg_pixmap)
            else:
                img = QPixmap(logo_path)
                if not img.isNull():
                    img = img.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    painter.drawPixmap((ancho-180)//2, 50, img)
        finally:
            painter.end()
        self.setPixmap(pixmap)
        self.repaint()

    def set_theme(self, theme):
        """Permite cambiar el tema (oscuro/claro) en tiempo de ejecución y refresca colores e imagen."""
        self.theme = theme
        self._apply_theme_colors()
        self.set_image(self.logo_path)

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
