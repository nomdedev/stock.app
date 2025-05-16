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
            # Conectar señales para la pestaña de importación CSV
            if hasattr(self.view, "boton_seleccionar_csv"):
                self.view.boton_seleccionar_csv.clicked.connect(self.seleccionar_archivo_csv)
            if hasattr(self.view, "boton_importar_csv"):
                self.view.boton_importar_csv.clicked.connect(self.importar_csv_inventario)
        except AttributeError as e:
            print(f"Error en ConfiguracionController: {e}")
        except Exception as e:
            print(f"Error al conectar señales de importación CSV: {e}")

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

    # --- Métodos para la pestaña de importación CSV ---
    def seleccionar_archivo_csv(self):
        from PyQt6.QtWidgets import QFileDialog
        archivo, _ = QFileDialog.getOpenFileName(self.view, "Seleccionar archivo CSV", "", "Archivos CSV (*.csv)")
        if archivo:
            self.view.csv_file_input.setText(archivo)

    def importar_csv_inventario(self):
        import csv, re
        from core.database import DatabaseConnection
        ruta_csv = self.view.csv_file_input.text()
        if not ruta_csv or not ruta_csv.lower().endswith('.csv'):
            self.view.import_result_label.setText("Selecciona un archivo CSV válido.")
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
            self.view.import_result_label.setText(resumen)
        except Exception as e:
            self.view.import_result_label.setText(f"Error al importar: {e}")
