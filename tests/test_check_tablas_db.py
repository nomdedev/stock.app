import pytest
import pyodbc
import inspect
import os
import re

# Mapeo de cada tabla a su base de datos REAL (solo las que existen: inventario, users, auditoria)
TABLA_A_BASE = {
    # USERS
    'usuarios': 'users',
    'permisos_modulos': 'users',
    'logs_usuarios': 'users',
    'notificaciones': 'users',
    # INVENTARIO
    'inventario_items': 'inventario',
    'inventario_perfiles': 'inventario',
    'movimientos_stock': 'inventario',
    'reservas_stock': 'inventario',
    'reservas_materiales': 'inventario',
    'perfiles_por_obra': 'inventario',
    'materiales': 'inventario',
    # OBRAS Y PEDIDOS (si están en inventario)
    'obras': 'inventario',
    'cronograma_obras': 'inventario',
    'materiales_por_obra': 'inventario',
    'pedidos': 'inventario',
    'pedidos_compra': 'inventario',
    'detalle_pedido': 'inventario',
    'pedidos_por_obra': 'inventario',
    # AUDITORIA
    'auditorias_sistema': 'auditoria',
    'errores_sistema': 'auditoria',
}

# Listado de tablas y columnas requeridas por módulo (solo las que están en las bases reales)
TABLAS_Y_COLUMNAS = {
    # USERS
    'usuarios': [
        'id', 'nombre', 'apellido', 'email', 'usuario', 'password_hash', 'rol', 'estado', 'fecha_creacion', 'ultimo_login', 'ip_ultimo_login', 'rowversion'
    ],
    'permisos_modulos': [
        'id', 'usuario_id', 'modulo', 'permiso', 'fecha_otorgado', 'puede_ver', 'puede_modificar', 'puede_aprobar', 'creado_por'
    ],
    'logs_usuarios': [
        'id', 'usuario_id', 'accion', 'fecha', 'detalle', 'ip_origen'
    ],
    'notificaciones': [
        'id', 'mensaje', 'fecha', 'tipo', 'leido', 'usuario_id'
    ],
    # INVENTARIO
    'inventario_items': [
        'id', 'codigo', 'nombre', 'tipo', 'stock_actual', 'stock_minimo', 'ubicacion', 'descripcion', 'qr', 'imagen_referencia', 'rowversion'
    ],
    'inventario_perfiles': [
        'id', 'codigo', 'nombre', 'tipo_material', 'unidad', 'stock_actual', 'stock_minimo', 'ubicacion', 'descripcion', 'qr', 'imagen_referencia', 'rowversion'
    ],
    'movimientos_stock': [
        'id', 'id_item', 'tipo_movimiento', 'cantidad', 'fecha', 'usuario', 'detalle'
    ],
    'reservas_stock': [
        'id', 'id_item', 'id_obra', 'cantidad_reservada', 'fecha', 'estado'
    ],
    'reservas_materiales': [
        'id', 'id_item', 'cantidad_reservada', 'referencia_obra', 'estado'
    ],
    'perfiles_por_obra': [
        'id', 'id_obra', 'id_perfil', 'cantidad_reservada', 'estado'
    ],
    'materiales': [
        'id', 'codigo', 'descripcion', 'cantidad', 'ubicacion', 'observaciones', 'rowversion'
    ],
    # OBRAS Y PEDIDOS (si están en inventario)
    'obras': [
        'id', 'nombre', 'cliente', 'estado', 'fecha', 'cantidad_aberturas', 'pago_completo', 'pago_porcentaje', 'monto_usd', 'monto_ars', 'fecha_medicion', 'dias_entrega', 'fecha_entrega', 'usuario_creador', 'rowversion'
    ],
    'cronograma_obras': [
        'id', 'id_obra', 'etapa', 'fecha_inicio', 'fecha_fin', 'estado', 'fecha_programada', 'fecha_realizada', 'observaciones', 'responsable'
    ],
    'materiales_por_obra': [
        'id', 'id_obra', 'id_item', 'cantidad_necesaria', 'cantidad_reservada', 'estado'
    ],
    'pedidos': [
        'id', 'id_obra', 'fecha_emision', 'estado', 'total_estimado', 'usuario', 'rowversion'
    ],
    'pedidos_compra': [
        'id', 'id_obra', 'fecha', 'estado', 'usuario', 'total_usd', 'total_ars', 'rowversion'
    ],
    'detalle_pedido': [
        'id', 'id_pedido', 'id_item', 'cantidad', 'precio_unitario', 'subtotal', 'estado'
    ],
    'pedidos_por_obra': [
        'id', 'id_pedido', 'id_obra', 'id_item', 'tipo_item', 'cantidad_requerida'
    ],
    # AUDITORIA
    'auditorias_sistema': [
        'id', 'usuario', 'modulo', 'accion', 'fecha', 'detalle', 'ip_origen', 'modulo_afectado', 'tipo_evento'
    ],
    'errores_sistema': [
        'id', 'fecha', 'modulo', 'detalle', 'usuario', 'ip_origen'
    ],
}

