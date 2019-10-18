from narnia.core import ROSActuator, ROSServiceSubscriber, image_msg_to_numpy

import time
import cv2
import numpy as np
import base64

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class ZEDCamera(ROSActuator):
    def __init__(self):
        print('Initializing camera, cool camera...')
        super().__init__()
        self.t = 0
        self.data = None

    def after_init(self):
        pass

    def get_frame(self):
        if self.data:
            img_msg = AttrDict(self.data)
            x = np.fromstring(base64.b64decode(img_msg.data), dtype=np.uint8)
            img = cv2.imdecode(x, 1)
            return img
        return None

    @ROSServiceSubscriber('/lr_rectified')
    def read_ros(self):
        pass

    def read(self):
        self.data = self.read_ros().data['image']
        return self.get_frame()