import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from unittest.mock import Mock, patch
from modules.configuracion.controller import ConfiguracionController
from modules.configuracion.model import ConfiguracionModel

# --- Utilidad para los tests de integración de importación CSV ---
def _patch_view_with_attrs(view, attrs):
    for attr in attrs:
        setattr(view, attr, Mock())
    return view

def _assert_mensaje_llamado(mock_mostrar_mensaje, mensaje_esperado, tipo_esperado):
    llamadas = mock_mostrar_mensaje.call_args_list
    for call in llamadas:
        args, kwargs = call
        if mensaje_esperado in args or kwargs.get('mensaje') == mensaje_esperado:
            if ('tipo' in kwargs and kwargs['tipo'] == tipo_esperado) or (len(args) > 1 and args[1] == tipo_esperado):
                return True
    raise AssertionError(f"No se encontró llamada a mostrar_mensaje con mensaje='{mensaje_esperado}' y tipo='{tipo_esperado}'. Llamadas: {llamadas}")

@pytest.fixture
def db_conn():
    mock_db = Mock()
    mock_db.transaction = Mock()
    mock_db.transaction.return_value.__enter__ = lambda s: s
    mock_db.transaction.return_value.__exit__ = lambda s, exc_type, exc_val, tb: None
    return mock_db

@pytest.fixture
def model(db_conn):
    return ConfiguracionModel(db_conn)

@pytest.fixture
def controller(model, db_conn):
    mock_view = Mock()
    mock_usuarios = Mock()
    controller = ConfiguracionController(model, mock_view, db_conn, mock_usuarios, usuario_actual={'nombre': 'admin', 'rol': 'admin'})
    # Mockear registrar_evento para evitar error de argumentos
    controller.auditoria_model.registrar_evento = Mock()
    controller.usuarios_model.tiene_permiso = Mock(return_value=True)
    return controller

def test_probar_conexion_correcta(controller):
    with patch('pyodbc.connect') as mock_connect:
        mock_connect.return_value = Mock(close=Mock())
        controller._get_text = lambda nombre: {
            'server_input': 'srv',
            'username_input': 'user',
            'password_input': 'pass',
            'default_db_input': 'db',
            'port_input': '1433',
            'timeout_input': '5',
        }[nombre]
        result = controller.probar_conexion_bd(retornar_resultado=True)
        assert result['exito'] is True
        assert 'Conexión exitosa' in result['mensaje']

def test_probar_conexion_incorrecta(controller):
    with patch('pyodbc.connect', side_effect=Exception('timeout')):
        controller._get_text = lambda nombre: {
            'server_input': 'srv',
            'username_input': 'user',
            'password_input': 'pass',
            'default_db_input': 'db',
            'port_input': '1433',
            'timeout_input': '5',
        }[nombre]
        result = controller.probar_conexion_bd(retornar_resultado=True)
        assert result['exito'] is False
        assert 'timeout' in result['mensaje']

def test_guardar_y_obtener_config(model):
    # Simula guardar y obtener configuración
    model.db.ejecutar_query = Mock()
    datos = {'clave1': 'valor1', 'clave2': 'valor2'}
    model.guardar_configuracion_conexion(datos)
    llamadas = model.db.ejecutar_query.call_args_list
    claves = set()
    for call in llamadas:
        args, _ = call
        if len(args) == 2 and isinstance(args[1], tuple):
            claves.add(args[1][1])
    assert 'clave1' in claves and 'clave2' in claves
    # Simula obtener configuración
    model.db.ejecutar_query.return_value = [('clave1', 'valor1', 'desc1'), ('clave2', 'valor2', 'desc2')]
    config = model.obtener_configuracion()
    assert len(config) == 2
    assert config[0][0] == 'clave1'
    assert config[1][1] == 'valor2'

def test_obtener_apariencia_usuario(model):
    # Simula obtener apariencia de usuario
    model.db.ejecutar_query = Mock(return_value=[('oscuro', 'en', False, '14')])
    apariencia = model.obtener_apariencia_usuario(1)
    assert apariencia[0][0] == 'oscuro'
    assert apariencia[0][1] == 'en'
    assert apariencia[0][2] is False
    assert apariencia[0][3] == '14'

def test_actualizar_apariencia_usuario(model):
    # Simula actualización de apariencia de usuario
    model.db.ejecutar_query = Mock()
    datos = ('oscuro', 'en', True, '14')
    model.actualizar_apariencia_usuario(1, datos)
    model.db.ejecutar_query.assert_called_with(
        '\n        UPDATE apariencia_usuario\n        SET modo_color = ?, idioma_preferido = ?, mostrar_notificaciones = ?, tamaño_fuente = ?\n        WHERE usuario_id = ?\n        ',
        (*datos, 1)
    )

