from narnia.core import Behaviour, MultiStepAction

from agent.behaviours.memory import Memory
from agent.drivers.arm import ArmDriver
from agent.drivers.ui import UIDriver
from agent.drivers.zed_camera import ZEDCameraDriver
from ..constants.positions import Positions
from ..drivers.gripper import GripperDriver

from random import random
from math import pi

import cv2
import asyncio
import numpy as np

from skimage.exposure import rescale_intensity
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
import matplotlib.pyplot as plt
from skimage import segmentation, color


async def ensure(f, *args, **kwargs):
    while True:
        res = await f(*args, **kwargs)
        print('--> ', res)
        if res == 'DONE':
            break
        else:
            await asyncio.sleep(3)


def segment_colorfulness(image, mask):
    # split the image into its respective RGB components, then mask
    # each of the individual RGB channels so we can compute
    # statistics only for the masked region
    (B, G, R) = cv2.split(image.astype("float"))
    R = np.ma.masked_array(R, mask=mask)
    G = np.ma.masked_array(B, mask=mask)
    B = np.ma.masked_array(B, mask=mask)

    cv2.imshow('w', R)
    cv2.waitKey(1)
    # compute rg = R - G
    rg = np.absolute(R - G)

    # compute yb = 0.5 * (R + G) - B
    yb = np.absolute(0.5 * (R + G) - B)

    # compute the mean and standard deviation of both `rg` and `yb`,
    # then combine them
    stdRoot = np.sqrt((rg.std() ** 2) + (yb.std() ** 2))
    meanRoot = np.sqrt((rg.mean() ** 2) + (yb.mean() ** 2))

    # derive the "colorfulness" metric and return it
    return stdRoot + (0.3 * meanRoot)


