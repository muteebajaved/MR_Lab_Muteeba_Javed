Q1. Define the following (one sentence each):

Node: A node is a single program in ROS 2 that performs a specific task like sensing or control.

Topic: A topic is a named channel used by nodes to exchange messages continuously.

Package: A package is a folder that contains ROS 2 code, dependencies, and configuration files.

Workspace: A workspace is a directory that holds ROS 2 packages along with build and install files.
Q2. Why is sourcing required? What happens if you do not source a workspace?

Sourcing sets environment variables so ROS 2 can find packages and executables.
If you do not source the workspace, ROS 2 will not recognize your package or node.
Q3. Purpose of colcon build and generated folders

colcon build compiles and installs ROS 2 packages.
It generates build/, install/, and log/ folders.
Q4. Purpose of entry_points console script in setup.py

The console script maps a terminal command to a Python function so ROS 2 can run the node using ros2 run.
Q5.
Publisher--->topic----->subscriber.
