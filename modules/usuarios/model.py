import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from core.database import UsuariosDatabaseConnection

class UsuariosModel:
    """Modelo de Usuarios."""

    _SQL_SELECT_ID_BY_ROL = "SELECT id FROM usuarios WHERE rol = ?"
    _SQL_DELETE_PERMISOS_MODULOS_BY_USUARIO = "DELETE FROM permisos_modulos WHERE id_usuario = ?"
    _SQL_INSERT_PERMISOS_MODULOS = "INSERT INTO permisos_modulos (id_usuario, modulo, puede_ver, puede_modificar, puede_aprobar, creado_por) VALUES (?, ?, ?, ?, ?, ?)"

    def __init__(self, db_connection):
        """Inicializa el modelo con una conexión de base de datos."""
        if db_connection is None:
            raise TypeError("UsuariosModel requiere un db_connection explícito para evitar conexiones reales en tests y cumplir la política de aislamiento.")
        self.db = db_connection

    def obtener_usuarios(self):
        """Devuelve una lista de todos los usuarios."""
        query = "SELECT * FROM usuarios"
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def agregar_usuario(self, datos):
        """Agrega un nuevo usuario validando unicidad de usuario y email."""
        email = datos[2]
        username = datos[3]
        existe = self.db.ejecutar_query("SELECT * FROM usuarios WHERE email = ? OR usuario = ?", (email, username))
        if existe:
            raise ValueError("Usuario o email ya existe")
        query = "INSERT INTO usuarios (nombre, apellido, email, usuario, password_hash, rol, estado) VALUES (?, ?, ?, ?, ?, ?, 'Activo')"
        self.db.ejecutar_query(query, datos)

    def actualizar_password(self, usuario_id, password_hash):
        """Actualiza el hash de la contraseña de un usuario."""
        query = "UPDATE usuarios SET password_hash = ? WHERE id = ?"
        self.db.ejecutar_query(query, (password_hash, usuario_id))

    def actualizar_usuario(self, id_usuario, datos, fecha_actualizacion):
        """Actualiza los datos de un usuario."""
        set_clause = ", ".join([f"{k} = ?" for k in datos.keys()])
        valores = list(datos.values()) + [fecha_actualizacion, id_usuario]
        query = f"UPDATE usuarios SET {set_clause}, fecha_actualizacion = ? WHERE id = ?"
        self.db.ejecutar_query(query, valores)

    def eliminar_usuario(self, usuario_id):
        """Elimina un usuario por su ID."""
        query = "DELETE FROM usuarios WHERE id = ?"
        self.db.ejecutar_query(query, (usuario_id,))

    def actualizar_estado_usuario(self, usuario_id, nuevo_estado):
        """Actualiza el estado de un usuario."""
        query = "UPDATE usuarios SET estado = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, usuario_id))

    def obtener_roles(self):
        """Devuelve una lista de roles distintos registrados en la tabla usuarios."""
        query = "SELECT DISTINCT rol FROM usuarios"
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def obtener_permisos_por_rol(self, rol):
        """Devuelve los permisos asociados a un rol agrupados por módulo."""
        query = (
            "SELECT modulo, MAX(puede_ver), MAX(puede_modificar), MAX(puede_aprobar) "
            "FROM permisos_modulos pm "
            "JOIN usuarios u ON pm.id_usuario = u.id "
            "WHERE u.rol = ? "
            "GROUP BY modulo"
        )
        resultado = self.db.ejecutar_query(query, (rol,))
        return [(rol, *r) for r in resultado] if resultado else []

    def obtener_permisos_por_usuario(self, usuario_id, modulo):
        """Devuelve los permisos del usuario para un módulo específico."""
        query = (
            "SELECT puede_ver, puede_modificar, puede_aprobar "
            "FROM permisos_modulos "
            "WHERE id_usuario = ? AND modulo = ?"
        )
        resultado = self.db.ejecutar_query(query, (usuario_id, modulo))
        if resultado:
            return {
                "ver": bool(resultado[0][0]),
                "modificar": bool(resultado[0][1]),
                "aprobar": bool(resultado[0][2])
            }
        return {}

    def suspender_cuenta(self, id_usuario):
        """Suspende la cuenta de un usuario."""
        query = "UPDATE usuarios SET estado = 'suspendido' WHERE id = ?"
        self.db.ejecutar_query(query, (id_usuario,))
        return f"Cuenta del usuario {id_usuario} suspendida."

    def reactivar_cuenta(self, id_usuario):
        """Reactiva la cuenta de un usuario."""
        query = "UPDATE usuarios SET estado = 'activo' WHERE id = ?"
        self.db.ejecutar_query(query, (id_usuario,))
        return f"Cuenta del usuario {id_usuario} reactivada."

    def obtener_todos_los_modulos(self):
        """Devuelve una lista de todos los módulos registrados en permisos_modulos."""
        query = "SELECT DISTINCT modulo FROM permisos_modulos"
        resultado = self.db.ejecutar_query(query)
        return [r[0] for r in resultado] if resultado else []

    def actualizar_permisos_modulos_usuario(self, id_usuario, permisos_dict, creado_por):
        """Actualiza los permisos de módulos para un usuario, eliminando los previos para evitar duplicados."""
        # Eliminar permisos previos
        self.db.ejecutar_query(self._SQL_DELETE_PERMISOS_MODULOS_BY_USUARIO, (id_usuario,))
        # Insertar nuevos permisos
        for modulo, permisos in permisos_dict.items():
            self.db.ejecutar_query(
                self._SQL_INSERT_PERMISOS_MODULOS,
                (id_usuario, modulo, int(permisos.get('ver', False)), int(permisos.get('modificar', False)), int(permisos.get('aprobar', False)), creado_por)
            )

    def obtener_headers_usuarios(self):
        """Obtiene los nombres de columnas (headers) de la tabla usuarios desde la metadata de la base de datos."""
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
            return ['id', 'nombre', 'apellido', 'email', 'usuario', 'password_hash', 'rol', 'estado', 'fecha_creacion', 'fecha_actualizacion']

    def exportar_usuarios(self, formato: str) -> str:
        """Exporta la lista de usuarios en el formato solicitado ('excel' o 'pdf')."""
        query = "SELECT id, nombre, apellido, email, usuario, rol, estado, fecha_creacion, fecha_actualizacion FROM usuarios"
        try:
            datos = self.db.ejecutar_query(query) or []
            if not datos:
                return "No hay usuarios para exportar."
            formato = (formato or '').lower().strip()
            if formato not in ("excel", "pdf"):
                return "Formato no soportado. Use 'excel' o 'pdf'."
            from datetime import datetime
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            columnas = ["ID", "Nombre", "Apellido", "Email", "Usuario", "Rol", "Estado", "Fecha Creación", "Fecha Actualización"]
            if formato == "excel":
                nombre_archivo = f"usuarios_{fecha_str}.xlsx"
                return self._exportar_usuarios_excel(datos, columnas, nombre_archivo)
            else:
                nombre_archivo = f"usuarios_{fecha_str}.pdf"
                return self._exportar_usuarios_pdf(datos, columnas, nombre_archivo)
        except Exception as e:
            return f"Error al exportar los usuarios: {e}"

    def _exportar_usuarios_excel(self, datos, columnas, nombre_archivo):
        """Exporta usuarios a Excel."""
        try:
            import pandas as pd
            df = pd.DataFrame(datos, columns=columnas)
            df.to_excel(nombre_archivo, index=False)
            return f"Usuarios exportados a Excel: {nombre_archivo}"
        except Exception as e:
            return f"Error al exportar a Excel: {e}"

    def _exportar_usuarios_pdf(self, datos, columnas, nombre_archivo):
        """Exporta usuarios a PDF."""
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, "Listado de Usuarios", ln=True, align="C")
            pdf.set_font("Arial", style="B", size=10)
            header = " | ".join(columnas)
            pdf.cell(0, 8, header, ln=True)
            pdf.set_font("Arial", size=10)
            for row in datos:
                fila = " | ".join([str(x) if x is not None else "" for x in row])
                pdf.cell(0, 8, fila, ln=True)
            pdf.output(nombre_archivo)
            return f"Usuarios exportados a PDF: {nombre_archivo}"
        except Exception as e:
            return f"Error al exportar a PDF: {e}"

    def obtener_logs_usuarios(self):
        """Obtiene todos los logs de usuarios desde la tabla logs_usuarios."""
        query = "SELECT id, usuario_id, accion, modulo, fecha_hora, detalle, ip_origen FROM logs_usuarios ORDER BY fecha_hora DESC"
        resultado = self.db.ejecutar_query(query)
        return resultado if resultado else []

    def exportar_logs_usuarios(self, formato: str) -> str:
        """Exporta los logs de usuarios en el formato solicitado ('excel' o 'pdf')."""
        try:
            datos = self.obtener_logs_usuarios()
            if not datos:
                return "No hay logs de usuarios para exportar."
            formato = (formato or '').lower().strip()
            if formato not in ("excel", "pdf"):
                return "Formato no soportado. Use 'excel' o 'pdf'."
            import pandas as pd
            from datetime import datetime
            fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            columnas = ["ID", "Usuario ID", "Acción", "Módulo", "Fecha/Hora", "Detalle", "IP Origen"]
            if formato == "excel":
                nombre_archivo = f"logs_usuarios_{fecha_str}.xlsx"
                try:
                    df = pd.DataFrame(datos, columns=columnas)
                    df.to_excel(nombre_archivo, index=False)
                    return f"Logs de usuarios exportados a Excel: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a Excel: {e}"
            elif formato == "pdf":
                nombre_archivo = f"logs_usuarios_{fecha_str}.pdf"
                try:
                    from fpdf import FPDF
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, "Logs de Usuarios", ln=True, align="C")
                    pdf.set_font("Arial", style="B", size=10)
                    header = " | ".join(columnas)
                    pdf.cell(0, 8, header, ln=True)
                    pdf.set_font("Arial", size=10)
                    for row in datos:
                        fila = " | ".join([str(x) if x is not None else "" for x in row])
                        pdf.cell(0, 8, fila, ln=True)
                    pdf.output(nombre_archivo)
                    return f"Logs de usuarios exportados a PDF: {nombre_archivo}"
                except Exception as e:
                    return f"Error al exportar a PDF: {e}"
        except Exception as e:
            return f"Error al exportar los logs de usuarios: {e}"

    def obtener_usuario_por_nombre(self, nombre_usuario):
        """Devuelve todos los campos relevantes del usuario por nombre de usuario."""
        query = "SELECT id, usuario, password_hash, rol, nombre, apellido, email, estado FROM usuarios WHERE usuario = ?"
        res = self.db.ejecutar_query(query, (nombre_usuario,))
        if res and len(res) > 0:
            row = res[0]
            return {
                'id': row[0],
                'usuario': row[1],
                'password_hash': row[2],
                'rol': row[3] if len(row) > 3 else 'usuario',
                'nombre': row[4] if len(row) > 4 else '',
                'apellido': row[5] if len(row) > 5 else '',
                'email': row[6] if len(row) > 6 else '',
                'estado': row[7] if len(row) > 7 else 'activo'
            }
        return None

    def crear_usuarios_iniciales(self):
        """Crea los usuarios iniciales (admin y prueba) y asigna permisos básicos si no existen."""
        import hashlib

        admin_id = self._crear_usuario_si_no_existe("Administrador", "Admin", "admin@demo.com", "admin", "admin", "admin")
        prueba_id = self._crear_usuario_si_no_existe("Prueba", "Test", "prueba@demo.com", "prueba", "1", "usuario")

        modulos = self.obtener_todos_los_modulos()
        if not modulos:
            modulos = self.db.ejecutar_query("SELECT DISTINCT modulo FROM permisos_modulos")
            modulos = [m[0] for m in modulos] if modulos else []
        if not modulos:
            modulos = [
                'Inventario', 'Obras', 'Logística', 'Usuarios', 'Configuración'
            ]
        self._asignar_permisos(admin_id, modulos, (1, 1, 1))
        self._asignar_permisos(prueba_id, modulos, (1, 0, 0))

        modulos_criticos = [
            'Inventario', 'Obras', 'Logística', 'Usuarios', 'Configuración',
            'Herrajes', 'Compras / Pedidos', 'Vidrios', 'Mantenimiento', 'Producción', 'Contabilidad', 'Auditoría'
        ]
        self._asignar_permisos_criticos(admin_id, modulos_criticos, (1, 1, 1), admin_id)
        self._asignar_permisos_criticos(prueba_id, modulos_criticos, (1, 0, 0), admin_id)

    def _crear_usuario_si_no_existe(self, nombre, apellido, email, usuario, password, rol):
        """Crea un usuario si no existe y retorna su id."""
        import hashlib
        usuarios = self.db.ejecutar_query("SELECT usuario, id FROM usuarios")
        usernames = {u[0]: u[1] for u in usuarios} if usuarios else {}
        if usuario not in usernames:
            self.db.ejecutar_query(
                "INSERT INTO usuarios (nombre, apellido, email, usuario, password_hash, rol, estado) VALUES (?, ?, ?, ?, ?, ?, 'activo')",
                (nombre, apellido, email, usuario, hashlib.sha256(password.encode()).hexdigest(), rol)
            )
            return self.db.ejecutar_query("SELECT id FROM usuarios WHERE usuario = ?", (usuario,))[0][0]
        return usernames[usuario]

    def _asignar_permisos(self, usuario_id, modulos, permisos):
        """Asigna permisos a un usuario para una lista de módulos."""
        for modulo in modulos:
            self.db.ejecutar_query(
                self._SQL_INSERT_PERMISOS_MODULOS,
                (usuario_id, modulo, *permisos, usuario_id)
            )
            

    def _asignar_permisos_criticos(self, usuario_id, modulos_criticos, permisos, creado_por):
        """Asigna permisos críticos a un usuario si no existen."""
        for modulo in modulos_criticos:
            existe = self.db.ejecutar_query(
                "SELECT 1 FROM permisos_modulos WHERE id_usuario = ? AND modulo = ?", (usuario_id, modulo)
            )
            if not existe:
                self.db.ejecutar_query(
                    self._SQL_INSERT_PERMISOS_MODULOS,
                    (usuario_id, modulo, *permisos, creado_por)
                )

    def obtener_modulos_permitidos(self, usuario):
        """
        Devuelve una lista de módulos a los que el usuario tiene permiso de ver.
        Si el usuario es admin (rol == 'admin'), devuelve todos los módulos.
        Acepta usuario como dict, id o username.
        """
        # Si es dict, extraer id y rol
        usuario_id = None
        rol = None
        if isinstance(usuario, dict):
            usuario_id = usuario.get('id')
            rol = usuario.get('rol')
            if not usuario_id and usuario.get('username'):
                # Buscar id por username
                res = self.db.ejecutar_query("SELECT id, rol FROM usuarios WHERE usuario = ?", (usuario['username'],))
                if res:
                    usuario_id = res[0][0]
                    if not rol:
                        rol = res[0][1]
        elif isinstance(usuario, int):
            usuario_id = usuario
        elif isinstance(usuario, str):
            # Buscar id y rol por username
            res = self.db.ejecutar_query("SELECT id, rol FROM usuarios WHERE usuario = ?", (usuario,))
            if res:
                usuario_id = res[0][0]
                rol = res[0][1]
        # Si es admin, devolver todos los módulos
        if rol == 'admin':
            return self.obtener_todos_los_modulos()
        # Si no hay id, no puede consultar
        if not usuario_id:
            return []
        query = "SELECT modulo FROM permisos_modulos WHERE id_usuario = ? AND puede_ver = 1"
        resultado = self.db.ejecutar_query(query, (usuario_id,))
        return [r[0] for r in resultado] if resultado else []