def test_obtener_estado_notificaciones(model):
    # Simula obtener estado de notificaciones activas
    model.db.ejecutar_query = Mock(return_value=[('True',)])
    estado = model.obtener_estado_notificaciones()
    assert estado is True
    model.db.ejecutar_query = Mock(return_value=[('False',)])
    estado = model.obtener_estado_notificaciones()
    assert estado is False
    model.db.ejecutar_query = Mock(return_value=[])
    estado = model.obtener_estado_notificaciones()
    assert estado is False

def test_actualizar_estado_notificaciones(model):
    # Simula actualización de estado de notificaciones
    model.db.ejecutar_query = Mock()
    model.actualizar_estado_notificaciones(True)
    model.db.ejecutar_query.assert_called_with(
        "UPDATE configuracion_sistema SET valor = ? WHERE clave = 'notificaciones_activas'",
        ("True",)
    )
    model.actualizar_estado_notificaciones(False)
    model.db.ejecutar_query.assert_called_with(
        "UPDATE configuracion_sistema SET valor = ? WHERE clave = 'notificaciones_activas'",
        ("False",)
    )

def test_guardar_cambios_apariencia_usuario(controller):
    # Simula widgets y métodos para guardar_cambios
    controller._get_text = lambda nombre: {
        'nombre_app_input': 'StockApp',
        'modo_color_input': 'oscuro',
        'idioma_input': 'en',
        'tamaño_fuente_input': '14',
    }[nombre]
    controller._get_widget = lambda nombre: Mock(currentText=Mock(return_value='America/Argentina/Buenos_Aires'), isChecked=Mock(return_value=True))
    controller._get_checked = lambda nombre: True
    controller.model.actualizar_configuracion = Mock()
    controller.model.actualizar_apariencia_usuario = Mock()
    controller.mostrar_mensaje = Mock()
    controller.guardar_cambios()
    controller.model.actualizar_apariencia_usuario.assert_called_with(1, ('oscuro', 'en', True, '14'))
    controller.mostrar_mensaje.assert_called_with('Cambios guardados exitosamente.', tipo='exito')

def test_guardar_cambios_apariencia_usuario_widget_faltante(controller):
    # Simula error de widget faltante
    controller._get_text = Mock(side_effect=AttributeError('widget no encontrado'))
    controller._get_widget = Mock(side_effect=AttributeError('widget no encontrado'))
    controller.mostrar_mensaje = Mock()
    controller.guardar_cambios()
    controller.mostrar_mensaje.assert_called()
    args, kwargs = controller.mostrar_mensaje.call_args
    assert 'widget crítico' in args[0] or 'no encontrado' in args[0].lower()

def test_activar_modo_offline(controller):
    controller.model.activar_modo_offline = Mock()
    controller.mostrar_mensaje = Mock()
    controller.activar_modo_offline()
    controller.model.activar_modo_offline.assert_called_once()
    controller.mostrar_mensaje.assert_called_with('Modo offline activado.', tipo='info')

def test_desactivar_modo_offline(controller):
    controller.model.desactivar_modo_offline = Mock()
    controller.mostrar_mensaje = Mock()
    controller.desactivar_modo_offline()
    controller.model.desactivar_modo_offline.assert_called_once()
    controller.mostrar_mensaje.assert_called_with('Modo offline desactivado.', tipo='info')

def test_cambiar_estado_notificaciones(controller):
    controller.model.obtener_estado_notificaciones = Mock(side_effect=[False, True])
    controller.model.actualizar_estado_notificaciones = Mock()
    controller.mostrar_mensaje = Mock()
    controller.cambiar_estado_notificaciones()
    controller.model.actualizar_estado_notificaciones.assert_called_with(True)
    controller.mostrar_mensaje.assert_called_with('Notificaciones activadas.', tipo='info')
    controller.cambiar_estado_notificaciones()
    controller.model.actualizar_estado_notificaciones.assert_called_with(False)
    controller.mostrar_mensaje.assert_called_with('Notificaciones desactivadas.', tipo='info')

def test_cambiar_estado_notificaciones_error(controller):
    # Simula excepción en model.actualizar_estado_notificaciones
    controller.model.obtener_estado_notificaciones = Mock(return_value=True)
    controller.model.actualizar_estado_notificaciones = Mock(side_effect=Exception('DB error'))
    controller.mostrar_mensaje = Mock()
    controller.cambiar_estado_notificaciones()
    controller.mostrar_mensaje.assert_called()
    args, kwargs = controller.mostrar_mensaje.call_args
    assert 'error' in args[0].lower()

