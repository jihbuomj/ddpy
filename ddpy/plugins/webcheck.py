import pathlib
import re
import requests
import json
import logging

logger = logging.getLogger(f'ddpy.plugin.{__name__}')


def get_ip(config):
    response = requests.get(config[__name__]['web_check_url']).text
    ip = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response).group(0)
    return {
        'ip': ip,
        'plugin': __name__
    }


def check_cache(config, info):
    try:
        cache = json.load(open(config['config']['cache_path'], 'r'))
    except FileNotFoundError:
        cache = None
        logger.info('No cache found')

    if not cache:
        return False

    return cache == info


def save_cache(config, info):
    json.dump(info, open(config['config']['cache_path'], 'w'))
