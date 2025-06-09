"""
Helper global para registrar eventos críticos en auditoría.
Cumple: docs/estandares_auditoria.md
Permite inyectar conexión para tests y nunca interrumpe el flujo principal.
"""
from core.logger import Logger
from modules.auditoria.model import AuditoriaModel
from core.database import AuditoriaDatabaseConnection  # Importar la clase correcta

def _registrar_evento_auditoria(usuario, modulo, accion, db_conn=None):
    """
    Inserta un registro en auditorias_sistema con timestamp.
    Se invoca en cada acción crítica de modelos.
    Logging INFO. Ver docs/estandares_auditoria.md
    - usuario: str o dict (puede incluir 'id' y 'ip')
    - modulo: str (nombre del módulo)
    - accion: str (detalle de la acción)
    - db_conn: conexión opcional (para tests)
    Devuelve True si registra, False si hay error (nunca lanza excepción).
    """
    logger = Logger()
    try:
        db = db_conn or AuditoriaDatabaseConnection()
        auditoria = AuditoriaModel(db)
        usuario_id = usuario['id'] if isinstance(usuario, dict) and 'id' in usuario else usuario
        ip = usuario.get('ip', '') if isinstance(usuario, dict) else ''
        auditoria.registrar_evento(usuario_id, modulo, 'accion', accion, ip)
        logger.info(f"[AUDITORÍA] {modulo}: {accion}")
        return True
    except Exception as e:
        logger.warning(f"[AUDITORÍA] Error registrando evento: {e}")
        return False
