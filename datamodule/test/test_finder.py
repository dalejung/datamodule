from unittest import TestCase
import sys
from importlib import util

from datamodule.finder import find_module_file

class TestDataModule(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_find_module_file(self):
        module = 'datamodule'
        parent_spec = util.find_spec(module)
        test = find_module_file(module, sys.path)
        assert test == parent_spec.loader.get_filename()

        fullname = 'datamodule.test'
        module = fullname.rpartition('.')[-1]
        child_spec = util.find_spec(fullname)
        test = find_module_file(module, parent_spec.submodule_search_locations)
        assert test == child_spec.loader.get_filename()

if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-vvs','-x','--pdb', '--pdb-failure'],exit=False)   
