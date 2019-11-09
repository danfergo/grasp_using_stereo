import random
from agent.behaviours.memory import Memory
import numpy as np
from cv2 import resize

BASE_I = 0
O_SIZE = (224, 224)
TRIM_TOP = 50
VAL_SPLIT = 50
IN = '../data/20191102_2/'
OUT = '../data/dataset_2/'


def horizontal_split(img):
    h, w, c = np.shape(img)
    left = img[:, :w // 2, :]
    right = img[:, w // 2:, :]
    return left, right


def cut_square(img):
    h, w, _ = np.shape(img)
    min_d = min(w, h)

    w_l2 = (w - min_d) // 2
    h_l2 = (h - min_d) // 2

    return img[h_l2:(h - h_l2), w_l2: (w - w_l2), :]


def is_success(range):
    return range > 0.05


def get_grasp(memory, i):
    grasps = memory['grasps'][0]
    return grasps[i] if i in grasps else None


def get_camera(memory, i, name):
    frame = memory.read_img('data', i, name)
    return frame if frame is not None else None


def get_final_range(memory, i):
    true_ranges = memory['true_amplitudes'][0]
    return true_ranges[i] if i in true_ranges else None


def get_all(memory, max_i):
    index = [[], []]

    def range_arg(r):
        return 1 if r is not None and is_success(r) else 0

    [index[range_arg(get_final_range(memory, i))].append(i) for i in range(1, max_i + 1)]
    return index


def main():
    if IN == OUT:
        print('INPUT PATH CANT BE THE SAME AS OUTPUT!')
        return

    in_mem = Memory(IN)
    out_mem = Memory(OUT)

    max_i = in_mem['meta'][0]
    print('Indexing ...')
    index = get_all(in_mem, max_i)
    print('Finished indexing.')
    train, val = [[], []], [[], []]
    for c in range(len(index)):
        val[c] = random.sample(index[c], VAL_SPLIT)
        train[c] = [x for x in index[c] if x not in val[c]]
    print('Split.')

    grasps = {'val': {0: {}, 1: {}}, 'train': {0: {}, 1: {}}}
    final_ranges = {'val': {0: {}, 1: {}}, 'train': {0: {}, 1: {}}}
    for i in range(max_i + 1):
        grasp = get_grasp(in_mem, i)
        final_range = get_final_range(in_mem, i)
        b_img = get_camera(in_mem, i, 'before')

        if grasp is None or b_img is None or final_range is None:
            continue

        successful = is_success(final_range)
        b_left, b_right = horizontal_split(b_img[TRIM_TOP:, :, :])
        b_left, b_right = resize(cut_square(b_left), O_SIZE), resize(cut_square(b_right), O_SIZE)

        ii = i + BASE_I
        cls = 1 if successful else 0
        split = 'val' if i in val[cls] else 'train'
        out_mem.save_img((split, cls, ii, 'left'), b_left)
        out_mem.save_img((split, cls, ii, 'right'), b_right)
        grasps[split][cls][ii] = np.array(grasp)
        final_ranges[split][cls][ii] = final_range

        if i % 10 == 0:
            print(str(round(i * 100 / (max_i + 1))) + '% , ' + str(i))

    out_mem['grasps'] = np.array(grasps)
    out_mem['final_ranges'] = np.array(final_ranges)
    print('Done')


main()
