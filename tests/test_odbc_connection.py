import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

def probar_conexion(driver, server, username, password, database):
    try:
        print(f"Probando conexión con el controlador: {driver}")
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"UID={username};"
            f"PWD={password};"
            f"DATABASE={database};"
        )
        with pyodbc.connect(connection_string) as conn:
            print(f"Conexión exitosa con el controlador: {driver}")
    except Exception as e:
        print(f"Error al conectar con el controlador {driver}: {e}")

if __name__ == "__main__":
    # Configuración de la base de datos desde variables de entorno
    server = os.getenv("DB_SERVER")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_DEFAULT_DATABASE", "inventario_perfiles")

    # Lista de controladores a probar
    drivers = ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]

    for driver in drivers:
        probar_conexion(driver, server, username, password, database)
