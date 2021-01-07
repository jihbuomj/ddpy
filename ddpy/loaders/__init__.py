from importlib.machinery import FileFinder, SOURCE_SUFFIXES, SourceFileLoader
from importlib._bootstrap import _init_module_attrs
from importlib.util import module_from_spec
import sys
import pathlib
import toml
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_format = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(stream_format)
logger.addHandler(stream_handler)

def load_config(path):
    config_file_list = ['./ddpy.toml', '/etc/ddpy/ddpy.toml']

    if path:
        config_file_list.insert(0, path)

    for config_file in config_file_list:
        if pathlib.Path(config_file).exists():
            return toml.load(config_file)

    logger.error('No config found')
    sys.exit(1)

def load_plugins(plugin_path):
    finder = FileFinder(str(plugin_path), (SourceFileLoader, SOURCE_SUFFIXES))

    plugins = {}
    for entry in plugin_path.iterdir():
        if entry.name in ('__init__.py'):
            continue

        spec = finder.find_spec(entry.stem)
        if not spec.loader:
            continue

        module = module_from_spec(spec)
        sys.modules[module.__name__] = module
        plugins[module.__name__] = module
        spec.loader.exec_module(module)
    return plugins
