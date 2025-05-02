import os
import pyodbc
from datetime import datetime
from core.logger import Logger
from core.config import DB_SERVER, DB_USERNAME, DB_PASSWORD
from dotenv import load_dotenv
from mps.services.app_state import AppState

# Cargar variables de entorno desde .env
load_dotenv()

class BaseDatabaseConnection:
    def __init__(self, database):
        self.server = os.getenv("DB_SERVER", "localhost")
        self.username = os.getenv("DB_USERNAME", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = database
        self.driver = self.detectar_driver_odbc()

    @staticmethod
    def detectar_driver_odbc():
        # Detectar el controlador ODBC disponible
        drivers = pyodbc.drivers()
        if "ODBC Driver 18 for SQL Server" in drivers:
            return "ODBC Driver 18 for SQL Server"
        elif "ODBC Driver 17 for SQL Server" in drivers:
            return "ODBC Driver 17 for SQL Server"
        else:
            raise RuntimeError("No se encontró un controlador ODBC compatible. Instala ODBC Driver 17 o 18 para SQL Server.")

    def ejecutar_query(self, query, params=None):
        try:
            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"DATABASE={self.database};"
            )
            with pyodbc.connect(connection_string, timeout=10) as conn:  # Agregar timeout
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                AppState.set_db_status(self.database, True)  # Actualizar estado de conexión
                return cursor.fetchall()
        except pyodbc.OperationalError as e:
            Logger().error(f"Error de conexión: {e}")
            AppState.set_db_status(self.database, False)  # Marcar como desconectado
            raise RuntimeError(
                "No se pudo conectar a la base de datos. Verifica el nombre del servidor/instancia, "
                "las credenciales y que SQL Server permita conexiones remotas."
            ) from e
        except pyodbc.ProgrammingError as e:
            Logger().error(f"Error en la consulta SQL: {e}")
            raise RuntimeError("Error en la consulta SQL. Verifica la sintaxis y los parámetros.") from e
        except Exception as e:
            Logger().error(f"Error inesperado al ejecutar la consulta: {e}")
            raise RuntimeError("Ocurrió un error inesperado al ejecutar la consulta.") from e

class InventarioDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("inventario")

class UsuariosDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("users")

class AuditoriaDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("auditoria")

class ObrasDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("obras")

class ProduccionDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("produccion")

class LogisticaDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("logistica")

class PedidosDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("pedidos")

class ConfiguracionDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("configuracion")

class DatabaseConnection:
    def __init__(self, server="DESKTOP-QHMPTG0\\SQLEXPRESS", username="sa", password="mps.1887"):
        self.server = server
        self.username = username
        self.password = password
        self.driver = BaseDatabaseConnection.detectar_driver_odbc()

    def conectar_a_base(self, database):
        try:
            bases_validas = ["inventario", "users", "auditoria"]
            if database not in bases_validas:
                raise ValueError(f"La base de datos '{database}' no es válida. Bases disponibles: {bases_validas}")
            self.database = database
            print(f"Conexión establecida con la base de datos '{database}'.")
        except ValueError as e:
            print(f"Error de validación: {e}")
            Logger().error(f"Error de validación: {e}")
            raise
        except Exception as e:
            print(f"Error inesperado al conectar a la base de datos: {e}")
            Logger().error(f"Error inesperado al conectar a la base de datos: {e}")
            raise

    def ejecutar_query(self, query, params=None):
        if not hasattr(self, 'database'):
            raise ValueError("No se ha establecido una conexión a ninguna base de datos.")
        try:
            connection_string = (
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"DATABASE={self.database};"
            )
            with pyodbc.connect(connection_string, timeout=10) as conn:  # Agregar timeout
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                AppState.set_db_status(self.database, True)  # Actualizar estado de conexión
                return cursor.fetchall()
        except pyodbc.OperationalError as e:
            Logger().error(f"Error de conexión: {e}")
            AppState.set_db_status(self.database, False)  # Marcar como desconectado
            raise RuntimeError(
                "No se pudo conectar a la base de datos. Verifica el nombre del servidor/instancia, "
                "las credenciales y que SQL Server permita conexiones remotas."
            ) from e
        except pyodbc.ProgrammingError as e:
            Logger().error(f"Error en la consulta SQL: {e}")
            raise RuntimeError("Error en la consulta SQL. Verifica la sintaxis y los parámetros.") from e
        except Exception as e:
            Logger().error(f"Error inesperado al ejecutar la consulta: {e}")
            raise RuntimeError("Ocurrió un error inesperado al ejecutar la consulta.") from e

    @staticmethod
    def listar_bases_de_datos(server, username, password):
        try:
            driver = BaseDatabaseConnection.detectar_driver_odbc()
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"UID={username};"
                f"PWD={password};"
            )
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE state = 0;")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            Logger().error(f"Error al listar las bases de datos: {e}")
            raise

