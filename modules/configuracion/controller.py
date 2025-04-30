class ConfiguracionController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_guardar_cambios.clicked.connect(self.guardar_cambios)

    def cargar_configuracion(self):
        configuracion = self.model.obtener_configuracion()
        for clave, valor, descripcion in configuracion:
            if clave == "nombre_app":
                self.view.nombre_app_input.setText(valor)
            elif clave == "zona_horaria":
                self.view.zona_horaria_input.setCurrentText(valor)
            elif clave == "modo_mantenimiento":
                self.view.modo_mantenimiento_checkbox.setChecked(valor == "True")

        # Cargar apariencia del usuario (ejemplo con usuario_id = 1)
        apariencia = self.model.obtener_apariencia_usuario(1)
        if apariencia:
            modo_color, idioma, notificaciones, tamaño_fuente = apariencia[0]
            self.view.modo_color_input.setCurrentText(modo_color)
            self.view.idioma_input.setCurrentText(idioma)
            self.view.notificaciones_checkbox.setChecked(notificaciones)
            self.view.tamaño_fuente_input.setCurrentText(tamaño_fuente)

    def guardar_cambios(self):
        # Guardar configuración general
        self.model.actualizar_configuracion("nombre_app", self.view.nombre_app_input.text())
        self.model.actualizar_configuracion("zona_horaria", self.view.zona_horaria_input.currentText())
        self.model.actualizar_configuracion("modo_mantenimiento", str(self.view.modo_mantenimiento_checkbox.isChecked()))

        # Guardar apariencia del usuario (ejemplo con usuario_id = 1)
        datos_apariencia = (
            self.view.modo_color_input.currentText(),
            self.view.idioma_input.currentText(),
            self.view.notificaciones_checkbox.isChecked(),
            self.view.tamaño_fuente_input.currentText()
        )
        self.model.actualizar_apariencia_usuario(1, datos_apariencia)

        self.view.label.setText("Cambios guardados exitosamente.")

    def guardar_configuracion_conexion(self):
        datos = {
            "base_predeterminada": self.view.base_predeterminada_input.text(),
            "servidor": self.view.servidor_input.text(),
            "puerto": self.view.puerto_input.text(),
        }
        self.model.guardar_configuracion_conexion(datos)
        self.view.label.setText("Configuración de conexión guardada exitosamente.")

    def activar_modo_offline(self):
        self.model.activar_modo_offline()
        self.view.label.setText("Modo offline activado.")

    def desactivar_modo_offline(self):
        self.model.desactivar_modo_offline()
        self.view.label.setText("Modo offline desactivado.")

    def cambiar_estado_notificaciones(self):
        estado_actual = self.model.obtener_estado_notificaciones()
        nuevo_estado = not estado_actual
        self.model.actualizar_estado_notificaciones(nuevo_estado)
        self.view.label.setText(f"Notificaciones {'activadas' if nuevo_estado else 'desactivadas'}.")
