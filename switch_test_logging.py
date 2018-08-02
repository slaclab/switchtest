import os
import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

rotating_log_handler = RotatingFileHandler(os.path.join("logs", "switch-test.log"), maxBytes=100000, backupCount=10000)
rotating_log_handler.setFormatter(log_formatter)
logger.addHandler(rotating_log_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

