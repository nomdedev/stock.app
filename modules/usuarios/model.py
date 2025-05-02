from core.database import UsuariosDatabaseConnection  # Importar la clase correcta

class UsuariosModel:
    def __init__(self, db_connection=None):
        self.db = db_connection or UsuariosDatabaseConnection()  # Usar UsuariosDatabaseConnection

    def obtener_usuarios(self):
        query = "SELECT * FROM usuarios"
        return self.db.ejecutar_query(query)

    def agregar_usuario(self, datos):
        # datos: (nombre, apellido, email, usuario, password_hash, rol)
        query = "INSERT INTO usuarios (nombre, apellido, email, usuario, password_hash, rol, estado) VALUES (?, ?, ?, ?, ?, ?, 'Activo')"
        self.db.ejecutar_query(query, datos)

    def actualizar_password(self, usuario_id, password_hash):
        query = "UPDATE usuarios SET password_hash = ? WHERE id = ?"
        self.db.ejecutar_query(query, (password_hash, usuario_id))

    def actualizar_usuario(self, id_usuario, datos, fecha_actualizacion):
        self.db.actualizar_registro("usuarios", id_usuario, datos, fecha_actualizacion)

    def eliminar_usuario(self, usuario_id):
        query = "DELETE FROM usuarios WHERE id = ?"
        self.db.ejecutar_query(query, (usuario_id,))

    def actualizar_estado_usuario(self, usuario_id, nuevo_estado):
        query = "UPDATE usuarios SET estado = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, usuario_id))

    def obtener_roles(self):
        query = "SELECT DISTINCT rol FROM roles_permisos"
        return self.db.ejecutar_query(query)

    def obtener_permisos_por_rol(self, rol):
        query = "SELECT * FROM roles_permisos WHERE rol = ?"
        return self.db.ejecutar_query(query, (rol,))

    def actualizar_permisos(self, rol, permisos):
        query = """
        UPDATE roles_permisos
        SET permiso_ver = ?, permiso_editar = ?, permiso_aprobar = ?, permiso_eliminar = ?
        WHERE rol = ? AND modulo = ?
        """
        for modulo, permiso in permisos.items():
            self.db.ejecutar_query(query, (*permiso, rol, modulo))

    def registrar_log_usuario(self, datos):
        query = """
        INSERT INTO logs_usuarios (usuario_id, accion, modulo, detalle, ip_origen)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def obtener_permisos_por_usuario(self, usuario_id, modulo):
        query = """
        SELECT permiso_ver, permiso_editar, permiso_aprobar, permiso_eliminar
        FROM roles_permisos
        WHERE rol = (SELECT rol FROM usuarios WHERE id = ?) AND modulo = ?
        """
        resultado = self.db.ejecutar_query(query, (usuario_id, modulo))
        if resultado:
            return {
                "ver": resultado[0][0],
                "editar": resultado[0][1],
                "aprobar": resultado[0][2],
                "eliminar": resultado[0][3]
            }
        return {}

    def suspender_cuenta(self, id_usuario):
        query = "UPDATE usuarios SET estado = 'suspendido' WHERE id = ?"
        self.db.ejecutar_query(query, (id_usuario,))
        return f"Cuenta del usuario {id_usuario} suspendida."

    def reactivar_cuenta(self, id_usuario):
        query = "UPDATE usuarios SET estado = 'activo' WHERE id = ?"
        self.db.ejecutar_query(query, (id_usuario,))
        return f"Cuenta del usuario {id_usuario} reactivada."

    def clonar_permisos(self, rol_origen, rol_destino):
        query_obtener_permisos = """
        SELECT modulo, permiso_ver, permiso_editar, permiso_aprobar, permiso_eliminar
        FROM roles_permisos
        WHERE rol = ?
        """
        permisos = self.db.ejecutar_query(query_obtener_permisos, (rol_origen,))
        if not permisos:
            return f"No se encontraron permisos para el rol '{rol_origen}'."

        query_insertar_permisos = """
        INSERT INTO roles_permisos (rol, modulo, permiso_ver, permiso_editar, permiso_aprobar, permiso_eliminar)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        for permiso in permisos:
            self.db.ejecutar_query(query_insertar_permisos, (rol_destino, *permiso))

        return f"Permisos del rol '{rol_origen}' clonados al rol '{rol_destino}'."

    def obtener_usuarios_activos(self):
        query = "SELECT * FROM usuarios WHERE estado = 'activo'"
        return self.db.ejecutar_query(query)

    def obtener_estadisticas_usuarios(self):
        query = """
        SELECT estado, COUNT(*) as total
        FROM usuarios
        GROUP BY estado
        """
        return self.db.ejecutar_query(query)

    def eliminar_usuarios_por_estado(self, estado):
        query = "DELETE FROM usuarios WHERE estado = ?"
        self.db.ejecutar_query(query, (estado,))

    def verificar_usuario_existente(self, email, usuario):
        query = "SELECT COUNT(*) FROM usuarios WHERE email = ? OR usuario = ?"
        resultado = self.db.ejecutar_query(query, (email, usuario))
        return resultado[0][0] > 0
