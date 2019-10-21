from narnia.core import Narnia
from agent.agent_md import AgentModule

Narnia.bootstrap(AgentModule)

# from agent.drivers.gripper import GripperDriver

# import time

# gripper = GripperDriver()
#
# time.sleep(1)
# gripper.reset()
#
# time.sleep(1)
# gripper.activate()
# time.sleep(1)
# gripper.open()

# while True:
#     gripper.close()
#     time.sleep(1)
#     gripper.open()
#     time.sleep(1)




# import cv2
# import time
#
# from agent.drivers.zed_camera import ZEDCamera
# from agent.drivers.gripper import Gripper
# from agent.drivers.arm import Arm
#
# from narnia.core.drivers.ros_actuator import print_ros_topics

# print_ros_topics()

# from math import pi


# DETECT_POS = [0.4, 0, 0.4, pi, 0, -pi / 4 + pi]
# START_POS = [0.52, 0, 0.3, pi, 0, -pi / 4 + pi]

# gripper = Gripper()
# arm = Arm()
#
# gripper.reset()
# gripper.activate()
# gripper.open()
#
# time.sleep(2)
# time.sleep(2)
#
# time.sleep(2)
# gripper.close()
#


# move start

# forever
# sample a random point
# move to that random point

# def when(x):
#     pass

#
# @when(lambda self: self.goal == self.current)
# def y():
#     pass
#
#
# def move_arm():
#     counter = 0
#     counter += 1
#     yield counter
#
#
# def state_machine():
#     while True:
#         yield move_arm()
#
#
# for num in state_machine():
#     print(num)

# while True:
#
#     arm.move_abs(DETECT_POS)
#     time.sleep(10)
#     arm.move_abs(START_POS)
#     time.sleep(10)
# time.sleep(1)

# arm.move_abs2()

# time.sleep(1)
# gripper.reset()
#
# time.sleep(1)
# gripper.activate()
# time.sleep(1)
# gripper.open()

# while True:
#     gripper.close()
#     time.sleep(1)
#     gripper.open()
#     time.sleep(1)

# cam = ZEDCamera()
#
# while True:
#     img = cam.get_frame()
#     i = cam.read()
#     # if img is not None:
#     cv2.imshow('frame', i)
#     cv2.waitKey(1)
#     # time.sleep(1)

# from narnia.core import Module
# from narnia.core.controllers import Actuator


# from agent.behaviours.data_collector import DataCollector
#
# @Module(
#     behaviours=[
#
#     ],
# )
# class Agent:
#     pass
#
#
#     def xx():
# @Agent({
#
# })
# def Agent:
#
#
#     def xx():
