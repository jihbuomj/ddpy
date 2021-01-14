import sys
import pathlib
import logging
import argparse
from ddpy.loaders import load_plugins, load_config

log_format = logging.Formatter(
    '%(asctime)s - %(levelname)s:%(name)s - %(message)s')


def generate_logger(log_file):
    logger_temp = logging.getLogger('ddpy')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)

    if(log_file):
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(log_format)
        logger_temp.addHandler(file_handler)

    logger_temp.addHandler(stream_handler)

    return logger_temp


def main():
    parser = argparse.ArgumentParser(
        prog='ddpy', description='Dynamic DNS client written in python')
    parser.add_argument('--config', metavar='PATH', help='path to config file')
    parser.add_argument(
        '--loglevel', choices=['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'])
    parser.add_argument('--log', metavar='PATH', help='path to log file')
    args = parser.parse_args()

    logger = generate_logger(args.log)
    if args.loglevel:
        logger.setLevel(args.loglevel)

    config = load_config(args.config)

    if config['config']['log_file'] and not args.log:
        file_handler = logging.FileHandler(config['config']['log_file'])
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

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
