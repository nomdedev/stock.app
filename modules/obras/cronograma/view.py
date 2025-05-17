from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QGraphicsRectItem, QToolTip, QTableWidget, QLabel
from PyQt6.QtGui import QBrush, QColor, QPen, QFont, QLinearGradient, QPainter
from PyQt6.QtCore import Qt, QRectF
import datetime
from core.table_responsive_mixin import TableResponsiveMixin

# NOTA: Este módulo no utiliza QTableWidget principal, por lo que no aplica TableResponsiveMixin aquí.
# No requiere sincronización dinámica de headers ni menú contextual de columnas.

ESTADO_COLORES = {
    "Medición": QColor(100, 181, 246),      # Azul claro
    "Fabricación": QColor(255, 202, 40),    # Amarillo
    "Entrega": QColor(102, 187, 106),       # Verde
}

def parse_fecha_safe(fecha):
    # Soporta datetime.date, datetime.datetime, string 'YYYY-MM-DD', None
    if isinstance(fecha, datetime.date):
        return fecha
    if isinstance(fecha, datetime.datetime):
        return fecha.date()
    if isinstance(fecha, str):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.datetime.strptime(fecha, fmt).date()
            except Exception:
                continue
    return None

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
        fecha_inicio = parse_fecha_safe(self.obra.get('fecha'))
        fecha_entrega = parse_fecha_safe(self.obra.get('fecha_entrega'))
        if not fecha_inicio or not fecha_entrega:
            return
        dias_total = max(1, (fecha_entrega - fecha_inicio).days)
        dias_transcurridos = max(0, (hoy - fecha_inicio).days)
        dias_restantes = (fecha_entrega - hoy).days
        progreso = max(0, min(1, dias_transcurridos / dias_total)) if dias_total > 0 else 1
        porcentaje = int(progreso * 100)
        color_estado = ESTADO_COLORES.get(self.obra.get('estado', ''), QColor(120, 120, 120))
        color_estado_hex = color_estado.name() if hasattr(color_estado, 'name') else '#2196F3'
        texto = f"""
        <div style='background:#23272e; color:#fff; border-radius:10px; border:2px solid {color_estado_hex}; padding:10px; min-width:220px;'>
            <b style='font-size:15px; color:{color_estado_hex};'>{self.obra.get('nombre','')}</b><br>
            <span style='color:#bbb'>Cliente:</span> {self.obra.get('cliente','')}<br>
            <span style='color:#bbb'>Estado:</span> <b style='color:{color_estado_hex}'>{self.obra.get('estado','')}</b><br>
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
        color_estado = ESTADO_COLORES.get(self.obra.get('estado', ''), QColor(120, 120, 120))
        grad = QLinearGradient(rect.x(), rect.y(), rect.x() + rect.width(), rect.y())
        grad.setColorAt(0, color_estado.lighter(120))
        grad.setColorAt(1, color_estado.darker(120))
        brush = QBrush(grad)
        painter.setBrush(brush)
        pen = QPen(color_estado.darker(150), 2)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.drawRoundedRect(rect, 8, 8)
        hoy = datetime.date.today()
        fecha_inicio = parse_fecha_safe(self.obra.get('fecha'))
        fecha_entrega = parse_fecha_safe(self.obra.get('fecha_entrega'))
        if not fecha_inicio or not fecha_entrega:
            return
        dias_total = max(1, (fecha_entrega - fecha_inicio).days)
        dias_transcurridos = max(0, (hoy - fecha_inicio).days)
        progreso = max(0, min(1, dias_transcurridos / dias_total)) if dias_total > 0 else 1
        ancho = int(rect.width() * progreso)
        if ancho > 0:
            painter.save()
            painter.setBrush(QColor(60, 180, 75, 180))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(rect.x()), int(rect.y()), ancho, int(rect.height()), 8, 8)
            painter.restore()
        if self.hovered:
            painter.save()
            painter.setBrush(QColor(60, 180, 75, 60))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            painter.restore()
        if fecha_inicio <= hoy <= fecha_entrega:
            x_hoy = int(rect.x() + rect.width() * progreso)
            painter.save()
            painter.setPen(QPen(QColor(230, 57, 53), 2, Qt.PenStyle.DashLine))
            painter.drawLine(x_hoy, int(rect.y()), x_hoy, int(rect.y() + rect.height()))
            painter.restore()

class CronogramaView(QWidget, TableResponsiveMixin):
    def __init__(self, obras=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: white; border-radius: 10px;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 8, 16, 8)
        self.layout.setSpacing(4)
        self.gantt_view = QGraphicsView()
        self.gantt_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.gantt_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.layout.addWidget(self.gantt_view)
        self.setLayout(self.layout)
        self.tabla_cronograma = QTableWidget()
        self.make_table_responsive(self.tabla_cronograma)
        self.label = QLabel()
        self.obras = []
        self._zoom_factor = 0.8
        self._min_day_width = 4
        self._max_day_width = 40
        self._base_day_width = 18
        self.set_obras(obras or [])

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
        # Robustez: acepta lista de dicts, ignora obras sin fechas válidas
        self.obras = []
        for o in obras or []:
            try:
                fecha = parse_fecha_safe(o.get('fecha'))
                fecha_entrega = parse_fecha_safe(o.get('fecha_entrega'))
                if not fecha or not fecha_entrega:
                    continue
                self.obras.append({
                    'id': o.get('id'),
                    'nombre': o.get('nombre', ''),
                    'cliente': o.get('cliente', ''),
                    'estado': o.get('estado', ''),
                    'fecha': fecha,
                    'fecha_entrega': fecha_entrega,
                })
            except Exception:
                continue
        self._draw_gantt()

    def mostrar_mensaje(self, texto, tipo="info"):
        # tipo: info, exito, advertencia, error
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        self.label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.label.setText(texto)

    def mostrar_error(self, texto):
        self.mostrar_mensaje(texto, tipo="error")

    def _draw_gantt(self):
        scene = QGraphicsScene(self)
        if not self.obras:
            self.gantt_view.setScene(scene)
            return
        fechas_inicio = [o['fecha'] for o in self.obras]
        fechas_fin = [o['fecha_entrega'] for o in self.obras]
        fecha_min = min(fechas_inicio)
        fecha_max = max(fechas_fin)
        dias_totales = (fecha_max - fecha_min).days + 1
        if dias_totales < 90:
            dias_totales = 90
            fecha_max = fecha_min + datetime.timedelta(days=89)
        row_height = 70
        bar_height = 32
        left_margin = 140
        top_margin = 60
        day_width = max(self._min_day_width, min(self._base_day_width * self._zoom_factor, self._max_day_width))
        font = QFont("Segoe UI", 11)
        font_bold = QFont("Segoe UI", 11)
        font_bold.setBold(True)
        fechas_entrega_set = set(o['fecha_entrega'] for o in self.obras if o['fecha_entrega'])
        # Líneas verticales por semana
        for d in range(0, dias_totales, 7):
            x = left_margin + d * day_width
            scene.addLine(x, top_margin, x, top_margin + len(self.obras)*row_height, QPen(QColor(220,220,220), 1, Qt.PenStyle.DashLine))
            fecha = fecha_min + datetime.timedelta(days=d)
            if fecha in fechas_entrega_set:
                text = scene.addText(fecha.strftime("%d/%m"), font_bold)
                text.setDefaultTextColor(QColor(200, 40, 40))
            else:
                text = scene.addText(fecha.strftime("%d/%m"), font)
                text.setDefaultTextColor(QColor(120,120,120))
            text.setPos(x-18, 10)
        # Marcas visuales para cada fecha de entrega
        for fecha_entrega in fechas_entrega_set:
            dias = (fecha_entrega - fecha_min).days
            if 0 <= dias < dias_totales:
                x = left_margin + dias * day_width
                scene.addLine(x, top_margin, x, top_margin + len(self.obras)*row_height, QPen(QColor(200,40,40), 2, Qt.PenStyle.SolidLine))
                text = scene.addText(fecha_entrega.strftime("%d/%m"), font_bold)
                text.setDefaultTextColor(QColor(200, 40, 40))
                text.setPos(x-18, 10)
        hoy = datetime.date.today()
        for idx, obra in enumerate(self.obras):
            y = top_margin + idx * row_height
            nombre = obra.get('nombre', '')
            cliente = obra.get('cliente', '')
            fecha = obra.get('fecha')
            fecha_entrega = obra.get('fecha_entrega')
            estado = obra.get('estado', '')
            nombre_html = f"""
                <div style='font-size:15px;font-weight:bold;color:#2563eb'>{nombre}</div>
                <div style='font-size:12px;color:#555'>{cliente}</div>
                <div style='font-size:11px;color:#888'>Medición: {fecha.strftime('%d/%m/%Y')} | Entrega: <b style='color:#e53935'>{fecha_entrega.strftime('%d/%m/%Y')}</b></div>
            """
            text_widget = scene.addText(nombre, font)
            # setHtml solo disponible en PyQt6 >= 6.4, fallback seguro
            if hasattr(text_widget, "setHtml"):
                try:
                    text_widget.setHtml(nombre_html)
                except Exception:
                    text_widget.setPlainText(f"{nombre}\n{cliente}\nMedición: {fecha.strftime('%d/%m/%Y')} | Entrega: {fecha_entrega.strftime('%d/%m/%Y')}")
            else:
                text_widget.setPlainText(f"{nombre}\n{cliente}\nMedición: {fecha.strftime('%d/%m/%Y')} | Entrega: {fecha_entrega.strftime('%d/%m/%Y')}")
            text_widget.setPos(10, y+row_height/2-18)
            inicio = (fecha - fecha_min).days
            fin = (fecha_entrega - fecha_min).days
            x1 = left_margin + inicio * day_width
            x2 = left_margin + fin * day_width
            color = ESTADO_COLORES.get(estado, QColor(200,200,200))
            rect = QRectF(x1, y+10, max(10, x2-x1), bar_height)  # Asegura ancho mínimo
            bar = GanttBarItem(obra, rect, fecha_min)
            bar.setBrush(QBrush(color))
            bar.setPen(QPen(Qt.GlobalColor.transparent))
            scene.addItem(bar)
            label = f"<span style='font-weight:bold;color:#2563eb'>{estado}</span>"
            t = scene.addText(cliente + ' - ' + estado, font)
            if hasattr(t, "setHtml"):
                try:
                    t.setHtml(label)
                except Exception:
                    t.setPlainText(estado)
            else:
                t.setPlainText(estado)
            t.setPos(x1+8, y+14)
        scene.setSceneRect(0, 0, left_margin + dias_totales*day_width + 100, top_margin + len(self.obras)*row_height + 60)
        self.gantt_view.setScene(scene)
        self._apply_zoom()
