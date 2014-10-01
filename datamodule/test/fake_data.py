from datetime import datetime
import itertools
import contextlib
DATAMODULE_ENABLED = True
DATAMODULE_RANDOM = ['hello', 'random', 'datamodule', 'var']

v1 = 1
v2 = 2
v3 = 3
v4 = 4

vlist = range(10)

ts = datetime.now()

it = itertools.count()

# for loop will not cache
for x in [1]:
    run_count = next(it)
    non_caching = datetime.now()

lambda_test = lambda x: x * 2
def func_test():
    bob = 'bob'
    frank = 'frank'
    return locals()

func_res = func_test()

class ClassTest(object):
    wooooo = 123

@contextlib.contextmanager
def local_only():
    yield 123

with local_only(), local_only() as f:
    print((list(locals().keys())))
    dale = 'dale'
    booty = 123
