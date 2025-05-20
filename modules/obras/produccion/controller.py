from modules.auditoria.model import AuditoriaModel
from PyQt6.QtWidgets import QTableWidgetItem

class ProduccionController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.auditoria_model = AuditoriaModel(db_connection)
        self.view.boton_agregar.clicked.connect(self.agregar_etapa)
        self.view.boton_ver_detalles.clicked.connect(self.ver_detalles_abertura)
        self.view.boton_finalizar_etapa.clicked.connect(self.finalizar_etapa)

    def _registrar_evento_auditoria(self, tipo_evento, detalle, exito=True):
        usuario_id = self.usuario_actual['id'] if self.usuario_actual and 'id' in self.usuario_actual else None
        ip = self.usuario_actual.get('ip', '') if self.usuario_actual else ''
        estado = "éxito" if exito else "error"
        detalle_final = f"{detalle} - {estado}"
        self.auditoria_model.registrar_evento(usuario_id, "produccion", tipo_evento, detalle_final, ip)

    def agregar_etapa(self):
        """Agrega una nueva etapa de fabricación."""
        try:
            campos = {
                "abertura": self.view.abertura_input.text(),
                "etapa": self.view.etapa_input.text(),
                "estado": self.view.estado_input.text()
            }
            if not all(campos.values()):
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje("Por favor, complete todos los campos.", tipo='warning')
                elif hasattr(self.view, 'label'):
                    self.view.label.setText("Por favor, complete todos los campos.")
                self._registrar_evento_auditoria("agregar_etapa", "Campos incompletos", exito=False)
                return
            self.model.agregar_etapa((*campos.values(), None, None))
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje("Etapa agregada exitosamente.", tipo='exito')
            elif hasattr(self.view, 'label'):
                self.view.label.setText("Etapa agregada exitosamente.")
            self._registrar_evento_auditoria("agregar_etapa", f"Etapa agregada: {campos}")
        except Exception as e:
            mensaje = f"Error al agregar la etapa: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText("Error al agregar la etapa.")
            self._registrar_evento_auditoria("agregar_etapa", mensaje, exito=False)
            from core.logger import log_error
            log_error(mensaje)

    def ver_detalles_abertura(self):
        fila_seleccionada = self.view.tabla_aberturas.currentRow()
        if fila_seleccionada == -1:
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje("Seleccione una abertura para ver detalles.", tipo='warning')
            elif hasattr(self.view, 'label'):
                self.view.label.setText("Seleccione una abertura para ver detalles.")
            return
        id_abertura = self.view.tabla_aberturas.item(fila_seleccionada, 0).text()
        etapas = self.model.obtener_etapas_por_abertura(id_abertura)
        self.view.tabla_etapas.setRowCount(len(etapas))
        for row, etapa in enumerate(etapas):
            for col, value in enumerate(etapa):
                self.view.tabla_etapas.setItem(row, col, QTableWidgetItem(str(value)))

    def finalizar_etapa(self):
        """Finaliza una etapa de fabricación."""
        try:
            fila_seleccionada = self.view.tabla_etapas.currentRow()
            if fila_seleccionada == -1:
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje("Seleccione una etapa para finalizar.", tipo='warning')
                elif hasattr(self.view, 'label'):
                    self.view.label.setText("Seleccione una etapa para finalizar.")
                self._registrar_evento_auditoria("finalizar_etapa", "No se seleccionó etapa", exito=False)
                return
            id_etapa = self.view.tabla_etapas.item(fila_seleccionada, 0).text()
            fecha_fin = "2023-12-31"  # Ejemplo, debería obtenerse dinámicamente
            tiempo_real = "2 horas"  # Ejemplo, debería calcularse
            self.model.finalizar_etapa(id_etapa, fecha_fin, tiempo_real)
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Etapa {id_etapa} finalizada exitosamente.", tipo='exito')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(f"Etapa {id_etapa} finalizada exitosamente.")
            self._registrar_evento_auditoria("finalizar_etapa", f"Etapa finalizada: {id_etapa}")
        except Exception as e:
            mensaje = f"Error al finalizar la etapa: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText("Error al finalizar la etapa.")
            self._registrar_evento_auditoria("finalizar_etapa", mensaje, exito=False)
            from core.logger import log_error
            log_error(mensaje)

    def cargar_kanban(self):
        etapas = self.model.obtener_etapas_fabricacion()
        for etapa in etapas:
            id_abertura, etapa_nombre, estado = etapa
            tarjeta_texto = f"Abertura {id_abertura} - {estado}"
            self.view.agregar_tarjeta_kanban(etapa_nombre, tarjeta_texto)

    # --- Todos los métodos públicos deben validar argumentos, usar feedback visual moderno y registrar auditoría ---
