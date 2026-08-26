# Sentinel SLAM Rover

Original ROS 2 workspace for a differential-drive robot that can map, localize, navigate, and explore indoor spaces with a 2D LiDAR and IMU.

This project is intentionally structured as a clean-room implementation. It targets the same robotics problem as common SLAM rover projects, but uses its own package names, launch orchestration, robot model, autonomy nodes, parameters, and documentation.

## What is included

- Gazebo-ready differential-drive robot model built from simple xacro geometry
- SLAM Toolbox configuration for online asynchronous mapping
- Nav2 configuration for autonomous path planning and obstacle avoidance
- frontier-based exploration node that sends Nav2 goals into unknown space
- velocity safety supervisor that filters unsafe commands using LiDAR ranges
- map quality monitor that reports explored, free, occupied, and unknown map ratios
- scan watchdog for basic LiDAR health monitoring
- simulation and full-stack launch files

## Packages

```text
sentinel_slam_ws/
└── src/
    ├── sentinel_description/   # robot model, world, visualisation launch
    ├── sentinel_autonomy/      # exploration, safety, and monitoring nodes
    └── sentinel_bringup/       # integrated SLAM/Nav2/simulation launch configs
```

## Quick start

```bash
cd sentinel_slam_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch sentinel_bringup sim_slam_nav.launch.py
```

Start autonomous exploration in a second terminal:

```bash
source sentinel_slam_ws/install/setup.bash
ros2 launch sentinel_autonomy autonomy_tools.launch.py explore:=true
```

## Why this is stronger

- clear separation between robot description, autonomy logic, and system bringup
- no dependency on custom mesh files for the base robot model
- safety supervisor can sit between manual/autonomy commands and `/cmd_vel`
- exploration and map-quality monitoring provide visible progress metrics
- configs are grouped in one bringup package for easier deployment

## Hardware assumptions

- ROS 2 Humble or newer
- differential-drive base
- 2D laser scanner publishing `sensor_msgs/LaserScan`
- optional IMU publishing `sensor_msgs/Imu`
- Nav2 and SLAM Toolbox installed

