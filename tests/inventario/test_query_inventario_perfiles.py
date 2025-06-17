import os
from dotenv import load_dotenv
import pyodbc

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Parámetros de conexión desde variables de entorno para evitar hardcodeo
server = os.getenv("DB_SERVER")
database = os.getenv("DB_DEFAULT_DATABASE", "inventario")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

try:
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    with pyodbc.connect(connection_string, timeout=5) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 20 * FROM inventario_perfiles")
        rows = cursor.fetchall()
        print("Primeros 20 registros de inventario_perfiles:")
        for row in rows:
            print(row)
except Exception as e:
    print(f"Error al conectar: {e}")
