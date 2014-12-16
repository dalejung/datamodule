from collections import OrderedDict
import ast

def _get_di_vars(code):
    """
    Running through an ast.Module and returning DATAMODULE variables. 
    These are just simple assignments with the name prefixed with
    DATAMODULE. 

    DATAMODULE_ENALBLED = True
    DATAMODULE_CACHE_KEY = 'some_key'
    """
    data = OrderedDict()
    for node in code.body:
        if isinstance(node, ast.Assign):
            try:
                names = [n.id for n in node.targets]
                value = ast.literal_eval(node.value)
            except:
                continue

            names = [name for name in names if name.startswith('DATAMODULE')]
            for name in names:
                data[name] = value
    return data

def skip_nodes_in_cache(nodes, cache, verbose=True):
    """
    remove the assign statements that were gotten 
    from cache
    """
    new_body = []
    skipped = []
    for node in nodes:
        skip = _is_skip_node(node, cache)
        if not skip:
            new_body.append(node)
        else:
            skipped.append(skip)

    if verbose:
        print(("Following loaded from cache: {0}".format(', '.join(skipped))))

    return new_body

def _is_skip_node(node, cache):
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

def _clean_vars(vars):
    """
    Dont' store variables that are things like modules, lambdas, classes, etc
    """
    SKIP_TYPES = (types.ModuleType, types.FunctionType, types.LambdaType, 
                    type, IOBase)
    is_magic = lambda s: s.startswith('__') and s.endswith('__')
    vars = {k:v for k, v in list(vars.items()) 
            if not isinstance(v, SKIP_TYPES) and not is_magic(k)}
    # remove DATAMODULE vars
    for k in list(vars.keys()):
        if k.startswith('DATAMODULE_'):
            vars.pop(k)
    return vars

def run_code(code, cache, user_ns, source_path=None):
    ns = {}
    ns.update(user_ns)
    ns.update(cache)

    # get the datamodule specific config lines and grab cache
    config = _get_di_vars(code)

    # process the ast and remove the cache vars
    new_body = skip_nodes_in_cache(code.body, cache, verbose)
    code.body = new_body

    if source_path is None:
        source_path = '<DataModule>'
    code = compile(code, source_path, 'exec')
    ns['__datastore__'] = cache

    # execute module with cache-hot namespace
    try:
        exec(code, ns)
    except Exception as error:
        print("*" * 20)
        print(error)
        print("*" * 20)
    finally:
        # update the calling namespace
        user_ns.update(ns)
        # SAVE CACHE
        ns = _clean_vars(ns)
        cache.sync(ns, config)

        # flag for datamodule.patch._gcd_import
        mod._is_datamodule = True
