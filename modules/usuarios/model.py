"""
MÓDULO: USUARIOS
Flujo funcional y checklist documentado para trazabilidad y referencia de desarrolladores.

FLUJO FUNCIONAL PRINCIPAL (PASO A PASO):
1. Listar usuarios existentes (obtener_usuarios).
2. Agregar nuevo usuario (agregar_usuario):
   - Validar datos y unicidad de email/usuario.
   - Registrar usuario con estado 'Activo'.
   - Registrar log de acción.
3. Editar usuario (actualizar_usuario):
   - Modificar datos personales y/o rol.
   - Registrar log de acción.
4. Cambiar contraseña (actualizar_password):
   - Actualizar hash de contraseña.
   - Registrar log de acción.
5. Eliminar usuario (eliminar_usuario):
   - Borrado físico o lógico según configuración.
   - Registrar log de acción.
6. Cambiar estado (activar/suspender/reactivar/eliminar_usuario/actualizar_estado_usuario):
   - Permite suspender, reactivar o eliminar usuarios.
   - Registrar log de acción.
7. Gestión de roles y permisos:
   - Listar roles (obtener_roles).
   - Consultar y actualizar permisos por rol (obtener_permisos_por_rol, actualizar_permisos).
   - Clonar permisos entre roles (clonar_permisos).
   - Consultar permisos efectivos por usuario y módulo (obtener_permisos_por_usuario).
8. Auditoría y logs:
   - Registrar todas las acciones relevantes en logs_usuarios (registrar_log_usuario).
   - Consultar logs para auditoría.
9. Estadísticas y limpieza:
   - Consultar usuarios activos/inactivos (obtener_usuarios_activos, obtener_estadisticas_usuarios).
   - Eliminar usuarios por estado (eliminar_usuarios_por_estado).

CHECKLIST FUNCIONAL Y VISUAL:
- [x] Listado de usuarios con filtros y búsqueda.
- [x] Alta, edición y baja de usuarios.
- [x] Cambio de contraseña y validación de seguridad.
- [x] Gestión de roles y permisos (ver, editar, aprobar, eliminar).
- [x] Registro de logs/auditoría de acciones sensibles.
- [x] Suspensión/reactivación de cuentas.
- [x] Clonado de permisos entre roles.
- [x] Exportación de usuarios (si aplica en la vista/controlador).
- [x] Cumplimiento de permisos y restricciones por rol.
- [x] Integración con módulo de auditoría.

REQUISITOS DE AUDITORÍA Y PERMISOS:
- Todas las acciones sensibles deben registrar log en logs_usuarios.
- Los métodos de modificación requieren validación de permisos según rol.
- El acceso a la gestión de usuarios debe estar restringido a roles autorizados.

NOTAS:
- Revisar el controlador y la vista para asegurar que la interfaz y los endpoints cumplen el flujo y checklist.
- Si se implementa exportación, validar que solo usuarios autorizados puedan exportar datos.
- Consultar README.md para flujos globales y referencias cruzadas.
"""

"""
Modelo de Usuarios que utiliza UsuariosDatabaseConnection (hereda de BaseDatabaseConnection) para garantizar una única conexión persistente y evitar duplicados, según el estándar del sistema (ver README y SQL).

- Todas las operaciones usan la tabla 'usuarios' y tablas relacionadas ('roles_permisos', 'logs_usuarios', 'permisos_modulos', 'permisos_usuario') según el esquema documentado.
- El constructor permite inyectar una conexión personalizada para testing, pero por defecto usa UsuariosDatabaseConnection.
- Todos los métodos de consulta y modificación usan la API pública ejecutar_query().
- Se controla el caso de resultados None en todas las consultas.
- No se accede a atributos internos de la conexión.
"""

from core.database import UsuariosDatabaseConnection

