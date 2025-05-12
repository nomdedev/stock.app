from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QGraphicsRectItem, QToolTip
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QLinearGradient, QPainter
from PyQt6.QtCore import Qt, QRectF
import datetime

ESTADO_COLORES = {
    "Medición": QColor(100, 181, 246),      # Azul claro
    "Fabricación": QColor(255, 202, 40),    # Amarillo
    "Entrega": QColor(102, 187, 106),       # Verde
}

class GanttBarItem(QGraphicsRectItem):
    def __init__(self, obra, rect, fecha_min, parent=None):
        super().__init__(rect, parent)
        self.obra = obra
        self.fecha_min = fecha_min
        self.setAcceptHoverEvents(True)
        self.setZValue(1)
        self.hovered = False

    def hoverEnterEvent(self, event):
        self.hovered = True
        hoy = datetime.date.today()
        fecha_inicio = self.obra['fecha']
        fecha_entrega = self.obra['fecha_entrega']
        dias_total = (fecha_entrega - fecha_inicio).days
        dias_transcurridos = (hoy - fecha_inicio).days
        dias_restantes = (fecha_entrega - hoy).days
        progreso = max(0, min(1, dias_transcurridos / dias_total)) if dias_total > 0 else 1
        porcentaje = int(progreso * 100)
        # Tooltip visual moderno
        color_estado = ESTADO_COLORES.get(self.obra['estado'], QColor(120, 120, 120))
        color_estado_hex = color_estado.name() if hasattr(color_estado, 'name') else '#2196F3'
        texto = f"""
        <div style='background:#23272e; color:#fff; border-radius:10px; border:2px solid {color_estado_hex}; padding:10px; min-width:220px;'>
            <b style='font-size:15px; color:{color_estado_hex};'>{self.obra['nombre']}</b><br>
            <span style='color:#bbb'>Cliente:</span> {self.obra['cliente']}<br>
            <span style='color:#bbb'>Estado:</span> <b style='color:{color_estado_hex}'>{self.obra['estado']}</b><br>
            <span style='color:#bbb'>Entrega:</span> <b style='color:#e53935'>{fecha_entrega.strftime('%d/%m/%Y')}</b><br>
            {f"<span style='color:#43a047'>Faltan: {dias_restantes} días</span>" if dias_restantes >= 0 else f"<span style='color:#e53935'>Vencido hace {-dias_restantes} días</span>"}<br>
            <span style='color:#bbb'>Progreso:</span> <b>{porcentaje}%</b>
            <div style='background:#181c20;border-radius:6px;width:120px;height:12px;margin-top:6px;'><div style='background:#43a047;width:{porcentaje}%;height:12px;border-radius:6px;'></div></div>
        </div>
        """
        QToolTip.setFont(QFont('Segoe UI', 11))
        QToolTip.showText(event.screenPos(), texto)
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hovered = False
        QToolTip.hideText()
        self.update()
        super().hoverLeaveEvent(event)

    def paint(self, painter, option, widget=None):
        rect = self.rect()
        color_estado = ESTADO_COLORES.get(self.obra['estado'], QColor(120, 120, 120))
        grad = QLinearGradient(rect.x(), rect.y(), rect.x() + rect.width(), rect.y())
        grad.setColorAt(0, color_estado.lighter(120))
        grad.setColorAt(1, color_estado.darker(120))
        brush = QBrush(grad)
        painter.setBrush(brush)
        pen = QPen(color_estado.darker(150), 2)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawRoundedRect(rect, 8, 8)
        # Barra de progreso encima
        hoy = datetime.date.today()
        fecha_inicio = self.obra['fecha']
        fecha_entrega = self.obra['fecha_entrega']
        dias_total = (fecha_entrega - fecha_inicio).days
        dias_transcurridos = (hoy - fecha_inicio).days
        progreso = max(0, min(1, dias_transcurridos / dias_total)) if dias_total > 0 else 1
        ancho = int(rect.width() * progreso)
        if ancho > 0:
            painter.save()
            painter.setBrush(QColor(60, 180, 75, 180))  # Verde semitransparente
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(rect.x()), int(rect.y()), ancho, int(rect.height()), 8, 8)
            painter.restore()
        # Animación de opacidad al hacer hover
        if self.hovered:
            painter.save()
            painter.setBrush(QColor(60, 180, 75, 60))  # Verde más notorio en hover
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            painter.restore()
        # Línea de hoy
        if fecha_inicio <= hoy <= fecha_entrega:
            x_hoy = int(rect.x() + rect.width() * progreso)
            painter.save()
            painter.setPen(QPen(QColor(230, 57, 53), 2, Qt.PenStyle.DashLine))
            painter.drawLine(x_hoy, int(rect.y()), x_hoy, int(rect.y() + rect.height()))
            painter.restore()

