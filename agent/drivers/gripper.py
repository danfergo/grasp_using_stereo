from narnia.core import ROSActuator, ROSTopicPublisher, ROSTopicSubscriber, Driver
from functools import partial

from asyncio import Future
import asyncio

import time

loop = asyncio.get_event_loop()


@Driver()
class GripperDriver(ROSActuator):
    def __init__(self):
        print('Initializing gripper...')

        self.current_command = None
        self.state = None
        self.STATUS = None
        self.GOAL = None
        self.publisher = None
        self.cmd = {}
        self.future = None
        self.future_condition = None
        super().__init__()

    async def perceive(self):
        print('Passed')
        if self.future is not None and not self.future.done() and self.future_condition(time.time()):
            print('1 hello')
            self.future.set_result('DONE')
        print('1 hello')
        # print('Perceive gripper')

    def after_init(self):
        # self.publisher = roslibpy.Topic(self.ros_client, '/Robotiq3FGripperRobotOutput',
        #                                 'robotiq_3f_gripper_articulated_msgs/Robotiq3FGripperRobotOutput')
        #
        # def _status(data):
        #     # print('SELF STATUS', data)
        #     self.STATUS = data
        #
        # roslibpy.Topic(self.ros_client, '/Robotiq3FGripperRobotInput',
        #                'robotiq_3f_gripper_articulated_msgs/Robotiq3FGripperRobotInput') \
        #     .subscribe(_status)

        print('Gripper ready.')

    def set_future(self, cond):
        if self.future and not self.future.done():
            self.future.set_result('Interrupted')
        self.future = loop.create_future()
        self.future_condition = partial(cond, time.time())
        return self.future

    @ROSTopicPublisher('/Robotiq2FGripperRobotOutput')
    def send_cmd(self, msg):
        self.cmd = {**self.cmd, **msg}
        # print('Publish ?', self.cmd)
        return self.cmd

    @ROSTopicSubscriber('/Robotiq2FGripperRobotInput')
    def on_status(self, status):
        # print(time.time() - self.future_timestamp)
        self.STATUS = status


    def reset(self):
        self.cmd = {}
        self.send_cmd({'rACT': 0})
        return self.set_future(lambda ts, t: t - ts > 1000)

    async def activate(self):
        self.cmd = {}
        self.send_cmd({
            'rACT': 1,
            'rGTO': 1,
            'rSP': 255,
            'rFR': 150
        })
        print('ret')
#        lambda ts, t: self.STATUS['gSTA'] == 3 and self.STATUS['gACT'] == 1)
        x = await self.set_future(lambda x: print(self.STATUS))
        print('>>> ', x)

    def open(self):
        self.send_cmd({'rPR': 0})
        return self.set_future(lambda ts, t: True)

    def close(self):
        self.send_cmd({'rPR': 255})
        return self.set_future(lambda ts, t: True)

    def set_opening(self, angle):
        self.send_cmd({'rPRA': int(min(max(0, angle), 1) * 255)})
        return self.set_future(lambda ts, t: True)

    #
    # def set_pinch(self, force=None):
    #     self.current_command['rMOD'] = 1
    #     if force is not None:
    #         self.current_command['rFRA'] = int(force * 255)
    #     self.send_command(self.current_command)
    #
    # def set_finger_control(self):
    #     self.current_command.rICF = 1
    #     self.current_command.rICS = 1
    #     self.send_command(self.current_command)
    #
    # def set_fingers(self, a, b, c, s):
    #     self.current_command.rPRA = min(max(0, a), 255)
    #     self.current_command.rPRB = min(max(0, b), 255)
    #     self.current_command.rPRC = min(max(0, c), 255)
    #     self.current_command.rPRS = min(max(0, s), 255)
    #     self.send_command(self.current_command)
    #
    # def send_command(self, command):
    #     self.publisher.publish(command)
    #     # print('Sending message...')
    #     time.sleep(0.1)
    #
    # def stop(self):
    #     command = roslibpy.Message()
    #     command.rGTO = 0
    #     command.rATR = 0
    #     self.current_command.rMOD = 1
    #     self.send_command(command)
    #     self.current_command = command
    #
    # def reactivate(self):
    #     if self.STATUS.gACT == 0:
    #         self.activate()
    #         return True
    #     return False
    #
    # def push(self, command):
    #     if command == 'reset':
    #         self.reset()
    #     elif command == 'activate':
    #         self.activate()
    #     elif command == 'pinch':
    #         self.set_pinch()
    #     elif command == 'open':
    #         self.open()
    #     else:
    #         # print(command)
    #         self.set_angle(command)
    #
    # def pull(self):
    #     pass
    #
    # def wait_ready(self):
    #     time.sleep(0.1)
    #
    #     def working():
    #         if self.STATUS['gGTO'] == 1 and self.STATUS['gSTA'] == 0:
    #             return False
    #
    #         if self.STATUS['gIMC'] == 1 or self.STATUS['gIMC'] == 2:
    #             return True
    #
    #         return not (self.STATUS['gIMC'] == 0 or self.STATUS['gIMC'] == 3)
    #
    #     while working():
    #         time.sleep(0.1)
