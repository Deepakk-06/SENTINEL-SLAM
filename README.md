# 🕷️ SENTINEL-SLAM

**A LiDAR-mapping robot that also sees depth through a plain webcam — no LiDAR needed for that part.**

Most SLAM robots stop at "here's the map." This one also runs a real-time
monocular depth estimation pipeline alongside the mapping stack, and can
find its way back home using ArUco markers if it ever loses track of where
it is. Built, broken, and rebuilt with a small team over way too many late
nights debugging a fried WiFi chip.

## Why this exists

We wanted a robot that didn't just map a room — it should *understand* how
far things are, live, from a single cheap camera. Stereo rigs and depth
cameras are expensive and finicky. So instead: LiDAR handles the mapping,
and a separate depth model (Depth Anything V2) running on a beefier machine
handles per-pixel depth in real time, streamed live off the robot.

## What it actually does

- 🗺️ **Live SLAM + navigation** — `slam_toolbox` + Nav2 build and update an
  occupancy grid as the robot explores, with loop closure and autonomous
  exploration, all watchable in RViz.
- 🎯 **IMU sensor fusion** — the map used to warp because of how the LiDAR
  was mounted. Fixed it by fusing IMU data in.
- 👁️ **Real-time monocular depth** — Depth Anything V2 chews on a live
  camera feed and spits out a color-mapped depth overlay at ~35-40 FPS,
  running on a GPU/MPS host so the Pi doesn't choke.
- 📍 **ArUco relocalization** — lose tracking, spot a marker, and the robot
  re-anchors itself on the map instead of just being lost forever.
- 🎮 **Manual override** — drive it straight from the keyboard when you just
  want to mess around.

## How it's wired together

The Raspberry Pi is the workhorse for control — camera capture, the full
ROS2 stack, SLAM, Nav2, motors. But depth models are hungry, and the Pi
just doesn't have the muscle for real-time inference. So the camera feed
gets streamed off the Pi over Flask, and a separate host machine with a
real GPU does the depth math and renders the HUD.

    Raspberry Pi  --(Flask video stream)-->  Host Machine
    camera, ROS2, SLAM,   http://<pi-ip>:5000/video   Depth Anything V2,
    Nav2, motor control                               GPU/MPS, live HUD

## Hardware Components

| Component | Purpose |
|---|---|
| Raspberry Pi 4 | Onboard compute, ROS 2 nodes, motor control |
| 2D LiDAR | Environment scanning for SLAM |
| MPU6050 IMU | Orientation feedback, sensor fusion |
| Zebronics Webcam | Camera feed for monocular depth estimation |
| 25GA-370 DC Geared Motor with Encoder | Drive motors with encoder feedback for odometry |
| Arduino Nano / L298N | Motor driver interface |
| WAGO 221-Series Lever Connectors (5-way) | Wiring connections between components |
| Bonka 2200mAh 3S1P 11.1V LiPo Battery | Main power source |
| XL4015 5A Buck Converter | Steps down LiPo voltage to power the Pi/electronics |
| Mac (GPU host) | Runs Depth Anything V2 inference for real-time depth estimation |

## Stack

| Layer | Tools |
|---|---|
| SLAM / Nav | ROS2, slam_toolbox, Nav2, RViz |
| Sensors | LiDAR, IMU |
| Depth vision | Depth Anything V2 (small), PyTorch, HF Transformers, OpenCV |
| Streaming | Flask |
| Hardware | Raspberry Pi 4, Arduino Nano, L298 motor driver |

## Running it

**On the Pi** — kick off the camera stream:

    source ~/depth_env/bin/activate
    python3 pi_stream.py

**On the host machine** — run the depth HUD, pointed at the Pi's stream:

    source ~/depth_env/bin/activate
    python3 depth_mac_final.py

**SLAM + navigation** (on the Pi, separate terminal):

    source ~/sentinel_slam_ws/install/setup.bash
    ros2 launch sentinel_bringup sim_slam_nav.launch.py

**Autonomous exploration:**

    ros2 launch sentinel_autonomy autonomy_tools.launch.py explore:=true

**Manual driving:**

    ros2 run key_teleop key_teleop

## Heads up

Depth Anything V2 gives *relative* depth, not calibrated real-world
distance — great for "is this closer than that," not for "this is exactly
1.4 meters away."

## Credits

Chassis URDF and mesh files adapted from [ROBOTIS TurtleBot3](https://github.com/ROBOTIS-GIT/turtlebot3) (Apache 2.0 License), with an added second base plate for our physical build.

---
Built by a small team, one debugging session at a time. 🛠️
