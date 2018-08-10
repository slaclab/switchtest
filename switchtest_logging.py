
import logging

log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Set the starting logging level high so that this test won't be polluted with all the pyrogue debug and info log
# messages
logger.setLevel(logging.WARNING)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(console_handler)


