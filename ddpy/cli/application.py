import sys
import pathlib
import logging
import argparse
from ddpy.loaders import load_plugins, load_config

def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    stream_format = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(stream_format)
    logger.addHandler(stream_handler)

    parser = argparse.ArgumentParser(description='Dynamic DNS client written in python')
    parser.add_argument('--config')
    args = parser.parse_args()

    config = load_config(args.config)

    plugins = load_plugins(pathlib.Path(__file__).parent.parent / 'plugins')
    if 'plugin_dirs' in config:
        for path in config['plugin_dirs']:
            plugins.update(load_plugins(pathlib.Path(path)))

    try:
        ip_plugin = plugins[config['config']['ip_plugin']]
    except KeyError:
        logger.error(f'No plugin named {config["config"]["ip_plugin"]}')
        return

    try:
        info = ip_plugin.get_ip(config)
    except:
        logger.exception(f'Error in {config["config"]["ip_plugin"]}')
        return

    if ip_plugin.check_cache(config, info):
        logger.info('Cache is still valid')
        sys.exit(0)

    for config_zone in config['zones']:
        try:
            plugins[config_zone['plugin']].update_domains(info, config_zone)
        except KeyError:
            logger.warning(f'Zone "{config_zone["zone"]}" not updated')
            logger.error(f'No plugin named {config_zone["plugin"]}')

    try:
        ip_plugin.save_cache(config, info)
    except PermissionError:
        logger.error('Insufficient permissions to save cache')
