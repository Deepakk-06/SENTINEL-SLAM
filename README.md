# SENTINEL-SLAM

Autonomous SLAM robot with real-time monocular depth vision.

Built on a 3D-printed TurtleBot chassis running ROS2, this project combines real-time
SLAM-based mapping and localization with a separate, real-time monocular depth
estimation pipeline — giving the robot both a live map of its environment and a
sense of depth from a single standard webcam, no LiDAR or stereo rig required for
the vision component.

## What it does

- **Autonomous mapping & localization** — uses `slam_toolbox` on ROS2 to build a
  live occupancy grid map as the robot explores an environment, with real-time
  pose tracking and loop closure, visualized in RViz.
- **Real-time monocular depth estimation** — runs Depth Anything V2
  on a live camera feed to generate per-pixel relative depth, rendered as a color-mapped
  overlay in real time (~35-40 FPS).
- **Manual teleoperation** — drive the robot directly via keyboard using `key_teleop`.

## Architecture

Compute is split across two devices to work around the Raspberry Pi's limited
horsepower for running a depth model:

Raspberry Pi (camera capture, ROS2 stack, slam_toolbox, motor control)
        |
        |  Flask video stream (http://<pi-ip>:5000/video)
        v
Host Machine / Mac (Depth Anything V2, runs on GPU/MPS, live HUD overlay)

The Pi handles robot control, SLAM, and camera streaming. Depth inference runs
on a separate machine with GPU acceleration, pulling frames from the Pi over the
local network, so depth estimation runs at real-time speed without being bottlenecked
by the Pi's onboard compute.

## Tech stack

- **Robot / SLAM**: ROS2, slam_toolbox, RViz, key_teleop
- **Depth vision**: Depth Anything V2 (small model), PyTorch, Hugging Face transformers, OpenCV
- **Streaming**: Flask (camera feed served from the Pi)
- **Hardware**: 3D-printed TurtleBot chassis, Raspberry Pi, standard USB webcam

## Running it

On the Raspberry Pi — start the camera stream:

    source ~/depth_env/bin/activate
    python3 pi_stream.py

On the host machine — run the depth vision HUD (point it at the Pi's stream URL):

    source ~/depth_env/bin/activate
    python3 depth_mac_final.py

For SLAM mapping (on the Pi, in a separate terminal):

    source ~/sentinel_slam_ws/install/setup.bash
    ros2 launch sentinel_bringup sim_slam_nav.launch.py

For manual driving:

    ros2 run key_teleop key_teleop

## Status

Actively being extended — next up is ArUco marker-based relocalization, so the
robot can re-establish its position on the map after losing tracking.

## Notes

Depth Anything V2 produces relative depth (not calibrated real-world distance),
so depth values are useful for comparison/thresholding within a scene but should
not be treated as precise metric measurements.
