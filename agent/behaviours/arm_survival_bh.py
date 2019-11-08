import asyncio

from narnia.core import Behaviour

from agent.behaviours.data_collection_bh import DataCollectionBehaviour
from agent.drivers.arm import ArmDriver

from math import sqrt

from agent.drivers.gripper import GripperDriver

import asyncio
import numpy as np


def magnitude(v):
    return sqrt(sum([vv ** 2 for vv in v]))


@Behaviour()
class ArmSurvival:
    arm: ArmDriver
    gripper: GripperDriver

    data_collection: DataCollectionBehaviour

    def __init__(self):
        self.collision_threshold = 30
        self.collection = None

    async def action(self):
        if self.arm_in_collision():
            await self.arm.stop()
            await self.arm.move_rel([0, 0, -0.025, 0, 0, 0])

            force = self.arm.tcp_force()
            m = magnitude(force)
            opposite = [0, 0, 0] if m == 0 else np.round((np.array(force) / m) * -0.02, decimals=3).tolist()
            await self.arm.move_rel(opposite + [0, 0, 0])

        else:

            if self.collection is None or self.collection.done():
                loop = asyncio.get_event_loop()
                self.collection = loop.create_task(self.data_collection.action())

    def arm_in_collision(self):
        tcp_force = self.arm.tcp_force()
        return tcp_force is not None and magnitude(tcp_force) > self.collision_threshold and \
               tcp_force['z'] > self.collision_threshold
               # and self.arm.tcp_position()[2] < 0.35
