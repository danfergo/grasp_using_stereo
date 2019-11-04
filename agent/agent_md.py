from narnia.core import Module

from agent.drivers.ui import UIDriver
from .drivers.arm import ArmDriver
from .drivers.gripper import GripperDriver
from .drivers.zed_camera import ZEDCameraDriver

from .behaviours.data_collection_bh import DataCollectionBehaviour
from .behaviours.arm_survival_bh import ArmSurvival


@Module(
    drivers=[
        ArmDriver,
        GripperDriver,
        ZEDCameraDriver,
        UIDriver
    ],
    behaviours=[
        DataCollectionBehaviour,
        ArmSurvival
    ],
    bootstrap=ArmSurvival
)
class AgentModule:
    pass
