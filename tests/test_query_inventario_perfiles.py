import pyodbc

# Parámetros de conexión
server = "192.168.88.205"
database = "inventario"
username = "sa"
password = "mps.1887"
driver = "ODBC Driver 17 for SQL Server"

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
    print(f"Error al consultar la base de datos: {e}")