@Behaviour()
class DataCollectionBehaviour:
    arm: ArmDriver
    gripper: GripperDriver
    camera: ZEDCameraDriver
    ui: UIDriver

    def __init__(self):
        self.successful_grasps = 0
        self.unsuccessful_grasps = 0
        self.failed_attempts = 0
        self.refresh_after = 10
        self.swipe_every = 8
        self.manipulator_meta = {}
        self.h = None
        self.i = 0

        self.grasps = {}
        self.true_amplitudes = {}

        self.memory = Memory('/media/danfergo/c60e6fb7-633f-46ff-a6ab-2930ec98d57f/experimental_data/20191103')

        meta = self.memory['meta']
        if meta is not None:
            self.i = meta[0]

        homography = self.memory['homography']
        if homography is not None:
            self.h = homography[0]

        grasps = self.memory['grasps']
        if grasps is not None:
            self.grasps = grasps[0]

        true_amplitudes = self.memory['true_amplitudes']
        if true_amplitudes is not None:
            self.true_amplitudes = true_amplitudes[0]

        manipulator_meta = self.memory['manipulator_meta']
        if manipulator_meta is not None:
            self.manipulator_meta = manipulator_meta.reshape((1,))[0]

    def save_meta(self):
        self.memory['meta'] = np.array([
            self.i
        ])

    def save_grasp(self, grasp):
        self.grasps[self.i] = grasp
        self.memory['grasps'] = np.array([self.grasps])
        print('Saved grasp ', grasp)

    def save_true_amplitude(self, amplitude):
        self.true_amplitudes[self.i] = amplitude
        self.memory['true_amplitudes'] = np.array([self.true_amplitudes])

    def save_camera(self, name):
        self.memory.save_img(('data', self.i, name), self.camera.read())
        print('Saved image ', name)

    def save_homography(self, h):
        self.memory['homography'] = np.array([h])

    def save_manipulator(self, name):
        if self.i not in self.manipulator_meta:
            self.manipulator_meta[self.i] = {}

        self.manipulator_meta[self.i][name] = {
            'gripper': self.gripper.STATUS,
            'arm_tcp': self.arm.TCP_POSE_DATA,
            'arm_wrench': self.arm.WRENCH_DATA,
            'arm_joints': self.arm.JOINTS_STATE
        }

        self.memory['manipulator_meta'] = self.manipulator_meta

    def save_moment(self, name):
        self.save_camera(name)
        self.save_manipulator(name)

    async def after_init(self):
        print('Moving start position...')
        await self.arm.move_abs(Positions.start())

        print('Activating Gripper.')
        await self.gripper.reset()
        await self.gripper.open()

        print('Activation done.')

    def percent_2_centered_coords(self, xp, yp):
        xx = 0.22
        yy = 0.42

        x = (xp - 0.5) * xx
        y = (yp - 0.5) * yy
        return x, y

    def shift_p(self, pose, x, y, z=0, angle=0):
        pose[0] += x
        pose[1] += y
        pose[2] += z
        pose[5] += angle
        return pose

    async def flush_objects(self):
        await ensure(self.arm.move_abs, Positions.start(), speed=0.7)

        await self.arm.move_abs(Positions.gate_high())
        await self.gripper.open()

        await self.arm.move_abs(Positions.gate_low(), speed=0.1)
        await self.gripper.close()
        await self.arm.move_abs(Positions.gate_high(), speed=0.1)
        await asyncio.sleep(3)
        await self.arm.move_abs(Positions.gate_low(), speed=0.1)

        await self.gripper.open()
        await self.arm.move_abs(Positions.gate_high(), speed=0.5)

        await ensure(self.arm.move_abs, Positions.start(), speed=0.7)

    async def drop_object(self):
        await ensure(self.arm.move_abs, Positions.start())

        # await self.arm.move_abs(Positions.drop_entrance())
        await ensure(self.arm.move_abs, Positions.drop_final(), speed=0.7)
        await self.gripper.open()

        await ensure(self.arm.move_abs, Positions.start(), speed=0.7)

        # await self.arm.move_abs(Positions.drop_entrance())

    async def try_one_grasp(self):
        await ensure(self.arm.move_abs, Positions.start())
        await self.gripper.open()

        self.save_moment('before')

        x, y, alpha, beta = self.sample_vision_based()
        print('Sampled', (x, y, alpha, beta))

        angle = alpha * pi - (pi / 2)
        amplitude = 0.5 + random() * 0.3
        self.save_grasp((x, y, alpha, beta))

        await self.gripper.set_opening(amplitude)

        if await self.arm.move_abs(self.shift_p(Positions.pre_down(), x, y, angle=angle)) == 'DONE':
            res = await self.arm.move_abs(self.shift_p(Positions.down(), x, y, angle=angle), speed=0.05)
            self.save_moment('during')
            if res == 'DONE':
                await self.gripper.close(speed=0)
                return True
        else:
            print('Interrupted.')
            await asyncio.sleep(2)
            self.save_moment('during')
            return False

    async def swipe_box(self, frx=None, fry=None):
        await self.arm.move_abs(Positions.start())
        await self.gripper.close()

        rx = frx if (frx is not None) else round(random())
        ry = fry if (fry is not None) else round(random())

        sx = abs(rx - 0.1)
        sy = abs(ry - 0.1)
        ex = abs(1 - rx - 0.3)
        ey = abs(1 - ry - 0.3)

        hsx = 1.11 if sx > 0.5 else -0.11
        hsy = 1.11 if sy > 0.5 else -0.11

        await self.arm.move_abs(
            self.shift_p(Positions.pre_down(), *self.percent_2_centered_coords(hsx, hsy), angle=-pi / 2, z=0.05))

        if await self.arm.move_abs(
                self.shift_p(Positions.down(), *self.percent_2_centered_coords(sx, sy), angle=-pi / 2),
                speed=0.2) == 'DONE':
            self.gripper.open()
            await self.arm.move_abs(
                self.shift_p(Positions.down(), *self.percent_2_centered_coords(ex, ey), angle=pi / 2))
            await self.arm.move_abs(
                self.shift_p(Positions.pre_down(), *self.percent_2_centered_coords(ex, ey), angle=pi / 2))

        await self.arm.move_abs(Positions.start())

    def sample_random_grasp(self):
        xx = 7
        yy = 14

        x = random() * 2 * xx - xx
        y = random() * 2 * yy - yy
        angle = random() * pi - (pi / 2)

        return x, y, angle

    def sample_vision_based(self):
        frame = self.camera.left()
        frame = cv2.warpPerspective(frame, self.h, (192, 108))
        f_h, f_w, _ = np.shape(frame)
        frame = img_as_float(frame)

        img_segments = segmentation.slic(frame, compactness=50, n_segments=40, max_iter=10, max_size_factor=10)
        frame1 = color.label2rgb(img_segments, frame, kind='avg')

        for i in range(100):
            mask = np.zeros((108, 192))
            mask[img_segments == int(random() * np.max(img_segments))] = 255

            M = cv2.moments(mask)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            value = cv2.cvtColor(np.array([[frame1[cY, cX, :] * 255]]).astype(np.uint8), cv2.COLOR_RGB2HSV)[0, 0, 2]
            if value < 90 or value > 115:
                break
            print('v', value)
        # cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)

        # disp = np.concatenate((frame1, frame), axis=1)
        # self.ui.show(disp)

        # cv2.imwrite('frame.jpg', disp)

        x, y = self.percent_2_centered_coords(cY / f_h, cX / f_w)
        alpha = random()
        beta = random()

        return x, y, alpha, beta

    async def action(self):
        if self.h is not None:
            self.i += 1
            self.save_meta()

            # :::::::::::: COLLECT SAMPLE ::::::::::::
            successful = await self.try_one_grasp()
            await ensure(self.arm.move_abs, Positions.start())
            await asyncio.sleep(0.3)
            self.save_moment('after')
            if successful:
                opening = self.gripper.get_opening()
                self.save_true_amplitude(opening)
                if self.gripper.get_opening() > 0.05:
                    await self.drop_object()
                    self.successful_grasps += 1
                else:
                    self.unsuccessful_grasps += 1
            else:
                self.failed_attempts += 1

            # :::::::::::: BIN MANAGMENT :::::::::::::
            if self.successful_grasps >= self.refresh_after:
                await self.flush_objects()
                self.successful_grasps = 0
                self.unsuccessful_grasps = 0
                self.failed_attempts = 0
                # await self.swipe_box(0, 0)

            elif self.i % self.swipe_every == 0:
                await self.swipe_box()

            print('============== STATS ==============')
            tp = self.successful_grasps
            all = self.successful_grasps + self.unsuccessful_grasps + self.failed_attempts
            success_rate = 0 if all == 0 else tp / all
            print(success_rate)
            print('============== END S ==============')


        else:
            self.ui.show(self.camera.left())

            if len(self.ui.selected_points) > 3:
                self.ui.show(self.camera.left())

                h, status = cv2.findHomography(np.array(self.ui.selected_points),
                                               np.array([(0, 0), (192, 0), (192, 108), (0, 108)]))
                self.h = h
                self.save_homography(self.h)
                self.ui.close()
