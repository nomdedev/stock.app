from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QTableWidgetItem, QPushButton, QCheckBox
from datetime import datetime
import secrets
import hashlib
from core.base_controller import BaseController
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from core.logger import log_error

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
                ip = usuario.get('ip', '') if usuario else ''
                if not usuario or not usuario_model or not auditoria_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                if usuario['rol'] not in ('admin', 'supervisor'):
                    modulos_permitidos = usuario_model.obtener_modulos_permitidos(usuario)
                    if self.modulo not in modulos_permitidos:
                        if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                            controller.view.label.setText(f"No tiene permiso para acceder al módulo: {self.modulo}")
                        usuario_id = usuario.get('id') if usuario else None
                        detalle = f"{accion} - denegado (módulo)"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                        return None
                if not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - denegado (permiso)"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return None
                try:
                    print(f"[LOG ACCIÓN] Ejecutando acción '{accion}' en módulo '{self.modulo}' por usuario: {usuario.get('username', 'desconocido')} (id={usuario.get('id', '-')})")
                    resultado = func(controller, *args, **kwargs)
                    print(f"[LOG ACCIÓN] Acción '{accion}' en módulo '{self.modulo}' finalizada con éxito.")
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    print(f"[LOG ACCIÓN] Error en acción '{accion}' en módulo '{self.modulo}': {e}")
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - error: {e}"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_usuarios = PermisoAuditoria('usuarios')

