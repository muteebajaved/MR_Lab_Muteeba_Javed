# MCT-454L Mobile Robotics

## Lab 7: Autonomous Navigation with Nav2 and Multi-Waypoint Mission Planning

### Objective

This lab demonstrates autonomous navigation in ROS 2 using the Nav2
stack, AMCL localization, and TurtleBot3 in Gazebo. Students will load a
saved map, localize the robot, send navigation goals, and execute
multi-waypoint missions.

------------------------------------------------------------------------

## Prerequisites

-   ROS 2 Humble installed
-   TurtleBot3 packages installed
-   Nav2 packages installed
-   Completion of Lab 5 (SLAM & Mapping)
-   Saved map files:
    -   `~/maps/my_map.pgm`
    -   `~/maps/my_map.yaml`

------------------------------------------------------------------------

## Installation

``` bash
sudo apt update
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install ros-humble-turtlebot3-navigation2
```

Add the following to `~/.bashrc`:

``` bash
source /opt/ros/humble/setup.bash
export TURTLEBOT3_MODEL=burger
```

Reload:

``` bash
source ~/.bashrc
```

------------------------------------------------------------------------

## Launch Gazebo

``` bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

Verify running nodes:

``` bash
rqt_graph
```

------------------------------------------------------------------------

## Launch Nav2

``` bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py \
use_sim_time:=True \
map:=$HOME/maps/my_map.yaml
```

If RViz does not open:

``` bash
ros2 launch nav2_bringup rviz_launch.py
```

------------------------------------------------------------------------

## AMCL Localization

1.  Open RViz.
2.  Select **2D Pose Estimate**.
3.  Click robot's approximate location.
4.  Drag arrow to set orientation.
5.  Use teleop to refine localization.

``` bash
ros2 run turtlebot3_teleop teleop_keyboard
```

------------------------------------------------------------------------

## Send Navigation Goals

### Using RViz

-   Click **Nav2 Goal**
-   Select target position
-   Set orientation
-   Observe generated path

### Using Command Line

``` bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
"{pose: {header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}}"
```

------------------------------------------------------------------------

## Multi-Waypoint Navigation

Create package structure:

``` bash
mkdir -p ~/ros2_ws/src/lab6_nav/lab6_nav
cd ~/ros2_ws/src/lab6_nav/lab6_nav
```

Create:

``` bash
nano waypoint_navigator.py
```

Run:

``` bash
python3 waypoint_navigator.py
```

Example waypoints:

  Waypoint   X     Y
  ---------- ----- ------
  1          0.5   0.0
  2          1.0   0.5
  3          1.0   -0.5
  4          0.0   -0.5
  5          0.0   0.0

------------------------------------------------------------------------

## RViz Visualization

Enable:

-   Map
-   Global Costmap
-   Local Costmap
-   Global Path
-   Local Path
-   AMCL Particle Cloud
-   TF
-   Odometry
-   LaserScan

Set:

``` text
Fixed Frame = map
```

------------------------------------------------------------------------

## Tasks

### Task 1

-   Send 3 navigation goals.
-   Record start/end pose.
-   Observe success or recovery behavior.

### Task 2

-   Define 5 waypoints.
-   Execute full waypoint mission.
-   Capture screenshots.

### Task 3

-   Modify node to accept command-line waypoints.

Example:

``` bash
python3 waypoint_navigator.py 0.5 0.0 1.0 1.0 0.5 1.0 0.0 0.0 1.0
```

### Task 4

-   Observe local and global costmaps.
-   Identify costmap topics.
-   Compare their functions.

### Task 5

-   Insert obstacle in Gazebo.
-   Observe recovery behavior.
-   Analyze replanning and obstacle avoidance.

------------------------------------------------------------------------

## Deliverables

1.  Lab report
2.  Completed waypoint table
3.  Python source code
4.  RViz screenshots
5.  rqt_graph screenshots
6.  Recovery behavior observations
7.  Final conclusion

------------------------------------------------------------------------

## Conclusion

This lab introduces the complete ROS 2 navigation pipeline using Nav2,
AMCL localization, occupancy-grid maps, and waypoint-based navigation.
It provides practical experience in autonomous robot navigation and
mission execution in simulation.
