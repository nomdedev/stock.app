import logging
import os
import logging.handlers
from PyQt6.QtWidgets import QMessageBox
import json
import uuid

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', None),
            'module': record.module,
            'funcName': record.funcName,
            'lineno': record.lineno,
        }
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)

class Logger:
    def __init__(self, log_file="logs/app.log", correlation_id=None):
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger("MPSLogger")
        self.logger.setLevel(logging.DEBUG)

        # Formato del log (texto y JSON)
        text_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        json_formatter = JsonFormatter()

        # Handler para archivo rotativo (texto)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        file_handler.setFormatter(text_formatter)
        self.logger.addHandler(file_handler)

        # Handler para consola (texto)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(text_formatter)
        self.logger.addHandler(console_handler)

        # Handler para logs en JSON (archivo separado)
        json_log_file = os.path.join(log_dir, "app_json.log")
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)

        # Handler para auditoría (archivo separado, texto)
        audit_log_file = os.path.join(log_dir, "audit.log")
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file, maxBytes=2 * 1024 * 1024, backupCount=2
        )
        audit_handler.setFormatter(text_formatter)
        audit_handler.setLevel(logging.INFO)
        self.logger.addHandler(audit_handler)

        self.correlation_id = correlation_id or str(uuid.uuid4())

    def _extra(self):
        return {'correlation_id': self.correlation_id}

    def debug(self, message):
        self.logger.debug(message, extra=self._extra())

    def info(self, message):
        self.logger.info(message, extra=self._extra())

    def warning(self, message):
        self.logger.warning(message, extra=self._extra())

    def error(self, message):
        self.logger.error(message, extra=self._extra())

    def critical(self, message):
        self.logger.critical(message, extra=self._extra())

    def log_error_popup(self, message):
        self.error(message)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error Crítico")
        texto = message if message else "Ha ocurrido un error crítico. Por favor, revisa los logs o contacta al administrador."
        msg.setText(texto)
        msg.exec()

    def log_auditoria(self, usuario, accion, detalles):
        self.logger.info(f"Auditoría - Usuario: {usuario}, Acción: {accion}, Detalles: {detalles}", extra=self._extra())

# Función utilitaria para loguear errores desde cualquier módulo.
def log_error(msg, correlation_id=None):
    try:
        logger = Logger(correlation_id=correlation_id)
        logger.error(msg)
    except Exception:
        print(f"[ERROR] {msg}")
