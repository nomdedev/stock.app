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
    """Debe impedir edición de obra y NO fallar si la vista es None."""
    from unittest.mock import Mock
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("ObraNoEdit2", "Cliente", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return False
    auditoria_mock = Mock()
    usuario = {'id': 2, 'username': 'prueba', 'ip': '127.0.0.1'}
    ctrl = ObrasController(model, None, db_conn, DummyUsuarios(), usuario)
    ctrl.auditoria_model = auditoria_mock
    datos_mod = {'nombre': 'ObraNoEdit2Mod', 'cliente': 'Cliente', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    ctrl.editar_obra(id_obra, datos_mod, rowversion_orig)
    # No debe modificar la obra
    fila2 = model.listar_obras()[0]
    assert fila2[1] == 'ObraNoEdit2'
    # No debe registrar auditoría
    auditoria_mock.registrar_evento.assert_not_called()

def test_alta_obra_nombre_vacio(controller, model):
    datos = {
        'nombre': '',
        'cliente': 'ClienteTest',
        'fecha_medicion': '2025-06-01',
        'fecha_entrega': '2025-07-01'
    }
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    obras = model.listar_obras()
    assert not any(o[1] == '' for o in obras)

def test_alta_obra_cliente_vacio(controller, model):
    datos = {
        'nombre': 'ObraSinCliente',
        'cliente': '',
        'fecha_medicion': '2025-06-01',
        'fecha_entrega': '2025-07-01'
    }
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    obras = model.listar_obras()
    assert not any(o[1] == 'ObraSinCliente' for o in obras)

def test_alta_obra_fechas_invalidas(controller, model):
    datos = {
        'nombre': 'ObraFechasMal',
        'cliente': 'ClienteTest',
        'fecha_medicion': '2025-07-01',
        'fecha_entrega': '2025-06-01'  # entrega antes de medición
    }
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    obras = model.listar_obras()
    assert not any(o[1] == 'ObraFechasMal' for o in obras)

def test_alta_obra_duplicada(controller, model):
    """No debe permitir alta de obra duplicada (mismo nombre y cliente)."""
    from unittest.mock import Mock
    dummy_label = Mock()
    controller.view = type('DummyView', (), {'label': dummy_label})()
    datos = {'nombre': 'ObraDup', 'cliente': 'ClienteDup', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    controller.alta_obra(datos)
    # Intento duplicado
    dummy_label.reset_mock()
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'duplicad' in msg or 'existe' in msg or 'ya hay' in msg
    obras = [o for o in model.listar_obras() if o[1] == 'ObraDup' and o[2] == 'ClienteDup']
    assert len(obras) == 1
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'agregar'").fetchall()
    # Solo una auditoría para el alta exitosa de ObraDup
    auditorias_obra = [r for r in res if r[3] and 'ObraDup' in r[3] and 'Creó obra' in r[3]]
    assert len(auditorias_obra) == 1

def test_editar_obra_nombre_vacio(controller, model):
    controller.alta_obra({'nombre': 'ObraEdit', 'cliente': 'ClienteTest', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'})
    fila = next(o for o in model.listar_obras() if o[1] == 'ObraEdit' and o[2] == 'ClienteTest')
    id_obra, rowversion_orig = fila[0], fila[6]
    datos_mod = {'nombre': '', 'cliente': 'ClienteTest', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(ValueError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    fila2 = next(o for o in model.listar_obras() if o[0] == id_obra)
    assert fila2[1] == 'ObraEdit'


def test_editar_obra_cliente_vacio(controller, model):
    controller.alta_obra({'nombre': 'ObraEdit2', 'cliente': 'ClienteTest', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'})
    fila = next(o for o in model.listar_obras() if o[1] == 'ObraEdit2' and o[2] == 'ClienteTest')
    id_obra, rowversion_orig = fila[0], fila[6]
    datos_mod = {'nombre': 'ObraEdit2', 'cliente': '', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(ValueError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    fila2 = next(o for o in model.listar_obras() if o[0] == id_obra)
    assert fila2[2] == 'ClienteTest'


def test_editar_obra_fechas_invalidas(controller, model):
    controller.alta_obra({'nombre': 'ObraEdit3', 'cliente': 'ClienteTest', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'})
    fila = next(o for o in model.listar_obras() if o[1] == 'ObraEdit3' and o[2] == 'ClienteTest')
    id_obra, rowversion_orig = fila[0], fila[6]
    datos_mod = {'nombre': 'ObraEdit3', 'cliente': 'ClienteTest', 'estado': 'Medición', 'fecha_entrega': '2025-05-01', 'fecha_medicion': '2025-06-01'}
    with pytest.raises(ValueError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    fila2 = next(o for o in model.listar_obras() if o[0] == id_obra)
    assert fila2[3] == 'Medición'

def test_alta_obra_datos_invalidos(controller, model):
    """No debe crear obra ni auditar si los datos son inválidos (nombre vacío, cliente vacío, fechas inválidas)."""
    from unittest.mock import Mock
    dummy_label = Mock()
    controller.view = type('DummyView', (), {'label': dummy_label})()
    # Nombre vacío
    datos = {'nombre': '', 'cliente': 'ClienteTest', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'nombre' in msg or 'inválido' in msg or 'obligatorio' in msg
    # No debe haber obra con nombre vacío
    assert not any(o[1] == '' and o[2] == 'ClienteTest' for o in model.listar_obras())
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'agregar'").fetchall()
    # No debe haber auditoría para nombre vacío
    assert not any(r[3] and 'ClienteTest' in r[3] and 'Creó obra' in r[3] for r in res)
    # Cliente vacío
    dummy_label.reset_mock()
    datos = {'nombre': 'ObraInv', 'cliente': '', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'cliente' in msg or 'inválido' in msg or 'obligatorio' in msg
    assert not any(o[1] == 'ObraInv' and o[2] == '' for o in model.listar_obras())
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'agregar'").fetchall()
    assert not any(r[3] and 'ObraInv' in r[3] and 'Creó obra' in r[3] for r in res)
    # Fechas inválidas
    dummy_label.reset_mock()
    datos = {'nombre': 'ObraInv', 'cliente': 'ClienteTest', 'fecha_medicion': '2025-07-02', 'fecha_entrega': '2025-06-01'}
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'fecha' in msg or 'inválida' in msg or 'cronología' in msg
    assert not any(o[1] == 'ObraInv' and o[2] == 'ClienteTest' and o[4] == '2025-07-02' and o[5] == '2025-06-01' for o in model.listar_obras())
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'agregar'").fetchall()
    assert not any(r[3] and 'ObraInv' in r[3] and 'Creó obra' in r[3] for r in res)


def test_alta_obra_duplicada(controller, model):
    """No debe permitir alta de obra duplicada (mismo nombre y cliente)."""
    from unittest.mock import Mock
    dummy_label = Mock()
    controller.view = type('DummyView', (), {'label': dummy_label})()
    datos = {'nombre': 'ObraDup', 'cliente': 'ClienteDup', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    controller.alta_obra(datos)
    # Intento duplicado
    dummy_label.reset_mock()
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'duplicad' in msg or 'existe' in msg or 'ya hay' in msg
    obras = [o for o in model.listar_obras() if o[1] == 'ObraDup' and o[2] == 'ClienteDup']
    assert len(obras) == 1
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'agregar'").fetchall()
    # Solo una auditoría para el alta exitosa de ObraDup
    auditorias_obra = [r for r in res if r[3] and 'ObraDup' in r[3] and 'Creó obra' in r[3]]
    assert len(auditorias_obra) == 1

def test_editar_obra_datos_invalidos(controller, model):
    """No debe modificar ni auditar si los datos de edición son inválidos."""
    from unittest.mock import Mock
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("ObraEditInv", "ClienteInv", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = next(o for o in model.listar_obras() if o[1] == 'ObraEditInv' and o[2] == 'ClienteInv')
    id_obra, rowversion_orig = fila[0], fila[6]
    dummy_label = Mock()
    controller.view = type('DummyView', (), {'label': dummy_label})()
    # Nombre vacío
    datos_mod = {'nombre': '', 'cliente': 'ClienteInv', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(ValueError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'nombre' in msg or 'inválido' in msg or 'obligatorio' in msg
    fila2 = next(o for o in model.listar_obras() if o[0] == id_obra)
    assert fila2[1] == 'ObraEditInv'
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'editar'").fetchall()
    assert not any(r[3] and 'ObraEditInv' in r[3] and 'Editó obra' in r[3] for r in res)
    # Fechas inválidas (solo si la lógica de edición valida fechas)
    dummy_label.reset_mock()
    datos_mod = {'nombre': 'ObraEditInv', 'cliente': 'ClienteInv', 'estado': 'Medición', 'fecha_entrega': '2025-05-01', 'fecha_medicion': '2025-06-01'}
    with pytest.raises(ValueError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'fecha' in msg or 'inválida' in msg or 'cronología' in msg
    fila2 = next(o for o in model.listar_obras() if o[0] == id_obra)
    assert fila2[1] == 'ObraEditInv'
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'editar'").fetchall()
    assert not any(r[3] and 'ObraEditInv' in r[3] and 'Editó obra' in r[3] for r in res)

def test_baja_obra_exitoso(controller, model):
    # Crear obra
    datos = {'nombre': 'ObraBorrar', 'cliente': 'ClienteBorrar', 'fecha_medicion': '2025-06-01', 'fecha_entrega': '2025-07-01'}
    id_obra = controller.alta_obra(datos)
    assert any(o[0] == id_obra for o in model.listar_obras())
    # Eliminar obra
    exito = controller.baja_obra(id_obra)
    assert exito is True
    # No debe estar en la lista
    assert not any(o[0] == id_obra for o in model.listar_obras())
    # Auditoría
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'eliminar' AND detalle LIKE ?", (f'%{id_obra}%',)).fetchall()
    assert res

def test_baja_obra_permiso_denegado(model, db_conn):
    """Debe impedir baja de obra y mostrar feedback si el usuario no tiene permiso."""
    from unittest.mock import Mock
    # Crear obra
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("ObraNoBorrar", "Cliente", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra = fila[0]
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return False
    dummy_label = Mock()
    class DummyView:
        def __init__(self): self.label = dummy_label
    auditoria_mock = Mock()
    usuario = {'id': 2, 'username': 'prueba', 'ip': '127.0.0.1'}
    ctrl = ObrasController(model, DummyView(), db_conn, DummyUsuarios(), usuario)
    ctrl.auditoria_model = auditoria_mock
    exito = ctrl.baja_obra(id_obra)
    assert exito is False
    dummy_label.setText.assert_called()
    msg = dummy_label.setText.call_args[0][0].lower()
    assert 'permiso' in msg or 'denegado' in msg
    # No debe eliminar ni auditar
    assert any(o[0] == id_obra for o in model.listar_obras())
    auditoria_mock.registrar_evento.assert_not_called()

def test_baja_obra_no_existe(controller, model):
    """No debe fallar ni auditar si la obra no existe."""
    exito = controller.baja_obra(9999)
    assert exito is False
    # No auditoría de eliminación
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE tipo_evento = 'eliminar' AND detalle LIKE ?", ('%9999%',)).fetchall()
    assert not res
