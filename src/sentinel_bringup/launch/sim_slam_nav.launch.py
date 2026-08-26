import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_share = get_package_share_directory("sentinel_bringup")
    description_share = get_package_share_directory("sentinel_description")
    slam_params = os.path.join(bringup_share, "config", "slam_toolbox.yaml")
    nav2_params = os.path.join(bringup_share, "config", "nav2.yaml")
    world = os.path.join(description_share, "worlds", "indoor_lab.world")

    sim_launch = os.path.join(description_share, "launch", "sim_world.launch.py")
    slam_launch = os.path.join(
        get_package_share_directory("slam_toolbox"),
        "launch",
        "online_async_launch.py",
    )
    nav2_launch = os.path.join(
        get_package_share_directory("nav2_bringup"),
        "launch",
        "navigation_launch.py",
    )
    tools_launch = os.path.join(
        get_package_share_directory("sentinel_autonomy"),
        "launch",
        "autonomy_tools.launch.py",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("explore", default_value="false"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(sim_launch),
                launch_arguments={"world": world}.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(slam_launch),
                launch_arguments={
                    "use_sim_time": LaunchConfiguration("use_sim_time"),
                    "slam_params_file": slam_params,
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(nav2_launch),
                launch_arguments={
                    "use_sim_time": LaunchConfiguration("use_sim_time"),
                    "params_file": nav2_params,
                }.items(),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(tools_launch),
                launch_arguments={"explore": LaunchConfiguration("explore")}.items(),
            ),
        ]
    )

