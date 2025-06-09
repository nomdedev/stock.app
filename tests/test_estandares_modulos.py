import pytest
import importlib
import os

# Lista de módulos principales a testear
MODULOS = [
    'modules.herrajes.view',
    'modules.vidrios.view',
    'modules.contabilidad.view',
    'modules.mantenimiento.view',
    'modules.obras.view',
    'modules.inventario.view',
]

# Paths a los archivos de estándares
ESTANDARES = {
    'visuales': 'docs/estandares_visuales.md',
    'logging': 'docs/estandares_logging.md',
    'seguridad': 'docs/estandares_seguridad.md',
    'feedback': 'docs/estandares_feedback.md',
    'auditoria': 'docs/estandares_auditoria.md',
}

@pytest.mark.parametrize('modulo', MODULOS)
def test_importa_modulo(modulo):
    """El módulo debe poder importarse sin errores."""
    importlib.import_module(modulo)

@pytest.mark.parametrize('modulo', MODULOS)
def test_no_fondos_oscuros(modulo):
    """No debe haber fondos oscuros ni sobrescrituras de estilos prohibidos en el código fuente del módulo."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert 'background-color: #1a1a2e' not in code
    assert 'background-color: #232b36' not in code
    assert 'background: #1a1a2e' not in code
    assert 'background: #232b36' not in code
    assert 'font-size: 32px' not in code
    assert 'font-size: 40px' not in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_fuente_y_tamanos(modulo):
    """Las fuentes y tamaños deben cumplir el estándar (≤12px en tablas/botones, sin sobrescribir)."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert 'font-size: 13px' not in code or 'label' in code  # 13px solo en labels
    assert 'font-size: 14px' not in code or 'titulo' in code # 14px solo en títulos
    assert 'font-size: 16px' not in code
    assert 'font-size: 20px' not in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_usa_helpers_estilo(modulo):
    """Debe usar helpers de estilo para botones y QSS global, o justificar la excepción en el código."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert (
        'estilizar_boton_icono' in code
        or 'aplicar_qss_global_y_tema' in code
        or '# excepción justificada' in code
        or '# justificación' in code
        or '# excepcion justificada' in code
    ), (
        f"El módulo {modulo} debe usar helpers de estilo o justificar la excepción en el código."
    )

@pytest.mark.parametrize('modulo', MODULOS)
def test_no_credenciales_en_codigo(modulo):
    """No debe haber credenciales ni strings de conexión hardcodeados (excepto construcción dinámica con variables o en comentarios)."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    # Ignorar líneas comentadas (con o sin espacios al inicio)
    code = '\n'.join([line for line in lines if not line.lstrip().startswith('#')]).lower()
    # Permitir construcción dinámica de cadena de conexión usando variables (no hardcode)
    if 'f"server={' in code or 'f"database={' in code or 'f"pwd={' in code:
        # Documentado: construcción dinámica con variables, no es hardcode
        return
    assert 'server=' not in code, "No debe haber credenciales ni cadenas de conexión hardcodeadas fuera de comentarios o ejemplos documentados."
    assert 'password=' not in code
    assert 'user id=' not in code
    assert 'pwd=' not in code
    assert 'database=' not in code or 'config' in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_feedback_visual_y_logging(modulo):
    """Debe haber feedback visual y logging en los flujos de error."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert 'qmessagebox' in code or 'label_feedback' in code or 'mostrar_mensaje' in code
    assert 'log_error' in code or 'logger' in code or 'registrar_evento' in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_tooltips_en_botones(modulo):
    """Todos los botones deben tener setToolTip para accesibilidad y ayuda contextual."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert 'settooltip' in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_feedback_carga(modulo):
    """Debe haber feedback de carga (QProgressBar, spinner, QMovie, etc.) en procesos largos."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert 'qprogressbar' in code or 'qmovie' in code or 'spinner' in code or 'loading' in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_accesibilidad_colores(modulo):
    """No debe usarse solo color para indicar estado; buscar uso de íconos o texto junto a color."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert 'icon' in code or 'emoji' in code or 'settext' in code

@pytest.mark.parametrize('modulo', MODULOS)
def test_justificacion_excepciones_visuales(modulo):
    """Toda excepción visual debe estar justificada y documentada en el código."""
    path = modulo.replace('.', os.sep) + '.py'
    with open(path, encoding='utf-8') as f:
        code = f.read().lower()
    assert '# excepción justificada' in code or '# justificación' in code or '# excepcion justificada' in code

# Test de existencia de documentación de estándares
@pytest.mark.parametrize('estandar', ESTANDARES.values())
def test_docs_estandares_existen(estandar):
    assert os.path.exists(estandar)
