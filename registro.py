"""Configuración del archivo de logs (única persistencia permitida)."""
import logging
import os

RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "software_fj.log")


def obtener_logger() -> logging.Logger:
    logger = logging.getLogger("SoftwareFJ")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        h = logging.FileHandler(RUTA_LOG, mode="w", encoding="utf-8")
        h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
        logger.addHandler(h)
    return logger


log = obtener_logger()
