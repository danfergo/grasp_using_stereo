from narnia.core import Narnia, print_ros_topics
from agent.agent_md import AgentModule

print_ros_topics()

Narnia.bootstrap(AgentModule)
