# Mobile Robotics Lab Session 8
## Building and Visualizing a Custom Mobile Robot using URDF

## Objective
The objective of this lab is to design and visualize a custom mobile robot using URDF in ROS 2.

---

## Environment Setup

Source ROS 2:

```bash
source /opt/ros/humble/setup.bash
```

Install required packages:

```bash
sudo apt install ros-humble-urdf-tutorial
sudo apt install ros-humble-tf2-tools
```

---

## Package Structure

Created robot description package:

```bash
cd ~/ros2_ws_Muteeba_javed/src
ros2 pkg create my_robot_description
```

Created folders:

```bash
mkdir urdf launch rviz
```

---

## Robot Design

Created custom robot model in:

```bash
urdf/my_robot.urdf
```

Robot includes:

- Base link
- Camera sensor
- Left wheel
- Right wheel
- LiDAR sensor
- Antenna

Used geometries:

- Box
- Cylinder
- Sphere

Used joint types:

- Fixed Joint
- Continuous Joint

---

## Build Package

```bash
cd ~/ros2_ws_Muteeba_javed
colcon build --packages-select my_robot_description
source install/setup.bash
```

---

## Visualization in RViz

Launch robot model:

```bash
ros2 launch urdf_tutorial display.launch.py model:=/home/muteeba/ros2_ws_Muteeba_javed/src/my_robot_description/urdf/my_robot.urdf
```

RViz settings:

- Fixed Frame: `base_link`
- Added Displays:
  - RobotModel
  - TF

---

## TF Tree Visualization

Run TF tree:

```bash
ros2 run tf2_tools view_frames
```

---

## Customizations Made

The following customizations were implemented:

- Added two wheels for robot movement
- Added a camera sensor
- Added a LiDAR sensor
- Added an antenna structure
- Used multiple geometries
- Verified TF frames successfully

---

## Deliverables

- Custom URDF file
- RViz visualization screenshot
- TF tree verification
