from utils.theme_manager import aplicar_tema, guardar_modo_tema
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QCheckBox

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

    def importar_csv_inventario(self):
        import csv, re
        from core.database import DatabaseConnection
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        auditoria_model = getattr(self, 'auditoria_model', None)
        ruta_csv = self.view.csv_file_input.text()
        if not ruta_csv or not ruta_csv.lower().endswith('.csv'):
            self.mostrar_mensaje("Selecciona un archivo CSV válido.", tipo="error", destino="import_result_label")
            if auditoria_model:
                auditoria_model.registrar_evento(usuario, 'configuracion', 'importar_csv_inventario', ip_origen=ip, resultado="denegado (archivo inválido)")
            return
        db = self.model.db
        count = 0
        codigos_omitidos = []
        codigos_repetidos = set()
        codigos_vistos = set()
        def extraer_desde_descripcion(descripcion):
            tipo = ''
            acabado = ''
            longitud = ''
            if descripcion:
                tipo_match = re.search(r'^(.*?)\s*Euro-Design', descripcion, re.IGNORECASE)
                if tipo_match:
                    tipo = tipo_match.group(1).strip()
                acabado_match = re.search(r'Euro-Design\s*\d+\s*([\w\-/]+)', descripcion, re.IGNORECASE)
                if acabado_match:
                    acabado = acabado_match.group(1).strip()
                longitud_match = re.search(r'([\d,.]+)\s*m', descripcion)
                if longitud_match:
                    longitud = longitud_match.group(1).replace(',', '.')
            return tipo, acabado, longitud
        try:
            with open(ruta_csv, encoding='latin1') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    codigo = None
                    for value in row.values():
                        if isinstance(value, str) and re.match(r'^\d{6}\.\d{3}$', value.strip()):
                            codigo = value.strip()
                            break
                    if not codigo:
                        codigo = row.get('codigo') or row.get('Código')
                    if not codigo or not isinstance(codigo, str) or not re.match(r'^\d{6}\.\d{3}$', codigo):
                        codigos_omitidos.append(str(codigo))
                        continue
                    if codigo in codigos_vistos:
                        codigos_repetidos.add(codigo)
                        continue
                    codigos_vistos.add(codigo)
                    nombre = row.get('nombre') or row.get('Nombre') or row.get('descripcion') or row.get('Descripción')
                    tipo_material = row.get('tipo_material') or row.get('Tipo de material') or 'PVC'
                    unidad = row.get('unidad') or row.get('Unidad') or 'unidad'
                    stock_actual = row.get('stock_actual') or row.get('Stock') or 0
                    stock_minimo = row.get('stock_minimo') or row.get('Stock mínimo') or 0
                    ubicacion = row.get('ubicacion') or row.get('Ubicación') or ''
                    descripcion = row.get('descripcion') or row.get('Descripción') or ''
                    qr = row.get('qr') or f'QR-{codigo}'
                    imagen_referencia = row.get('imagen_referencia') or ''
                    tipo, acabado, longitud = extraer_desde_descripcion(descripcion)
                    try:
                        db.ejecutar_query('''
                            INSERT INTO inventario_perfiles (
                                codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia, tipo, acabado, longitud
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia, tipo, acabado, longitud
                        ))
                        count += 1
                    except Exception as e:
                        codigos_omitidos.append(f"{codigo} (error: {e})")
            resumen = f"Perfiles importados: {count}\n"
            if codigos_omitidos:
                resumen += f"Perfiles omitidos: {len(codigos_omitidos)}\nCódigos omitidos (primeros 10): {codigos_omitidos[:10]}\n"
            if codigos_repetidos:
                resumen += f"Perfiles omitidos por código repetido: {len(codigos_repetidos)}\nCódigos repetidos: {list(codigos_repetidos)[:10]}\n"
            self.mostrar_mensaje(resumen, tipo="exito" if count else "advertencia", destino="import_result_label")
            if auditoria_model:
                auditoria_model.registrar_evento(usuario, 'configuracion', 'importar_csv_inventario', ip_origen=ip, resultado=f"éxito ({count} importados, {len(codigos_omitidos)} omitidos, {len(codigos_repetidos)} repetidos)")
        except Exception as e:
            self.mostrar_mensaje(f"Error al importar: {e}", tipo="error", destino="import_result_label")
            if auditoria_model:
                auditoria_model.registrar_evento(usuario, 'configuracion', 'importar_csv_inventario', ip_origen=ip, resultado=f"error: {e}")

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
                usuario_rol = self.view.tabla_permisos.item(row, 0).text()
                modulo = self.view.tabla_permisos.item(row, 1).text()
                usuario = usuario_rol.split(' (')[0]
                usuarios = self.usuarios_model.obtener_usuarios()
                id_usuario = None
                rol = None
                for u in usuarios:
                    nombre_usuario = u[3] if isinstance(u, (list, tuple)) else u.get('usuario')
                    if nombre_usuario == usuario:
                        id_usuario = u[0] if isinstance(u, (list, tuple)) else u.get('id')
                        rol = u[6] if isinstance(u, (list, tuple)) else u.get('rol')
                        break
                if id_usuario is None:
                    continue
                if id_usuario not in permisos_dict_por_usuario:
                    permisos_dict_por_usuario[id_usuario] = {}
                permisos_dict_por_usuario[id_usuario][modulo] = {
                    'ver': self.view.tabla_permisos.cellWidget(row, 2).isChecked(),
                    'modificar': self.view.tabla_permisos.cellWidget(row, 3).isChecked(),
                    'aprobar': self.view.tabla_permisos.cellWidget(row, 4).isChecked(),
                }
            if not permisos_dict_por_usuario:
                self.mostrar_mensaje("No hay permisos para guardar.", tipo="advertencia", destino="permisos_result_label")
                return
            usuario_actual_id = self.usuario_actual['id'] if self.usuario_actual and 'id' in self.usuario_actual else None
            if usuario_actual_id is None:
                self.mostrar_mensaje("No se puede identificar al usuario actual para registrar cambios.", tipo="error", destino="permisos_result_label")
                return
            for id_usuario, permisos_dict in permisos_dict_por_usuario.items():
                self.usuarios_model.actualizar_permisos_modulos_usuario(id_usuario, permisos_dict, usuario_actual_id)
            self.mostrar_mensaje("Permisos actualizados correctamente.", tipo="exito", destino="permisos_result_label")
        except Exception as e:
            self.mostrar_mensaje(f"Error al guardar permisos: {e}", tipo="error", destino="permisos_result_label")

    def conectar_pestana_permisos(self):
        """
        Conecta los botones y carga inicial de la pestaña de permisos y visibilidad.
        """
        try:
            self.cargar_permisos_modulos()
            self.view.boton_guardar_permisos.clicked.connect(self.guardar_permisos_modulos)
        except Exception as e:
            self.mostrar_mensaje(f"Error al inicializar pestaña permisos: {e}", tipo="error", destino="permisos_result_label")

    def probar_conexion_bd(self, retornar_resultado=False):
        """Prueba la conexión a la base de datos con los datos ingresados en la vista y muestra el resultado visualmente. Si retornar_resultado=True, retorna un dict con el resultado."""
        from core.database import get_connection_string
        import pyodbc
        driver = self.view.server_input.text() or 'ODBC Driver 17 for SQL Server'
        server = self.view.server_input.text()
        username = self.view.username_input.text()
        password = self.view.password_input.text()
        database = self.view.default_db_input.text()
        port = self.view.port_input.text() or '1433'
        timeout = int(self.view.timeout_input.text() or '10')
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        try:
            with pyodbc.connect(connection_string, timeout=timeout) as conn:
                if retornar_resultado:
                    return {"exito": True, "mensaje": "Conexión exitosa"}
                self.mostrar_mensaje("Conexión exitosa", tipo="exito", destino="resultado_conexion_label")
        except Exception as e:
            if retornar_resultado:
                return {"exito": False, "mensaje": str(e)}
            self.mostrar_mensaje(f"Error: {str(e)}", tipo="error", destino="resultado_conexion_label")
        # Siempre retornar un dict si se solicita resultado
        if retornar_resultado:
            return {"exito": False, "mensaje": "Error desconocido al probar la conexión."}
