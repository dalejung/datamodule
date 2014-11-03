import importlib
from importlib import util
from importlib._bootstrap import SourceFileLoader
import ast
import types
import imp
import sys
from io import IOBase

from .util import _get_di_vars

# http://www.python.org/dev/peps/pep-0302/

def _get_mname_path(fullname, path=None):
    if '.' not in fullname:
        return fullname, path

    pkg, _, fullname = fullname.partition('.')
    fp, path, desc = imp.find_module(pkg, path)
    return _get_mname_path(fullname, path=[path])

def _load_code(fullname, path=None):
    mname, path = _get_mname_path(fullname)
    fp, pathname, desc = imp.find_module(mname, path)
    suffix, mode, type = desc

    with fp:
        source = fp.read()
    code = ast.parse(source, pathname)
    return code

class DataModuleLoader(SourceFileLoader):
    def __init__(self, fullname, path, cache_manager, verbose=True):
        self.fullname = fullname
        self.path = path
        mname = fullname.rpartition('.')[-1]
        self.mname = mname
        self.cache_manager = cache_manager
        self.verbose = verbose
        self.config = None

        super().__init__(fullname, path)

    def get_cache(self, config):
        # LOAD CACHE
        cache_key = self._cache_key(self.fullname, config)
        if self.verbose:
            print(("Loading Cache {cache_key}".format(cache_key=cache_key)))
        cache = self.load_cache(cache_key, config)
        if self.verbose:
            print("Done Loading Cache")
        return cache

    def get_code(self):
        fullname = self.fullname
        source_path = self.get_filename(fullname)
        source_bytes = self.get_data(source_path)
        code = ast.parse(source_bytes, source_path)

        # get the datamodule specific config lines and grab cache
        config = _get_di_vars(code)
        self.config = config
        cache = self.get_cache(config=self.config)

        # process the ast and remove the cache vars
        code = self.process_ast(code, config, cache)
        code = compile(code, source_path, 'exec')
        return code

    def exec_module(self, mod):
        ns = mod.__dict__

        # not get_code sets self.config
        code = self.get_code()
        cache = self.get_cache(config=self.config)
        # populate namespace with cache vars
        ns.update(cache)
        ns['__datastore__'] = cache

        # execute module with cache-hot namespace
        exec(code, ns)
        # Transfer vars to module dict. 
        # Note: The reason we executed in a dict is that 
        # mod.__dict__ comes standard with module specific vars
        mod.__dict__.update(ns)

        # SAVE CACHE
        ns = self._clean_vars(ns)
        cache.sync(ns, self.config)

        # flag for datamodule.patch._gcd_import
        mod._is_datamodule = True

    def _cache_key(self, fullname, config):
        custom_key = config.get('DATAMODULE_CACHE_KEY', None)
        return custom_key or fullname

    def load_cache(self, cache_key, config=None):
        cache = self.cache_manager.get(cache_key)
        return cache

    def _clean_vars(self, vars):
        """
        Dont' store variables that are things like modules, lambdas, classes, etc
        """
        SKIP_TYPES = (types.ModuleType, types.FunctionType, types.LambdaType, 
                     type, IOBase)
        vars = {k:v for k, v in list(vars.items()) 
                if not isinstance(v, SKIP_TYPES)}
        vars.pop('__builtins__', None)
        vars.pop('__datastore__', None)
        # remove DATAMODULE vars
        for k in list(vars.keys()):
            if k.startswith('DATAMODULE_'):
                vars.pop(k)
        return vars

    def process_ast(self, code, config, cache):
        """
        Preprocesses the AST before being executed in module scope. 

        For now all this does is remove ast.Assign nodes that 
        are already in cache.
        """
        new_body = skip_nodes_in_cache(code.body, cache, self.verbose)
        code.body = new_body
        return code

    def new_module(self):
        """ create a new module object """
        mname = self.mname
        mod = imp.new_module(mname)
        mod.__path__ = self.path
        mod.__name__ = self.fullname
        return mod


def skip_nodes_in_cache(nodes, cache, verbose=True):
    """
    remove the assign statements that were gotten 
    from cache
    """
    new_body = []
    skipped = []
    for node in nodes:
        skip = _skip_node(node, cache)
        if not skip:
            new_body.append(node)
        else:
            skipped.append(skip)

    if verbose:
        print(("Following loaded from cache: {0}".format(', '.join(skipped))))

    return new_body

def _skip_node(node, cache):
    """
    Return False if skipped, return the name if True
    """
    if not isinstance(node, ast.Assign):
        return False

    # only handle single assignments
    if len(node.targets) > 1:
        return False

    try:
        name = node.targets[0].id
    except:
        return False

    if name in list(cache.keys()):
        return name
