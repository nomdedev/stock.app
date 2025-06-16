import pytest
import pyodbc
import re
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env privado
load_dotenv()

# Ruta a la documentación de referencia
doc_path = "docs/estructura_tablas_por_modulo.md"

def get_db_connection():
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    server = os.environ.get('DB_SERVER')
    database = os.environ.get('DB_DEFAULT_DATABASE', 'inventario')
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    timeout = os.environ.get('DB_TIMEOUT', '5')
    assert server and username and password, "Faltan variables de entorno para la conexión a la base de datos"
    connection_string = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;Timeout={timeout};"
    )
    return pyodbc.connect(connection_string)

def parse_doc_tables(doc_path):
    """Parsea la documentación y devuelve un dict {tabla: [columnas]}"""
    tablas = {}
    with open(doc_path, encoding="utf-8") as f:
        lines = f.readlines()
    tabla_actual = None
    for line in lines:
        if line.strip().startswith('**Tabla:**'):
            tabla_actual = line.split('**Tabla:**')[1].strip().replace('`','')
            tablas[tabla_actual] = []
        elif line.strip().startswith('-') and tabla_actual and 'Columnas:' not in line:
            col_match = re.match(r'-\s+`([^`]+)`', line)
            if col_match:
                col = col_match.group(1)
                tablas[tabla_actual].append(col)
        elif line.strip().startswith('---'):
            tabla_actual = None
    return tablas

def get_db_tables_and_columns():
    """Devuelve un dict {tabla: [columnas]} de la base de datos actual"""
    tablas = {}
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        for row in cursor.fetchall():
            tabla = row[0]
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tabla}'")
            columnas = [r[0] for r in cursor.fetchall()]
            tablas[tabla] = columnas
    return tablas

def test_estructura_bd_vs_documentacion():
    doc_tablas = parse_doc_tables(doc_path)
    db_tablas = get_db_tables_and_columns()
    errores = []
    # Tablas faltantes
    for tabla in doc_tablas:
        if tabla not in db_tablas:
            errores.append(f"Tabla faltante en BD: {tabla}")
    # Columnas faltantes o sobrantes
    for tabla, cols_doc in doc_tablas.items():
        if tabla in db_tablas:
            cols_db = db_tablas[tabla]
            for col in cols_doc:
                if col not in cols_db:
                    errores.append(f"Columna faltante en BD: {tabla}.{col}")
            for col in cols_db:
                if col not in cols_doc:
                    errores.append(f"Columna extra en BD: {tabla}.{col}")
    # Tablas extra
    for tabla in db_tablas:
        if tabla not in doc_tablas:
            errores.append(f"Tabla extra en BD: {tabla}")
    assert not errores, "\n" + "\n".join(errores)
