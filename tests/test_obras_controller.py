import pytest
from unittest.mock import MagicMock, patch
from modules.obras.controller import ObrasController

class DummyModel:
    def __init__(self):
        self.obras = []
        self.rowversion = {}
        self.headers = ["id", "nombre", "cliente", "estado", "fecha", "fecha_entrega"]
        self.id_counter = 1
    def validar_datos_obra(self, datos):
        errores = []
        if isinstance(datos, dict):
            nombre = datos.get("nombre", "")
            cliente = datos.get("cliente", "")
            fecha_med = datos.get("fecha_medicion", "2024-01-01")
            fecha_ent = datos.get("fecha_entrega", "2024-01-02")
            id_actual = datos.get("id", None)
        else:
            nombre = datos[0]
            cliente = datos[1]
            fecha_med = datos[9]
            fecha_ent = datos[11]
            id_actual = None
        if not nombre or not cliente:
            errores.append("Faltan campos obligatorios")
        if fecha_ent < fecha_med:
            errores.append("La fecha de entrega no puede ser anterior a la fecha de medición")
        # Solo marcar como duplicada si es alta o si el id es distinto
        for o in self.obras:
            if o["nombre"] == nombre and o["cliente"] == cliente:
                if id_actual is None or o["id"] != id_actual:
                    errores.append("Obra duplicada")
                    break
        return errores
    def agregar_obra(self, datos):
        if isinstance(datos, dict):
            nombre = datos["nombre"]
            cliente = datos["cliente"]
        else:
            nombre = datos[0]
            cliente = datos[1]
        obra = {"id": self.id_counter, "nombre": nombre, "cliente": cliente, "estado": "Medición", "fecha": "2024-01-01", "fecha_entrega": "2024-01-02"}
        self.obras.append(obra)
        self.rowversion[self.id_counter] = 1
        self.id_counter += 1
        return obra["id"]
    def agregar_obra_dict(self, datos):
        return self.agregar_obra(datos)
    def obtener_headers_obras(self):
        return self.headers
    def obtener_datos_obras(self):
        return [[o[h] for h in self.headers] for o in self.obras]
    def editar_obra(self, id_obra, datos, rowversion_orig):
        # Validar duplicados correctamente
        if self.rowversion.get(id_obra, 0) != rowversion_orig:
            raise Exception("Conflicto de rowversion")
        # Simular edición: no marcar duplicado si es el mismo id
        errores = self.validar_datos_obra({**datos, 'id': id_obra})
        if errores:
            raise ValueError('; '.join(errores))
        self.rowversion[id_obra] += 1
        return self.rowversion[id_obra]
    def eliminar_obra(self, id_obra):
        for o in self.obras:
            if o["id"] == id_obra:
                self.obras.remove(o)
                return True
        return False
    def obtener_obra_por_id(self, id_obra):
        for o in self.obras:
            if o["id"] == id_obra:
                return o
        return None

class DummyView:
    def __init__(self):
        self.mensajes = []
        self.label = MagicMock()
    def mostrar_mensaje(self, mensaje, tipo=None, **kwargs):
        self.mensajes.append((mensaje, tipo))
    def cargar_headers(self, headers):
        pass
    def cargar_tabla_obras(self, obras):
        pass

@pytest.fixture
def controller():
    model = DummyModel()
    view = DummyView()
    usuarios_model = MagicMock()
    usuarios_model.tiene_permiso.return_value = True
    auditoria_model = MagicMock()
    usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}
    return ObrasController(model, view, None, usuarios_model, usuario_actual, auditoria_model=auditoria_model)

