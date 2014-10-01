class CacheManager(object):
    """
    Handle storing the DMCache objects. We want the use the same 
    object for each cache_key.

    Note: This original was just a module level dict
    """
    def __init__(self, cache_cls=None):
        if cache_cls is None:
            cache_cls = DMCache
        self.cache_cls = cache_cls
        self.caches = {}

    def __setitem__(self, name, obj):
        self.caches[name] = obj

    def get(self, name):
        """
        """
        if name not in self.caches:
            cache = self.cache_cls(name)
            self[name] = cache
        return self.caches.get(name)

class DMCache(object):
    """
    Object that stores variables for a DataModule

    Essentially a dict-like structure with a sync method
    """
    def __init__(self, cache_key):
        self.cache_key = cache_key
        self._vars = {}

    def sync(self, vars, config):
        """
        Sync to caches to the new vars. For a dict backend,
        it's a simple replace. 

        For filebackends, this gets more complicated as you don't 
        want to serialize cache values that don't change
        """
        self._vars = vars

    def iteritems(self):
        return iter(list(self._vars.items()))
    items = iteritems

    def keys(self):
        return list(self._vars.keys())

    def __contains__(self, key):
        return key in self._vars

    def __getitem__(self, key):
        return self._vars[key]
