import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    description_share = get_package_share_directory("sentinel_description")
    default_model = os.path.join(description_share, "urdf", "sentinel_rover.urdf.xacro")

    return LaunchDescription(
        [
            DeclareLaunchArgument("model", default_value=default_model),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": Command(["xacro ", LaunchConfiguration("model")])}],
                output="screen",
            ),
            Node(package="joint_state_publisher_gui", executable="joint_state_publisher_gui"),
            Node(package="rviz2", executable="rviz2", output="screen"),
        ]
    )