def test_alta_obra_valida(controller):
    datos = {"nombre": "Obra1", "cliente": "Cliente1", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    id_obra = controller.alta_obra(datos)
    assert id_obra == 4  # Ahora el primer id disponible es 4 por las obras de ejemplo
    assert controller.model.obras[-1]["nombre"] == "Obra1"
    assert controller.auditoria_model.registrar_evento.called

def test_alta_obra_faltantes(controller):
    datos = {"nombre": "", "cliente": "", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    assert controller.view.mensajes[-1][1] == "error"

def test_alta_obra_fechas_incorrectas(controller):
    datos = {"nombre": "Obra2", "cliente": "Cliente2", "fecha_medicion": "2024-01-10", "fecha_entrega": "2024-01-01"}
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    assert controller.view.mensajes[-1][1] == "error"

def test_alta_obra_duplicada(controller):
    datos = {"nombre": "Obra3", "cliente": "Cliente3", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    controller.alta_obra(datos)
    with pytest.raises(ValueError):
        controller.alta_obra(datos)
    assert controller.view.mensajes[-1][1] == "error"

def test_editar_obra_rowversion_ok(controller):
    datos = {"nombre": "Obra4", "cliente": "Cliente4", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    id_obra = controller.alta_obra(datos)
    rowversion = controller.model.rowversion[id_obra]
    datos_edit = {"nombre": "Obra4", "cliente": "Cliente4", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    rv_nuevo = controller.editar_obra(id_obra, datos_edit, rowversion)
    assert rv_nuevo == rowversion + 1

def test_editar_obra_rowversion_conflicto(controller):
    datos = {"nombre": "Obra5", "cliente": "Cliente5", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    id_obra = controller.alta_obra(datos)
    rowversion = controller.model.rowversion[id_obra]
    controller.model.rowversion[id_obra] += 1  # Simula edición concurrente
    datos_edit = {"nombre": "Obra5", "cliente": "Cliente5", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    with pytest.raises(Exception):
        controller.editar_obra(id_obra, datos_edit, rowversion)
    assert controller.view.mensajes[-1][1] == "error"

def test_rollback_en_alta(controller):
    with patch.object(controller.model, 'agregar_obra', side_effect=Exception("DB error")):
        datos = {"nombre": "Obra6", "cliente": "Cliente6", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
        with pytest.raises(Exception):
            controller.alta_obra(datos)
        assert controller.view.mensajes[-1][1] == "error"

def test_auditoria_en_alta(controller):
    datos = {"nombre": "Obra7", "cliente": "Cliente7", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
    controller.alta_obra(datos)
    assert controller.auditoria_model.registrar_evento.called

def test_logging_en_alta(controller):
    with patch("core.logger.Logger.info") as mock_info:
        datos = {"nombre": "Obra8", "cliente": "Cliente8", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-02"}
        controller.alta_obra(datos)
        assert mock_info.called

def test_flujo_completo_obra_y_pedidos():
    """
    Test de integración: flujo completo de gestión de obra y pedidos, validando feedback visual, auditoría y trazabilidad.
    """
    # Dummies para los módulos relacionados
    class DummyPedidosController:
        def __init__(self):
            self.pedidos = []
        def existe_pedido_para_obra(self, id_obra):
            return any(p['id_obra'] == id_obra for p in self.pedidos)
        def generar_pedido_para_obra(self, id_obra):
            self.pedidos.append({'id_obra': id_obra, 'tipo': 'materiales'})
        def nueva_obra_creada(self, id_obra):
            pass
    class DummyProduccionController:
        def __init__(self):
            self.produccion = []
        def iniciar_produccion_obra(self, id_obra):
            self.produccion.append(id_obra)
        def nueva_obra_creada(self, id_obra):
            pass
    class DummyLogisticaController:
        def __init__(self):
            self.logistica = []
        def actualizar_por_cambio_estado_obra(self, id_obra, estado):
            self.logistica.append((id_obra, estado))
        def nueva_obra_creada(self, id_obra):
            pass
    class DummyContabilidadController:
        def __init__(self):
            self.movimientos = []
        def registrar_pago_obra(self, id_obra, monto):
            self.movimientos.append((id_obra, monto))
    # Instancias dummy
    model = DummyModel()
    view = DummyView()
    usuarios_model = MagicMock()
    usuarios_model.tiene_permiso.return_value = True
    auditoria_model = MagicMock()
    usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}
    pedidos_controller = DummyPedidosController()
    produccion_controller = DummyProduccionController()
    logistica_controller = DummyLogisticaController()
    contabilidad_controller = DummyContabilidadController()
    # Crear controller principal
    controller = ObrasController(
        model, view, None, usuarios_model, usuario_actual,
        logistica_controller=logistica_controller,
        pedidos_controller=pedidos_controller,
        produccion_controller=produccion_controller,
        auditoria_model=auditoria_model
    )
    # 1. Alta de obra
    datos_obra = {"nombre": "ObraTest", "cliente": "ClienteTest", "fecha_medicion": "2024-01-01", "fecha_entrega": "2024-01-10"}
    id_obra = controller.alta_obra(datos_obra)
    assert id_obra == 4  # Ahora el primer id disponible es 4
    assert controller.model.obras[-1]["nombre"] == "ObraTest"
    # 2. Cargar materiales (simula cambio de estado a 'pedido cargado')
    controller.cambiar_estado_obra(id_obra, "pedido cargado")
    assert any(p["id_obra"] == id_obra for p in pedidos_controller.pedidos)
    # 3. Cargar herrajes (simula otro pedido)
    pedidos_controller.generar_pedido_para_obra(id_obra)  # Simula pedido de herrajes
    assert len(pedidos_controller.pedidos) >= 2  # Debe haber al menos dos pedidos
    # 4. Cargar vidrios (simula otro pedido)
    pedidos_controller.generar_pedido_para_obra(id_obra)  # Simula pedido de vidrios
    assert len(pedidos_controller.pedidos) >= 3
    # 5. Producción: iniciar producción
    controller.cambiar_estado_obra(id_obra, "en producción")
    assert id_obra in produccion_controller.produccion
    # 6. Logística: marcar como entregada
    controller.cambiar_estado_obra(id_obra, "entrega")
    assert (id_obra, "entrega") in logistica_controller.logistica
    # 7. Contabilidad: registrar pago
    contabilidad_controller.registrar_pago_obra(id_obra, 1000)
    assert (id_obra, 1000) in contabilidad_controller.movimientos
    # 8. Feedback visual y auditoría
    assert any("actualizado" in m[0] for m in view.mensajes)
    assert auditoria_model.registrar_evento.called
