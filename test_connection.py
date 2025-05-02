import pyodbc
from core.config import DB_SERVER, DB_SERVER_ALTERNATE, DB_USERNAME, DB_PASSWORD, DB_DEFAULT_DATABASE

def probar_conexion():
    try:
        print("Intentando conectar usando el nombre del servidor...")
        connection_string_alternate = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={DB_SERVER_ALTERNATE};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            f"DATABASE={DB_DEFAULT_DATABASE};"
        )
        with pyodbc.connect(connection_string_alternate, timeout=5) as conn:
            print("Conexión exitosa a la base de datos usando el nombre del servidor.")
            return
    except Exception as e:
        print(f"Error al conectar usando el nombre del servidor: {e}")

    try:
        print("Intentando conectar usando la IP del servidor...")
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={DB_SERVER};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            f"DATABASE={DB_DEFAULT_DATABASE};"
        )
        with pyodbc.connect(connection_string, timeout=5) as conn:
            print("Conexión exitosa a la base de datos usando IP.")
    except Exception as e:
        print(f"Error al conectar usando la IP: {e}")

if __name__ == "__main__":
    probar_conexion()
