class DataCollector:

    def __init__(self, injector):
        self.gripper = injector.get()

    async def action(self):
        await self.arm.move(self.positions.start())
        self.gripper.open()
        if await self.arm.move(self.chance.sample()):
            await self.gripper.close()