# Lógica para determinar la base de datos según el módulo
MODULO_BASE_DATOS = {
    "auditoria": "auditoria",  # Base de datos para auditorías
    "inventario": "inventario",  # Base de datos general
    "usuarios": "users",  # Base de datos para logs y usuarios
}

def obtener_base_datos_para_modulo(modulo):
    return MODULO_BASE_DATOS.get(modulo, None)

class DataAccessLayer:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_pedidos_por_estado(self, estado):
        query = "SELECT * FROM pedidos WHERE estado = %s"
        return self.db.ejecutar_query(query, (estado,))

    def insertar_material(self, material):
        query = "INSERT INTO materiales (nombre, cantidad, proveedor) VALUES (%s, %s, %s)"
        self.db.ejecutar_query(query, material)

    def get_usuarios_por_rol(self, rol):
        query = "SELECT * FROM usuarios WHERE rol = %s"
        return self.db.ejecutar_query(query, (rol,))

    def verificar_concurrencia(self, tabla, id_registro, fecha_actualizacion):
        query = f"SELECT fecha_actualizacion FROM {tabla} WHERE id = %s"
        resultado = self.db.ejecutar_query(query, (id_registro,))
        if resultado and resultado[0]['fecha_actualizacion'] != fecha_actualizacion:
            return False  # Conflicto detectado
        return True

    def actualizar_registro(self, tabla, id_registro, datos, fecha_actualizacion):
        if not self.verificar_concurrencia(tabla, id_registro, fecha_actualizacion):
            raise Exception("Conflicto de concurrencia detectado.")
        campos = ", ".join([f"{campo} = %s" for campo in datos.keys()])
        query = f"UPDATE {tabla} SET {campos}, fecha_actualizacion = %s WHERE id = %s"
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
        query = "INSERT INTO auditoria (usuario, accion, detalles, fecha) VALUES (%s, %s, %s, %s)"
        self.db.ejecutar_query(query, (usuario, accion, detalles, datetime.now().isoformat()))

    def registrar_login_fallido(self, ip, usuario, timestamp, estado):
        query = "INSERT INTO login_fallidos (ip, usuario, timestamp, estado) VALUES (%s, %s, %s, %s)"
        self.db.ejecutar_query(query, (ip, usuario, timestamp, estado))

    def actualizar_configuracion(self, clave, valor):
        query = "UPDATE configuracion SET valor = %s WHERE clave = %s"
        self.db.ejecutar_query(query, (valor, clave))

    def obtener_metricas(self):
        metricas = {
            "total_usuarios": self.db.ejecutar_query("SELECT COUNT(*) FROM usuarios")[0][''],
            "empresas_activas": self.db.ejecutar_query("SELECT COUNT(*) FROM empresas WHERE estado = 'Activo'")[0][''],
            "sesiones_activas": self.db.ejecutar_query("SELECT COUNT(*) FROM sesiones WHERE estado = 'Activa'")[0][''],
            "logs_sistema": self.db.ejecutar_query("SELECT COUNT(*) FROM logs")[0][''],
        }
        return metricas

    def obtener_actividad_reciente(self):
        query = "SELECT usuario, accion, fecha FROM auditoria ORDER BY fecha DESC LIMIT 10"
        return self.db.ejecutar_query(query)

    def sincronizar_datos(self):
        # Simulación de sincronización manual
        try:
            # Aquí se implementaría la lógica de sincronización con un servidor o base de datos remota
            pass  # Asegúrate de que no falte un paréntesis o carácter aquí
        except Exception as e:
            return f"Error durante la sincronización: {str(e)}"

    @staticmethod
    def detectar_plugins(modules_path="modules"):
        # Detectamos plugins en el directorio `modules`
        plugins = []
        for carpeta in os.listdir(modules_path):
            ruta_modulo = os.path.join(modules_path, carpeta)
            if os.path.isdir(ruta_modulo):
                archivos = os.listdir(ruta_modulo)
                if "controller.py" in archivos and "view.py" in archivos:
                    plugins.append(carpeta)
        return plugins