class UsuariosController(BaseController):
    def __init__(self, model, view, db_connection, usuario_actual=None):
        super().__init__(model, view)
        self.usuario_actual = usuario_actual
        self.auditoria_model = AuditoriaModel(db_connection)

    def inicializar_vista(self):
        # Llamar esto tras login o al inicializar la vista
        self.mostrar_tab_permisos_si_admin()
        self.setup_view_signals()
        self.cargar_usuarios()

    def setup_view_signals(self):
        # Diccionario para mapear botones a métodos
        botones_acciones = {
            'boton_agregar': self.agregar_usuario,
            'boton_gestion_roles': self._mostrar_roles_permisos,
            'boton_exportar_logs': self.exportar_logs,
            'boton_nuevo_usuario': self.limpiar_formulario,
            'boton_suspender': self._suspender_selected,
            'boton_reactivar': self._reactivar_selected,
            'boton_clonar_permisos': self._clonar_permisos,
            'boton_guardar_permisos': self.guardar_permisos
        }

        # Conectar señales dinámicamente
        for boton, accion in botones_acciones.items():
            if hasattr(self.view, boton):
                getattr(self.view, boton).clicked.connect(accion)

        # Llenar combo de roles y cargar usuarios al iniciar la vista
        roles_data = self.model.obtener_roles()
        if hasattr(self.view, 'rol_input') and self.view.rol_input:
            roles = [r[0] for r in roles_data]
            self.view.rol_input.clear()
            self.view.rol_input.addItems(roles)

        # Cargar usuarios solo si la vista está lista
        if hasattr(self.view, 'tabla_usuarios'):
            self.cargar_usuarios()

    @permiso_auditoria_usuarios('agregar')
    def agregar_usuario(self):
        nombre = self.view.nombre_input.text()
        email = self.view.email_input.text()
        rol = self.view.rol_input.text()

        if not (nombre and email and rol):
            self.view.label.setText("Por favor, complete todos los campos.")
            return

        if self.model.verificar_usuario_existente(email, nombre):
            QMessageBox.warning(
                self.view,
                "Usuario Existente",
                "Ya existe un usuario con el mismo email o nombre de usuario."
            )
            self.view.email_input.setStyleSheet("border: 1px solid red;")
            self.view.nombre_input.setStyleSheet("border: 1px solid red;")
            return

        self.model.agregar_usuario((nombre, email, rol))
        self.view.label.setText("Usuario agregado exitosamente.")
        self._registrar_evento_auditoria('agregar', estado="éxito")
        self.view.email_input.setStyleSheet("")
        self.view.nombre_input.setStyleSheet("")

    @permiso_auditoria_usuarios('actualizar')
    def actualizar_usuario(self, id_usuario, datos, fecha_actualizacion):
        try:
            self.model.actualizar_usuario(id_usuario, datos, fecha_actualizacion)
            self.view.label.setText("Usuario actualizado exitosamente.")
            self._registrar_evento_auditoria('actualizar', estado="éxito")
        except Exception as e:
            self.view.label.setText(f"Error: {str(e)}")
            log_error(f"Error actualizando usuario: {e}")

    def marcar_como_favorito(self):
        self.view.parent().agregar_a_favoritos("Usuarios")
        self._registrar_evento_auditoria('marcar_favorito', estado="éxito")

    def registrar_login_fallido(self, ip, usuario):
        self.model.db.registrar_login_fallido(ip, usuario, datetime.now().isoformat(), "fallido")
        self.view.label.setText(f"Intento de login fallido registrado para el usuario: {usuario}")

    def limpiar_formulario(self):
        self.view.nombre_input.clear()
        self.view.apellido_input.clear()
        self.view.usuario_input.clear()
        self.view.password_input.clear()
        self.view.email_input.clear()
        self.view.rol_input.setCurrentIndex(0)

    def _get_selected_user_id(self):
        row = self.view.tabla_usuarios.currentRow()
        if row == -1:
            return None
        item = self.view.tabla_usuarios.item(row, 0)
        return int(item.text()) if item else None

    @permiso_auditoria_usuarios('suspender')
    def _suspender_selected(self):
        user_id = self._get_selected_user_id()
        if user_id:
            msg = self.model.suspender_cuenta(user_id)
            self.view.label.setText(msg)
            self.cargar_usuarios()

    @permiso_auditoria_usuarios('reactivar')
    def _reactivar_selected(self):
        user_id = self._get_selected_user_id()
        if user_id:
            msg = self.model.reactivar_cuenta(user_id)
            self.view.label.setText(msg)
            self.cargar_usuarios()

    @permiso_auditoria_usuarios('resetear_password')
    def _resetear_password_selected(self):
        user_id = self._get_selected_user_id()
        if user_id:
            new_pass = secrets.token_urlsafe(8)
            hashed = hashlib.sha256(new_pass.encode()).hexdigest()
            self.model.actualizar_password(user_id, hashed)
            self.view.label.setText(f"Contraseña restablecida: {new_pass}")

    @permiso_auditoria_usuarios('clonar_permisos')
    def _clonar_permisos(self):
        origen = self.view.input_rol_origen.text()
        destino = self.view.input_rol_destino.text()
        if origen and destino:
            msg = self.model.clonar_permisos(origen, destino)
            self.view.label.setText(msg)
            self.setup_view_signals()

    def cargar_usuarios(self):
        usuarios = self.model.obtener_usuarios()
        self.view.tabla_usuarios.setRowCount(len(usuarios))
        for row, usuario in enumerate(usuarios):
            for col, dato in enumerate(usuario[:7]):  # id, nombre, apellido, email, usuario, rol, estado
                self.view.tabla_usuarios.setItem(row, col, QTableWidgetItem(str(dato)))
            # Botones de acción
            cols = {'editar': 7, 'susp': 8, 'reset': 9}
            # Editar
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda _, u=usuario: self.editar_usuario(u))
            self.view.tabla_usuarios.setCellWidget(row, cols['editar'], btn_edit)
            # Suspender/Reactivar
            btn_susp = QPushButton("Susp/Act")
            btn_susp.clicked.connect(lambda _, u_id=usuario[0], est=usuario[6]: self.cambiar_estado_usuario(u_id, est))
            self.view.tabla_usuarios.setCellWidget(row, cols['susp'], btn_susp)
            # Resetear Contraseña
            btn_reset = QPushButton("Reset Pass")
            btn_reset.clicked.connect(lambda _, r=row: self._resetear_password_selected())
            self.view.tabla_usuarios.setCellWidget(row, cols['reset'], btn_reset)

    @permiso_auditoria_usuarios('editar')
    def editar_usuario(self, usuario):
        dialog = QDialog()
        dialog.setWindowTitle("Editar Usuario")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Editar usuario: {usuario[0]}"))
        dialog.exec()

    @permiso_auditoria_usuarios('eliminar')
    def eliminar_usuario(self, usuario_id):
        confirmacion = QMessageBox.question(
            self.view,
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar al usuario con ID {usuario_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirmacion == QMessageBox.StandardButton.Yes:
            self.model.eliminar_usuario(usuario_id)
            self.view.label.setText(f"Usuario con ID {usuario_id} eliminado exitosamente.")
            self.cargar_usuarios()

    @permiso_auditoria_usuarios('cambiar_estado')
    def cambiar_estado_usuario(self, usuario_id, estado_actual):
        nuevo_estado = "Inactivo" if estado_actual == "Activo" else "Activo"
        self.model.actualizar_estado_usuario(usuario_id, nuevo_estado)
        self.view.label.setText(f"Estado del usuario con ID {usuario_id} cambiado a {nuevo_estado}.")
        self.cargar_usuarios()
        self._registrar_evento_auditoria('cambiar_estado', estado="éxito")

    def _mostrar_roles_permisos(self):
        # Carga la tabla de roles y permisos con checkboxes
        roles = self.model.obtener_roles()
        self.view.tabla_roles_permisos.setRowCount(len(roles))
        for row, rol in enumerate(roles):
            permisos = self.model.obtener_permisos_por_rol(rol[0])
            for permiso in permisos:
                modulo = permiso[1]
                datos_perm = permiso[2:6]  # ver, editar, aprobar, eliminar
                # Colocar rol y módulo
                self.view.tabla_roles_permisos.setItem(row, 0, QTableWidgetItem(rol[0]))
                self.view.tabla_roles_permisos.setItem(row, 1, QTableWidgetItem(modulo))
                # Insertar checkboxes para cada permiso
                for i, estado in enumerate(datos_perm, start=2):
                    chk = QCheckBox()
                    chk.setChecked(bool(estado))
                    self.view.tabla_roles_permisos.setCellWidget(row, i, chk)

    @permiso_auditoria_usuarios('guardar_permisos')
    def guardar_permisos(self):
        # Recoger permisos desde la tabla y actualizar
        filas = self.view.tabla_roles_permisos.rowCount()
        permisos_a_actualizar = {}
        for row in range(filas):
            rol = self.view.tabla_roles_permisos.item(row, 0).text()
            modulo = self.view.tabla_roles_permisos.item(row, 1).text()
            estados = []
            for col in range(2, 6):
                chk = self.view.tabla_roles_permisos.cellWidget(row, col)
                estados.append(1 if chk.isChecked() else 0)
            permisos_a_actualizar[modulo] = estados
            # Llamar al modelo por cada módulo
            self.model.actualizacion_permisos(rol, {modulo: permisos_a_actualizar[modulo]})
        self.view.label.setText("Permisos guardados exitosamente.")

    @permiso_auditoria_usuarios('exportar_logs')
    def exportar_logs(self, formato):
        """
        Exporta los logs de usuarios en el formato solicitado ('excel' o 'pdf') usando el método robusto del modelo.
        Muestra feedback visual y registra auditoría.
        """
        mensaje = self.model.exportar_logs_usuarios(formato)
        self.view.label.setText(mensaje)
        self._registrar_evento_auditoria('exportar_logs', estado="éxito" if 'exportado' in mensaje else "error")

    @permiso_auditoria_usuarios('exportar_usuarios')
    def exportar_usuarios(self, formato):
        """
        Exporta la lista de usuarios en el formato solicitado ('excel' o 'pdf') usando el método robusto del modelo.
        Muestra feedback visual y registra auditoría.
        """
        mensaje = self.model.exportar_usuarios(formato)
        self.view.label.setText(mensaje)
        self._registrar_evento_auditoria('exportar_usuarios', estado="éxito" if 'exportado' in mensaje else "error")

    def verificar_permiso(self, usuario_id, modulo, accion):
        permisos = self.model.obtener_permisos_por_usuario(usuario_id, modulo)
        if permisos and permisos.get(accion, False):
            return True
        self.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
        return False

    def suspender_cuenta(self, id_usuario):
        mensaje = self.model.suspender_cuenta(id_usuario)
        self.view.label.setText(mensaje)

    def reactivar_cuenta(self, id_usuario):
        mensaje = self.model.reactivar_cuenta(id_usuario)
        self.view.label.setText(mensaje)

    def clonar_permisos(self, rol_origen, rol_destino):
        mensaje = self.model.clonar_permisos(rol_origen, rol_destino)
        self.view.label.setText(mensaje)

    def mostrar_tab_permisos_si_admin(self):
        # Solo el admin puede ver la pestaña de permisos
        if hasattr(self, 'usuario_actual') and self.usuario_actual and self.usuario_actual.get('rol') == 'admin':
            self.view.mostrar_tab_permisos(True)
            self.cargar_gestion_permisos_modulos()
        else:
            self.view.mostrar_tab_permisos(False)

    def cargar_gestion_permisos_modulos(self):
        # Llenar combo con usuarios normales
        usuarios = self.model.obtener_usuarios()
        usuarios_normales = [u for u in usuarios if u[2] == 'usuario']  # Suponiendo col 2 es rol
        self.view.combo_usuario.clear()
        for u in usuarios_normales:
            self.view.combo_usuario.addItem(f"{u[0]}", u[0])  # username como display y data
        # Cargar módulos disponibles, excluyendo los restringidos
        modulos_restringidos = {"Usuarios", "Auditoría", "Configuración"}
        modulos = self.model.obtener_todos_los_modulos() if hasattr(self.model, 'obtener_todos_los_modulos') else []
        modulos = [m for m in modulos if m not in modulos_restringidos]
        self.view.tabla_permisos_modulos.setRowCount(len(modulos))
        self.view.tabla_permisos_modulos.setColumnCount(2)
        self.view.tabla_permisos_modulos.setHorizontalHeaderLabels(["Módulo", "Permitido"])
        for row, modulo in enumerate(modulos):
            self.view.tabla_permisos_modulos.setItem(row, 0, QTableWidgetItem(modulo))
            chk = QCheckBox()
            self.view.tabla_permisos_modulos.setCellWidget(row, 1, chk)
        # Cargar permisos actuales al cambiar usuario
        self.view.combo_usuario.currentIndexChanged.connect(self.actualizar_permisos_modulos_usuario)
        self.view.boton_guardar_permisos.clicked.connect(self.guardar_permisos_modulos_usuario)
        self.actualizar_permisos_modulos_usuario()

    def actualizar_permisos_modulos_usuario(self):
        username = self.view.combo_usuario.currentData()
        if not username:
            return
        # Obtener módulos permitidos actuales
        modulos_permitidos = self.model.obtener_modulos_permitidos({'username': username, 'rol': 'usuario'})
        for row in range(self.view.tabla_permisos_modulos.rowCount()):
            modulo = self.view.tabla_permisos_modulos.item(row, 0).text()
            chk = self.view.tabla_permisos_modulos.cellWidget(row, 1)
            chk.setChecked(modulo in modulos_permitidos)

    def guardar_permisos_modulos_usuario(self):
        username = self.view.combo_usuario.currentData()
        if not username:
            return
        nuevos_permisos = []
        for row in range(self.view.tabla_permisos_modulos.rowCount()):
            modulo = self.view.tabla_permisos_modulos.item(row, 0).text()
            chk = self.view.tabla_permisos_modulos.cellWidget(row, 1)
            if chk.isChecked():
                nuevos_permisos.append(modulo)
        # Guardar en la tabla permisos_usuario usando username
        self.model.actualizar_permisos_usuario(username, nuevos_permisos)
        QMessageBox.information(self.view, "Permisos actualizados", "Los permisos de módulos han sido actualizados para el usuario seleccionado.")

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        usuario_id = usuario.get('id') if usuario else None
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'usuarios', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")
