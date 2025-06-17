"""
Test de verificación de existencia de tablas y columnas críticas en la base de datos de inventario.
Este archivo NO debe subirse a git (agregar a .gitignore si es necesario).
Configura los datos de conexión antes de ejecutar.
"""
import pyodbc
import pytest

# Configuración de conexión (ajusta según tu entorno, NO subir a git)
DB_SERVER = "localhost"
DB_NAME = "inventario"
DB_USER = "sa"
DB_PASSWORD = "mps.1887"
DRIVER = "ODBC Driver 17 for SQL Server"

# Tablas y columnas requeridas
TABLAS_COLUMNAS = {
    "inventario_perfiles": [
        "codigo", "descripcion", "tipo", "acabado", "numero", "vs", "proveedor", "longitud", "ancho", "alto", "necesarias", "stock", "faltan", "ped_min", "emba", "pedido", "importe"
    ],
    "materiales_por_obra": [
        "id_obra", "id_item", "cantidad_necesaria", "cantidad_reservada", "estado"
    ],
    "obras": [
        "nombre", "cliente", "estado", "fecha_compra", "cantidad_aberturas", "pago_completo", "pago_porcentaje", "monto_usd", "monto_ars", "fecha_medicion", "dias_entrega", "fecha_entrega", "usuario_creador", "rowversion"
    ],
    "cronograma_obras": [
        "id_obra", "etapa", "fecha_programada", "fecha_realizada", "observaciones", "responsable", "estado"
    ]
}

def get_connection():
    conn_str = (
        f"DRIVER={{{DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD};TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def test_tablas_y_columnas_existentes():
    """Verifica que todas las tablas y columnas críticas existen en la base de datos de inventario."""
    with get_connection() as conn:
        cursor = conn.cursor()
        for tabla, columnas in TABLAS_COLUMNAS.items():
            cursor.execute(f"SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", (tabla,))
            assert cursor.fetchone() is not None, f"Falta la tabla: {tabla}"
            for columna in columnas:
                cursor.execute(
                    "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? AND COLUMN_NAME = ?",
                    (tabla, columna)
                )
                assert cursor.fetchone() is not None, f"Falta la columna: {columna} en la tabla {tabla}"

if __name__ == "__main__":
    # Permite ejecutar el test directamente sin pytest
    test_tablas_y_columnas_existentes()
    print("✔ Todas las tablas y columnas requeridas existen en la base de datos de inventario.")
