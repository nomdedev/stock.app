import hashlib
from core.base_controller import BaseController
from PyQt6.QtWidgets import QTableWidgetItem
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', UsuariosModel())
                auditoria_model = getattr(controller, 'auditoria_model', AuditoriaModel())
                usuario = getattr(controller, 'usuario_actual', None)
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                resultado = func(controller, *args, **kwargs)
                auditoria_model.registrar_evento(usuario, self.modulo, accion)
                return resultado
            return wrapper
        return decorador

permiso_auditoria_contabilidad = PermisoAuditoria('contabilidad')

class ContabilidadController(BaseController):
    def __init__(self, model, view, usuario_actual=None):
        super().__init__(model, view)
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel()
        self.auditoria_model = AuditoriaModel()

    def setup_view_signals(self):
        if hasattr(self.view, 'boton_agregar_recibo'):
            self.view.boton_agregar_recibo.clicked.connect(self.agregar_recibo)
        if hasattr(self.view, 'boton_generar_pdf'):
            self.view.boton_generar_pdf.clicked.connect(self.generar_recibo_pdf_desde_vista)

    @permiso_auditoria_contabilidad('agregar_recibo')
    def agregar_recibo(self):
        fecha_emision = self.view.fecha_emision_input.text()
        obra_id = self.view.obra_id_input.text()
        monto_total = self.view.monto_total_input.text()
        concepto = self.view.concepto_input.text()
        destinatario = self.view.destinatario_input.text()
        if fecha_emision and obra_id and monto_total and concepto and destinatario:
            firma_digital = hashlib.sha256(f"{fecha_emision}{obra_id}{monto_total}{concepto}{destinatario}".encode()).hexdigest()
            self.model.agregar_recibo((fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital, 1, "emitido", "archivo.pdf"))
            self.view.label.setText("Recibo agregado exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

    @permiso_auditoria_contabilidad('generar_recibo_pdf')
    def generar_recibo_pdf(self, id_recibo):
        mensaje = self.model.generar_recibo_pdf(id_recibo)
        self.view.label.setText(mensaje)

    def generar_recibo_pdf_desde_vista(self):
        fila_seleccionada = self.view.tabla_recibos.currentRow()
        if fila_seleccionada != -1:
            id_recibo = self.view.tabla_recibos.item(fila_seleccionada, 0).text()
            self.generar_recibo_pdf(id_recibo)
        else:
            self.view.label.setText("Seleccione un recibo para generar el PDF.")

    @permiso_auditoria_contabilidad('agregar_movimiento_contable')
    def agregar_movimiento_contable(self, datos):
        self.model.agregar_movimiento_contable(datos)
        if datos[2] > 10000:  # Notificar si el monto es mayor a 10,000
            self.view.label.setText("Movimiento elevado registrado. Notificación enviada.")
        else:
            self.view.label.setText("Movimiento registrado.")

    @permiso_auditoria_contabilidad('exportar_balance')
    def exportar_balance(self, formato):
        datos_balance = self.model.obtener_datos_balance()  # Método que debe obtener los datos del balance
        mensaje = self.model.exportar_balance(formato, datos_balance)
        self.view.label.setText(mensaje)

    @permiso_auditoria_contabilidad('generar_firma_digital')
    def generar_firma_digital(self, datos_recibo):
        firma = self.model.generar_firma_digital(datos_recibo)
        self.view.label.setText(f"Firma generada: {firma}")

    @permiso_auditoria_contabilidad('verificar_firma_digital')
    def verificar_firma_digital(self, id_recibo):
        es_valida = self.model.verificar_firma_digital(id_recibo)
        if es_valida == "Recibo no encontrado.":
            self.view.label.setText(es_valida)
        elif es_valida:
            self.view.label.setText("La firma digital es válida.")
        else:
            self.view.label.setText("La firma digital no es válida.")

    def actualizar_tabla_recibos(self):
        recibos = self.model.obtener_recibos()
        self.view.tabla_recibos.setRowCount(len(recibos))
        for row, recibo in enumerate(recibos):
            for col, value in enumerate(recibo[:6]):
                self.view.tabla_recibos.setItem(row, col, QTableWidgetItem(str(value)))

    def crear_recibo(self, obra_id, monto_total, concepto, destinatario):
        try:
            self.model.generar_recibo(obra_id, monto_total, concepto, destinatario)
            self.view.label.setText("Recibo creado exitosamente.")
        except Exception as e:
            self.view.label.setText(f"Error al crear el recibo: {e}")
