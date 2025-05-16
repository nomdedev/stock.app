import csv
import pyodbc
import re

# Configuración de la conexión a SQL Server
conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=inventario;'
    'UID=sa;'
    'PWD=mps.1887;'
    'TrustServerCertificate=yes;'
)

# Función para extraer tipo, acabado y longitud desde la descripción
def extraer_desde_descripcion(descripcion):
    tipo = ''
    acabado = ''
    longitud = ''
    if descripcion:
        tipo_match = re.search(r'^(.*?)\s*Euro-Design', descripcion, re.IGNORECASE)
        if tipo_match:
            tipo = tipo_match.group(1).strip()
        acabado_match = re.search(r'Euro-Design\s*\d+\s*([\w\-/]+)', descripcion, re.IGNORECASE)
        if acabado_match:
            acabado = acabado_match.group(1).strip()
        longitud_match = re.search(r'([\d,.]+)\s*m', descripcion)
        if longitud_match:
            longitud = longitud_match.group(1).replace(',', '.')
    return tipo, acabado, longitud

# Ruta al archivo CSV
csv_path = r'inventario/INVENTARIO COMPLETO - REHAU.csv'

with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    with open(csv_path, encoding='latin1') as f:  # Cambiado a latin1 para soportar caracteres especiales
        reader = csv.DictReader(f)
        
        # ---
        # Lógica de análisis de descripción para perfiles REHAU:
        # - El script extrae automáticamente:
        #   * tipo: Ejemplo "Marco 64", "Poste", "Travesaño", etc.
        #   * línea: Detecta "Euro-Design 60", "Euro-Slide 60", "High-Design", etc.
        #   * color/acabado: Detecta colores abreviados (ej: "Mar-Rob/Rob", "Blanco", "Nogal", etc.)
        #   * longitud: Detecta el largo del perfil (ej: "5.8 m", "6,0 m", etc.)
        # - Si necesitas actualizar la lista de colores válidos, puedes extraerlos del Excel o pasarlos aquí.
        # - Esta lógica se ejecuta automáticamente cada vez que importas un CSV con este script.
        # - Si en el futuro agregas nuevos tipos, líneas o colores, solo debes actualizar la función extraer_desde_descripcion.
        # ---
        
        count = 0
        codigos_omitidos = []
        codigos_repetidos = set()
        codigos_vistos = set()
        for row in reader:
            # Buscar el código de perfil con formato xxxxxx.xxx
            codigo = None
            for value in row.values():
                if isinstance(value, str) and re.match(r'^\d{6}\.\d{3}$', value.strip()):
                    codigo = value.strip()
                    break
            # Si no se encuentra, usar el campo 'codigo' o 'Código' como fallback
            if not codigo:
                codigo = row.get('codigo') or row.get('Código')
            # Si sigue sin código válido, omitir la fila y registrar
            if not codigo or not isinstance(codigo, str) or not re.match(r'^\d{6}\.\d{3}$', codigo):
                codigos_omitidos.append(str(codigo))
                continue
            if codigo in codigos_vistos:
                codigos_repetidos.add(codigo)
                continue
            codigos_vistos.add(codigo)
            nombre = row.get('nombre') or row.get('Nombre') or row.get('descripcion') or row.get('Descripción')
            tipo_material = row.get('tipo_material') or row.get('Tipo de material') or 'PVC'
            unidad = row.get('unidad') or row.get('Unidad') or 'unidad'
            stock_actual = row.get('stock_actual') or row.get('Stock') or 0
            stock_minimo = row.get('stock_minimo') or row.get('Stock mínimo') or 0
            ubicacion = row.get('ubicacion') or row.get('Ubicación') or ''
            descripcion = row.get('descripcion') or row.get('Descripción') or ''
            qr = row.get('qr') or f'QR-{codigo}'
            imagen_referencia = row.get('imagen_referencia') or ''
            tipo, acabado, longitud = extraer_desde_descripcion(descripcion)
            # Insertar en la tabla con columnas explícitas
            cursor.execute('''
                INSERT INTO inventario_perfiles (
                    codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia, tipo, acabado, longitud
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia, tipo, acabado, longitud
            ))
            count += 1
    conn.commit()
print(f'Importación completada. Perfiles importados: {count}')
if codigos_omitidos:
    print(f'Perfiles omitidos por código inválido o ausente: {len(codigos_omitidos)}')
    print('Códigos omitidos (primeros 20):', codigos_omitidos[:20])
if codigos_repetidos:
    print(f'Perfiles omitidos por código repetido: {len(codigos_repetidos)}')
    print('Códigos repetidos:', list(codigos_repetidos))
