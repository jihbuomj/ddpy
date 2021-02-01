from importlib.machinery import FileFinder, SOURCE_SUFFIXES, SourceFileLoader
from importlib.util import module_from_spec
import sys
import pathlib
import toml
import logging

logger = logging.getLogger(__name__)


def load_config(path):
    config_file_list = ['./ddpy.toml', '/etc/ddpy/ddpy.toml']

    if path:
        config_file_list.insert(0, path)

    for config_file in config_file_list:
        if pathlib.Path(config_file).exists():
            try:
                return toml.load(config_file)
            except:
                logger.error(f'{config_file} is not valid')
        else:
            logger.info(f'{config_file} not found, trying next')

    logger.error('No config found')
    sys.exit(1)
