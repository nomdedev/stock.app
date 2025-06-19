import pandas as pd
import re
import unicodedata
from core.logger import Logger

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

LINEAS_REALES = [
    'Euro Design 60', 'Euro Design Slide', 'High Design Slide', 'Synego',
    'Euro-Design 60', 'Euro-Design Slide', 'High-Design Slide'  # variantes aceptadas
]

# Normaliza tildes y mayúsculas
def normalizar(texto):
    if not isinstance(texto, str):
        return ''
    texto = texto.strip().lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def traducir_acabado_a_color_real(acabado):
    for abrev, color_real in ABREVIATURAS_COLOR_REAL.items():
        if abrev in acabado:
            return color_real
    return acabado

def extraer_campos(descripcion):
    desc = normalizar(descripcion)
    linea = ''
    tipo = ''
    acabado = ''
    color_real = ''
    longitud = ''
    # Regex robusto para variantes de 'design/desing' y errores comunes
    linea_regex = r'(euro[- ]?(?:d[e3]s[i1l]g?n?|d[e3]s[i1l]n?g?) ?60|euro[- ]?(?:d[e3]s[i1l]g?n?|d[e3]s[i1l]n?g?) ?slide|high[- ]?(?:d[e3]s[i1l]g?n?|d[e3]s[i1l]n?g?) ?slide|synego)'
    match_linea = re.search(linea_regex, desc, re.IGNORECASE)
    if match_linea:
        linea = match_linea.group(1)
        partes = re.split(linea_regex, desc, flags=re.IGNORECASE)
        tipo = partes[0].strip().title()
        after_linea = partes[2] if len(partes) > 2 else ''
        after_linea = after_linea if isinstance(after_linea, str) else str(after_linea)
        # Color/acabado: lo que está entre la línea y 'pres'
        match_color = re.search(r'(.+?)\s*pres', after_linea)
        if match_color:
            acabado = match_color.group(1).strip()
        else:
            # Si no hay 'pres', tomar hasta el final
            acabado = after_linea.strip()
    else:
        # CASOS ESPECIALES: mosquitero, vierteaguas, etc.
        tipo_match = re.match(r'([a-záéíóúüñ ]+)', desc)
        if tipo_match:
            tipo = tipo_match.group(1).strip().title()
        match_color = re.search(r'contramarco [\w-]+ ([\w ./-]+)\s*pres', desc)
        if not match_color:
            match_color = re.search(r'contramarco [\w-]+ ([\w ./-]+)', desc)
        if not match_color:
            match_color = re.search(r'perfil [\w-]+ ([\w ./-]+)\s*pres', desc)
        if not match_color:
            match_color = re.search(r'perfil [\w-]+ ([\w ./-]+)', desc)
        if not match_color:
            match_color = re.search(r'viertea?guas? [\w-]+ ([\w ./-]+)\s*pres', desc)
        if not match_color:
            match_color = re.search(r'viertea?guas? [\w-]+ ([\w ./-]+)', desc)
        if match_color:
            acabado = match_color.group(1).strip()
        if not acabado:
            match_color2 = re.search(r'([\w ./-]+)\s*pres', desc)
            if match_color2:
                acabado = match_color2.group(1).strip()
        long_match = re.search(r'pres\.?\s*([\d,.]+)', desc)
        if long_match:
            longitud = long_match.group(1).replace(',', '.')
        else:
            long_match2 = re.search(r'(\d+[.,]?\d*)\s*m\.?$', desc)
            if long_match2:
                longitud = long_match2.group(1).replace(',', '.')
    # Color real: parte después de la barra o traducido
    color_real = traducir_acabado_a_color_real(acabado.split('/')[-1] if '/' in acabado else acabado)
    if not acabado:
        match_color2 = re.search(r'(\w+)\s*pres', desc)
        if match_color2:
            acabado = match_color2.group(1)
            color_real = traducir_acabado_a_color_real(acabado)
    return tipo, linea, acabado, color_real, longitud

def procesar():
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    # Normalizar nombres de columnas para acceso flexible
    df.columns = [c.strip().lower() for c in df.columns]
    # Buscar nombres de columna compatibles
    col_codigo = next((c for c in df.columns if 'codigo' in c), 'codigo')
    col_desc = next((c for c in df.columns if 'desc' in c), 'descripcion')
    col_stock = next((c for c in df.columns if 'stock' in c), 'stock')
    col_pedidos = next((c for c in df.columns if 'pedido' in c), 'pedidos')
    rows = []
    incompletos = []
    for _, row in df.iterrows():
        codigo = str(row.get(col_codigo, '')).strip()
        descripcion = str(row.get(col_desc, '')).strip()
        stock = row.get(col_stock, 0)
        pedidos = row.get(col_pedidos, 0)
        tipo, linea, acabado, color_real, longitud = extraer_campos(descripcion)
        if not (tipo and linea and acabado and longitud):
            incompletos.append({
                'codigo': codigo, 'descripcion': descripcion, 'tipo': tipo, 'linea': linea, 'acabado': acabado, 'color_real': color_real, 'longitud': longitud
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
    Logger().info(f"Archivo final generado: {out_path}")
    if incompletos:
        Logger().info(f"Se encontraron {len(incompletos)} items incompletos. Ver inventario_items_incompletos.csv")

if __name__ == '__main__':
    procesar()
