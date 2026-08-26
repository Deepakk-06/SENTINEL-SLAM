import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory("sentinel_description")
    default_model = os.path.join(description_share, "urdf", "sentinel_rover.urdf.xacro")
    default_world = os.path.join(description_share, "worlds", "indoor_lab.world")
    robot_description = Command(["xacro ", LaunchConfiguration("model")])

    return LaunchDescription(
        [
            DeclareLaunchArgument("model", default_value=default_model),
            DeclareLaunchArgument("world", default_value=default_world),
            ExecuteProcess(
                cmd=["gazebo", "--verbose", LaunchConfiguration("world"), "-s", "libgazebo_ros_factory.so"],
                output="screen",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description, "use_sim_time": True}],
                output="screen",
            ),
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                arguments=["-topic", "robot_description", "-entity", "sentinel_rover", "-x", "0", "-y", "0", "-z", "0.05"],
                output="screen",
            ),
        ]
    )

