#!/usr/bin/env python3
"""MatHDF5Reader reads Matlab .mat file which are based on HDF5 in Python.
Mat-file version 7.3 are based on HDF5.

save('test_basic.mat', 'data', '-v7.3')

"""

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import copy
import numpy as np
import h5py

class MatHDF5Reader_cellarray:
    """MatHDF5Reader_cellarray
    Iterator class fir cell array
    """

    def __init__(self, name, mat, dataset):
        self.mat = mat
        self.dataset = dataset
        self.name = name
        self.iter_index = -1

    def __str__(self):
        return """MatHDF5Reader_cellarray({name})""".format(name=self.name)

    __repr__ = __str__


    def __getitem__(self, key):
        val = self.mat.hdf5[self.dataset[()][key][0]]
        if isinstance(val, h5py.Group): # FIXME:
            m = copy.copy(self.mat)
            m.group = val
            return m
        val = val[()]
        val = val if val.ndim < 2 else val.swapaxes(-1, -2)
        return val

    def get_as_str(self, key):
        val = self.mat.hdf5[self.dataset[()][key][0]]
        if isinstance(val, h5py.Dataset):
            vn = val[()]
            if val.dtype == np.uint16:
                return "".join([chr(c) for c in vn.flat])
        return None

    def __iter__(self):
        return self

    def __next__(self):
        self.iter_index += 1
        if self.iter_index >= len(self.dataset):
            raise StopIteration
        return self[self.iter_index]

    def iter_text(self):
        return MatHDF5Reader_cellarray_iter_text(self)

class MatHDF5Reader_cellarray_iter_text:

    def __init__(self, cellarray):
        self.cellarray = cellarray
        self.iter_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.iter_index += 1
        if self.iter_index >= len(self.cellarray.dataset):
            raise StopIteration
        return self.cellarray.get_as_str(self.iter_index)

class MatHDF5Reader:
    """
    matlab:
        %% creat test file
        data = {};
        data.val001 = 1;
        data.val002 = pi;
        data.array = [1:0.5:10];
        data.cel = {};
        for i = [1:10]
            data.cel{end+1} = [1:10]*i;
        end
    save('test_basic.mat', 'data', '-v7.3')

    python:
        mat = MatHDF5Reader('test_basic.mat')

    """

    def __init__(self, filename):
        self.filename = filename
        self.hdf5 = None
        self.open()
        self.cd()
        self.refs = None
        try:
            self.refs = self.hdf5['/#refs#']
        except KeyError as e:
            logger.warning('KeyError:' + str(e) + f' >{filename}<')


    def __str__(self):
        return """MatHDF5Reader('{fn}')
open: {open}
path: {path}""".format(fn=self.filename,
                       open=(self.hdf5 is not None),
                       path=self.pwd())

    __repr__ = __str__

    def open(self):
        if self.hdf5 is None:
            self.hdf5 = h5py.File(self.filename, 'r')
            self.group = self.hdf5['/']
        else:
            logging.error('There is already a file opened.')

    def close(self):
        self.hdf5.close()
        self.hdf5 = None

    def cd(self, path='/'):
        if path == '..':
            path = self.pwd().rsplit('/',1)[0]
        v = self.group[path]
        if isinstance(v, h5py.Group):
            self.group = v
        else:
            logging.error('{} is not a group'.format(path))

    def ls(self):
        print(self.pwd())
        for k, v in self.group.items():
            if k == '#refs#':
                continue
            if isinstance(v, h5py.Group):
                t = 'group'
            elif isinstance(v, h5py.Dataset):
                vn = v[()]
                if vn.dtype == 'object':
                    t = 'cell array'
                elif vn.shape == (1, 1):
                    t = vn.dtype.name
                else:
                    t = '{} {}'.format(vn.dtype.name, vn.shape)
            else:
                t = type(v)
            print("{:12} : {}".format(k, t))

    def pwd(self):
        return self.group.name

    def get(self, key):
        v = self.group[key]
        if isinstance(v, h5py.Dataset):
            if v[()].dtype == 'object':
                return MatHDF5Reader_cellarray(v.name, self, v)
            val = v[()]
            if val.shape == (1, 1):
                return val[0, 0]
            val = val if val.ndim < 2 else val.swapaxes(-1, -2)
            return val
        return v

    def get_as_str(self, key):
        v = self.group[key]
        if isinstance(v, h5py.Dataset):
            vn = v[()]
            if v.dtype == np.uint16:
                return "".join([chr(c) for c in vn.flat])
        return None

    def __getitem__(self, key):
        return self.get(key)

# eof