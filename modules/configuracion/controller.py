from utils.theme_manager import aplicar_tema, guardar_modo_tema
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QCheckBox
import pandas as pd
import pyodbc
import os
from scripts.procesar_e_importar_inventario import importar_inventario_desde_archivo

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
    """
    Controlador para el módulo de Configuración.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_configuracion,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_configuracion('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_configuracion('editar')
        def guardar_cambios(self):
            ...
    """
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.db_connection = db_connection
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
            # Conectar señales para la pestaña de importación CSV
            if hasattr(self.view, "boton_seleccionar_csv"):
                self.view.boton_seleccionar_csv.clicked.connect(self.seleccionar_archivo_csv)
            if hasattr(self.view, "boton_importar_csv"):
                self.view.boton_importar_csv.clicked.connect(self.importar_csv_inventario)
            # Conectar lógica de la pestaña de permisos y visibilidad
            if hasattr(self.view, "boton_guardar_permisos"):
                self.conectar_pestana_permisos()
            # Conectar botón de probar conexión
            if hasattr(self.view, "boton_probar_conexion"):
                self.view.boton_probar_conexion.clicked.connect(self.probar_conexion_bd)
        except AttributeError as e:
            print(f"Error en ConfiguracionController: {e}")
        except Exception as e:
            print(f"Error al conectar señales de importación CSV: {e}")

    def mostrar_mensaje(self, mensaje, tipo="info", destino="label"):
        """
        Muestra un mensaje visual moderno en el label indicado de la vista.
        tipo: 'exito', 'error', 'advertencia', 'info'
        destino: nombre del atributo QLabel en la vista (por defecto 'label')
        """
        colores = {
            "exito": "#22c55e",
            "error": "#ef4444",
            "advertencia": "#f59e42",
            "info": "#2563eb"
        }
        iconos = {
            "exito": "✅",
            "error": "❌",
            "advertencia": "⚠️",
            "info": "ℹ️"
        }
        color = colores.get(tipo, "#2563eb")
        icono = iconos.get(tipo, "ℹ️")
        label = getattr(self.view, destino, None)
        if label:
            label.setText(f"<span style='color:{color};'>{icono} {mensaje}</span>")

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
            self.mostrar_mensaje(f"Error al cargar configuración: {e}", tipo="error")

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

            self.mostrar_mensaje("Cambios guardados exitosamente.", tipo="exito")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar cambios: {e}", tipo="error")

    @permiso_auditoria_configuracion('editar')
    def guardar_configuracion_conexion(self):
        try:
            campos_obligatorios = [
                (self.view.server_input, "Servidor"),
                (self.view.username_input, "Usuario"),
                (self.view.password_input, "Contraseña"),
                (self.view.default_db_input, "Base de datos")
            ]
            for campo, nombre in campos_obligatorios:
                if not campo.text().strip():
                    self.mostrar_mensaje(f"El campo '{nombre}' es obligatorio.", tipo="error", destino="resultado_conexion_label")
                    return
            datos = {
                "servidor": self.view.server_input.text(),
                "usuario": self.view.username_input.text(),
                "contraseña": self.view.password_input.text(),
                "puerto": self.view.port_input.text(),
                "base_predeterminada": self.view.default_db_input.text(),
                "timeout": self.view.timeout_input.text(),
            }
            # Probar conexión antes de guardar
            resultado = self.probar_conexion_bd(retornar_resultado=True)
            if not resultado.get('exito'):
                self.mostrar_mensaje(f"No se puede guardar: {resultado.get('mensaje')}", tipo="error", destino="resultado_conexion_label")
                return
            self.model.guardar_configuracion_conexion(datos)
            self.mostrar_mensaje("Configuración guardada correctamente", tipo="exito", destino="resultado_conexion_label")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar: {str(e)}", tipo="error", destino="resultado_conexion_label")

    @permiso_auditoria_configuracion('editar')
    def activar_modo_offline(self):
        try:
            self.model.activar_modo_offline()
            self.mostrar_mensaje("Modo offline activado.", tipo="info")
        except Exception as e:
            self.mostrar_mensaje(f"Error al activar el modo offline: {e}", tipo="error")

    @permiso_auditoria_configuracion('editar')
    def desactivar_modo_offline(self):
        try:
            self.model.desactivar_modo_offline()
            self.mostrar_mensaje("Modo offline desactivado.", tipo="info")
        except Exception as e:
            self.mostrar_mensaje(f"Error al desactivar el modo offline: {e}", tipo="error")

    @permiso_auditoria_configuracion('editar')
    def cambiar_estado_notificaciones(self):
        try:
            estado_actual = self.model.obtener_estado_notificaciones()
            nuevo_estado = not estado_actual
            self.model.actualizar_estado_notificaciones(nuevo_estado)
            self.mostrar_mensaje(f"Notificaciones {'activadas' if nuevo_estado else 'desactivadas'}.", tipo="info")
        except Exception as e:
            self.mostrar_mensaje(f"Error al cambiar estado de notificaciones: {e}", tipo="error")

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
            self.mostrar_mensaje(f"Error al cambiar tema: {e}", tipo="error")

    # --- Métodos para la pestaña de importación CSV ---
    def seleccionar_archivo_csv(self):
        from PyQt6.QtWidgets import QFileDialog
        archivo, _ = QFileDialog.getOpenFileName(self.view, "Seleccionar archivo CSV", "", "Archivos CSV (*.csv)")
        if archivo:
            self.view.csv_file_input.setText(archivo)

    @permiso_auditoria_configuracion('editar')
    def importar_csv_inventario(self):
        """
        Importa el inventario desde un archivo CSV/Excel usando el flujo seguro y centralizado del sistema.
        - Solo admin puede ejecutar.
        - Usa la conexión centralizada (core/database.py).
        - Feedback visual claro y uniforme.
        """
        if not self.usuario_actual or not getattr(self.usuario_actual, 'rol', None) == 'admin':
            self.view.mostrar_mensaje("Solo el usuario admin puede importar el inventario.", tipo="error")
            return
        ruta_csv = self.view.csv_file_input.text().strip() if hasattr(self.view, 'csv_file_input') else ''
        if not ruta_csv or not os.path.exists(ruta_csv):
            self.view.mostrar_mensaje(f"No se encontró el archivo: {ruta_csv}", tipo="error")
            return
        def confirmar(df, resultado):
            self.view.mostrar_preview(df)
            self.view.mostrar_advertencias(resultado["advertencias"])
            return self.view.confirmar_importacion(len(df))
        resultado = importar_inventario_desde_archivo(ruta_csv, self.usuario_actual, confirmar_importacion_callback=confirmar)
        if resultado["exito"]:
            self.view.mostrar_exito(resultado["mensajes"])
        else:
            self.view.mostrar_errores(resultado["errores"])
            if resultado["mensajes"]:
                self.view.mostrar_mensaje("\n".join(resultado["mensajes"]), tipo="info")
        self.view.mostrar_advertencias(resultado["advertencias"])

    def _mostrar_mensaje(self, mensaje, error=False):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(mensaje, error=error)
        elif hasattr(self.view, 'label'):
            self.view.label.setText(mensaje)
        else:
            print(mensaje)

    # --- Métodos para la pestaña de permisos y visibilidad ---
    def cargar_permisos_modulos(self):
        """
        Carga la tabla de permisos (usuarios/roles x módulos) en la pestaña de permisos y visibilidad.
        """
        try:
            usuarios = self.usuarios_model.obtener_usuarios()
            modulos = self.usuarios_model.obtener_todos_los_modulos()
            # Limpiar tabla
            self.view.tabla_permisos.setRowCount(0)
            for usuario in usuarios:
                id_usuario = usuario[0] if isinstance(usuario, (list, tuple)) else usuario.get('id')
                nombre_usuario = usuario[3] if isinstance(usuario, (list, tuple)) else usuario.get('usuario')
                rol = usuario[6] if isinstance(usuario, (list, tuple)) else usuario.get('rol')
                for modulo in modulos:
                    row = self.view.tabla_permisos.rowCount()
                    self.view.tabla_permisos.insertRow(row)
                    self.view.tabla_permisos.setItem(row, 0, QTableWidgetItem(f"{nombre_usuario} ({rol})"))
                    self.view.tabla_permisos.setItem(row, 1, QTableWidgetItem(modulo))
                    permisos = self.usuarios_model.obtener_permisos_modulo({'id': id_usuario, 'rol': rol}, modulo)
                    for col, accion in enumerate(['ver', 'modificar', 'aprobar'], start=2):
                        chk = QCheckBox()
                        chk.setChecked(permisos.get(accion, False))
                        self.view.tabla_permisos.setCellWidget(row, col, chk)
        except Exception as e:
            self.mostrar_mensaje(f"Error al cargar permisos: {e}", tipo="error", destino="permisos_result_label")

    def guardar_permisos_modulos(self):
        """
        Guarda los permisos editados en la tabla de permisos y visibilidad.
        """
        try:
            permisos_dict_por_usuario = {}
            for row in range(self.view.tabla_permisos.rowCount()):
                usuario_modulo = self.view.tabla_permisos.item(row, 0).text()
                modulo = self.view.tabla_permisos.item(row, 1).text()
                permisos = {
                    'ver': self.view.tabla_permisos.cellWidget(row, 2).isChecked(),
                    'modificar': self.view.tabla_permisos.cellWidget(row, 3).isChecked(),
                    'aprobar': self.view.tabla_permisos.cellWidget(row, 4).isChecked()
                }
                permisos_dict_por_usuario.setdefault(usuario_modulo, {})[modulo] = permisos
            self.usuarios_model.guardar_permisos_modulos(permisos_dict_por_usuario)
            self.mostrar_mensaje("Permisos guardados exitosamente.", tipo="exito", destino="permisos_result_label")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar permisos: {e}", tipo="error", destino="permisos_result_label")