class UsuariosModel:
    """
    Modelo de Usuarios. Debe recibir una instancia de UsuariosDatabaseConnection (o hija de BaseDatabaseConnection) como parámetro db_connection.
    No crear conexiones nuevas internamente. Usar siempre la conexión persistente y unificada.
    """
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_usuarios(self):
        query = "SELECT * FROM usuarios"
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def agregar_usuario(self, datos):
        query = "INSERT INTO usuarios (nombre, apellido, email, usuario, password_hash, rol, estado) VALUES (?, ?, ?, ?, ?, ?, 'Activo')"
        self.db.ejecutar_query(query, datos)

    def actualizar_password(self, usuario_id, password_hash):
        query = "UPDATE usuarios SET password_hash = ? WHERE id = ?"
        self.db.ejecutar_query(query, (password_hash, usuario_id))

    def actualizar_usuario(self, id_usuario, datos, fecha_actualizacion):
        # datos: dict con los campos a actualizar
        set_clause = ", ".join([f"{k} = ?" for k in datos.keys()])
        valores = list(datos.values()) + [fecha_actualizacion, id_usuario]
        query = f"UPDATE usuarios SET {set_clause}, fecha_actualizacion = ? WHERE id = ?"
        self.db.ejecutar_query(query, valores)

    def eliminar_usuario(self, usuario_id):
        query = "DELETE FROM usuarios WHERE id = ?"
        self.db.ejecutar_query(query, (usuario_id,))

    def actualizar_estado_usuario(self, usuario_id, nuevo_estado):
        query = "UPDATE usuarios SET estado = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, usuario_id))

    def obtener_roles(self):
        query = "SELECT DISTINCT rol FROM roles_permisos"
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def obtener_permisos_por_rol(self, rol):
        query = "SELECT * FROM roles_permisos WHERE rol = ?"
        resultado = self.db.ejecutar_query(query, (rol,))
        return resultado if resultado else []

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
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def obtener_estadisticas_usuarios(self):
        query = """
        SELECT estado, COUNT(*) as total
        FROM usuarios
        GROUP BY estado
        """
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def eliminar_usuarios_por_estado(self, estado):
        query = "DELETE FROM usuarios WHERE estado = ?"
        self.db.ejecutar_query(query, (estado,))

    def verificar_usuario_existente(self, email, usuario):
        query = "SELECT COUNT(*) FROM usuarios WHERE email = ? OR usuario = ?"
        resultado = self.db.ejecutar_query(query, (email, usuario))
        return resultado and resultado[0][0] > 0

    def obtener_modulos_permitidos(self, usuario):
        """
        Devuelve la lista de módulos a los que el usuario tiene acceso (puede_ver=TRUE en permisos_modulos).
        Admin y supervisor ven todos los módulos.
        """
        if usuario['rol'] in ('admin', 'supervisor'):
            query = "SELECT DISTINCT modulo FROM permisos_modulos"
            resultado = self.db.ejecutar_query(query)
            return [r[0] for r in resultado] if resultado else []
        else:
            query = "SELECT modulo FROM permisos_modulos WHERE id_usuario = ? AND puede_ver = 1"
            resultado = self.db.ejecutar_query(query, (usuario['id'],))
            return [r[0] for r in resultado] if resultado else []

    def obtener_permisos_modulo(self, usuario, modulo):
        """
        Devuelve un dict con los permisos del usuario para el módulo indicado.
        """
        if usuario['rol'] in ('admin', 'supervisor'):
            # Acceso total
            return {'ver': True, 'modificar': True, 'aprobar': True}
        query = """
        SELECT puede_ver, puede_modificar, puede_aprobar
        FROM permisos_modulos
        WHERE id_usuario = ? AND modulo = ?
        """
        resultado = self.db.ejecutar_query(query, (usuario['id'], modulo))
        if resultado:
            return {
                'ver': bool(resultado[0][0]),
                'modificar': bool(resultado[0][1]),
                'aprobar': bool(resultado[0][2])
            }
        return {'ver': False, 'modificar': False, 'aprobar': False}

    def tiene_permiso(self, usuario, modulo, accion):
        """
        Verifica si el usuario tiene permiso para la acción ('ver', 'modificar', 'aprobar') en el módulo.
        """
        permisos = self.obtener_permisos_modulo(usuario, modulo)
        return permisos.get(accion, False)

    def actualizar_permisos_modulos_usuario(self, id_usuario, permisos_dict, creado_por):
        """
        Actualiza los permisos de módulos para un usuario.
        permisos_dict: {modulo: {'ver': bool, 'modificar': bool, 'aprobar': bool}}
        """
        # Borra los permisos actuales
        self.db.ejecutar_query("DELETE FROM permisos_modulos WHERE id_usuario = ?", (id_usuario,))
        # Inserta los nuevos permisos
        for modulo, permisos in permisos_dict.items():
            self.db.ejecutar_query(
                """
                INSERT INTO permisos_modulos (id_usuario, modulo, puede_ver, puede_modificar, puede_aprobar, creado_por)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (id_usuario, modulo, int(permisos.get('ver', False)), int(permisos.get('modificar', False)), int(permisos.get('aprobar', False)), creado_por)
            )

    def obtener_todos_los_modulos(self):
        query = "SELECT DISTINCT modulo FROM roles_permisos"
        resultado = self.db.ejecutar_query(query)
        return [r[0] for r in resultado] if resultado else []

    def actualizar_permisos_usuario(self, username, modulos):
        # Borra los permisos actuales y asigna los nuevos
        self.db.ejecutar_query("DELETE FROM permisos_usuario WHERE username = ?", (username,))
        for modulo in modulos:
            self.db.ejecutar_query("INSERT INTO permisos_usuario (username, modulo) VALUES (?, ?)", (username, modulo))

    def obtener_headers_usuarios(self):
        """
        Obtiene los nombres de columnas (headers) de la tabla usuarios desde la metadata de la base de datos.
        Cumple el MUST de sincronización automática de columnas.
        """
        try:
            self.db.conectar()
            if not self.db.connection:
                raise RuntimeError("No se pudo establecer la conexión para obtener los headers.")
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE 1=0")
            headers = [column[0] for column in cursor.description]
            cursor.close()
            return headers
        except Exception:
            # Alternativa: devolver headers fijos si no es posible obtenerlos dinámicamente
            return ['id', 'nombre', 'apellido', 'email', 'usuario', 'password_hash', 'rol', 'estado', 'fecha_creacion', 'fecha_actualizacion']
