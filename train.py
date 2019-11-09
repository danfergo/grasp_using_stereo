from keras.metrics import categorical_accuracy

from agent.nn.grasp_finder import is_grasp_successful, decode_success
from agent.behaviours.memory import Memory
import numpy as np
import time
import datetime
from data_loader import DataLoader
from plots import plot_discriminator_solo, plot_to_file

IN = '../data/dataset_2'
WEIGHTS_BASE = './_results/'
EXPERIMENT_NAME = 'DRY_TESTS'

memory = Memory(IN)
time_human_readable = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d_%H%M%S')
exp_path = WEIGHTS_BASE + EXPERIMENT_NAME + '_' + time_human_readable + '/'
exp_memory = Memory(exp_path)

grasps = memory['grasps'].reshape((1,))[0]
grasps_split = grasps['train']
grasps_split_cls = grasps_split[0]

# class Trainer:
#
#     def train(self, fn, data_generator, n_epochs, batch_size):
#         for e in range(len(n_epochs)):
#             batch = data_generator.sample_train()
#


N_EPOCHS = 30
N_BATCHES_PER_EPOCH = 1
data_loader = DataLoader(IN)


def main():
    exp_memory['weights', '.weights'] = np.array([])

    train_gen = data_loader.sample_train()
    val_gen = data_loader.sample_validation(batch_size=10)

    train_losses = []
    train_accs = []
    val_losses = []
    val_accs = []

    train_loss, train_acc = None, None

    for e in range(N_EPOCHS):
        for b in range(N_BATCHES_PER_EPOCH):
            train_i_left, train_i_right, train_grasp_conf, train_successful = next(train_gen)
            train_loss, train_acc = is_grasp_successful.adapt([train_i_left, train_grasp_conf], train_successful)
            print('[train]', train_loss, train_acc)

        train_losses.append(train_loss)
        train_accs.append(train_acc)

        val_i_left, val_i_right, val_grasp_conf, val_successful = next(val_gen)
        val_loss, val_acc = is_grasp_successful.model.evaluate([val_i_left, val_grasp_conf], val_successful)

        print('[validation]', val_loss, val_acc)
        val_losses.append(val_loss)
        val_accs.append(val_acc)

        is_grasp_successful.model.save_weights(exp_path + '/weights/' + str(e))

        plot_discriminator_solo(train_losses, train_accs, val_losses, val_accs)
        plot_to_file()

        exp_memory['train', 'losses'] = train_losses
        exp_memory['train', 'accuracies'] = train_accs
        exp_memory['val', 'losses'] = val_losses
        exp_memory['val', 'accuracies'] = val_accs

    # for grasp_id, grasp_conf in grasps_split_cls.items():
    #     i_left = memory.read_img('train', 0, grasp_id, 'left')
    #
    #     # cv2.imshow('window', i_left)
    #     # cv2.waitKey(0)
    #
    #
    #     print(success)
    #     break


main()
