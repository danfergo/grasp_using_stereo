from narnia.core import ROSActuator, ROSTopicPublisher

from math import pi, sqrt

import time
import roslibpy


def magnitude(v):
    return sqrt(v['x'] ** 2 + v['y'] ** 2 + v['z'] ** 2)


class Arm(ROSActuator):
    def __init__(self):
        self.collision_threshold = 30
        print('Initializing arm...')
        self.JOINTS_STATE = None
        self.WRENCH_DATA = None
        self.ur_script = None
        super().__init__()

    def after_init(self):
        pass
        # self.ur_script = roslibpy.Topic(self.ros_client, '/ur_driver/URScript', 'std_msgs/String')
        #
        # def _wrench(data):
        #     self.WRENCH_DATA = data
        #
        # roslibpy.Topic(self.ros_client, '/wrench', 'geometry_msgs/WrenchStamped').subscribe(_wrench)
        #
        # def _joint_states(data):
        #     self.JOINTS_STATE = data
        #
        # roslibpy.Topic(self.ros_client, "/joint_states", 'sensor_msgs/JointState').subscribe(_joint_states)
        #
        # time.sleep(0.5)
        # print('Arm ready.')

    @ROSTopicPublisher('/ur_driver/URScript')
    def exec(self, script):
        return {'data': script}

    def move_abs(self, pose):
        pose = [round(p, 2) for p in pose]
        move_cmd = """
def cmd():        
global abs_pos = [{}, {}, {}]
global abs_ori = rpy2rotvec([{}, {}, {}])
global abs_pose = p[abs_pos[0], abs_pos[1], abs_pos[2], abs_ori[0], abs_ori[1], abs_ori[2]]
global corrected_frame = p[0, 0, 0, 0, 0, {}]
global corrected_pose = pose_trans(corrected_frame, abs_pose)
movep(corrected_pose, a=1, v=0.09)
end"""
        print('>>>>>>>>>', (pose + [-pi / 2 - pi / 4]))
        self.exec(move_cmd.format(*(pose + [round(-pi / 2 - pi / 4, 2)])))
        time.sleep(2)

    def move_rel(self, pose):
        pose = [round(p, 2) for p in pose]

        move_cmd = """
def cmd():
global pos = [{}, {}, {}]
global ori = rpy2rotvec([{}, {}, {}])
global pose_wrt_tool = p[pos[0], pos[1], pos[2], ori[0], ori[1], ori[2]]
global pose_wrt_base = pose_trans(get_forward_kin(), pose_wrt_tool)
movel(pose_wrt_base, a=0.5, v=0.01)
end"""
        cmd = move_cmd.format(*pose)
        self.ur_script.publish(roslibpy.Message({'data': cmd}))
        time.sleep(0.5)

    def stop(self):

        move_cmd = """
def cmd():        
speedj([0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 2)
end"""
        cmd = move_cmd
        self.ur_script.publish(roslibpy.Message({'data': cmd}))

    def push(self, command):
        if isinstance(command, tuple) and command[0] == 'rel':
            self.move_rel(command[1])
        elif command == 'stop':
            self.stop()
        else:
            self.move_abs(command)

    def pull(self):
        return {
            'joints_velocity': self.JOINTS_STATE['velocity'] if self.JOINTS_STATE is not None else None,
            'wrench': self.WRENCH_DATA['wrench'] if (
                    self.WRENCH_DATA is not None and time.time() - self.WRENCH_DATA['header']['stamp'][
                'secs'] < 1) else None
        }

    def collision(self):
        f = self.WRENCH_DATA['wrench']['force']
        return magnitude(f) > self.collision_threshold and f['z'] > self.collision_threshold

    def moving(self):
        return sum([abs(x) for x in self.JOINTS_STATE['velocity']]) > 0.001

    def waits_stops(self):
        while self.moving() and not self.collision():
            time.sleep(0.01)

        if self.collision():
            self.stop()
            time.sleep(0.2)
            self.move_rel([0, 0, -0.01, 0, 0, 0])

            self.waits_stops()
            return False
        return True
