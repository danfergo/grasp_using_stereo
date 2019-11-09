from agent.behaviours.memory import Memory
from keras.utils.np_utils import to_categorical

import numpy as np
from random import shuffle, sample

import itertools


class DataLoader:

    def __init__(self, path):
        self.m_memory = Memory(path)
        self.grasps = self.m_memory['grasps']

    def sample_from(self, split, batch_size=32):
        grasps = self.grasps.reshape((1,))[0]
        ids = [grasps[split][c].keys() for c in grasps[split]]
        img = self.m_memory.read_img

        while True:
            samples_ids = [[(c, s) for s in sample(ids[c], batch_size)] for c in range(len(ids))]
            samples_ids = list(itertools.chain.from_iterable(samples_ids))
            shuffle(samples_ids)

            b_lefts = np.array([img(split, c, idx, 'left') for c, idx in samples_ids])
            b_rights = np.array([img(split, c, idx, 'left') for c, idx in samples_ids])
            b_grasps = np.array([grasps[split][c][idx] for c, idx in samples_ids])
            successful = to_categorical(np.array([c for c, _ in samples_ids]), num_classes=len(ids))

            yield b_lefts, b_rights, b_grasps, successful

    def sample_train(self, *args, **kwargs):
        return self.sample_from('train', *args, **kwargs)

    def sample_validation(self, *args, **kwargs):
        return self.sample_from('val', *args, **kwargs)
# IN = '../data/dataset'
# data_loader = DataLoader(IN)
# print(next(data_loader.sample_train()))
