import logging
import json
import socket
import fcntl
import struct
from ddpy.plugin_base import GetPluginBase

logger = logging.getLogger(__name__)

class GetPlugin(GetPluginBase):
    def __init__(self, *args, **kwargs):
        self.plugin_name = __name__.rsplit('.')[-1]
        self.cache_path = args[0]['config']['cache_path']
        self.interface = args[0][self.plugin_name]['interface']

    def get_ip(self, *args, **kwargs):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', bytes(self.interface, 'ascii')[:15])
            )[20:24])
        except OSError as err:
            if err.errno == 19:
                logger.error(f'No interface named {self.interface}')
                raise ValueError
            else:
                raise OSError

        return {
            'ip': ip,
            'interface': self.interface,
            'plugin': self.plugin_name
        }


    def check_cache(self, *args, **kwargs):
        try:
            cache = json.load(open(self.cache_path, 'r'))
        except FileNotFoundError:
            cache = None
            print('No cache found')

        if not cache:
            return False

        return cache == args[0]


    def save_cache(self, info):
        json.dump(info, open(self.cache_path, 'w'))
