                   Lab Report: Gazebo and RViz with ROS 2
                   
1) Objective

To simulate and visualize TurtleBot3 in ROS 2 using Gazebo and RViz, and to understand robot control, SLAM, and ROS 2 communication.

2) Steps Followed
Updated system and installed TurtleBot3 + Gazebo packages
Set TURTLEBOT3_MODEL=burger and sourced ROS 2
Launched simulation in Gazebo
Ran RViz with Cartographer for SLAM and mapping
Added plugins (LaserScan, TF, Map, Odometry) in RViz
Controlled robot using keyboard teleoperation
Recorded data using ros2 bag record -a
Saved generated map using map saver
Implemented /cmd_vel publisher (move/stop every 2 sec)
Implemented /odom subscriber to print position

3) Observations
Robot movement matched commands with slight simulation delay
LiDAR and odometry data were clearly visible in RViz
SLAM successfully generated the environment map

4) Conclusion
The lab provided practical understanding of ROS 2 simulation, visualization, and communication. It helped in learning robot navigation, SLAM, and real-time data handling.


                        Observations on Discrepancies
                        
A slight delay was observed between issuing teleoperation commands and the robot’s movement due to simulation processing time.

The robot did not always move in a perfectly straight line as expected, showing small deviations because of simulated sensor noise and wheel dynamics.

Odometry readings showed minor drift over time, causing slight differences between the expected and actual position.

The SLAM-generated map had small inaccuracies and distortions, especially during fast movements or sharp turns.

Sudden starts and stops in velocity commands resulted in less smooth motion compared to ideal real-world behavior.


                                   Conclusion

At the start of the lab, Gazebo took noticeable time to load and RViz was not functioning properly, which caused initial setup difficulties. However, after proper configuration and setup, both tools worked correctly.

This lab provided practical experience with ROS 2 simulation using Gazebo and visualization using RViz. It helped in understanding robot control, SLAM, and real-time sensor data analysis. Implementing publisher and subscriber nodes improved understanding of ROS 2 communication.

Some challenges included simulation delays, minor inaccuracies in odometry and mapping, and handling multiple terminals. Overall, the lab built a strong foundation for developing and testing robotic navigation systems.
