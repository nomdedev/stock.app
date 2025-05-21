import pandas as pd
import re
import unicodedata

# Archivo fuente y destino
csv_path = 'data_inventario/INVENTARIO_COMPLETO_REHAU_LIMPIO.csv'
out_path = 'data_inventario/inventario_formato_final.csv'

# Diccionario de abreviaturas a color real
ABREVIATURAS_COLOR_REAL = {
    'Rob': 'Roble', 'Nog': 'Nogal', 'Win': 'Winchester', 'Nut': 'Nutmeg', 'Hab': 'Habano',
    'B.Smoke': 'Black Smoke', 'B.Brow': 'Black Brown', 'Qua': 'Quartz', 'Sheff': 'Sheffield',
    'Tit': 'Titanium', 'N.M': 'Negro M', 'Ant L': 'Ant L', 'Ant M': 'Ant M', 'Turn': 'Turner',
    'Mon': 'Monument', 'Bco': 'Blanco',
}

def traducir_acabado_a_color_real(acabado):
    for abrev, color_real in ABREVIATURAS_COLOR_REAL.items():
        if abrev in acabado:
            return color_real
    return acabado

def extraer_campos(descripcion):
    # Tipo: hasta Euro-Design o primer número
    tipo = ''
    linea = ''
    color = ''
    longitud = ''
    # Buscar línea
    linea_match = re.search(r'Euro-Design \d+', descripcion)
    if linea_match:
        linea = linea_match.group(0)
    # Tipo: antes de la línea
    if linea:
        tipo = descripcion.split(linea)[0].strip()
    else:
        tipo_match = re.match(r'^(.*?)(\d+)', descripcion)
        if tipo_match:
            tipo = tipo_match.group(1).strip()
    # Color: entre línea y Pres
    color_match = re.search(r'\d+\s+([\w\-./ ]+)\s+Pres', descripcion)
    if color_match:
        color = color_match.group(1).strip()
    # Longitud: número antes de m.
    longitud_match = re.search(r'([\d,.]+)\s*m', descripcion)
    if longitud_match:
        longitud = longitud_match.group(1).replace(',', '.')
    return tipo, linea, color, longitud

def normalizar_col(col):
    col = col.strip().lower()
    col = ''.join(c for c in unicodedata.normalize('NFD', col) if unicodedata.category(c) != 'Mn')
    return col

def procesar():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    df.columns = [normalizar_col(c) for c in df.columns]
    rows = []
    incompletos = []
    for _, row in df.iterrows():
        codigo = str(row.get('codigo', '')).strip()
        descripcion = str(row.get('descripcion', '')).strip()
        stock = row.get('stock', 0)
        pedidos = row.get('pedidos', 0)
        tipo, linea, color, longitud = extraer_campos(descripcion)
        acabado = color
        color_real = traducir_acabado_a_color_real(acabado)
        if not (tipo and linea and color and longitud):
            incompletos.append({
                'codigo': codigo, 'descripcion': descripcion, 'tipo': tipo, 'linea': linea, 'color': color, 'longitud': longitud
            })
        rows.append({
            'codigo': codigo,
            'descripcion': descripcion,
            'tipo': tipo,
            'linea': linea,
            'acabado': acabado,
            'color_real': color_real,
            'longitud': longitud,
            'stock': stock,
            'pedidos': pedidos
        })
    # Guardar CSV final
    df_final = pd.DataFrame(rows)
    df_final.to_csv(out_path, sep=';', index=False)
    # Guardar incompletos
    if incompletos:
        pd.DataFrame(incompletos).to_csv('data_inventario/inventario_items_incompletos.csv', sep=';', index=False)
    print(f"Archivo final generado: {out_path}")
    if incompletos:
        print(f"Se encontraron {len(incompletos)} items incompletos. Ver inventario_items_incompletos.csv")

if __name__ == '__main__':
    procesar()