class CronogramaView(QWidget):
    def __init__(self, obras=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white; border-radius: 10px;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 8, 16, 8)  # Menos margen superior e inferior
        self.layout.setSpacing(4)  # Menor separación
        self.gantt_view = QGraphicsView()
        self.gantt_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.gantt_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.layout.addWidget(self.gantt_view)
        self.setLayout(self.layout)
        self.obras = obras or []
        self._zoom_factor = 0.8  # Zoom por defecto x0.8
        self._min_day_width = 4
        self._max_day_width = 40
        self._base_day_width = 18
        self._draw_gantt()
        self._apply_zoom()

    def zoom_in(self):
        if self._base_day_width * self._zoom_factor < self._max_day_width:
            self._zoom_factor *= 1.15
            self._draw_gantt()

    def zoom_out(self):
        if self._base_day_width * self._zoom_factor > self._min_day_width:
            self._zoom_factor /= 1.15
            self._draw_gantt()

    def _apply_zoom(self):
        self.gantt_view.resetTransform()
        self.gantt_view.scale(self._zoom_factor, self._zoom_factor)

    def set_obras(self, obras):
        self.obras = obras
        self._draw_gantt()

    def _draw_gantt(self):
        scene = QGraphicsScene(self)
        if not self.obras:
            self.gantt_view.setScene(scene)
            return
        # Calcular fechas mínimas y máximas
        fechas_inicio = [o['fecha'] for o in self.obras]
        fechas_fin = [o['fecha_entrega'] for o in self.obras]
        fecha_min = min(fechas_inicio)
        fecha_max = max(fechas_fin)
        dias_totales = (fecha_max - fecha_min).days + 1
        # Asegurar al menos 90 días de visualización
        if dias_totales < 90:
            dias_totales = 90
            fecha_max = fecha_min + datetime.timedelta(days=89)
        # Parámetros visuales
        row_height = 50
        bar_height = 28
        left_margin = 120
        top_margin = 40
        day_width = max(self._min_day_width, min(self._base_day_width * self._zoom_factor, self._max_day_width))
        font = QFont("Segoe UI", 10)
        font_bold = QFont("Segoe UI", 10)
        font_bold.setBold(True)
        # Fechas de entrega a resaltar
        fechas_entrega_set = set(o['fecha_entrega'] for o in self.obras if o['fecha_entrega'])
        # Dibujar líneas verticales por semana
        for d in range(0, dias_totales, 7):
            x = left_margin + d * day_width
            scene.addLine(x, top_margin, x, top_margin + len(self.obras)*row_height, QPen(QColor(220,220,220), 1, Qt.PenStyle.DashLine))
            # Etiqueta de fecha
            fecha = fecha_min + datetime.timedelta(days=d)
            if fecha in fechas_entrega_set:
                text = scene.addText(fecha.strftime("%d/%m"), font_bold)
                text.setDefaultTextColor(QColor(200, 40, 40))  # Rojo oscuro
            else:
                text = scene.addText(fecha.strftime("%d/%m"), font)
                text.setDefaultTextColor(QColor(120,120,120))
            text.setPos(x-18, 10)
        # Dibujar marcas visuales para cada fecha de entrega
        for fecha_entrega in fechas_entrega_set:
            dias = (fecha_entrega - fecha_min).days
            if 0 <= dias < dias_totales:
                x = left_margin + dias * day_width
                # Línea vertical sólida
                scene.addLine(x, top_margin, x, top_margin + len(self.obras)*row_height, QPen(QColor(200,40,40), 2, Qt.PenStyle.SolidLine))
                # Etiqueta de fecha (ya dibujada si coincide con semana, pero la reforzamos)
                text = scene.addText(fecha_entrega.strftime("%d/%m"), font_bold)
                text.setDefaultTextColor(QColor(200, 40, 40))
                text.setPos(x-18, 10)
        # Dibujar filas y barras
        hoy = datetime.date.today()
        for idx, obra in enumerate(self.obras):
            y = top_margin + idx * row_height
            # Nombre de la obra
            text = scene.addText(obra['nombre'], font)
            text.setDefaultTextColor(QColor(60,60,60))
            text.setPos(10, y+row_height/2-10)
            # Barra de Gantt
            inicio = (obra['fecha'] - fecha_min).days
            fin = (obra['fecha_entrega'] - fecha_min).days
            x1 = left_margin + inicio * day_width
            x2 = left_margin + fin * day_width
            color = ESTADO_COLORES.get(obra['estado'], QColor(200,200,200))
            rect = QRectF(x1, y+10, x2-x1, bar_height)
            bar = GanttBarItem(obra, rect, fecha_min)
            bar.setBrush(QBrush(color))
            bar.setPen(QPen(Qt.GlobalColor.transparent))
            scene.addItem(bar)
            # Texto sobre la barra
            label = f"{obra['cliente']} - {obra['estado']}"
            t = scene.addText(label, font)
            t.setDefaultTextColor(QColor(30,30,30))
            t.setPos(x1+8, y+14)
        # Ajustar tamaño de la escena
        scene.setSceneRect(0, 0, left_margin + dias_totales*day_width + 100, top_margin + len(self.obras)*row_height + 60)
        self.gantt_view.setScene(scene)
