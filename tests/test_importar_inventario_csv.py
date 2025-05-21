import os
import pyodbc
import pandas as pd

def test_importar_csv_y_consultar():
    # Ejecutar el script de importación
    resultado = os.system('python scripts/importar_inventario_csv.py')
    assert resultado == 0, "El script de importación falló"

    # Conexión a la base de datos
    server = "192.168.88.205"
    database = "inventario"
    username = "sa"
    password = "mps.1887"
    driver = "ODBC Driver 17 for SQL Server"
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
        cursor.execute("SELECT COUNT(*) FROM inventario_perfiles")
        total = cursor.fetchone()[0]
        assert total > 0, "La tabla inventario_perfiles está vacía tras la importación"
        cursor.execute("SELECT TOP 5 codigo, descripcion, stock, pedido FROM inventario_perfiles")
        filas = cursor.fetchall()
        assert len(filas) > 0, "No se obtuvieron registros tras la importación"
        for fila in filas:
            assert fila[0] is not None, "El campo 'codigo' no debe ser None"
            assert fila[1] is not None, "El campo 'descripcion' no debe ser None"
    print("Test de importación y consulta de inventario_perfiles: OK")

def test_coincidencia_columnas_csv_sql():
    # Leer el CSV y verificar que las columnas requeridas existen
    csv_path = os.path.join('inventario', 'INVENTARIO COMPLETO - REHAU.csv')
    # Usar encoding utf-8 y mostrar nombres de columnas para debug
    try:
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(csv_path, sep=';', encoding='latin1')
    print("Columnas detectadas en el CSV:", list(df.columns))
    requeridas = {'Código', 'Descripción', 'STOCK', 'PEDIDOS'}
    assert requeridas.issubset(set(df.columns)), f"Faltan columnas requeridas en el CSV: {requeridas - set(df.columns)}"
    print("Test de columnas del CSV: OK")

if __name__ == "__main__":
    test_coincidencia_columnas_csv_sql()
    test_importar_csv_y_consultar()
