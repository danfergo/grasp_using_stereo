import numpy as np
from os import listdir, makedirs, path

import cv2


def as_str_tuple(x):
    return tuple(str(xx) for xx in (x if type(x) == tuple else (x,)))


class Memory:

    def __init__(self, base):
        self.base = base

    def __getitem__(self, at):
        _, __, file_path = self.get_paths(at)

        if path.isdir(self.abs_path(file_path)):
            return MemoryDirectory(self, file_path)

        try:
            return np.load(self.abs_path(file_path) + '.npy', allow_pickle=True)
        except IOError:
            return None

    def __setitem__(self, at, value):

        parent_path, _, file_path = self.get_paths(as_str_tuple(at))

        if not path.exists(self.abs_path(parent_path)):
            makedirs(self.abs_path(parent_path))

        np.save(self.abs_path(file_path) + '.npy', value)

    def save_img(self, at, value):

        parent_path, _, file_path = self.get_paths(as_str_tuple(at))

        if not path.exists(self.abs_path(parent_path)):
            makedirs(self.abs_path(parent_path))

        file_path = self.abs_path(file_path) + '.png'
        status = cv2.imwrite(file_path, value)

        if not status:
            print("Failed to write image: ", file_path)

    def read_img(self, *at):
        _, __, file_path = self.get_paths(at)

        if path.isdir(self.abs_path(file_path)):
            return MemoryDirectory(self, file_path)

        try:
            return cv2.imread(self.abs_path(file_path) + '.png')
        except IOError:
            return None

    def dir(self, *dir_path):
        return MemoryDirectory(self, "/".join(dir_path))

    def get_paths(self, at):

        if type(at) is tuple:
            if len(at) == 1:
                parts = '', at[0]
            else:
                parts = '/'.join(as_str_tuple(at[0:-1])), at[-1]
        else:
            parts = '', at

        parent_path = '' if parts[0] == '' else parts[0]
        name = parts[1]
        file_path = name if parent_path == '' else parent_path + '/' + name

        return parent_path, name, file_path

    def abs_path(self, rel_path):
        return self.base + '/' + rel_path


class MemoryDirectory:

    def __init__(self, memory, m_path):
        self.memory = memory
        self.path = m_path

    def __iter__(self):
        self.i = 0
        self.files = [
            f for f in listdir(self.memory.abs_path(self.path))]
        self.files = [f[:f.rfind('.')] for f in listdir(self.memory.abs_path(self.path))]
        return self

    def __next__(self):
        if self.i < len(self.files):
            file = MemoryFile(self, self.files[self.i])
            self.i += 1
            return file
        else:
            raise StopIteration

    def next(self):
        return self.__next__()

    def __getitem__(self, at):
        args = tuple(self.path.split('/')) + as_str_tuple(at)
        return self.memory[args]

    def __setitem__(self, at, value):
        args = tuple(self.path.split('/')) + as_str_tuple(at)
        self.memory[args] = value


class MemoryFile:

    def __init__(self, directory, name):
        self.dir = directory
        self.name = name

    def value(self):
        args = tuple(self.dir.path.split('/')) + (self.name,)
        return self.dir.memory[args]