class ProduccionController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_etapa)
        self.view.boton_ver_detalles.clicked.connect(self.ver_detalles_abertura)
        self.view.boton_finalizar_etapa.clicked.connect(self.finalizar_etapa)

    def agregar_etapa(self):
        """Agrega una nueva etapa de fabricación."""
        try:
            campos = {
                "abertura": self.view.abertura_input.text(),
                "etapa": self.view.etapa_input.text(),
                "estado": self.view.estado_input.text()
            }

            if not all(campos.values()):
                self.view.label.setText("Por favor, complete todos los campos.")
                return

            self.model.agregar_etapa((*campos.values(), None, None))
            self.view.label.setText("Etapa agregada exitosamente.")
        except Exception as e:
            print(f"Error al agregar etapa: {e}")
            self.view.label.setText("Error al agregar la etapa.")

    def ver_detalles_abertura(self):
        fila_seleccionada = self.view.tabla_aberturas.currentRow()
        if fila_seleccionada == -1:
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
                self.view.label.setText("Seleccione una etapa para finalizar.")
                return

            id_etapa = self.view.tabla_etapas.item(fila_seleccionada, 0).text()
            fecha_fin = "2023-12-31"  # Ejemplo, debería obtenerse dinámicamente
            tiempo_real = "2 horas"  # Ejemplo, debería calcularse
            self.model.finalizar_etapa(id_etapa, fecha_fin, tiempo_real)
            self.view.label.setText(f"Etapa {id_etapa} finalizada exitosamente.")
        except Exception as e:
            print(f"Error al finalizar etapa: {e}")
            self.view.label.setText("Error al finalizar la etapa.")

    def cargar_kanban(self):
        etapas = self.model.obtener_etapas_fabricacion()
        for etapa in etapas:
            id_abertura, etapa_nombre, estado = etapa
            tarjeta_texto = f"Abertura {id_abertura} - {estado}"
            self.view.agregar_tarjeta_kanban(etapa_nombre, tarjeta_texto)