def obtener_columnas_tabla(cursor, tabla):
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (tabla,))
    return set(row[0] for row in cursor.fetchall())

def obtener_tablas_db(cursor):
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    return set(row[0] for row in cursor.fetchall())

def get_db_connection(base):
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    server = os.environ.get('DB_SERVER')
    username = os.environ.get('DB_USERNAME')
    password = os.environ.get('DB_PASSWORD')
    timeout = os.environ.get('DB_TIMEOUT', '5')
    assert server and username and password, "Faltan variables de entorno para la conexión a la base de datos"
    connection_string = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={base};UID={username};PWD={password};TrustServerCertificate=yes;Timeout={timeout};"
    )
    return pyodbc.connect(connection_string)

def get_conn_for_tabla(tabla):
    base = TABLA_A_BASE.get(tabla)
    assert base is not None, f"No se ha definido la base de datos para la tabla '{tabla}'"
    return get_db_connection(base)

@pytest.mark.parametrize("tabla, columnas", TABLAS_Y_COLUMNAS.items())
def test_tabla_y_columnas(tabla, columnas):
    conn = get_conn_for_tabla(tabla)
    cursor = conn.cursor()
    # Verificar existencia de la tabla
    cursor.execute("SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = ?", (tabla,))
    assert cursor.fetchone() is not None, f"La tabla '{tabla}' no existe en la base de datos correspondiente."
    # Verificar columnas
    columnas_db = obtener_columnas_tabla(cursor, tabla)
    for col in columnas:
        assert col in columnas_db, f"Falta la columna '{col}' en la tabla '{tabla}'"
    conn.close()

def test_tablas_extra_y_faltantes():
    """Verifica si hay tablas en la base que no están en el modelo y viceversa, por base."""
    bases = set(TABLA_A_BASE.values())
    for base in bases:
        conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER=localhost;DATABASE={base};Trusted_Connection=yes;")
        cursor = conn.cursor()
        tablas_db = obtener_tablas_db(cursor)
        tablas_modelo = {t for t, b in TABLA_A_BASE.items() if b == base}
        extra = tablas_db - tablas_modelo
        faltantes = tablas_modelo - tablas_db
        if extra:
            print(f"Tablas en la base de datos '{base}' que no están en el modelo: {extra}")
        if faltantes:
            print(f"Tablas requeridas por el modelo que faltan en la base '{base}': {faltantes}")
        assert not faltantes, f"Faltan tablas en la base de datos '{base}': {faltantes}"
        conn.close()

def test_columnas_extra_y_faltantes():
    """Verifica si hay columnas en la base que no están en el modelo y viceversa, por tabla y base."""
    bases = set(TABLA_A_BASE.values())
    for base in bases:
        conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER=localhost;DATABASE={base};Trusted_Connection=yes;")
        cursor = conn.cursor()
        tablas_db = obtener_tablas_db(cursor)
        tablas_modelo = {t for t, b in TABLA_A_BASE.items() if b == base}
        tablas_comunes = tablas_db & tablas_modelo
        for tabla in tablas_comunes:
            columnas_db = obtener_columnas_tabla(cursor, tabla)
            columnas_modelo = set(TABLAS_Y_COLUMNAS.get(tabla, []))
            extra = columnas_db - columnas_modelo
            faltantes = columnas_modelo - columnas_db
            if extra:
                print(f"Columnas en la tabla '{tabla}' de la base '{base}' que no están en el modelo: {extra}")
            if faltantes:
                print(f"Columnas requeridas por el modelo que faltan en la tabla '{tabla}' de la base '{base}': {faltantes}")
            assert not faltantes, f"Faltan columnas en la tabla '{tabla}' de la base '{base}': {faltantes}"
        conn.close()
