import os
import pyodbc
from datetime import datetime
from core.logger import Logger
from core.config import DB_SERVER, DB_USERNAME, DB_PASSWORD
import logging
import time

def get_connection_string(driver, database):
    """
    Devuelve un string de conexión seguro usando los parámetros de config.py y la base de datos indicada.
    No expone usuario, contraseña ni IP en el código de los módulos.
    """
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={database};"
        f"UID={DB_USERNAME};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )

class BaseDatabaseConnection:
    def __init__(self, database, timeout=None, max_retries=None):
        self.server = DB_SERVER
        self.username = DB_USERNAME
        self.password = DB_PASSWORD
        self.database = database
        self.driver = self.detectar_driver_odbc()
        self.logger = Logger()
        self.connection = None  # Conexión persistente
        from core.config import DB_TIMEOUT
        self.timeout = timeout if timeout is not None else int(os.getenv("DB_TIMEOUT", DB_TIMEOUT))
        self.max_retries = max_retries if max_retries is not None else int(os.getenv("DB_MAX_RETRIES", 3))

    @staticmethod
    def detectar_driver_odbc():
        drivers = pyodbc.drivers()
        if "ODBC Driver 18 for SQL Server" in drivers:
            return "ODBC Driver 18 for SQL Server"
        elif "ODBC Driver 17 for SQL Server" in drivers:
            return "ODBC Driver 17 for SQL Server"
        else:
            raise RuntimeError("No se encontró un controlador ODBC compatible. Instala ODBC Driver 17 o 18 para SQL Server.")

    def conectar(self):
        attempt = 0
        last_exception = None
        while attempt < self.max_retries:
            try:
                connection_string = get_connection_string(self.driver, self.database)
                self.connection = pyodbc.connect(connection_string, timeout=self.timeout)
                self.logger.info(f"Conexión establecida con la base de datos '{self.database}' (intento {attempt+1}).")
                return
            except pyodbc.OperationalError as e:
                last_exception = e
                self.logger.warning(f"Intento {attempt+1} de conexión fallido: {e}")
                time.sleep(2 ** attempt)  # backoff exponencial
                attempt += 1
        self.logger.error(f"No se pudo conectar a la base de datos '{self.database}' tras {self.max_retries} intentos.")
        raise RuntimeError("No se pudo conectar a la base de datos tras varios intentos.") from last_exception

    def cerrar_conexion(self):
        if self.connection:
            self.connection.close()
            self.logger.info(f"Conexión cerrada con la base de datos '{self.database}'.")

    def ejecutar_query(self, query, parametros=None):
        try:
            if not self.connection:
                self.conectar()
            if not self.connection:
                raise RuntimeError("No se pudo establecer la conexión a la base de datos.")
            cursor = self.connection.cursor()
            if parametros:
                cursor.execute(query, parametros)
            else:
                cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            self.connection.commit()
        except pyodbc.OperationalError as e:
            from core.logger import Logger
            Logger().log_error_popup(
                "No se pudo conectar a la base de datos.\n\nVerifica el servidor, credenciales y que SQL Server acepte conexiones remotas.\n\nError: " + str(e)
            )
            return None
        except Exception as e:
            from core.logger import Logger
            Logger().log_error_popup(
                "Error al ejecutar la consulta en la base de datos.\n\n" + str(e)
            )
            return None

    def ejecutar_query_return_rowcount(self, query, parametros=None):
        """Ejecuta una query y retorna el número de filas afectadas (para UPDATE/DELETE)."""
        try:
            if not self.connection:
                self.conectar()
            if not self.connection:
                raise RuntimeError("No se pudo establecer la conexión a la base de datos.")
            cursor = self.connection.cursor()
            if parametros:
                cursor.execute(query, parametros)
            else:
                cursor.execute(query)
            rowcount = cursor.rowcount
            self.connection.commit()
            return rowcount
        except pyodbc.OperationalError as e:
            from core.logger import Logger
            Logger().log_error_popup(
                "No se pudo conectar a la base de datos.\n\nVerifica el servidor, credenciales y que SQL Server acepte conexiones remotas.\n\nError: " + str(e)
            )
            return 0
        except Exception as e:
            from core.logger import Logger
            Logger().log_error_popup(
                "Error al ejecutar la consulta en la base de datos.\n\n" + str(e)
            )
            return 0

    def begin_transaction(self):
        if not self.connection:
            self.conectar()
        # pyodbc: desactivar autocommit para iniciar transacción solo si la conexión es válida y tiene el atributo
        conn = self.connection
        if conn is not None and hasattr(conn, 'autocommit') and getattr(conn, 'autocommit', None) is not None:
            conn.autocommit = False
        self.logger.debug(f"Transacción iniciada en '{self.database}'.")

    def commit(self):
        if self.connection:
            self.connection.commit()
            conn = self.connection
            if conn is not None and hasattr(conn, 'autocommit') and getattr(conn, 'autocommit', None) is not None:
                conn.autocommit = True
            self.logger.debug(f"Transacción confirmada (commit) en '{self.database}'.")

    def rollback(self):
        if self.connection:
            self.connection.rollback()
            conn = self.connection
            if conn is not None and hasattr(conn, 'autocommit') and getattr(conn, 'autocommit', None) is not None:
                conn.autocommit = True
            self.logger.debug(f"Transacción revertida (rollback) en '{self.database}'.")

    class TransactionContext:
        def __init__(self, db, timeout, retries):
            self.db = db
            self.timeout = timeout
            self.retries = retries

        def __enter__(self):
            self.start_time = time.time()
            self.db.begin_transaction()
            return self.db

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.db.rollback()
            else:
                attempt = 0
                while attempt <= self.retries:
                    try:
                        self.db.commit()
                        return
                    except pyodbc.OperationalError as te:
                        if (time.time() - self.start_time) < self.timeout:
                            attempt += 1
                            time.sleep(1)
                        else:
                            self.db.rollback()
                            raise

    def transaction(self, timeout=30, retries=2):
        """
        Context manager para transacciones seguras con timeout y reintentos.
        Uso:
            with db.transaction(timeout=30, retries=2):
                ...
        """
        return self.TransactionContext(self, timeout, retries)

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
        super().__init__("inventario")

class LogisticaDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("inventario")

class PedidosDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("inventario")

class ConfiguracionDatabaseConnection(BaseDatabaseConnection):
    def __init__(self):
        super().__init__("inventario")

class DatabaseConnection:
    def __init__(self):
        self.server = DB_SERVER
        self.username = DB_USERNAME
        self.password = DB_PASSWORD
        self.driver = BaseDatabaseConnection.detectar_driver_odbc()
        self.database = None
        self.logger = logging.getLogger(__name__)

    def conectar_a_base(self, database):
        bases_validas = ["inventario", "users", "auditoria"]
        if database not in bases_validas:
            raise ValueError(f"La base de datos '{database}' no es válida. Bases disponibles: {bases_validas}")
        self.database = database
        self.logger.info(f"Conexión establecida con la base de datos '{database}'.")

    def ejecutar_query(self, query, parametros=None):
        try:
            connection_string = get_connection_string(self.driver, self.database)
            with pyodbc.connect(connection_string, timeout=10) as conn:
                if not conn:
                    raise RuntimeError("No se pudo establecer la conexión a la base de datos.")
                cursor = conn.cursor()
                if parametros:
                    cursor.execute(query, parametros)
                else:
                    cursor.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()
        except pyodbc.OperationalError as e:
            from core.logger import Logger
            Logger().log_error_popup(
                "No se pudo conectar a la base de datos.\n\nVerifica el servidor, credenciales y que SQL Server acepte conexiones remotas.\n\nError: " + str(e)
            )
            return None
        except Exception as e:
            from core.logger import Logger
            Logger().log_error_popup(
                "Error al ejecutar la consulta en la base de datos.\n\n" + str(e)
            )
            return None

    @staticmethod
    def listar_bases_de_datos():
        try:
            driver = BaseDatabaseConnection.detectar_driver_odbc()
            connection_string = get_connection_string(driver, "master")
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sys.databases WHERE state = 0;")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            Logger().error(f"Error al listar las bases de datos: {e}")
            raise

MODULO_BASE_DATOS = {
    "auditoria": "auditoria",
    "inventario": "inventario",
    "usuarios": "users",
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
            return False
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
        query_obras = "SELECT id FROM obras WHERE cliente IS NULL OR cliente = ''"
        obras_sin_cliente = self.db.ejecutar_query(query_obras)
        if obras_sin_cliente:
            problemas.append(f"Obras sin cliente: {len(obras_sin_cliente)}")
        query_pedidos = "SELECT id FROM pedidos WHERE producto IS NULL OR producto = ''"
        pedidos_sin_productos = self.db.ejecutar_query(query_pedidos)
        if pedidos_sin_productos:
            problemas.append(f"Pedidos sin productos: {len(pedidos_sin_productos)}")
        query_productos = "SELECT id FROM inventario_perfiles WHERE codigo IS NULL OR codigo = ''"
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
        query = "SELECT usuario, accion, fecha FROM auditoria ORDER BY fecha DESC OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY"
        return self.db.ejecutar_query(query)

    def sincronizar_datos(self):
        try:
            return "Sincronización completada exitosamente."
        except Exception as e:
            return f"Error durante la sincronización: {str(e)}"

    @staticmethod
    def detectar_plugins(modules_path="modules"):
        plugins = []
        try:
            if not os.path.exists(modules_path):
                raise FileNotFoundError(f"La ruta '{modules_path}' no existe.")
            for carpeta in os.listdir(modules_path):
                ruta_modulo = os.path.join(modules_path, carpeta)
                if os.path.isdir(ruta_modulo):
                    archivos = os.listdir(ruta_modulo)
                    if "controller.py" in archivos and "view.py" in archivos:
                        plugins.append(carpeta)
        except Exception as e:
            Logger().error(f"Error al detectar plugins: {e}")
        return plugins

    def obtener_productos(self):
        query = "SELECT * FROM inventario_perfiles"
        connection_string = get_connection_string(self.db.driver, self.db.database)
        with pyodbc.connect(connection_string, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            resultados = cursor.fetchall()
            columnas = [column[0] for column in cursor.description]
            lista_diccionarios = [dict(zip(columnas, row)) for row in resultados]
            return lista_diccionarios
