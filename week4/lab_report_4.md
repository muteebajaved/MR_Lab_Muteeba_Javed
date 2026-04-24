**Mobile Robotics Lab – Session 4 Report**

**Topic:** ROS 2 Launch, Rosbag, and rqt-plot

1. Objective

To learn how to run multiple nodes using ROS 2 launch files.
To record and replay topic data using Rosbag.
To visualize topic data using rqt_plot.


2. Approach

ROS 2 Launch

I created a custom package and wrote a launch file to run multiple nodes at once.
The launch file started:

turtlesim node (simulation)
teleoperation node (keyboard control)

This helped in managing multiple nodes efficiently without running commands separately.


Rosbag Recording & Playback

I recorded turtle motion data using:

`/turtle1/pose` (position data)
`/turtle1/cmd_vel` (velocity commands)

Steps followed:

Started recording using `ros2 bag record`
Controlled the turtle using keyboard
Stopped recording and replayed data

This allowed me to reproduce the exact motion of the turtle.



rqt Visualization

I used rqt_plot to visualize real-time data:

Plotted `/turtle1/cmd_vel`
Observed changes in linear and angular velocity while moving the turtle

This helped in understanding how control inputs change over time.


Additional Task (Follow-the-Leader)

I implemented a simple logic:

Subscribed to `/turtle1/pose`
Published velocity commands to `/turtle2/cmd_vel`

The second turtle followed the first turtle based on position difference.


3. Findings

Launch files simplify execution of multiple nodes.
Rosbag is useful for debugging and data analysis.
rqt_plot provides clear visualization of system behavior.
Real-time plotting helps in tuning control systems.


4. Observations

Turtle motion during playback matched the recorded data exactly.
Velocity graphs showed smooth and sudden changes depending on key input.
In follow behavior, delay and accuracy depended on control logic.
Multiple nodes can be easily managed using a single launch file.


5. Conclusion

This lab provided me practical understanding of ROS 2 tools for launching nodes, recording data, and analyzing system behavior. These tools are essential for debugging, testing, and developing mobile robotic systems.
