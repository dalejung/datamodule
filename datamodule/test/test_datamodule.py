from unittest import TestCase
import sys
import types

import datamodule

datamodule.install_datamodule()

class TestDataModule(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

import datamodule.test.fake_data as fd
old_ts = fd.ts
old_nc = fd.non_caching
import datamodule.test.fake_data as fd
# non caching should rerun
assert old_nc != fd.non_caching
# ts should be cached
assert old_ts is fd.ts
assert 'datamodule.test.fake_data' not in sys.modules

# grab cache
cache = fd.__datastore__
"""
Make sure we're not caching types we mean to skip
"""
SKIP_TYPES = (types.ModuleType, types.FunctionType, types.LambdaType, 
             types.ClassType, types.FileType)
for k, v in cache.iteritems():
    assert not isinstance(v, SKIP_TYPES)

# do not cache DATAMODULE_VARS
for k, v in cache.iteritems():
    assert not k.startswith('DATAMODULE_')

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
