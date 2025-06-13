import pytest
import pyodbc

DB = 'inventario'

@pytest.mark.parametrize("item_id, ajuste, usuario", [
    (1, 5, 'admin'),   # Suma 5 al stock del item 1
    (2, -3, 'admin'),  # Resta 3 al stock del item 2
])
def test_ajuste_stock_y_movimiento(item_id, ajuste, usuario):
    conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER=localhost;DATABASE={DB};Trusted_Connection=yes;")
    cursor = conn.cursor()
    # Obtener stock actual antes
    cursor.execute("SELECT stock_actual FROM inventario_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    assert row is not None, f"No existe el item con id {item_id}"
    stock_antes = row[0]
    # Realizar el ajuste (simula la lógica del modelo/controlador)
    nuevo_stock = stock_antes + ajuste
    cursor.execute("UPDATE inventario_items SET stock_actual = ? WHERE id = ?", (nuevo_stock, item_id))
    conn.commit()
    # Registrar movimiento
    cursor.execute("""
        INSERT INTO movimientos_stock (id_item, fecha, tipo_movimiento, cantidad, realizado_por, detalle)
        VALUES (?, GETDATE(), ?, ?, ?, ?)
    """, (item_id, 'ajuste', ajuste, usuario, f'Ajuste de stock: {ajuste}'))
    conn.commit()
    # Verificar stock actualizado
    cursor.execute("SELECT stock_actual FROM inventario_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    assert row is not None, f"No existe el item con id {item_id} después del ajuste"
    stock_despues = row[0]
    assert stock_despues == nuevo_stock, f"El stock no se actualizó correctamente (esperado {nuevo_stock}, real {stock_despues})"
    # Verificar movimiento registrado
    cursor.execute("SELECT TOP 1 tipo_movimiento, cantidad, realizado_por FROM movimientos_stock WHERE id_item = ? ORDER BY id DESC", (item_id,))
    mov = cursor.fetchone()
    assert mov is not None, "No se registró el movimiento de stock"
    assert mov[0] == 'ajuste', f"El tipo de movimiento no es 'ajuste' sino {mov[0]}"
    assert mov[1] == ajuste, f"La cantidad registrada no coincide (esperado {ajuste}, real {mov[1]})"
    assert mov[2] == usuario, f"El usuario registrado no coincide (esperado {usuario}, real {mov[2]})"
    conn.close()
