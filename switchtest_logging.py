import os
import socket

import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Set the starting logging level high so that this test won't be polluted with all the pyrogue debug and info log
# messages
logger.setLevel(logging.WARNING)

# Make sure a logs directory is available
hostname = socket.gethostname()
log_dirname = "logs_" + hostname

try:
    os.makedirs(log_dirname)
except os.error:
    pass

rotating_log_handler = RotatingFileHandler(os.path.join(log_dirname, "switch-test.log"), maxBytes=2000000,
                                           backupCount=60)
rotating_log_handler.setFormatter(log_formatter)
logger.addHandler(rotating_log_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)

