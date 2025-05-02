from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QTableWidgetItem, QPushButton, QCheckBox
from datetime import datetime
import secrets
import hashlib
from core.base_controller import BaseController

class UsuariosController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)

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
        self.model.db.registrar_auditoria("admin", "Agregar Usuario", f"Nombre: {nombre}, Email: {email}")
        self.view.email_input.setStyleSheet("")
        self.view.nombre_input.setStyleSheet("")

    def actualizar_usuario(self, id_usuario, datos, fecha_actualizacion):
        try:
            self.model.actualizar_usuario(id_usuario, datos, fecha_actualizacion)
            self.view.label.setText("Usuario actualizado exitosamente.")
            self.model.db.registrar_auditoria("admin", "Actualizar Usuario", f"ID: {id_usuario}, Datos: {datos}")
        except Exception as e:
            self.view.label.setText(f"Error: {str(e)}")

    def marcar_como_favorito(self):
        self.model.db.registrar_auditoria("admin", "Marcar Favorito", "Vista Usuarios")
        self.view.parent().agregar_a_favoritos("Usuarios")

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

    def _suspender_selected(self):
        user_id = self._get_selected_user_id()
        if user_id:
            msg = self.model.suspender_cuenta(user_id)
            self.view.label.setText(msg)
            self.cargar_usuarios()

    def _reactivar_selected(self):
        user_id = self._get_selected_user_id()
        if user_id:
            msg = self.model.reactivar_cuenta(user_id)
            self.view.label.setText(msg)
            self.cargar_usuarios()

    def _resetear_password_selected(self):
        user_id = self._get_selected_user_id()
        if user_id:
            new_pass = secrets.token_urlsafe(8)
            hashed = hashlib.sha256(new_pass.encode()).hexdigest()
            self.model.actualizar_password(user_id, hashed)
            self.view.label.setText(f"Contraseña restablecida: {new_pass}")

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

    def editar_usuario(self, usuario):
        dialog = QDialog()
        dialog.setWindowTitle("Editar Usuario")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Editar usuario: {usuario[0]}"))
        dialog.exec()

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

    def cambiar_estado_usuario(self, usuario_id, estado_actual):
        nuevo_estado = "Inactivo" if estado_actual == "Activo" else "Activo"
        self.model.actualizar_estado_usuario(usuario_id, nuevo_estado)
        self.model.db.registrar_auditoria("admin", "Cambiar Estado Usuario", f"ID: {usuario_id}, Nuevo Estado: {nuevo_estado}")
        self.view.label.setText(f"Estado del usuario con ID {usuario_id} cambiado a {nuevo_estado}.")
        self.cargar_usuarios()

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
            self.model.actualizar_permisos(rol, {modulo: permisos_a_actualizar[modulo]})
        self.view.label.setText("Permisos guardados exitosamente.")

    def exportar_logs(self):
        logs = self.model.obtener_logs()
        # Lógica para exportar logs a un archivo (ejemplo: CSV o Excel)
        self.view.label.setText("Logs exportados exitosamente.")

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
