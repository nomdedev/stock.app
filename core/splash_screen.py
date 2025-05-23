from PyQt6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QGraphicsDropShadowEffect, QProgressBar
from PyQt6.QtGui import QPixmap, QFont, QPainter, QColor, QGuiApplication, QBrush
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from core.theme import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR

class SplashScreen(QSplashScreen):
    def __init__(self, pixmap_path=None, message="Cargando...", duration=2000):
        ancho, alto = 640, 400  # Más grande
        custom_img_path = "img/pantalla-carga.jpg"
        use_custom_img = QPixmap(custom_img_path).isNull() is False
        # Fondo blanco con sombra y bordes redondeados
        pixmap = QPixmap(ancho, alto)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(PRIMARY_COLOR))
        painter.setPen(QColor(BORDER_COLOR))
        painter.drawRoundedRect(0, 0, ancho, alto, 12, 12)
        # Imagen redondeada centrada
        if use_custom_img:
            img = QPixmap(custom_img_path).scaled(360, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            mask = QPixmap(360, 200)
            mask.fill(Qt.GlobalColor.transparent)
            mask_painter = QPainter(mask)
            mask_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            mask_painter.setBrush(QBrush(Qt.GlobalColor.white))
            mask_painter.setPen(Qt.PenStyle.NoPen)
            mask_painter.drawRoundedRect(0, 0, 360, 200, 18, 18)
            mask_painter.end()
            img.setMask(mask.createMaskFromColor(Qt.GlobalColor.transparent, Qt.MaskMode.MaskInColor))
            painter.drawPixmap((ancho-360)//2, 40, img)
        painter.end()
        super().__init__(pixmap)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Sombra elegante
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0,0,0,60))
        shadow.setOffset(0, 12)
        self.setGraphicsEffect(shadow)
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
                p.drawPixmap(16, 16, 64, 64, logo_pix.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            p.end()
            self.logo.setPixmap(logo_bg)
            self.logo.setGeometry((ancho-96)//2, 60, 96, 96)
        # Mensaje y barra de carga minimalista
        self.label = QLabel(message, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 22px; font-weight: bold; background: transparent; font-family: 'Segoe UI', 'Arial', sans-serif;")
        self.label.setGeometry(0, alto-110, ancho, 40)
        self.progress = QProgressBar(self)
        self.progress.setGeometry(ancho//4, alto-60, ancho//2, 18)
        self.progress.setRange(0, 0)  # Barra indeterminada
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"QProgressBar {{background: {SECONDARY_COLOR}; border-radius: 9px;}} QProgressBar::chunk {{background: {ACCENT_COLOR}; border-radius: 9px;}}");
        self.duration = duration
        # Animación de opacidad
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(350)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)

    def mousePressEvent(self, event):
        # Ignorar cualquier clic del usuario en el splash
        pass

    def show_and_finish(self, main_window_callback):
        self.show()
        self.fade_in.start()
        # Esperar a que la ventana principal esté realmente visible antes de cerrar el splash
        def cerrar_splash():
            main_window_callback()
            self.fade_out.finished.connect(self.close)
            self.fade_out.start()
        QTimer.singleShot(self.duration, cerrar_splash)
