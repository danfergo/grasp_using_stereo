from functools import partial

from narnia.core import ROSActuator, ROSTopicPublisher, Driver, ROSTopicSubscriber, RequestAction

from math import pi, sqrt

import time

import asyncio

NET_LATENCY = 0.5

@Driver()
class ArmDriver(ROSActuator):

    def __init__(self):
        self.loop = asyncio.get_event_loop()

        self.JOINTS_STATE = None
        self.WRENCH_DATA = None
        self.TCP_POSE_DATA = None

        self.ur_script = None

        self.future = None
        self.future_condition = None

        super().__init__()

    def stopped(self):
        return self.JOINTS_STATE['velocity'] is not None and sum(
            [abs(x) for x in self.JOINTS_STATE['velocity']]) < 0.001

    def at_position(self, pos):
        if self.TCP_POSE_DATA is None:
            return False

        p = self.TCP_POSE_DATA['position']
        d = abs(sqrt((p['x'] - pos[0]) ** 2 + (p['y'] - pos[1]) ** 2 + (p['z'] - pos[2]) ** 2) - 0.174)
        return d < 0.003

    @ROSTopicSubscriber('/joint_states')
    def on_joint_states(self, joint_states):
        self.JOINTS_STATE = joint_states

    @ROSTopicSubscriber('/tcp_position')
    def on_data(self, data):
        self.TCP_POSE_DATA = data

    @ROSTopicSubscriber('/wrench')
    def on_wrench(self, wrench_data):
        self.WRENCH_DATA = wrench_data

    @ROSTopicPublisher('/ur_driver/URScript')
    def exec(self, script):
        return {'data': script}

    def move_abs(self, pose, speed=1.0):
        pose = [round(p, 2) for p in pose] + [round(-pi / 2 - pi / 4, 2)]
        move_cmd = """
def cmd():        
global abs_pos = [{}, {}, {}]
global abs_ori = rpy2rotvec([{}, {}, {}])
global abs_pose = p[abs_pos[0], abs_pos[1], abs_pos[2], abs_ori[0], abs_ori[1], abs_ori[2]]
global corrected_frame = p[0, 0, 0, 0, 0, {}]
global corrected_pose = pose_trans(corrected_frame, abs_pose)
movel(corrected_pose, a={}, v={})
end"""
        self.exec(move_cmd.format(*(pose + [0.3 * speed, 0.5 * speed])))
        return RequestAction(self, lambda ts, t: t - ts > NET_LATENCY and self.at_position(pose) and self.stopped())

    def move_rel(self, pose):
        pose = [round(p, 2) for p in pose]

        move_cmd = """
def cmd():
global pos = [{}, {}, {}]
global ori = rpy2rotvec([{}, {}, {}])
global pose_wrt_tool = p[pos[0], pos[1], pos[2], ori[0], ori[1], ori[2]]
global pose_wrt_base = pose_trans(get_forward_kin(), pose_wrt_tool)
movel(pose_wrt_base, a=0.3, v=0.05)
end"""
        self.exec(move_cmd.format(*pose))
        return RequestAction(self, lambda ts, t: t - ts > NET_LATENCY and self.stopped())

    def stop(self):
        move_cmd = """
def cmd():        
speedj([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 2)
end"""
        self.exec(move_cmd)
        return RequestAction(self, lambda ts, t: t - ts > NET_LATENCY and self.stopped())

    def tcp_force(self):
        return self.WRENCH_DATA['wrench']['force'] if self.WRENCH_DATA is not None else None

    def tcp_position(self):
        pose = self.TCP_POSE_DATA['position']
        return pose['x'], pose['y'], pose['z']

