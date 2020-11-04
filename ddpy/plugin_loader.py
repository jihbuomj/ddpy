from importlib.machinery import FileFinder, SOURCE_SUFFIXES, SourceFileLoader
from importlib._bootstrap import _init_module_attrs
from importlib.util import module_from_spec
import sys
import pathlib

def load_plugins(plugin_path):
    finder = FileFinder(str(plugin_path), (SourceFileLoader, SOURCE_SUFFIXES));

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
