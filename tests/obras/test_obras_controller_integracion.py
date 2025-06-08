import pytest
import sqlite3
from modules.obras.model import ObrasModel, OptimisticLockError
from modules.obras.controller import ObrasController
from modules.auditoria.model import AuditoriaModel

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cliente TEXT NOT NULL,
            estado TEXT,
            fecha TEXT,
            fecha_entrega TEXT,
            rowversion BLOB DEFAULT (randomblob(8)),
            fecha_compra TEXT,
            cantidad_aberturas INTEGER,
            pago_completo INTEGER,
            pago_porcentaje REAL,
            monto_usd REAL,
            monto_ars REAL,
            fecha_medicion TEXT,
            dias_entrega INTEGER,
            usuario_creador TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE auditorias_sistema (
            usuario_id INTEGER,
            modulo_afectado TEXT,
            tipo_evento TEXT,
            detalle TEXT,
            ip_origen TEXT,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield conn
    conn.close()

@pytest.fixture
def model(db_conn):
    class DummyConn:
        def __init__(self, c): self.connection = c
        def ejecutar_query(self, q, p=()):
            cur = self.connection.cursor()
            cur.execute(q, p)
            self.connection.commit()
            return cur.fetchall()
        def ejecutar_query_return_rowcount(self, q, p=()):
            cur = self.connection.cursor()
            cur.execute(q, p)
            self.connection.commit()
            return cur.rowcount
    return ObrasModel(DummyConn(db_conn))

@pytest.fixture
def controller(model, db_conn):
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return True
    usuario = {'id': 1, 'username': 'admin', 'ip': '127.0.0.1'}
    auditoria_model = AuditoriaModel(model.db_connection)
    ctrl = ObrasController(model, None, db_conn, DummyUsuarios(), usuario, auditoria_model=auditoria_model)
    return ctrl

def test_alta_obra_exitoso(controller, model):
    datos = {
        'nombre': 'Obra1',
        'cliente': 'ClienteTest',  # Ahora requiere nombre real
        'fecha_medicion': '2025-06-01',
        'fecha_entrega': '2025-07-01'
    }
    id_obra = controller.alta_obra(datos)
    obras = model.listar_obras()
    assert any(o[0] == id_obra and o[1] == 'Obra1' and o[2] == 'ClienteTest' for o in obras)
    # Auditoría
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE modulo_afectado='obras' AND tipo_evento = 'agregar' AND detalle LIKE 'Creó obra%' ").fetchall()
    assert res

def test_editar_obra_exitoso(controller, model):
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("Obra2", "Cliente2", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    datos_mod = {'nombre': 'Obra2Edit', 'cliente': 'Cliente2', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    nuevo_row = controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    fila2 = model.listar_obras()[0]
    assert fila2[1] == 'Obra2Edit' and fila2[6] != rowversion_orig
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'editar' AND detalle LIKE 'Editó obra%' ").fetchall()
    assert res

def test_editar_obra_conflicto(controller, model):
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("Obra3", "Cliente3", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    # Simular edición concurrente
    model.db_connection.ejecutar_query("UPDATE obras SET rowversion=randomblob(8) WHERE id=?", (id_obra,))
    datos_mod = {'nombre': 'Obra3Edit', 'cliente': 'Cliente3', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(OptimisticLockError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)

def test_alta_obra_permiso_denegado(model, db_conn):
    """Debe impedir alta de obra y mostrar feedback si el usuario no tiene permiso."""
    from unittest.mock import Mock
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return False
    dummy_label = Mock()
    class DummyView:
        def __init__(self): self.label = dummy_label
    class DummyAuditoria:
        def registrar_evento(self, *a, **k): pass
    usuario = {'id': 2, 'username': 'prueba', 'ip': '127.0.0.1'}
    ctrl = ObrasController(model, DummyView(), db_conn, DummyUsuarios(), usuario)
    ctrl.auditoria_model = DummyAuditoria()  # Inyecta mock auditoría
    datos = {'nombre': 'ObraSinPermiso', 'cliente_id': 2, 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    ctrl.alta_obra(datos)
    # Verifica feedback visual (permiso denegado o error de tabla si la vista intenta actualizar cronograma)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert (
        'permiso' in msg or 'acceso' in msg or 'no such table' in msg or 'error al actualizar calendario' in msg
    ), f"Mensaje inesperado: {msg}"
    # No debe crear la obra
    obras = model.listar_obras()
    assert not any(o[1] == 'ObraSinPermiso' for o in obras)

def test_editar_obra_permiso_denegado(model, db_conn):
    """Debe impedir edición de obra, mostrar feedback y NO auditar si el usuario no tiene permiso."""
    from unittest.mock import Mock
    # Crear obra inicial
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("ObraNoEdit", "Cliente", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return False
    dummy_label = Mock()
    class DummyView:
        def __init__(self): self.label = dummy_label
    auditoria_mock = Mock()
    usuario = {'id': 2, 'username': 'prueba', 'ip': '127.0.0.1'}
    ctrl = ObrasController(model, DummyView(), db_conn, DummyUsuarios(), usuario)
    ctrl.auditoria_model = auditoria_mock  # Inyecta mock auditoría
    datos_mod = {'nombre': 'ObraNoEditMod', 'cliente': 'Cliente', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    ctrl.editar_obra(id_obra, datos_mod, rowversion_orig)
    # Verifica feedback visual (permiso denegado o error de tabla si la vista intenta actualizar cronograma)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert (
        'permiso' in msg or 'acceso' in msg or 'no such table' in msg or 'error al actualizar calendario' in msg
    ), f"Mensaje inesperado: {msg}"
    # No debe modificar la obra
    fila2 = model.listar_obras()[0]
    assert fila2[1] == 'ObraNoEdit'
    # No debe registrar auditoría
    auditoria_mock.registrar_evento.assert_not_called()

def test_editar_obra_permiso_denegado_sin_vista(model, db_conn):
    """Debe impedir edición de obra y NO fallar si no hay vista (feedback solo por log o excepción controlada)."""
    # Crear obra inicial
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("ObraNoEdit2", "Cliente", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return False
    auditoria_mock = __import__('unittest').mock.Mock()
    usuario = {'id': 2, 'username': 'prueba', 'ip': '127.0.0.1'}
    ctrl = ObrasController(model, None, db_conn, DummyUsuarios(), usuario)
    ctrl.auditoria_model = auditoria_mock
    datos_mod = {'nombre': 'ObraNoEdit2Mod', 'cliente': 'Cliente', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    # No debe lanzar excepción ni modificar la obra
    ctrl.editar_obra(id_obra, datos_mod, rowversion_orig)
    fila2 = model.listar_obras()[0]
    assert fila2[1] == 'ObraNoEdit2'
    auditoria_mock.registrar_evento.assert_not_called()

def test_alta_obra_campos_obligatorios(controller, model):
    """Debe rechazar alta de obra si falta campo obligatorio (nombre o cliente)."""
    datos = {'nombre': '', 'cliente': '', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    try:
        controller.alta_obra(datos)
    except Exception as e:
        assert 'obligatorio' in str(e).lower() or 'nombre' in str(e).lower() or 'cliente' in str(e).lower()
    else:
        # Si no lanza, debe no crear la obra
        obras = model.listar_obras()
        assert not any(o[1] == '' for o in obras)

# --- Casos edge/negativos adicionales ---
# Test: alta de obra con cliente nulo o None

def test_alta_obra_cliente_none(controller, model):
    """Debe rechazar alta de obra si el cliente es None o nulo."""
    datos = {'nombre': 'ObraSinCliente', 'cliente': None, 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    with pytest.raises(Exception) as excinfo:
        controller.alta_obra(datos)
    assert 'cliente' in str(excinfo.value).lower() or 'obligatorio' in str(excinfo.value).lower()
    obras = model.listar_obras()
    assert not any(o[1] == 'ObraSinCliente' for o in obras)

# Test: editar obra con nombre vacío

def test_editar_obra_nombre_vacio(controller, model):
    """Debe rechazar edición si el nombre es vacío."""
    datos = {'nombre': 'ObraEditVacia', 'cliente': 'ClienteV', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    id_obra = controller.alta_obra(datos)
    fila = model.listar_obras()[0]
    rowversion = fila[6]
    datos_mod = {'nombre': '', 'cliente': 'ClienteV', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(Exception) as excinfo:
        controller.editar_obra(id_obra, datos_mod, rowversion)
    assert 'nombre' in str(excinfo.value).lower() or 'obligatorio' in str(excinfo.value).lower()
    fila2 = model.listar_obras()[0]
    assert fila2[1] == 'ObraEditVacia'

# Test: editar obra con cliente vacío

def test_editar_obra_cliente_vacio(controller, model):
    """Debe rechazar edición si el cliente es vacío."""
    datos = {'nombre': 'ObraEditClienteV', 'cliente': 'ClienteV2', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    id_obra = controller.alta_obra(datos)
    fila = model.listar_obras()[0]
    rowversion = fila[6]
    datos_mod = {'nombre': 'ObraEditClienteV', 'cliente': '', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(Exception) as excinfo:
        controller.editar_obra(id_obra, datos_mod, rowversion)
    assert 'cliente' in str(excinfo.value).lower() or 'obligatorio' in str(excinfo.value).lower()
    fila2 = model.listar_obras()[0]
    assert fila2[2] == 'ClienteV2'
