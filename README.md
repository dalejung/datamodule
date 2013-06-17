datamodule: iterative data
==========================

Introduction
------------

One of the great things about **IPython** notebooks is the ability to run "heavy" cells only once.  **datamodule** hooks into the import system to replicate this behavior by creating *datamodules*. Basically it reparses datamodules on each import to remove assignments that we have already have cached. 

Example
-------

**data.py**

    # required flag
    DATAMODULE_ENABLED = True

    v1 = 1
    v2 = 2
    v3 = 3
    v4 = 4

    vlist = range(10)

    ts = datetime.now()

    # for loop will not cache
    for x in [1]:
        non_caching = datetime.now()

**analysis.py**

    import datamodule
    datamodule.install_datamodule()

    import data as fd
    old_ts = fd.ts
    old_nc = fd.non_caching
    import data as fd
    # non caching should rerun
    assert old_nc != fd.non_caching
    # ts should be cached
    assert old_ts is fd.ts

datamodule variables
--------------------

`DATAMODULE_ENABLED` : bool
  Must be set to True to become a datamodule
`DATAMODULE_CACHE_KEY` : string
  Explicitly set a cache key. Important if using local import because datamodule defaults to the import name as cache key. If you always use fully qualified unique import names, this may not matter. i.e. `import pkg.subpkg.data` vs `import data`

Data Backend
------------

**datamodule** comes with a dictionary backend for caches. This means that caches will not persist. One can create a file-based backend by overridding `DMCache`. The only non-dict method is `sync`. With file-io you will want to be careful so you do not serialize cache variables that do not change.

```python
# method of some class that acts like a dict but writes to a file backend
def sync(self, vars):
    for k, v in vars.iteritems():
        # want to save on io. Assume that cache
        # is fully hot so we don't get any reads
        # only save if 
        if k not in self or v is not self[k]:
            print 'Writing {k} to cache'.format(k=k)
            self[k] = v
```

Notes
-----

* A datamodule will not cache in `sys.modules`. This is so the module is re-run on every import. 
* **datamodule** will attempt to smartly skip variables that should not be cached like modules, classes, functions, etc.
* Only *simple global assignments* will be cached. Anything within a `for`, `with`, `if`, etc are not currently cachable. 
