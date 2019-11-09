from keras.applications import ResNet50V2
from keras.layers import Dense, BatchNormalization, Activation, merge, Lambda, Flatten, concatenate

import numpy as np

from agent.nn.adaptive_programming import adaptive


IMG_SZ = (224, 224, 3)
ENC_IMG_SZ = (7 * 7 * 2048,)
CMD_SZ = (4,)


@adaptive('Encoder')
def encode_img(img: IMG_SZ):
    res_net = ResNet50V2(include_top=False,
                         weights='imagenet',
                         input_tensor=None)(img)
    return Flatten()(res_net)


@adaptive('Evaluator')
def evaluate_grasp(encoded_img: ENC_IMG_SZ, cmd: CMD_SZ):
    h1 = Dense(512)(concatenate([encoded_img, cmd]))
    h1 = BatchNormalization()(h1)
    h1 = Activation('relu')(h1)

    h2 = Dense(512)(h1)
    h2 = BatchNormalization()(h2)
    h2 = Activation('relu')(h2)

    return Dense(2, activation='softmax')(h2)


@adaptive('Full Discriminator', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
def is_grasp_successful(img_t: IMG_SZ, cmd: CMD_SZ):
    encoded_img_t = encode_img(img_t)
    return evaluate_grasp(encoded_img_t, cmd)


def decode_success(encoded_success):
    return True if np.amax(encoded_success) > 0 else False
