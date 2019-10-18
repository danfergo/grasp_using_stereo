from narnia.core import ROSActuator, ROSTopicPublisher


class Gripper(ROSActuator):
    def __init__(self):
        print('Initializing gripper...')

        self.current_command = None
        self.STATUS = None
        self.publisher = None
        self.cmd = {}
        super().__init__()

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

    @ROSTopicPublisher('/Robotiq2FGripperRobotOutput')
    def send_cmd(self, msg):
        self.cmd = {**self.cmd, **msg}
        return self.cmd

    def reset(self):
            self.cmd = {}
        self.send_cmd({'rACT': 0})

    def activate(self):
        self.cmd = {}
        self.send_cmd({
            'rACT': 1,
            'rGTO': 1,
            'rSP': 255,
            'rFR': 150
        })

    def open(self):
        self.send_cmd({'rPR': 0})

    def close(self):
        self.send_cmd({'rPR': 255})

    def set_opening(self, angle):
        self.send_cmd({'rPRA': int(min(max(0, angle), 1) * 255)})

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
