                                    Observations
                                    
1) Robot behavior near obstacles

When the robot approaches an obstacle, it detects it using LiDAR scan data from the /scan topic. As soon as the front distance becomes less than the defined threshold, the robot stops moving forward and changes direction. It then compares left and right distances and turns toward the side with more free space. This allows the robot to avoid collisions and navigate safely in unknown environments without using a map.

2) Oscillations or instability

Some oscillations can be observed when the robot is very close to obstacles or when left and right distances are almost equal. In such cases, the robot may slightly switch between turning left and right, causing small zig-zag movements. This instability is mainly due to noisy LiDAR readings and sudden changes in distance values. Increasing filtering or smoothing scan data can reduce this effect.

3) Effect of changing threshold values

Changing threshold values directly affects robot performance:

Low threshold (e.g., 0.3 m):
  Robot reacts late to obstacles
  Higher risk of collision
  Faster but less safe navigation
High threshold (e.g., 0.7–0.8 m):
  Robot becomes too sensitive
  Stops too early even when obstacle is far
  Movement becomes slow and inefficient
Balanced threshold (e.g., 0.5 m):
  Provides stable and safe navigation
  Good balance between speed and collision avoidance
  
                                     Conclusion

In this lab, a reactive navigation system was successfully implemented for the TurtleBot3 using LiDAR data in a ROS 2 Gazebo environment. The robot was able to interpret LaserScan data from the /scan topic, extract directional distance information (front, left, and right), and generate appropriate velocity commands through the /cmd_vel topic. This allowed the robot to perform basic autonomous behaviors such as obstacle detection, obstacle avoidance, and safe forward movement without using any pre-built map.

Through this exercise, the key learning outcomes included understanding how raw sensor data is processed in real time, how to divide scan data into meaningful regions, and how decision-making logic is implemented for robot control. It also strengthened understanding of ROS 2 communication between nodes using publishers and subscribers.

The main challenges faced during the lab included handling noisy LiDAR data (inf and NaN values), tuning threshold values for stable navigation, and reducing oscillatory behavior near obstacles. It was also observed that improper threshold selection can lead to either delayed reaction or overly sensitive behavior of the robot.

Overall, this lab provided practical insight into real-time robotic navigation and highlighted the importance of parameter tuning and robust control logic in autonomous mobile robots.
