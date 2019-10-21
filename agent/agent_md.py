from narnia.core import Module

from .drivers.arm import ArmDriver
from .drivers.gripper import GripperDriver
from .drivers.zed_camera import ZEDCameraDriver

from .behaviours.data_collection_bh import DataCollectionBehaviour
from .behaviours.arm_bh import ArmBehaviour


@Module(
    drivers=[
        ArmDriver,
        GripperDriver,
        ZEDCameraDriver
    ],
    behaviours=[
        DataCollectionBehaviour,
        ArmBehaviour
    ],
    bootstrap=DataCollectionBehaviour
)
class AgentModule:
    pass
