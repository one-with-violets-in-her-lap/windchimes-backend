from windchimes_backend.logging_setup import root_logger
from windchimes_backend.config import app_config


root_logger.info('Launching GraphQL api')

print(app_config)
