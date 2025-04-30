import pyodbc

def probar_conexion():
    try:
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-QHMPTG0\\SQLEXPRESS;"
            "UID=sa;"
            "PWD=mps.1887;"
            "DATABASE=inventario;"
        )
        with pyodbc.connect(connection_string) as conn:
            print("Conexión exitosa a la base de datos.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    probar_conexion()
