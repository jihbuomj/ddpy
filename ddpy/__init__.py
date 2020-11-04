__version__ = '0.1.0'
import toml
import pathlib
import re
import requests
import logging
from .plugin_loader import load_plugins
from dotenv import load_dotenv

def main():
    load_dotenv()

    config = toml.load('./ddpy.toml')

    logger = logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    stream_format = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(stream_format)

    logger.addHandler(stream_handler)

    plugins = load_plugins(pathlib.Path(__file__).parent / 'plugins')
    if 'plugin_dirs' in config:
        for path in config['plugin_dirs']:
            plugins.update(load_plugins(pathlib.Path(path)))

    ip_plugin = plugins[config['config']['ip_plugin']]

    info = ip_plugin.get_ip(config)

    if ip_plugin.check_cache(config, info):
        logger.info('Cache is still valid')
        return

    for config_zone in config['zones']:
        try:
            plugins[config_zone['plugin']].update_domains(info, config_zone)
        except KeyError:
            logger.warning(f'Zone "{config_zone["zone"]}" not updated')
            logger.error(f'No plugin named {config_zone["plugin"]}')

    ip_plugin.save_cache(config, info)
