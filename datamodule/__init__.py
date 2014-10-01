from collections import OrderedDict
import ast
import sys

from .loader import DataModuleLoader
from .finder import DataModuleFinder
from .cache import CacheManager, DMCache

# Taken from importlib/bootstrap.py
# Only real change is to make adding module to sys.modules optional
def _load_backward_compatible(self):
    # (issue19713) Once BuiltinImporter and ExtensionFileLoader
    # have exec_module() implemented, we can add a deprecation
    # warning here.
    spec = self.spec
    module = spec.loader.load_module(spec.name)
    # HACK storing in sys.modules is optional
    if spec.name in sys.modules:
        module = sys.modules[spec.name]
    if getattr(module, '__loader__', None) is None:
        try:
            module.__loader__ = spec.loader
        except AttributeError:
            pass
    if getattr(module, '__package__', None) is None:
        try:
            # Since module.__path__ may not line up with
            # spec.submodule_search_paths, we can't necessarily rely
            # on spec.parent here.
            module.__package__ = module.__name__
            if not hasattr(module, '__path__'):
                module.__package__ = spec.name.rpartition('.')[0]
        except AttributeError:
            pass
    if getattr(module, '__spec__', None) is None:
        try:
            module.__spec__ = spec
        except AttributeError:
            pass
    return module

def patch_specmethods():
    from importlib._bootstrap import _SpecMethods
    _SpecMethods._load_backward_compatible = _load_backward_compatible

def install_datamodule(loader_class=DataModuleLoader, cache_manager=None, cache_cls=DMCache, override=False):
    patch_specmethods()
    if cache_manager is None:
        cache_manager = CacheManager(cache_cls)
    sys.meta_path.insert(0, DataModuleFinder(loader_class, cache_manager=cache_manager))

