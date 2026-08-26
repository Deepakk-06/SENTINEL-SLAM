from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    explore = LaunchConfiguration("explore")

    return LaunchDescription(
        [
            DeclareLaunchArgument("explore", default_value="false"),
            Node(
                package="sentinel_autonomy",
                executable="velocity_guard",
                name="velocity_guard",
                output="screen",
            ),
            Node(
                package="sentinel_autonomy",
                executable="scan_watchdog",
                name="scan_watchdog",
                output="screen",
            ),
            Node(
                package="sentinel_autonomy",
                executable="map_quality_monitor",
                name="map_quality_monitor",
                output="screen",
            ),
            Node(
                package="sentinel_autonomy",
                executable="frontier_explorer",
                name="frontier_explorer",
                output="screen",
                condition=IfCondition(explore),
            ),
        ]
    )

