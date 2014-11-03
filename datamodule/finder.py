import imp
import sys
import ast
from importlib._bootstrap import (spec_from_file_location,
                                  _path_join,
                                  _path_isfile)

from .util import _get_di_vars

def _is_datamodule(fullpath):
    with open(fullpath) as fp:
        # parse source to get the DATAMODULE vars
        source = fp.read()

    code = ast.parse(source, fullpath)
    config = _get_di_vars(code)

    # check for datamodule flag
    enabled = config.get('DATAMODULE_ENABLED', False)
    return enabled

def find_module_file(mname, path, suffixes=['.py']):
    """
    mname : string
        the module name, known as tail_module in importutil source
    path : list of strings
        search path

    Note: We don't do the FileFinder caching and what not.
    """
    if path is None:
        path = sys.path

    for entry in path:
        base_path = _path_join(entry, mname)
        for suffix in suffixes:
            # check for package
            init_filename = '__init__' + suffix
            fullpath = _path_join(base_path, init_filename)
            if _path_isfile(fullpath):
                return fullpath

            # check for regular module
            fullpath = _path_join(entry, mname + suffix)
            if _path_isfile(fullpath):
                return fullpath
    raise ImportError("Could not find module file")

class DataModuleFinder(object):
    """
    sys.meta_path compatible class.

    Handles checking for datamodules and loading if necessary.
    Otherwise, let regualr import machinery handle module
    """
    def __init__(self, loader_class):
        self.loader_class = loader_class

    def find_spec(self, fullname, path=None, target=None):
        mname = fullname.rpartition('.')[-1]

        try:
            fullpath = find_module_file(mname, path, suffixes=['.py'])
        except ImportError:
            return None

        is_datamod = _is_datamodule(fullpath)
        # this is a datamodule, load it with our loaderclass
        if is_datamod:
            loader = self.loader_class(fullname, fullpath)
            spec = spec_from_file_location(fullname, loader=loader)
            return spec

        # not datamodule, punt to regular import process
        return None
