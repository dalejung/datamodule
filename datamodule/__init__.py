from collections import OrderedDict
import ast
import sys

from loader import DataModuleLoader
from finder import DataModuleFinder

def install_datamodule(loader_class=DataModuleLoader):
    sys.meta_path = [DataModuleFinder(loader_class)]
