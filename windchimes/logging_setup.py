import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: [%(levelname)s] %(name)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

root_logger = logging.getLogger()
