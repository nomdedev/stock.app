from utils.theme_manager import aplicar_tema, guardar_modo_tema
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QCheckBox, QFileDialog
import pandas as pd
import pyodbc
import os
from scripts.procesar_e_importar_inventario import importar_inventario_desde_archivo

# REGLA CRÍTICA: Nunca usar .text() directo sobre widgets. Usar siempre _get_text(nombre) o _get_checked(nombre).
# Si se modifica este archivo, revisar que no haya ningún .text() directo. Documentar cualquier excepción.
# Última revisión: 2025-05-25

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                usuario = getattr(controller, 'usuario_actual', None)
                if not usuario_model or not auditoria_model:
                    raise RuntimeError("Faltan modelos de usuario o auditoría en el controller.")
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                try:
                    resultado = func(controller, *args, **kwargs)
                    auditoria_model.registrar_evento(usuario, self.modulo, accion)
                    return resultado
                except Exception as e:
                    auditoria_model.registrar_evento(usuario, self.modulo, accion)
                    raise
            return wrapper
        return decorador

permiso_auditoria_configuracion = PermisoAuditoria('configuracion')

class ConfiguracionController:
    """
    Controlador robusto para el módulo de Configuración.
    - Valida argumentos y dependencias.
    - Gestiona permisos y feedback visual.
    - Refuerza la robustez en señales y métodos.
    """
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.db_connection = db_connection
        self.auditoria_model = AuditoriaModel(db_connection)
        self._conectar_senales()

    def _conectar_senales(self):
        botones = [
            ("save_button", self.guardar_cambios),
            ("switch_tema", self.toggle_tema, "stateChanged"),
            ("boton_activar_offline", self.activar_modo_offline),
            ("boton_desactivar_offline", self.desactivar_modo_offline),
            ("boton_guardar_conexion", self.guardar_configuracion_conexion),
            ("boton_cambiar_notificaciones", self.cambiar_estado_notificaciones),
            ("boton_seleccionar_csv", self.seleccionar_archivo_csv),
            ("boton_importar_csv", self.importar_csv_inventario)
        ]
        for nombre, funcion, *signal in botones:
            if hasattr(self.view, nombre):
                boton = getattr(self.view, nombre)
                try:
                    if signal and hasattr(boton, signal[0]):
                        getattr(boton, signal[0]).connect(funcion)
                    elif hasattr(boton, 'clicked'):
                        boton.clicked.connect(funcion)
                except Exception as e:
                    self.mostrar_mensaje(f"Error al conectar señal de '{nombre}': {e}", tipo="error")
            else:
                self.mostrar_mensaje(f"No se encontró el widget '{nombre}' en la vista.", tipo="advertencia")
        # Señal especial para permisos
        if hasattr(self.view, "boton_guardar_permisos") and hasattr(self, "cargar_permisos_modulos"):
            try:
                self.cargar_permisos_modulos()
            except Exception as e:
                self.mostrar_mensaje(f"Error al cargar permisos de módulos: {e}", tipo="error", destino="permisos_result_label")

    def mostrar_mensaje(self, mensaje, tipo="info", destino="label"):
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
        if label and hasattr(label, 'setText'):
            label.setText(f"<span style='color:{color};'>{icono} {mensaje}</span>")
        else:
            # Fallback: print o log si no hay label
            print(f"[{tipo.upper()}] {mensaje}")

    def _get_widget(self, nombre):
        return getattr(self.view, nombre, None)

    def _get_text(self, nombre):
        w = self._get_widget(nombre)
        return w.text() if w and hasattr(w, 'text') else ''

    def _get_checked(self, nombre):
        w = self._get_widget(nombre)
        return w.isChecked() if w and hasattr(w, 'isChecked') else False

    @permiso_auditoria_configuracion('ver')
    def cargar_configuracion(self):
        try:
            configuracion = self.model.obtener_configuracion()
            for clave, valor, descripcion in configuracion:
                w = self._get_widget(f"{clave}_input")
                if w:
                    if hasattr(w, 'setText'):
                        w.setText(str(valor))
                    elif hasattr(w, 'setCurrentText'):
                        w.setCurrentText(str(valor))
                    elif hasattr(w, 'setChecked'):
                        w.setChecked(str(valor) == "True")
            apariencia = self.model.obtener_apariencia_usuario(1)
            if apariencia:
                modo_color, idioma, notificaciones, tamaño_fuente = apariencia[0]
                w_color = self._get_widget('modo_color_input')
                if w_color: w_color.setCurrentText(modo_color)
                w_idioma = self._get_widget('idioma_input')
                if w_idioma: w_idioma.setCurrentText(idioma)
                w_notif = self._get_widget('notificaciones_checkbox')
                if w_notif: w_notif.setChecked(bool(notificaciones))
                w_tam = self._get_widget('tamaño_fuente_input')
                if w_tam: w_tam.setCurrentText(tamaño_fuente)
        except Exception as e:
            self.mostrar_mensaje(f"Error al cargar configuración: {e}", tipo="error")

    @permiso_auditoria_configuracion('editar')
    def guardar_cambios(self):
        try:
            nombre = self._get_text('nombre_app_input')
            if nombre:
                self.model.actualizar_configuracion("nombre_app", nombre)
            zona = self._get_widget('zona_horaria_input')
            if zona and hasattr(zona, 'currentText'):
                self.model.actualizar_configuracion("zona_horaria", zona.currentText())
            modo_mant = self._get_widget('modo_mantenimiento_checkbox')
            if modo_mant and hasattr(modo_mant, 'isChecked'):
                self.model.actualizar_configuracion("modo_mantenimiento", str(modo_mant.isChecked()))
            datos_apariencia = (
                self._get_text('modo_color_input'),
                self._get_text('idioma_input'),
                self._get_checked('notificaciones_checkbox'),
                self._get_text('tamaño_fuente_input')
            )
            self.model.actualizar_apariencia_usuario(1, datos_apariencia)
            self.mostrar_mensaje("Cambios guardados exitosamente.", tipo="exito")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar cambios: {e}", tipo="error")

    @permiso_auditoria_configuracion('editar')
    def probar_conexion_bd(self, retornar_resultado=False):
        try:
            servidor = self._get_text('server_input')
            usuario = self._get_text('username_input')
            password = self._get_text('password_input')
            base = self._get_text('default_db_input')
            puerto = self._get_text('port_input')
            timeout = self._get_text('timeout_input')
            if not all([servidor, usuario, password, base]):
                raise ValueError("Faltan campos obligatorios para la conexión.")
            timeout = int(timeout) if timeout.isdigit() else 5
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={servidor};DATABASE={base};UID={usuario};PWD={password};TrustServerCertificate=yes;"
            if puerto:
                conn_str += f"PORT={puerto};"
            conn = pyodbc.connect(conn_str, timeout=timeout)
            conn.close()
            if retornar_resultado:
                return {"exito": True, "mensaje": "Conexión exitosa"}
            self.mostrar_mensaje("Conexión exitosa", tipo="exito", destino="resultado_conexion_label")
        except Exception as e:
            if retornar_resultado:
                return {"exito": False, "mensaje": str(e)}
            self.mostrar_mensaje(f"Error de conexión: {e}", tipo="error", destino="resultado_conexion_label")

    @permiso_auditoria_configuracion('editar')
    def guardar_configuracion_conexion(self):
        try:
            # ESTÁNDAR: Siempre usar _get_text para obtener valores de widgets, nunca .text() directo
            campos_obligatorios = [
                ('server_input', "Servidor"),
                ('username_input', "Usuario"),
                ('password_input', "Contraseña"),
                ('default_db_input', "Base de datos")
            ]
            for campo_nombre, nombre in campos_obligatorios:
                valor = self._get_text(campo_nombre)
                if not valor.strip():
                    self.mostrar_mensaje(f"El campo '{nombre}' es obligatorio.", tipo="error", destino="resultado_conexion_label")
                    return
            datos = {
                "servidor": self._get_text('server_input'),
                "usuario": self._get_text('username_input'),
                "contraseña": self._get_text('password_input'),
                "puerto": self._get_text('port_input'),
                "base_predeterminada": self._get_text('default_db_input'),
                "timeout": self._get_text('timeout_input'),
            }
            resultado = self.probar_conexion_bd(retornar_resultado=True)
            if not (resultado and resultado.get('exito')):
                mensaje = resultado.get('mensaje') if resultado else 'Error desconocido.'
                self.mostrar_mensaje(f"No se puede guardar: {mensaje}", tipo="error", destino="resultado_conexion_label")
                return
            self.model.guardar_configuracion_conexion(datos)
            self.mostrar_mensaje("Configuración guardada correctamente", tipo="exito", destino="resultado_conexion_label")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar: {str(e)}", tipo="error", destino="resultado_conexion_label")
        # NOTA: No usar .text() directo en widgets, siempre usar _get_text para evitar errores de atributo.

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
            if not isinstance(estado, int):
                raise ValueError("El estado del tema debe ser un entero.")
            modos = {0: "light", 2: "oscuro"}
            nuevo_modo = modos.get(estado, "light")
            aplicar_tema(QApplication.instance(), nuevo_modo)
            guardar_modo_tema(nuevo_modo)
        except Exception as e:
            self.mostrar_mensaje(f"Error al cambiar tema: {e}", tipo="error")

    def seleccionar_archivo_csv(self):
        try:
            archivo, _ = QFileDialog.getOpenFileName(self.view, "Seleccionar archivo CSV", "", "Archivos CSV (*.csv)")
            if archivo and hasattr(self.view, 'csv_file_input') and self.view.csv_file_input:
                self.view.csv_file_input.setText(archivo)
            elif not archivo:
                self.mostrar_mensaje("No se seleccionó ningún archivo.", tipo="advertencia")
            else:
                self.mostrar_mensaje("No se encontró el campo para mostrar la ruta del CSV.", tipo="error")
        except Exception as e:
            self.mostrar_mensaje(f"Error al seleccionar archivo: {e}", tipo="error")

    @permiso_auditoria_configuracion('editar')
    def importar_csv_inventario(self):
        # Validación de usuario y permisos
        if not self.usuario_actual or not getattr(self.usuario_actual, 'rol', None) == 'admin':
            self.mostrar_mensaje("Solo el usuario admin puede importar el inventario.", tipo="error")
            return
        # Validación de campo de archivo
        if not hasattr(self.view, 'csv_file_input') or not self.view.csv_file_input:
            self.mostrar_mensaje("No se encontró el campo para seleccionar el archivo CSV.", tipo="error")
            return
        ruta_csv = self.view.csv_file_input.text().strip()
        if not ruta_csv:
            self.mostrar_mensaje("Debe seleccionar un archivo CSV para importar.", tipo="advertencia")
            return
        if not os.path.exists(ruta_csv):
            self.mostrar_mensaje(f"No se encontró el archivo: {ruta_csv}", tipo="error")
            return
        if not ruta_csv.lower().endswith('.csv'):
            self.mostrar_mensaje("El archivo seleccionado no es un CSV.", tipo="error")
            return
        # Callback robusto para preview y confirmación
        def confirmar(df, resultado):
            if hasattr(self.view, 'mostrar_preview'):
                try:
                    self.view.mostrar_preview(df)
                except Exception as e:
                    self.mostrar_mensaje(f"Error mostrando preview: {e}", tipo="error")
            if hasattr(self.view, 'mostrar_advertencias'):
                try:
                    self.view.mostrar_advertencias(resultado.get("advertencias", []))
                except Exception as e:
                    self.mostrar_mensaje(f"Error mostrando advertencias: {e}", tipo="error")
            if hasattr(self.view, 'confirmar_importacion'):
                try:
                    return self.view.confirmar_importacion(len(df))
                except Exception as e:
                    self.mostrar_mensaje(f"Error en confirmación de importación: {e}", tipo="error")
                    return False
            return True
        try:
            resultado = importar_inventario_desde_archivo(ruta_csv, self.usuario_actual, confirmar_importacion_callback=confirmar)
        except Exception as e:
            self.mostrar_mensaje(f"Error al procesar el archivo: {e}", tipo="error")
            return
        # Feedback visual y manejo de advertencias/errores
        if resultado.get("exito"):
            if hasattr(self.view, 'mostrar_exito'):
                try:
                    self.view.mostrar_exito(resultado.get("mensajes", []))
                except Exception as e:
                    self.mostrar_mensaje(f"Error mostrando mensajes de éxito: {e}", tipo="error")
            self.mostrar_mensaje("Inventario importado correctamente.", tipo="exito")
        else:
            if hasattr(self.view, 'mostrar_errores'):
                try:
                    self.view.mostrar_errores(resultado.get("errores", []))
                except Exception as e:
                    self.mostrar_mensaje(f"Error mostrando errores: {e}", tipo="error")
            if resultado.get("mensajes"):
                self.mostrar_mensaje("\n".join(resultado["mensajes"]), tipo="info")
            self.mostrar_mensaje("No se pudo importar el inventario. Revise los errores.", tipo="error")
        if hasattr(self.view, 'mostrar_advertencias'):
            try:
                self.view.mostrar_advertencias(resultado.get("advertencias", []))
            except Exception as e:
                self.mostrar_mensaje(f"Error mostrando advertencias: {e}", tipo="error")
        # Comentario para tests: cubrir casos de archivo inexistente, formato inválido, advertencias, errores y éxito.

    def cargar_permisos_modulos(self):
        try:
            usuarios = self.usuarios_model.obtener_usuarios()
            modulos = self.usuarios_model.obtener_todos_los_modulos()
            if hasattr(self.view, 'tabla_permisos') and self.view.tabla_permisos:
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
            else:
                self.mostrar_mensaje("No se encontró la tabla de permisos en la vista.", tipo="error", destino="permisos_result_label")
        except Exception as e:
            self.mostrar_mensaje(f"Error al cargar permisos: {e}", tipo="error", destino="permisos_result_label")

    def guardar_permisos_modulos(self):
        try:
            # Solo el admin puede modificar permisos
            if not self.usuario_actual or self.usuario_actual.id_rol != 1:
                self.view.mostrar_mensaje("Solo el admin puede modificar permisos.", tipo="error")
                return
            permisos_dict_por_usuario = {}
            if hasattr(self.view, 'tabla_permisos') and self.view.tabla_permisos:
                for row in range(self.view.tabla_permisos.rowCount()):
                    try:
                        usuario_modulo = self.view.tabla_permisos.item(row, 0).text()
                        modulo = self.view.tabla_permisos.item(row, 1).text()
                        permisos = {
                            'ver': self.view.tabla_permisos.cellWidget(row, 2).isChecked(),
                            'modificar': self.view.tabla_permisos.cellWidget(row, 3).isChecked(),
                            'aprobar': self.view.tabla_permisos.cellWidget(row, 4).isChecked()
                        }
                        permisos_dict_por_usuario.setdefault(usuario_modulo, {})[modulo] = permisos
                    except Exception as e:
                        self.mostrar_mensaje(f"Error en fila {row}: {e}", tipo="error", destino="permisos_result_label")
            else:
                self.mostrar_mensaje("No se encontró la tabla de permisos en la vista.", tipo="error", destino="permisos_result_label")
            if hasattr(self.usuarios_model, 'guardar_permisos_modulos'):
                self.usuarios_model.guardar_permisos_modulos(permisos_dict_por_usuario)
            self.mostrar_mensaje("Permisos guardados exitosamente.", tipo="exito", destino="permisos_result_label")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar permisos: {e}", tipo="error", destino="permisos_result_label")
