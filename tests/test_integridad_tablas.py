"""
Test de integridad de tablas y columnas: compara los modelos del código con la estructura real de la base de datos.
Para cada módulo, informa:
- Qué módulo se revisa
- Qué tablas utiliza
- Qué columnas espera cada tabla
Luego compara con la base y reporta diferencias.
"""
import pytest
import pyodbc

DB_CONN_STR = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=stockdb;UID=usuario;PWD=contraseña"

# Estructura: modulo -> {tabla: [columnas]}
MODULOS_TABLAS = {
    'Obras': {
        'obras': [
            'nombre', 'cliente', 'estado', 'fecha_compra', 'cantidad_aberturas', 'pago_completo', 'pago_porcentaje',
            'monto_usd', 'monto_ars', 'fecha_medicion', 'dias_entrega', 'fecha_entrega', 'usuario_creador', 'rowversion'
        ]
    },
    'Inventario': {
        'inventario': ['id_material', 'nombre', 'cantidad', 'ubicacion', 'stock_minimo', 'tipo', 'activo'],
        'movimientos_inventario': ['id', 'id_material', 'tipo_movimiento', 'cantidad', 'fecha', 'usuario', 'motivo'],
        'pedidos_materiales': ['id_pedido', 'id_obra', 'fecha', 'estado', 'usuario']
    },
    'Herrajes': {
        'herrajes': ['id', 'nombre', 'tipo', 'stock', 'proveedor', 'activo'],
        'pedidos_herrajes': ['id_pedido', 'id_obra', 'fecha', 'estado', 'usuario']
    },
    'Vidrios': {
        'vidrios': ['id', 'tipo', 'espesor', 'medidas', 'stock', 'proveedor', 'activo'],
        'pedidos_vidrios': ['id_pedido', 'id_obra', 'fecha', 'estado', 'usuario']
    },
    'Producción': {
        'produccion': ['id_obra', 'estado', 'fecha_inicio', 'fecha_fin', 'responsable']
    },
    'Logística': {
        'logistica': ['id_obra', 'fecha_entrega', 'transportista', 'estado', 'observaciones']
    },
    'Contabilidad': {
        'facturas': ['id_factura', 'id_obra', 'monto', 'fecha', 'estado', 'usuario'],
        'pagos': ['id_pago', 'id_factura', 'monto', 'fecha', 'usuario']
    },
    'Usuarios': {
        'usuarios': ['id', 'nombre', 'email', 'rol', 'activo']
    },
    'Auditoría': {
        'auditoria': ['id', 'usuario', 'fecha', 'accion', 'modulo', 'detalle']
    },
    'Configuración': {
        'configuracion': ['clave', 'valor', 'descripcion']
    },
}

def obtener_columnas_tabla(cursor, tabla):
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (tabla,))
    return set(row[0] for row in cursor.fetchall())

@pytest.mark.parametrize("modulo, tablas_columnas", MODULOS_TABLAS.items())
def test_integridad_modulo(modulo, tablas_columnas):
    print(f"\n--- Revisión del módulo: {modulo} ---")
    conn = pyodbc.connect(DB_CONN_STR)
    cursor = conn.cursor()
    for tabla, columnas in tablas_columnas.items():
        print(f"\nTabla: {tabla}")
        print(f"Columnas esperadas: {columnas}")
        columnas_en_bd = obtener_columnas_tabla(cursor, tabla)
        print(f"Columnas en base: {sorted(columnas_en_bd)}")
        for col in columnas:
            assert col in columnas_en_bd, f"Falta la columna '{col}' en la tabla '{tabla}' (módulo {modulo})"
    conn.close()
