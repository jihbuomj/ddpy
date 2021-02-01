import logging
import json
import re
import requests
from ddpy.plugin_base import GetPluginBase

logger = logging.getLogger(__name__)

class GetPlugin(GetPluginBase):
    def __init__(self, *args, **kwargs):
        self.plugin_name = __name__.rsplit('.')[-1]
        self.cache_path = args[0]['config']['cache_path']
        self.web_check_url = args[0][self.plugin_name]['web_check_url']

    def get_data(self):
        response = requests.get(self.web_check_url).text
        ip = re.search('\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}', response).group(0)
        return {
            'ip': ip,
            'plugin': self.plugin_name
        }

    def check_cache(self, info):
        try:
            cache = json.load(open(self.cache_path, 'r'))
        except FileNotFoundError:
            cache = None
            logger.info('No cache found')

        if not cache:
            return False

        return cache == info

    def save_cache(self, info):
        json.dump(info, open(self.cache_path, 'w'))
