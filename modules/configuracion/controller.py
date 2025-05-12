from utils.theme_manager import aplicar_tema, guardar_modo_tema
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QApplication

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

permiso_auditoria_configuracion = PermisoAuditoria('configuracion')

class ConfiguracionController:
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        try:
            # Validar y conectar botones
            if hasattr(self.view, "save_button"):
                self.view.save_button.clicked.connect(self.guardar_cambios)
            if hasattr(self.view, "switch_tema"):
                self.view.switch_tema.stateChanged.connect(self.toggle_tema)
            if hasattr(self.view, "boton_activar_offline"):
                self.view.boton_activar_offline.clicked.connect(self.activar_modo_offline)
            if hasattr(self.view, "boton_desactivar_offline"):
                self.view.boton_desactivar_offline.clicked.connect(self.desactivar_modo_offline)
            if hasattr(self.view, "boton_guardar_conexion"):
                self.view.boton_guardar_conexion.clicked.connect(self.guardar_configuracion_conexion)
            if hasattr(self.view, "boton_cambiar_notificaciones"):
                self.view.boton_cambiar_notificaciones.clicked.connect(self.cambiar_estado_notificaciones)
        except AttributeError as e:
            print(f"Error en ConfiguracionController: {e}")

    @permiso_auditoria_configuracion('ver')
    def cargar_configuracion(self):
        try:
            configuracion = self.model.obtener_configuracion()
            for clave, valor, descripcion in configuracion:
                inputs = {
                    "nombre_app": self.view.nombre_app_input.setText,
                    "zona_horaria": self.view.zona_horaria_input.setCurrentText,
                    "modo_mantenimiento": lambda v: self.view.modo_mantenimiento_checkbox.setChecked(v == "True")
                }
                if clave in inputs:
                    inputs[clave](valor)

            # Cargar apariencia del usuario (ejemplo con usuario_id = 1)
            apariencia = self.model.obtener_apariencia_usuario(1)
            if apariencia:
                modo_color, idioma, notificaciones, tamaño_fuente = apariencia[0]
                self.view.modo_color_input.setCurrentText(modo_color)
                self.view.idioma_input.setCurrentText(idioma)
                self.view.notificaciones_checkbox.setChecked(notificaciones)
                self.view.tamaño_fuente_input.setCurrentText(tamaño_fuente)
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    @permiso_auditoria_configuracion('editar')
    def guardar_cambios(self):
        try:
            # Guardar configuración general
            self.model.actualizar_configuracion("nombre_app", self.view.nombre_app_input.text())
            self.model.actualizar_configuracion("zona_horaria", self.view.zona_horaria_input.currentText())
            self.model.actualizar_configuracion("modo_mantenimiento", str(self.view.modo_mantenimiento_checkbox.isChecked()))

            # Guardar apariencia del usuario
            datos_apariencia = (
                self.view.modo_color_input.currentText(),
                self.view.idioma_input.currentText(),
                self.view.notificaciones_checkbox.isChecked(),
                self.view.tamaño_fuente_input.currentText()
            )
            self.model.actualizar_apariencia_usuario(1, datos_apariencia)

            self.view.label.setText("Cambios guardados exitosamente.")
        except Exception as e:
            print(f"Error al guardar cambios: {e}")

    @permiso_auditoria_configuracion('editar')
    def guardar_configuracion_conexion(self):
        try:
            datos = {
                "base_predeterminada": self.view.base_predeterminada_input.text(),
                "servidor": self.view.servidor_input.text(),
                "puerto": self.view.puerto_input.text(),
            }
            self.model.guardar_configuracion_conexion(datos)
            self.view.label.setText("Configuración de conexión guardada exitosamente.")
        except Exception as e:
            print(f"Error al guardar configuración de conexión: {e}")

    @permiso_auditoria_configuracion('editar')
    def activar_modo_offline(self):
        try:
            self.model.activar_modo_offline()
            self.view.label.setText("Modo offline activado.")
        except Exception as e:
            print(f"Error al activar el modo offline: {e}")

    @permiso_auditoria_configuracion('editar')
    def desactivar_modo_offline(self):
        try:
            self.model.desactivar_modo_offline()
            self.view.label.setText("Modo offline desactivado.")
        except Exception as e:
            print(f"Error al desactivar el modo offline: {e}")

    @permiso_auditoria_configuracion('editar')
    def cambiar_estado_notificaciones(self):
        try:
            estado_actual = self.model.obtener_estado_notificaciones()
            nuevo_estado = not estado_actual
            self.model.actualizar_estado_notificaciones(nuevo_estado)
            self.view.label.setText(f"Notificaciones {'activadas' if nuevo_estado else 'desactivadas'}.")
        except Exception as e:
            print(f"Error al cambiar estado de notificaciones: {e}")

    @permiso_auditoria_configuracion('editar')
    def toggle_tema(self, estado):
        try:
            modos = {0: "light", 2: "oscuro"}  # Diccionario para evitar condicionales
            nuevo_modo = modos.get(estado, "light")
            aplicar_tema(QApplication.instance(), nuevo_modo)
            guardar_modo_tema(nuevo_modo)
            # Llamar a recargar_tema en la ventana principal si está disponible
            app = QApplication.instance()
            if hasattr(app, 'main_window'):
                app.main_window.recargar_tema()
        except Exception as e:
            print(f"Error al cambiar tema: {e}")
