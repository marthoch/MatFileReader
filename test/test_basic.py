import unittest
import io
import contextlib
import sys
sys.path.insert(0, r'../src')

import matFileReader
from matFileReader import MatHDF5Reader

class Test(unittest.TestCase):


    def setUp(self):
        self.mat = MatHDF5Reader(r'test_basic.mat')


    def tearDown(self):
        self.mat.close()
        self.mat = None

    def testName(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.mat.ls()
        #print('"{}"'.format(f.getvalue()))
        self.assertEqual(f.getvalue(), "/\ndata         : group\n" )



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()