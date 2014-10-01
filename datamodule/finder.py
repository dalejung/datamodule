import imp
import ast

from .util import _get_di_vars

def _is_datamodule(mname, path):
    try:
        fp, pathname, desc = imp.find_module(mname, path)
        suffix, mode, type = desc
    except ImportError:
        return False

    # skip packages or non .py files
    if fp is None or type != imp.PY_SOURCE:
        return False

    # parse source to get the DATAMODULE vars
    source = fp.read()
    code = ast.parse(source, pathname)
    config = _get_di_vars(code)

    # check for datamodule flag
    enabled = config.get('DATAMODULE_ENABLED', False)
    return enabled

class DataModuleFinder(object):
    """
    sys.meta_path compatible class.

    Handles checking for datamodules and loading if necessary.
    Otherwise, let regualr import machinery handle module
    """
    def __init__(self, loader_class, cache_manager):
        self.loader_class = loader_class
        self.cache_manager = cache_manager
 
    def find_module(self, fullname, path=None):
        """
        Only match DataImport modules
        """
        mname = fullname.rpartition('.')[-1]
        is_datamod = _is_datamodule(mname, path)
        # this is a datamodule, load it with our loaderclass
        if is_datamod:
            loader = self.loader_class(fullname, path, cache_manager=self.cache_manager)
            return loader
        # not datamodule, punt to regular import process
        return None
