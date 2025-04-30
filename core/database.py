import os
import pyodbc
from datetime import datetime

class BaseDatabaseConnection:
    def __init__(self, server, username, password, database):
        self.server = server
        self.username = username
        self.password = password
        self.database = database
        self.driver = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")  # Cambiar si usas otro controlador
        self.connection_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"DATABASE={self.database}"
        )

    def ejecutar_query(self, query, params=None):
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

class InventarioDatabaseConnection(BaseDatabaseConnection):
    def __init__(self, server="DESKTOP-QHMPTG0\\SQLEXPRESS", username="sa", password="mps.1887"):
        super().__init__(server, username, password, "inventario")

class UsuariosDatabaseConnection(BaseDatabaseConnection):
    def __init__(self, server="DESKTOP-QHMPTG0\\SQLEXPRESS", username="sa", password="mps.1887"):
        super().__init__(server, username, password, "users")

class AuditoriaDatabaseConnection(BaseDatabaseConnection):
    def __init__(self, server="DESKTOP-QHMPTG0\\SQLEXPRESS", username="sa", password="mps.1887"):
        super().__init__(server, username, password, "auditoria")

class DatabaseConnection:
    def __init__(self, server="DESKTOP-QHMPTG0\\SQLEXPRESS", username="sa", password="mps.1887"):
        self.server = server
        self.username = username
        self.password = password
        self.driver = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")  # Cambiar si usas otro controlador
        self.connection_string_template = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"DATABASE={{}}"
        )
        self.connection_string = None

    def conectar_a_base(self, database):
        try:
            self.connection_string = self.connection_string_template.format(database)
        except KeyError as e:
            Logger().error(f"Error al conectar a la base de datos: {e}. Verifique que el controlador ODBC necesario esté instalado.")
            raise
        except Exception as e:
            Logger().error(f"Error inesperado al conectar a la base de datos: {e}")
            raise

    def ejecutar_query(self, query, params=None):
        if not self.connection_string:
            raise ValueError("No se ha establecido una conexión a ninguna base de datos.")
        with pyodbc.connect(self.connection_string) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def listar_bases_de_datos(server, username, password):
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"UID={username};"
            f"PWD={password}"
        )
        query = "SELECT name FROM sys.databases WHERE state = 0;"
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]

# Lógica para determinar la base de datos según el módulo
MODULO_BASE_DATOS = {
    "auditoria": "auditoria",  # Base de datos para auditorías
    "compras": "compras_db",
    "configuracion": "configuracion_db",
    "contabilidad": "contabilidad_db",
    "inventario": "inventario",  # Base de datos general
    "logistica": "logistica_db",
    "mantenimiento": "mantenimiento_db",
    "materiales": "materiales_db",
    "notificaciones": "notificaciones_db",
    "obras": "obras_db",
    "pedidos": "pedidos_db",
    "produccion": "produccion_db",
    "usuarios": "usuarios_db",  # Base de datos para logs y usuarios
    "vidrios": "vidrios_db",
}

def obtener_base_datos_para_modulo(modulo):
    return MODULO_BASE_DATOS.get(modulo, None)

class DataAccessLayer:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_pedidos_por_estado(self, estado):
        query = "SELECT * FROM pedidos WHERE estado = ?"
        return self.db.ejecutar_query(query, (estado,))

    def insertar_material(self, material):
        query = "INSERT INTO materiales (nombre, cantidad, proveedor) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, material)

    def get_usuarios_por_rol(self, rol):
        query = "SELECT * FROM usuarios WHERE rol = ?"
        return self.db.ejecutar_query(query, (rol,))

    def verificar_concurrencia(self, tabla, id_registro, fecha_actualizacion):
        query = f"SELECT fecha_actualizacion FROM {tabla} WHERE id = ?"
        resultado = self.db.ejecutar_query(query, (id_registro,))
        if resultado and resultado[0][0] != fecha_actualizacion:
            return False  # Conflicto detectado
        return True

    def actualizar_registro(self, tabla, id_registro, datos, fecha_actualizacion):
        if not self.verificar_concurrencia(tabla, id_registro, fecha_actualizacion):
            raise Exception("Conflicto de concurrencia detectado.")
        campos = ", ".join([f"{campo} = ?" for campo in datos.keys()])
        query = f"UPDATE {tabla} SET {campos}, fecha_actualizacion = ? WHERE id = ?"
        valores = list(datos.values()) + [datetime.now().isoformat(), id_registro]
        self.db.ejecutar_query(query, valores)

    def verificar_integridad(self):
        problemas = []
        # Verificar obras sin cliente
        query_obras = "SELECT id FROM obras WHERE cliente IS NULL OR cliente = ''"
        obras_sin_cliente = self.db.ejecutar_query(query_obras)
        if obras_sin_cliente:
            problemas.append(f"Obras sin cliente: {len(obras_sin_cliente)}")

        # Verificar pedidos sin productos
        query_pedidos = "SELECT id FROM pedidos WHERE producto IS NULL OR producto = ''"
        pedidos_sin_productos = self.db.ejecutar_query(query_pedidos)
        if pedidos_sin_productos:
            problemas.append(f"Pedidos sin productos: {len(pedidos_sin_productos)}")

        # Verificar productos sin código válido
        query_productos = "SELECT id FROM inventario WHERE codigo IS NULL OR codigo = ''"
        productos_sin_codigo = self.db.ejecutar_query(query_productos)
        if productos_sin_codigo:
            problemas.append(f"Productos sin código válido: {len(productos_sin_codigo)}")

        return problemas

    def registrar_auditoria(self, usuario, accion, detalles):
        query = "INSERT INTO auditoria (usuario, accion, detalles, fecha) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, (usuario, accion, detalles, datetime.now().isoformat()))

    def registrar_login_fallido(self, ip, usuario, timestamp, estado):
        query = "INSERT INTO login_fallidos (ip, usuario, timestamp, estado) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, (ip, usuario, timestamp, estado))

    def actualizar_configuracion(self, clave, valor):
        query = "UPDATE configuracion SET valor = ? WHERE clave = ?"
        self.db.ejecutar_query(query, (valor, clave))

    def obtener_metricas(self):
        metricas = {
            "total_usuarios": self.db.ejecutar_query("SELECT COUNT(*) FROM usuarios")[0][0],
            "empresas_activas": self.db.ejecutar_query("SELECT COUNT(*) FROM empresas WHERE estado = 'Activo'")[0][0],
            "sesiones_activas": self.db.ejecutar_query("SELECT COUNT(*) FROM sesiones WHERE estado = 'Activa'")[0][0],
            "logs_sistema": self.db.ejecutar_query("SELECT COUNT(*) FROM logs")[0][0],
        }
        return metricas

    def obtener_actividad_reciente(self):
        query = "SELECT usuario, accion, fecha FROM auditoria ORDER BY fecha DESC LIMIT 10"
        return self.db.ejecutar_query(query)

    def sincronizar_datos(self):
        # Simulación de sincronización manual
        try:
            # Aquí se implementaría la lógica de sincronización con un servidor o base de datos remota
            return "Sincronización completada exitosamente."
        except Exception as e:
            return f"Error durante la sincronización: {str(e)}"

    @staticmethod
    def detectar_plugins(modules_path="modules"):
        plugins = []
        for carpeta in os.listdir(modules_path):
            ruta_modulo = os.path.join(modules_path, carpeta)
            if os.path.isdir(ruta_modulo):
                archivos = os.listdir(ruta_modulo)
                if "controller.py" in archivos and "view.py" in archivos:
                    plugins.append(carpeta)
        return plugins
