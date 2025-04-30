import logging
import os
import logging.handlers
from PyQt6.QtWidgets import QMessageBox

class Logger:
    def __init__(self, log_file="logs/app.log"):
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger("MPSLogger")
        self.logger.setLevel(logging.DEBUG)

        # Formato del log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Handler para archivo rotativo
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler para auditoría (archivo separado)
        audit_log_file = os.path.join(log_dir, "audit.log")
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file, maxBytes=2 * 1024 * 1024, backupCount=2
        )
        audit_handler.setFormatter(formatter)
        audit_handler.setLevel(logging.INFO)
        self.logger.addHandler(audit_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def log_error_popup(self, message):
        self.error(message)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error Crítico")
        msg.setText(message)
        msg.exec()

    def log_auditoria(self, usuario, accion, detalles):
        self.logger.info(f"Auditoría - Usuario: {usuario}, Acción: {accion}, Detalles: {detalles}")
