import logging
import os

LOG_DIR = "logs"
LOG_FILE = "monitoramento.log"

os.makedirs(LOG_DIR, exist_ok=True)

class ContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "loja"):
            record.loja = "N/A"
        if not hasattr(record, "host"):
            record.host = "N/A"
        return True

# Formatter
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | loja=%(loja)s | host=%(host)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler
file_handler = logging.FileHandler(
    os.path.join(LOG_DIR, LOG_FILE),
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
file_handler.addFilter(ContextFilter())

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.addFilter(ContextFilter())

# Logger
logger = logging.getLogger("monitoramento")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False
