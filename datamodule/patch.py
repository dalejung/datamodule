from importlib._bootstrap import (_calc___package__, _handle_fromlist, 
                                  _sanity_check, _resolve_name, _find_and_load,
                                  _imp, _lock_unlock_module)
import sys

def _gcd_import(name, package=None, level=0):
    """Import and return the module based on its name, the package the call is
    being made from, and the level adjustment.

    This function represents the greatest common denominator of functionality
    between import_module and __import__. This includes setting __package__ if
    the loader did not.

    """
    _sanity_check(name, package, level)
    if level > 0:
        name = _resolve_name(name, package, level)
    _imp.acquire_lock()
    if name not in sys.modules:
        return _find_and_load(name, _gcd_import)
    module = sys.modules[name]


    # if it's a datamodule, reload
    if getattr(module, '_is_datamodule', False):
        del sys.modules[name]
        return _find_and_load(name, _gcd_import)

    if module is None:
        _imp.release_lock()
        message = ('import of {} halted; '
                   'None in sys.modules'.format(name))
        raise ImportError(message, name=name)
    _lock_unlock_module(name)
    return module

# exact replica. Need to rebind to new _gcd_import
def __import__(name, globals=None, locals=None, fromlist=(), level=0):
    """Import a module.

    The 'globals' argument is used to infer where the import is occuring from
    to handle relative imports. The 'locals' argument is ignored. The
    'fromlist' argument specifies what should exist as attributes on the module
    being imported (e.g. ``from module import <fromlist>``).  The 'level'
    argument represents the package location to import from in a relative
    import (e.g. ``from ..pkg import mod`` would have a 'level' of 2).

    """
    if level == 0:
        module = _gcd_import(name)
    else:
        globals_ = globals if globals is not None else {}
        package = _calc___package__(globals_)
        module = _gcd_import(name, package, level)
    if not fromlist:
        # Return up to the first dot in 'name'. This is complicated by the fact
        # that 'name' may be relative.
        if level == 0:
            return _gcd_import(name.partition('.')[0])
        elif not name:
            return module
        else:
            # Figure out where to slice the module's name up to the first dot
            # in 'name'.
            cut_off = len(name) - len(name.partition('.')[0])
            # Slice end needs to be positive to alleviate need to special-case
            # when ``'.' not in name``.
            return sys.modules[module.__name__[:len(module.__name__)-cut_off]]
    else:
        return _handle_fromlist(module, fromlist, _gcd_import)