def test_activar_modo_offline_error(controller):
    controller.model.activar_modo_offline = Mock(side_effect=Exception('DB error'))
    controller.mostrar_mensaje = Mock()
    controller.activar_modo_offline()
    controller.mostrar_mensaje.assert_called()
    args, kwargs = controller.mostrar_mensaje.call_args
    assert 'error' in args[0].lower()

def test_desactivar_modo_offline_error(controller):
    controller.model.desactivar_modo_offline = Mock(side_effect=Exception('DB error'))
    controller.mostrar_mensaje = Mock()
    controller.desactivar_modo_offline()
    controller.mostrar_mensaje.assert_called()
    args, kwargs = controller.mostrar_mensaje.call_args
    assert 'error' in args[0].lower()

def test_guardar_cambios_notificaciones_invalido(controller):
    # Simula notificaciones no booleano
    controller._get_text = lambda nombre: 'StockApp' if nombre == 'nombre_app_input' else 'oscuro'
    controller._get_widget = lambda nombre: Mock(currentText=Mock(return_value='America/Argentina/Buenos_Aires'), isChecked=Mock(return_value=True))
    controller._get_checked = lambda nombre: 'no-bool'  # Valor inválido
    controller.model.actualizar_configuracion = Mock()
    controller.model.actualizar_apariencia_usuario = Mock()
    controller.mostrar_mensaje = Mock()
    controller.guardar_cambios()
    controller.model.actualizar_apariencia_usuario.assert_not_called()
    controller.mostrar_mensaje.assert_called()
    args, kwargs = controller.mostrar_mensaje.call_args
    assert 'booleano' in args[0] or 'notificaciones' in args[0].lower()

def test_guardar_cambios_nombre_vacio(controller):
    # Simula nombre vacío
    controller._get_text = lambda nombre: '' if nombre == 'nombre_app_input' else 'oscuro'
    controller._get_widget = lambda nombre: Mock(currentText=Mock(return_value='America/Argentina/Buenos_Aires'), isChecked=Mock(return_value=True))
    controller._get_checked = lambda nombre: True
    controller.model.actualizar_configuracion = Mock()
    controller.model.actualizar_apariencia_usuario = Mock()
    controller.mostrar_mensaje = Mock()
    controller.guardar_cambios()
    controller.model.actualizar_apariencia_usuario.assert_not_called()
    controller.mostrar_mensaje.assert_called()
    args, kwargs = controller.mostrar_mensaje.call_args
    assert 'vacío' in args[0] or 'nombre' in args[0].lower()

def test_permisos_denegados_en_controller():
    # Simula usuario sin permiso para acción 'editar'
    mock_model = Mock()
    mock_view = Mock()
    mock_usuarios = Mock()
    mock_usuarios.tiene_permiso = Mock(return_value=False)
    controller = ConfiguracionController(mock_model, mock_view, Mock(), mock_usuarios, usuario_actual={'nombre': 'user', 'rol': 'usuario'})
    controller.auditoria_model.registrar_evento = Mock()
    # Simula que la view tiene un label para feedback visual
    mock_view.label = Mock()
    # Intentar acción protegida
    result = controller.guardar_cambios()
    # No debe ejecutar la acción ni modificar nada
    assert result is None
    assert mock_view.label.setText.called
    args, _ = mock_view.label.setText.call_args
    assert 'permiso' in args[0].lower()

def test_integracion_guardar_y_cargar_configuracion(controller):
    # Simula guardar y luego cargar configuración y apariencia
    controller._get_text = lambda nombre: {
        'nombre_app_input': 'StockApp',
        'modo_color_input': 'oscuro',
        'idioma_input': 'en',
        'tamaño_fuente_input': '14',
    }[nombre]
    controller._get_widget = lambda nombre: Mock(currentText=Mock(return_value='America/Argentina/Buenos_Aires'), isChecked=Mock(return_value=True))
    controller._get_checked = lambda nombre: True
    controller.model.actualizar_configuracion = Mock()
    controller.model.actualizar_apariencia_usuario = Mock()
    controller.model.obtener_configuracion = Mock(return_value=[('nombre_app', 'StockApp', ''), ('zona_horaria', 'America/Argentina/Buenos_Aires', '')])
    controller.model.obtener_apariencia_usuario = Mock(return_value=[('oscuro', 'en', True, '14')])
    controller.mostrar_mensaje = Mock()
    # Guardar cambios
    controller.guardar_cambios()
    controller.model.actualizar_apariencia_usuario.assert_called_with(1, ('oscuro', 'en', True, '14'))
    # Cargar configuración
    controller._get_widget = lambda nombre: Mock(setText=Mock(), setCurrentText=Mock(), setChecked=Mock())
    controller.cargar_configuracion()
    controller.model.obtener_configuracion.assert_called()
    controller.model.obtener_apariencia_usuario.assert_called_with(1)

