# MCT-454L Mobile Robotics Lab Week 2
## ROS, Packages, Nodes, Topics, Services and RQT
## Steps Followed

1. First, the ROS 2 environment was sourced using:

   source /opt/ros/humble/setup.bash

2. The turtlesim node was launched using:

   ros2 run turtlesim turtlesim_node

3. The turtle was controlled using the teleoperation node:

   ros2 run turtlesim turtle_teleop_key

4. ROS 2 topics were explored using:

   ros2 topic list

   The turtle position was observed using:

   ros2 topic echo /turtle1/pose

5. Velocity commands were sent using:

   ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist

6. The simulation was reset using the service:

   ros2 service call /reset std_srvs/srv/Empty

7. The rqt graphical interface was opened using:

   rqt

8. Using rqt, the `/reset` service was called to reset the simulation.

9. The `/spawn` service was used to create a second turtle by specifying its position and name.

10. The second turtle was controlled using the topic:

   /turtle2/cmd_vel

---

## Observations

- ROS 2 nodes communicate through topics and services.
- Topics allow continuous data communication between nodes.
- Services allow request and response communication.
- The turtlesim simulator helps understand robot control in ROS 2.
- Multiple turtles can be created and controlled independently using different topics.
- The rqt tool provides a graphical interface to visualize nodes, topics, and services.
