import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_share = get_package_share_directory("sentinel_bringup")
    description_share = get_package_share_directory("sentinel_description")
    model = os.path.join(description_share, "urdf", "sentinel_rover.urdf.xacro")
    slam_params = os.path.join(bringup_share, "config", "slam_toolbox.yaml")
    nav2_params = os.path.join(bringup_share, "config", "nav2.yaml")
    ekf_params = os.path.join(bringup_share, "config", "ekf.yaml")
    tools_launch = os.path.join(
        get_package_share_directory("sentinel_autonomy"),
        "launch",
        "autonomy_tools.launch.py",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("explore", default_value="false"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": Command(["xacro ", model])}],
                output="screen",
            ),
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_filter_node",
                parameters=[ekf_params],
                output="screen",
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("slam_toolbox"),
                        "launch",
                        "online_async_launch.py",
                    )
                ),
                launch_arguments={"slam_params_file": slam_params, "use_sim_time": "false"}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        get_package_share_directory("nav2_bringup"),
                        "launch",
                        "navigation_launch.py",
                    )
                ),
                launch_arguments={"params_file": nav2_params, "use_sim_time": "false"}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(tools_launch),
                launch_arguments={"explore": LaunchConfiguration("explore")}.items(),
            ),
        ]
    )
