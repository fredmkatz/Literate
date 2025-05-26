from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB

# with Diagram("Grouped Workers", show=False, direction="TB"):
#     ELB("lb") >> [EC2("worker1"),
#                   EC2("worker2"),
#                   EC2("worker3"),
#                   EC2("worker4"),
#                   EC2("worker5")] >> RDS("events")


from diagrams import Diagram, Cluster
from diagrams.programming.language import Python

with Diagram("Python Dataclass Model", show=True):
    with Cluster("dataclasses"):
        dataclass_decorator = Python("@dataclass")
        field_function = Python("field()")
        dataclass_class = Python("Dataclass")

        dataclass_decorator >> dataclass_class
        field_function >> dataclass_class

    with Cluster("User Defined Classes"):
        user_class = Python("MyClass")
        user_instance = Python("MyClass()")

        dataclass_class >> user_class
        user_class >> user_instance