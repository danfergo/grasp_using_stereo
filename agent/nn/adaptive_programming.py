import inspect
import tensorflow as tf

import numpy as np
from keras import Input, Model
from keras.optimizers import Adadelta

optimizer = Adadelta(lr=0.5, rho=0.95, epsilon=1e-8, decay=0.)


class AdaptiveFunction:

    def __init__(self, model):
        self.model = model

    def __call__(self, *args, **kwargs):
        if args == 0:
            raise Exception('Adaptive Functions can\'t have zero arguments')
        if tf.is_tensor(args[0]):
            return self.model(list(args))
        return self.model.predict([np.array([a]) for a in list(args)], batch_size=1)

    def adapt(self, *args, **kwargs):
        return self.model.train_on_batch(x=args[0], y=args[1], **kwargs)


def adaptive(*args, **kwargs):
    name = args[0] if len(args) > 0 else None

    def wrapper(fn):
        fn_spec = inspect.getfullargspec(fn)
        fn_args = fn_spec.args
        fn_args_shape = fn_spec.annotations

        def shape(a):
            return fn_args_shape[a] if a in fn_args_shape else kwargs[a]

        tensor_args = [Input(shape=shape(arg)) for arg in fn_args]
        out = fn(*tensor_args)
        model = Model(name=name, inputs=tensor_args, outputs=out)
        print(kwargs)

        if 'loss' in kwargs:
            model.compile(optimizer=optimizer, **kwargs)
        return AdaptiveFunction(model)

    return wrapper
