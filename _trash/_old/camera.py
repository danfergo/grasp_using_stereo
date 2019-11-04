import numpy as np
import cv2


class CameraDriver:

    def __init__(self, camera_id=1, mode='stereo', buffer_size=5):
        print('Initializing camera...')
        self.cap = cv2.VideoCapture(camera_id)
        self.mode = mode
        self.buffer_size = buffer_size

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        if self.cap is None or not self.cap.isOpened():
            raise Exception('Unable to open video source ' + str(camera_id))
        print('Camera ready.')

    def read_raw(self, skip_buffer):
        # Capture one frame
        if skip_buffer:
            i = 0
            while i < self.buffer_size:
                self.cap.read()
                i += 1

        return self.cap.read()

    def read(self, skip_buffer=True):
        _, frame = self.read_raw(skip_buffer)

        if self.mode == 'mono':
            return frame

        h, w, c = np.shape(frame)
        left = frame[:, 0: int(w / 2 - 1), :]
        right = frame[:, int(w / 2):, :]
        return left, right

    def left(self):
        if self.mode == 'mono':
            return self.read()

        return self.read()[0]

    def right(self):
        if self.mode == 'mono':
            return self.read()

        return self.read()[1]

    def release(self):
        # When everything done, release the capture
        self.cap.release()

    def display(self, skip_buffer=True):
        ret, frame = self.read_raw(skip_buffer)
        cv2.imshow('Camera', frame)
        # if not rospy.is_shutdown():
        cv2.waitKey(0)
