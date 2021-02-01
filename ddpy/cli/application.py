import sys
import pathlib
import logging
import argparse
import importlib
from ddpy.plugin_base import GetPluginBase, GivePluginBase
from ddpy.loaders import load_plugins, load_config


def main():
    parser = argparse.ArgumentParser(
        prog='ddpy', description='dynamic dns client written in python')
    parser.add_argument('--config', metavar='path', help='path to config file')
    parser.add_argument(
        '--loglevel', choices=['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], type=str.upper)
    parser.add_argument('--log', metavar='path', help='path to log file')
    args = parser.parse_args()

    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s:%(name)s - %(message)s')

    logger = logging.getLogger('ddpy')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)

    if(args.log):
        file_handler = logging.FileHandler(args.log)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    logger.addHandler(stream_handler)

    if args.loglevel:
        logger.setLevel(args.loglevel)

    config = load_config(args.config)

    if config['config']['log_file'] and not args.log:
        file_handler = logging.FileHandler(config['config']['log_file'])
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    try:
        get_plugin_module = importlib.import_module(
            'ddpy.plugins.' + config['config']['ip_plugin'])
    except KeyError:
        logger.error('No get-plugin specified')
        sys.exit(1)
    except ModuleNotFoundError:
        logger.error(
            f'Cannot find get-plugin "{config["config"]["ip_plugin"]}"')
        sys.exit(1)

    try:
        if not issubclass(getattr(get_plugin_module, 'GetPlugin'), GetPluginBase):
            raise TypeError()
        get_plugin = getattr(get_plugin_module, 'GetPlugin')(config)
    except AttributeError:
        logger.error(
            f'Get-plugin "{config["config"]["ip_plugin"]}" does not implement needed methods')
        sys.exit(1)
    except TypeError:
        logger.error(
            f'Get-plugin "{config["config"]["ip_plugin"]}" is not compatible')
        sys.exit(1)

    try:
        info = get_plugin.get_data()
    except:
        logger.exception(f'Error in {config["config"]["ip_plugin"]}')
        return

    if get_plugin.check_cache(info):
        logger.info('Cache is still valid')
        sys.exit(0)

    for config_zone in config['zones']:
        try:
            give_plugin_module = importlib.import_module(
                'ddpy.plugins.' + config_zone['plugin'])
        except KeyError:
            logger.error('No give-plugin specified')
            sys.exit(1)
        except ModuleNotFoundError:
            logger.error(f'Cannot find give-plugin "{config_zone["plugin"]}"')
            sys.exit(1)

        try:
            if not issubclass(getattr(give_plugin_module, 'GivePlugin'), GivePluginBase):
                raise TypeError()
            give_plugin = getattr(give_plugin_module,
                                  'GivePlugin')(config_zone)
        except AttributeError:
            logger.error(
                f'Give-plugin "{config_zone["plugin"]}" does not implement needed methods')
            sys.exit(1)
        except TypeError:
            logger.error(
                f'Give-plugin "{config_zone["plugin"]}" is not compatible')
            sys.exit(1)

        give_plugin.give_data(info)

    try:
        get_plugin.save_cache(info)
    except PermissionError:
        logger.error('Insufficient permissions to save cache')
