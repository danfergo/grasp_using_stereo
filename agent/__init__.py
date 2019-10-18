from narnia.core import Module
from .behaviours.data_collector import DataCollector


@Module(
    bootstrap=DataCollector
)
class AgentModule:
    pass
