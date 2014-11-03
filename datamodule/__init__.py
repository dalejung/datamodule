from collections import OrderedDict
import ast
import sys
from functools import partial

from .loader import DataModuleLoader
from .finder import DataModuleFinder
from .cache import CacheManager, DMCache

LOADED = False

def patch_specmethods():
    import builtins
    from .patch import __import__
    builtins.__import__ = __import__

def install_datamodule(loader_class=DataModuleLoader, cache_manager=None, cache_cls=DMCache, override=False):
    global LOADED
    if LOADED:
        return
    patch_specmethods()
    if cache_manager is None:
        cache_manager = CacheManager(cache_cls)
    loader_class = partial(loader_class, cache_manager=cache_manager) 
    sys.meta_path.insert(0, DataModuleFinder(loader_class))
    LOADED = True
