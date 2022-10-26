import logging


formatter = logging.Formatter("[%(asctime)s - %(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
logger.propagate = False
