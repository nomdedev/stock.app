import pytest
from core.database import DatabaseConnection, MODULO_BASE_DATOS

# Mapeo de tablas a las columnas que deberían existir según la implementación
EXPECTED_SCHEMA = {
    'obras': [
        'id', 'nombre', 'cliente', 'estado', 'fecha_compra', 'cantidad_aberturas',
        'pago_completo', 'pago_porcentaje', 'monto_usd', 'monto_ars',
        'fecha_medicion', 'dias_entrega', 'fecha_entrega', 'usuario_creador', 'rowversion'
    ],
    'inventario': [
        'id', 'id_material', 'nombre', 'cantidad', 'ubicacion', 'stock_minimo'
    ],
    'movimientos_inventario': [
        'id', 'id_inventario', 'tipo_movimiento', 'cantidad', 'fecha', 'usuario', 'motivo'
    ],
    'herrajes': [
        'id', 'nombre', 'tipo', 'stock', 'proveedor'
    ],
    'pedidos_herrajes': [
        'id_pedido', 'id_obra', 'fecha', 'estado', 'usuario'
    ],
    'vidrios': [
        'id', 'tipo', 'espesor', 'ancho', 'alto', 'stock', 'proveedor'
    ],
    'pedidos_vidrios': [
        'id_pedido', 'id_obra', 'fecha', 'estado', 'usuario'
    ],
    'pedidos_materiales': [
        'id_pedido', 'id_obra', 'fecha', 'estado', 'usuario'
    ],
    'produccion': [
        'id', 'id_obra', 'estado', 'fecha_inicio', 'fecha_fin', 'responsable'
    ],
    'logistica': [
        'id', 'id_obra', 'fecha_entrega', 'transportista', 'estado', 'observaciones'
    ],
    'facturas': [
        'id_factura', 'id_obra', 'monto', 'fecha', 'estado', 'usuario'
    ],
    'pagos': [
        'id_pago', 'id_factura', 'monto', 'fecha', 'usuario'
    ],
    'usuarios': [
        'id', 'username', 'email', 'rol', 'activo', 'password_hash', 'fecha_creacion'
    ],
    'auditoria': [
        'id', 'usuario_id', 'modulo', 'accion', 'detalle', 'fecha', 'ip'
    ],
    'configuracion': [
        'id', 'clave', 'valor', 'descripcion'
    ]
}

@pytest.mark.parametrize('table, expected_cols', EXPECTED_SCHEMA.items())
def test_table_columns_exist(table, expected_cols):
    """
    Verifica que cada tabla tenga exactamente las columnas esperadas.
    """
    db = DatabaseConnection()
    # Determinar la base de datos según el módulo
    module = table.split('_')[0]
    db_name = MODULO_BASE_DATOS.get(module, 'inventario')
    db.conectar_a_base(db_name)
    # Obtener columnas reales desde INFORMATION_SCHEMA
    rows = db.ejecutar_query(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (table,)
    )
    assert rows is not None, f"No se pudo obtener columnas para tabla {table}"
    actual_cols = {row[0] for row in rows}
    missing = set(expected_cols) - actual_cols
    extra = actual_cols - set(expected_cols)
    assert not missing, f"Faltan columnas en tabla '{table}': {sorted(missing)}"
    assert not extra, f"Columnas inesperadas en tabla '{table}': {sorted(extra)}"
