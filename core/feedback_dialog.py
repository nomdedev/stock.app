from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import os
from core.ui_components import aplicar_qss_global_y_tema

class FeedbackDialog(QDialog):
    ICONOS = {
        "info": ("resources/icons/info-blue.svg", "ℹ️"),
        "exito": ("resources/icons/check-green.svg", "✅"),
        "error": ("resources/icons/error-red.svg", "❌"),
        "advertencia": ("resources/icons/warning-yellow.svg", "⚠️"),
    }
    COLORES = {
        "info": ("#e3f6fd", "#2563eb"),
        "exito": ("#d1f7e7", "#15803d"),
        "error": ("#fee2e2", "#b91c1c"),
        "advertencia": ("#fef9c3", "#b45309"),
    }
    def __init__(self, titulo, mensaje, detalles, tipo="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setObjectName("feedback_dialog_dependencias")
        self.setFixedSize(440, 240)
        self.setStyleSheet("QDialog#feedback_dialog_dependencias { border-radius: 14px; border: 1.5px solid #e3e3e3; background: #fff; }")
        qss_global = os.path.join(os.path.dirname(__file__), "..", "resources", "qss", "theme_light.qss")
        aplicar_qss_global_y_tema(self, qss_global)
        color_fondo, color_texto = self.COLORES.get(tipo, ("#e3f6fd", "#2563eb"))
        icon_path, emoji = self.ICONOS.get(tipo, (None, "ℹ️"))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Banner superior
        banner = QFrame()
        banner.setObjectName("banner_feedback_dialog")
        banner.setStyleSheet(f"background: {color_fondo}; border-top-left-radius: 14px; border-top-right-radius: 14px; border-bottom: 1px solid #e3e3e3;")
        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(20, 20, 20, 20)
        banner_layout.setSpacing(12)
        icon_label = QLabel()
        icon_label.setObjectName("icono_feedback_dialog")
        if icon_path and os.path.exists(icon_path):
            icon_label.setPixmap(QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            icon_label.setText(emoji)
            icon_label.setFont(QFont("Segoe UI Emoji", 22))
        banner_layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignTop)
        msg_label = QLabel(mensaje)
        msg_label.setObjectName("label_feedback")
        msg_label.setProperty("feedback_tipo", tipo)
        msg_label.setStyleSheet(f"font-size: 1.2rem; font-weight: bold; color: {color_texto}; margin-bottom: 0px;")
        msg_label.setWordWrap(True)
        banner_layout.addWidget(msg_label, 1, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(banner)
        # Detalles
        detalles_frame = QFrame()
        detalles_frame.setStyleSheet(f"background: #f9fafb; border-radius: 8px; border: 1px solid #d1d5db; margin: 16px 20px 0 20px;")
        detalles_layout = QVBoxLayout(detalles_frame)
        detalles_layout.setContentsMargins(12, 8, 12, 8)
        detalles_label = QLabel(detalles)
        detalles_label.setObjectName("label_feedback_detalles")
        detalles_label.setStyleSheet(f"font-size: 14px; color: #1f2937; padding: 8px;")
        detalles_label.setWordWrap(True)
        detalles_layout.addWidget(detalles_label)
        layout.addWidget(detalles_frame)
        # Botón de cierre
        btn = QPushButton("Cerrar")
        btn.setObjectName("boton_cerrar_feedback_dialog")
        btn.setFixedHeight(32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("background:#3b82f6;color:white;border-radius:8px;font-size:15px;font-weight:600;margin:20px;padding:8px 24px;")
        btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(btn_layout)