def test_integracion_toggle_modo_offline(controller):
    # Simula activar y desactivar modo offline
    controller.model.activar_modo_offline = Mock()
    controller.model.desactivar_modo_offline = Mock()
    controller.mostrar_mensaje = Mock()
    controller.activar_modo_offline()
    controller.model.activar_modo_offline.assert_called()
    controller.mostrar_mensaje.assert_called_with('Modo offline activado.', tipo='info')
    controller.desactivar_modo_offline()
    controller.model.desactivar_modo_offline.assert_called()
    controller.mostrar_mensaje.assert_called_with('Modo offline desactivado.', tipo='info')

def test_integracion_cambiar_estado_notificaciones(controller):
    # Simula alternar notificaciones
    controller.model.obtener_estado_notificaciones = Mock(side_effect=[False, True])
    controller.model.actualizar_estado_notificaciones = Mock()
    controller.mostrar_mensaje = Mock()
    controller.cambiar_estado_notificaciones()
    controller.model.actualizar_estado_notificaciones.assert_called_with(True)
    controller.mostrar_mensaje.assert_called_with('Notificaciones activadas.', tipo='info')
    controller.cambiar_estado_notificaciones()
    controller.model.actualizar_estado_notificaciones.assert_called_with(False)
    controller.mostrar_mensaje.assert_called_with('Notificaciones desactivadas.', tipo='info')

def test_integracion_importar_csv_exito(controller):
    controller.usuario_actual = {'nombre': 'admin', 'rol': 'admin', 'id': 1}
    controller.mostrar_mensaje = Mock()
    controller.view = _patch_view_with_attrs(Mock(), ['mostrar_exito', 'mostrar_advertencias', 'mostrar_errores', 'mostrar_preview', 'confirmar_importacion'])
    controller.view.confirmar_importacion.return_value = True
    with patch('modules.configuracion.controller.importar_inventario_desde_archivo') as mock_importar:
        mock_importar.return_value = {"exito": True, "mensajes": ["Importación exitosa"]}
        controller.importar_csv_inventario = controller.__class__.importar_csv_inventario.__get__(controller)
        controller.importar_csv_inventario()
        assert controller.mostrar_mensaje.call_args_list
        _assert_mensaje_llamado(controller.mostrar_mensaje, "Inventario importado correctamente.", tipo_esperado="exito")

def test_integracion_importar_csv_error(controller):
    controller.usuario_actual = {'nombre': 'admin', 'rol': 'admin', 'id': 1}
    controller.mostrar_mensaje = Mock()
    controller.view = _patch_view_with_attrs(Mock(), ['mostrar_exito', 'mostrar_advertencias', 'mostrar_errores', 'mostrar_preview', 'confirmar_importacion'])
    controller.view.confirmar_importacion.return_value = True
    with patch('modules.configuracion.controller.importar_inventario_desde_archivo') as mock_importar:
        mock_importar.return_value = {"exito": False, "errores": ["Error en fila 1"], "mensajes": ["No se pudo importar"]}
        controller.importar_csv_inventario = controller.__class__.importar_csv_inventario.__get__(controller)
        controller.importar_csv_inventario()
        assert controller.mostrar_mensaje.call_args_list
        _assert_mensaje_llamado(controller.mostrar_mensaje, "No se pudo importar el inventario. Revise los errores.", tipo_esperado="error")

def test_integracion_importar_csv_advertencias(controller):
    controller.usuario_actual = {'nombre': 'admin', 'rol': 'admin', 'id': 1}
    controller.mostrar_mensaje = Mock()
    controller.view = _patch_view_with_attrs(Mock(), ['mostrar_exito', 'mostrar_advertencias', 'mostrar_errores', 'mostrar_preview', 'confirmar_importacion'])
    controller.view.confirmar_importacion.return_value = True
    with patch('modules.configuracion.controller.importar_inventario_desde_archivo') as mock_importar:
        mock_importar.return_value = {"exito": True, "mensajes": ["Importado con advertencias"], "advertencias": ["Fila 2 incompleta"]}
        controller.importar_csv_inventario = controller.__class__.importar_csv_inventario.__get__(controller)
        controller.importar_csv_inventario()
        assert controller.mostrar_mensaje.call_args_list
        _assert_mensaje_llamado(controller.mostrar_mensaje, "Inventario importado correctamente.", tipo_esperado="exito")
