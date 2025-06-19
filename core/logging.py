import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

handler = RotatingFileHandler(LOG_FILE, maxBytes=10**7, backupCount=5, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger('stock_app')
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(handler)

# Uso recomendado en módulos:
# from core.logging import logger
# logger.info("Mensaje informativo")
# logger.error("Mensaje de error")
