import pandas as pd
import pyodbc
import os
import numpy as np
import re
import unicodedata

# Ruta al archivo CSV LIMPIO (ahora siempre usará el archivo principal)
csv_path = os.path.join('data_inventario', 'INVENTARIO_COMPLETO_REHAU_LIMPIO.csv')

# Configuración de conexión (ajusta si es necesario)
server = "192.168.88.205"
database = "inventario"
username = "sa"
password = "mps.1887"
driver = "ODBC Driver 17 for SQL Server"

# Conectar a la base de datos
connection_string = (
    f"DRIVER={{{driver}}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
)

# Mapeo robusto: claves normalizadas
MAPEO_NORMALIZADO = {
    'codigo': 'codigo',
    'descripcion': 'descripcion',
    'stock': 'stock',
    'pedidos': 'pedido',
}

# Diccionario de abreviaturas a color real
ABREVIATURAS_COLOR_REAL = {
    'Rob': 'Roble',
    'Nog': 'Nogal',
    'Win': 'Winchester',
    'Nut': 'Nutmeg',
    'Hab': 'Habano',
    'B.Smoke': 'Black Smoke',
    'B.Brow': 'Black Brown',
    'Qua': 'Quartz',
    'Sheff': 'Sheffield',
    'Tit': 'Titanium',
    'N.M': 'Negro M',
    'Ant L': 'Ant L',
    'Ant M': 'Ant M',
    'Turn': 'Turner',
    'Mon': 'Monument',
    'Bco': 'Blanco',
}

def traducir_acabado_a_color_real(acabado):
    # Busca la abreviatura exacta o parcial en el string acabado
    for abrev, color_real in ABREVIATURAS_COLOR_REAL.items():
        if abrev in acabado:
            return color_real
    return acabado  # Si no encuentra, deja el valor original

# --- Utilidad para extraer tipo, acabado y longitud ---
def extraer_datos_descripcion_v2(descripcion):
    tipo = ""
    acabado = ""
    longitud = ""
    # Tipo: hasta 'Euro-Design'
    tipo_match = re.search(r"^(.*?)\s*Euro-Design", descripcion, re.IGNORECASE)
    if tipo_match:
        tipo = tipo_match.group(1).strip()
    # Acabado: entre '60' y 'Pres'
    acabado_match = re.search(r"60\s+(.*?)\s+Pres", descripcion)
    if acabado_match:
        acabado = acabado_match.group(1).strip()
    # Longitud: número antes de 'm.'
    longitud_match = re.search(r"([\d,.]+)\s*m", descripcion)
    if longitud_match:
        longitud = longitud_match.group(1).replace(",", ".")
    return tipo, acabado, longitud

# Leer el CSV (delimitador ; y probar utf-8, luego latin1)
try:
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(csv_path, sep=';', encoding='latin1')

# Normalizar nombres de columnas del DataFrame
def normalizar_columna(col):
    col = col.strip().lower()
    col = ''.join(c for c in unicodedata.normalize('NFD', col) if unicodedata.category(c) != 'Mn')
    return col

cols_norm = [normalizar_columna(c) for c in df.columns]
df.columns = cols_norm

# Renombrar usando el mapeo robusto
for col_orig, col_dest in MAPEO_NORMALIZADO.items():
    if col_orig in df.columns:
        df.rename(columns={col_orig: col_dest}, inplace=True)

# Renombrar columnas según mapeo y filtrar solo las que existen en la tabla
columnas_sql_base = [
    'codigo', 'descripcion', 'stock', 'pedido'
]
# Extra: campos granulares
columnas_extra = ['tipo', 'acabado', 'longitud', 'qr', 'color_real']

df = df[[col for col in columnas_sql_base if col in df.columns]]

# Limpiar y convertir campos numéricos problemáticos a float o 0
for campo in ['stock', 'pedido']:
    if campo in df.columns:
        df[campo] = pd.to_numeric(df[campo], errors='coerce').fillna(0)

# Asegurar que el código se trate siempre como string y con formato 'xxxxxx.xxx'
import re as _re
if 'codigo' in df.columns:
    def formatear_codigo(c):
        c = str(c).strip()
        # Si hay dos puntos, elimina solo el primero
        if c.count('.') == 2:
            c = c.replace('.', '', 1)
        # Si hay más de un punto, solo deja el último
        elif c.count('.') > 1:
            partes = c.split('.')
            c = ''.join(partes[:-1]) + '.' + partes[-1]
        return c
    df['codigo'] = df['codigo'].apply(lambda x: formatear_codigo(x) if pd.notnull(x) else '')

# Rellenar nulos en campos de texto con cadena vacía
for campo in ['codigo', 'descripcion']:
    if campo in df.columns:
        df[campo] = df[campo].fillna('')

# --- Desglose de descripción y generación de QR con extracción mejorada de color ---
if 'descripcion' in df.columns:
    tipos, acabados, longitudes, qrs, colores_reales = [], [], [], [], []
    for i in range(len(df['descripcion'])):
        desc = df['descripcion'].iloc[i]
        tipo, acabado, longitud = extraer_datos_descripcion_v2(desc)
        tipos.append(tipo)
        acabados.append(acabado)
        longitudes.append(longitud)
        codigo = df['codigo'].iloc[i] if 'codigo' in df.columns else ''
        qrs.append(f"QR-{codigo}" if isinstance(codigo, str) and codigo else '')
        color_real = traducir_acabado_a_color_real(acabado)
        colores_reales.append(color_real)
    df['tipo'] = tipos
    df['acabado'] = acabados
    df['longitud'] = longitudes
    df['qr'] = qrs
    df['color_real'] = colores_reales

# --- Validar columnas en la tabla SQL ---
def obtener_columnas_sql(cursor, tabla):
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{tabla}'")
    return set(row[0] for row in cursor.fetchall())

with pyodbc.connect(connection_string) as conn:
    cursor = conn.cursor()
    columnas_tabla = obtener_columnas_sql(cursor, 'inventario_perfiles')
    # Determinar columnas a insertar (solo las que existen en la tabla)
    columnas_insertar = [col for col in (columnas_sql_base + columnas_extra) if col in columnas_tabla and col in df.columns]
    if not set(['codigo', 'descripcion']).issubset(columnas_insertar):
        raise Exception(f"Faltan columnas obligatorias en la tabla inventario_perfiles: {set(['codigo','descripcion']) - set(columnas_insertar)}")
    # Limpiar la tabla antes de importar
    cursor.execute("DELETE FROM inventario_perfiles")
    # Resetear el contador de identidad (ID autoincremental)
    cursor.execute("DBCC CHECKIDENT ('inventario_perfiles', RESEED, 0)")
    conn.commit()
    errores = []
    for idx, row in df.iterrows():
        valores = [row.get(col, None) for col in columnas_insertar]
        placeholders = ','.join(['?'] * len(columnas_insertar))
        sql = f"INSERT INTO inventario_perfiles ({','.join(columnas_insertar)}) VALUES ({placeholders})"
        try:
            cursor.execute(sql, valores)
        except Exception as e:
            errores.append((idx, str(e), valores))
    conn.commit()

if errores:
    for idx, err, vals in errores:
        pass
else:
    pass
