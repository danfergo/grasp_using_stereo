from agent.behaviours.memory import Memory
from matplotlib import pyplot as plt

WEIGHTS_BASE = './_results/'

EXPERIMENT_FOLDER = 'DRY_TESTS_20191109_013214'


def plot_discriminator_solo(train_losses, train_accs, val_losses, val_accs):
    fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2)

    ax1.plot(train_losses, label='Train')
    ax1.plot(val_losses, label='Validation')
    ax1.legend(loc='lower right')

    ax2.plot(train_accs, label='Train')
    ax2.plot(val_accs, label='Validation')
    ax2.legend(loc='upper right')


def plot_to_file(name='plot.png'):
    plt.savefig(name)


def main():
    exp_path = WEIGHTS_BASE + EXPERIMENT_FOLDER + '/'
    exp_memory = Memory(exp_path)

    train_losses = exp_memory['train', 'losses']
    train_accs = exp_memory['train', 'accuracies']
    val_losses = exp_memory['val', 'losses']
    val_accs = exp_memory['val', 'accuracies']
    plot_discriminator_solo(train_losses, train_accs, val_losses, val_accs)

    # plt.savefig('myfig')
    plt.show()


# main()
