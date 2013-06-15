import imputil
import ast
import types
import imp

from util import _get_di_vars

# http://www.python.org/dev/peps/pep-0302/

_CACHE = {}

class DataModuleLoader(imputil.Importer):
    def __init__(self, fullname, path):
        self.fullname = fullname
        self.path = path
        mname = fullname.rpartition('.')[-1]
        self.mname = mname

    def load_module(self, fullname):
        """
        Note:
        -----
        We do not cache module in sys.modules
        """
        mname = self.mname
        fp, pathname, desc = imp.find_module(mname, self.path)
        suffix, mode, type = desc

        source = fp.read()
        code = ast.parse(source, pathname)
        config = _get_di_vars(code)
        # LOAD CACHE
        cache_key = self._cache_key(self.fullname, config)
        cache = self.load_cache(cache_key, config)

        # process the ast and remove the cache vars
        code = self.process_ast(code, config, cache)

        code = compile(code, pathname, 'exec')
        mod = self.new_module()
        ns = {}
        # populate namespace with cache vars
        ns.update(cache)
        ns['__datastore__'] = cache
        exec code in ns
        mod.__dict__.update(ns)

        # SAVE CACHE
        ns = self._clean_vars(ns)
        self.save_cache(ns, config)
        return mod

    def _cache_key(self, fullname, config):
        custom_key = config.get('DATAMODULE_CACHE_KEY', None)
        return custom_key or fullname

    def _load_cache(self, cache_key):
        # in process cache
        cache = _CACHE.get(cache_key, None)
        return cache

    # in process cache
    def load_cache(self, cache_key, config=None):
        cache = self._load_cache(cache_key)
        if cache is None:
            cache = {}
            self._save_cache(cache_key, cache)
        return cache

    def _save_cache(self, cache_key, cache):
        _CACHE[cache_key] = cache

    def save_cache(self, vars, config):
        cache_key = self._cache_key(self.fullname, config)
        # save to in process
        cache = self.load_cache(cache_key)
        cache.clear()
        cache.update(vars)
        self._save_cache(cache_key, cache)

    def _clean_vars(self, vars):
        """
        Dont' store variables that are things like modules, lambdas, classes, etc
        """
        SKIP_TYPES = (types.ModuleType, types.FunctionType, types.LambdaType, 
                     types.ClassType, types.FileType)
        vars = {k:v for k, v in vars.iteritems() 
                if not isinstance(v, SKIP_TYPES)}
        vars.pop('__builtins__', None)
        vars.pop('__datastore__', None)
        return vars

    def process_ast(self, code, config, cache):
        new_body = skip_nodes_in_cache(code.body, cache)
        code.body = new_body
        return code

    def new_module(self):
        mname = self.mname
        mod = imp.new_module(mname)
        mod.__path__ = self.path
        return mod


def skip_nodes_in_cache(nodes, cache):
    # remove the assign statements that were gotten 
    # from cache
    new_body = []
    for node in nodes:
        res = _skip_node(node, cache)
        if not res:
            new_body.append(node)
    return new_body

def _skip_node(node, cache):
    if not isinstance(node, ast.Assign):
        return False

    # only handle single assignments
    if len(node.targets) > 1:
        return False

    try:
        name = node.targets[0].id
    except:
        return False

    if name in cache.keys():
        return True

