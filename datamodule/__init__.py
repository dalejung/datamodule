from collections import OrderedDict
import ast
import sys

from loader import DataModuleLoader
from finder import DataModuleFinder
from cache import CacheManager

_CACHE_MANAGER = CacheManager()

def install_datamodule(loader_class=DataModuleLoader, cache_manager=_CACHE_MANAGER):
    sys.meta_path = [DataModuleFinder(loader_class, cache_manager=cache_manager)]
