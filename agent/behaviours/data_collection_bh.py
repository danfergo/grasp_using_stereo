from narnia.core import Behaviour

from .arm_bh import ArmBehaviour
from ..constants.positions import Positions
from ..drivers.gripper import GripperDriver

import time

@Behaviour()
class DataCollectionBehaviour:
    arm: ArmBehaviour
    gripper: GripperDriver

    async def after_init(self):
        print('================ >Gripper Active.?????')
        await self.gripper.activate()
        print('================ >Gripper Active.')

    def sample_random_grasp(self):
        pass

    async def action(self):
        time.sleep(1)
        # await self.arm.move(Positions.start())
        # await self.gripper.open()
        # while True:
        #     print(future, '->')
        #     time.sleep(0.1)
        #
        #     future.done()

        # print('returned')
        # await self.gripper.close()

        # print('.m')
        # # if await self.arm.move(self.sample_random_grasp()):
        # await self.gripper.close()
        # print('.')
