import sys
import pathlib
import toml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_format = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(stream_format)
logger.addHandler(stream_handler)

def load_config():
    config_file_list = ['./ddpy.toml', '/etc/ddpy/ddpy.toml']

    for config_file in config_file_list:
        if pathlib.Path(config_file).exists():
            return toml.load(config_file)

    logger.error('No config found')
    sys.exit(1)
