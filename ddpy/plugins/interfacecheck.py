import pathlib
import logging
import socket
import fcntl
import struct
import json

logger = logging.getLogger(__name__)

def register(config):
    logger.setLevel(logging.INFO)

    if 'log_file' in config['config']:
        log_path = config['config']['log_file']
    else:
        log_path = 'ddpy.log'

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

def get_ip(config):
    interface = config[__name__]['interface']

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,
            struct.pack('256s', bytes(interface, 'ascii')[:15])
    )[20:24])
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
