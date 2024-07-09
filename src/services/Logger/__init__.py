from .Logger import logger, console_handler, file_handler

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)