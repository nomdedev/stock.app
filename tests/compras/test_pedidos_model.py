import pytest
import sqlite3
from modules.pedidos.model import PedidosModel

def setup_db():
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE obras (id_obra INTEGER PRIMARY KEY, nombre TEXT);
        CREATE TABLE inventario_perfiles (id_perfil INTEGER PRIMARY KEY, stock_actual INTEGER, precio_unitario REAL);
        CREATE TABLE perfiles_por_obra (id_obra INTEGER, id_perfil INTEGER, cantidad_reservada INTEGER);
        CREATE TABLE herrajes (id_herraje INTEGER PRIMARY KEY, stock_actual INTEGER, precio_unitario REAL);
        CREATE TABLE herrajes_por_obra (id_obra INTEGER, id_herraje INTEGER, cantidad_reservada INTEGER);
        CREATE TABLE vidrios (id_vidrio INTEGER PRIMARY KEY, stock_actual INTEGER, precio_unitario REAL);
        CREATE TABLE vidrios_por_obra (id_obra INTEGER, id_vidrio INTEGER, cantidad_reservada INTEGER);
        CREATE TABLE pedidos (id_pedido INTEGER PRIMARY KEY AUTOINCREMENT, id_obra INTEGER, fecha_emision TEXT, estado TEXT, total_estimado REAL);
        CREATE TABLE pedidos_por_obra (id_pedido INTEGER, id_obra INTEGER, id_item INTEGER, tipo_item TEXT, cantidad_requerida INTEGER);
        CREATE TABLE movimientos_stock (id_mov INTEGER PRIMARY KEY AUTOINCREMENT, id_perfil INTEGER, tipo_movimiento TEXT, cantidad INTEGER, fecha TEXT, usuario TEXT);
        CREATE TABLE movimientos_herrajes (id_mov INTEGER PRIMARY KEY AUTOINCREMENT, id_herraje INTEGER, tipo_movimiento TEXT, cantidad INTEGER, fecha TEXT, usuario TEXT);
        CREATE TABLE movimientos_vidrios (id_mov INTEGER PRIMARY KEY AUTOINCREMENT, id_vidrio INTEGER, tipo_movimiento TEXT, cantidad INTEGER, fecha TEXT, usuario TEXT);
        CREATE TABLE auditorias_sistema (usuario TEXT, modulo TEXT, accion TEXT, fecha TEXT);
    """)
    return conn

@pytest.fixture
def model():
    conn = setup_db()
    class DummyConn:
        def __init__(self, c):
            self.connection = c
        def ejecutar_query(self, q, p=()):
            cur = self.connection.cursor()
            cur.execute(q, p)
            self.connection.commit()
            return cur.fetchall()
        def transaction(self, timeout=30, retries=2):
            class Tx:
                def __enter__(self_): return self
                def __exit__(self_, exc_type, exc_val, exc_tb): pass
            return Tx()
    return PedidosModel(DummyConn(conn))

def test_generar_pedido(model):
    db = model.db
    db.ejecutar_query("INSERT INTO obras (id_obra, nombre) VALUES (?, ?)", (1, "ObraTest"))
    db.ejecutar_query("INSERT INTO inventario_perfiles (id_perfil, stock_actual, precio_unitario) VALUES (1, 5, 100)")
    db.ejecutar_query("INSERT INTO perfiles_por_obra (id_obra, id_perfil, cantidad_reservada) VALUES (1, 1, 10)")
    id_pedido = model.generar_pedido_por_obra(1, usuario="admin")
    pedido = db.ejecutar_query("SELECT * FROM pedidos WHERE id_pedido=?", (id_pedido,))
    assert pedido and pedido[0][3] == "Pendiente" and pedido[0][4] == 500
    item = db.ejecutar_query("SELECT * FROM pedidos_por_obra WHERE id_pedido=?", (id_pedido,))
    assert item and item[0][2] == 1 and item[0][4] == 5
    aud = db.ejecutar_query("SELECT * FROM auditorias_sistema WHERE accion LIKE ?", (f"%{id_pedido}%",))
    assert aud

def test_recibir_pedido_exitoso(model):
    db = model.db
    db.ejecutar_query("INSERT INTO pedidos (id_pedido, id_obra, fecha_emision, estado, total_estimado) VALUES (1, 1, '2025-06-01', 'Pendiente', 500)")
    db.ejecutar_query("INSERT INTO pedidos_por_obra (id_pedido, id_obra, id_item, tipo_item, cantidad_requerida) VALUES (1, 1, 1, 'perfil', 5)")
    db.ejecutar_query("INSERT INTO inventario_perfiles (id_perfil, stock_actual, precio_unitario) VALUES (1, 5, 100)")
    ok = model.recibir_pedido(1, usuario="admin")
    assert ok
    pedido = db.ejecutar_query("SELECT estado FROM pedidos WHERE id_pedido=1")
    assert pedido[0][0] == "Recibido"
    stock = db.ejecutar_query("SELECT stock_actual FROM inventario_perfiles WHERE id_perfil=1")
    assert stock[0][0] == 10
    mov = db.ejecutar_query("SELECT * FROM movimientos_stock WHERE id_perfil=1 AND tipo_movimiento='Ingreso'")
    assert mov and mov[0][2] == "Ingreso" and mov[0][3] == 5
    aud = db.ejecutar_query("SELECT * FROM auditorias_sistema WHERE accion LIKE ?", ("%Recibió pedido%",))
    assert aud

def test_recibir_pedido_repetido(model):
    db = model.db
    db.ejecutar_query("INSERT INTO pedidos (id_pedido, id_obra, fecha_emision, estado, total_estimado) VALUES (2, 1, '2025-06-01', 'Recibido', 500)")
    with pytest.raises(ValueError):
        model.recibir_pedido(2, usuario="admin")
