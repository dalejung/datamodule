from collections import OrderedDict
import ast
import sys

from loader import DataModuleLoader
from finder import DataModuleFinder
from cache import CacheManager, DMCache

def install_datamodule(loader_class=DataModuleLoader, cache_manager=None, cache_cls=DMCache, override=False):
    if cache_manager is None:
        cache_manager = CacheManager(cache_cls)
    if sys.meta_path and not override:
        raise Exception('sys.meta_path is not empty')   
    sys.meta_path = [DataModuleFinder(loader_class, cache_manager=cache_manager)]
