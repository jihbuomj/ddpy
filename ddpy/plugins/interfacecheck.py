import pathlib
import logging
import socket
import fcntl
import struct
import json

logger = logging.getLogger(f'ddpy.plugin.{__name__}')


def get_ip(config):
    interface = config[__name__]['interface']

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', bytes(interface, 'ascii')[:15])
        )[20:24])
    except OSError as err:
        if err.errno == 19:
            logger.error(f'No interface named {interface}')
            raise ValueError

    return {
        'ip': ip,
        'interface': interface,
        'plugin': __name__
    }


def check_cache(config, info):
    try:
        cache = json.load(open(config['config']['cachePath'], 'r'))
    except FileNotFoundError:
        cache = None
        print('No cache found')

    if not cache:
        return False

    return cache == info


def save_cache(config, info):
    json.dump(info, open(config['config']['cachePath'], 'w'))
