export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
cd ros2_ws_alishba
colcon build
source install/setup.bash
ros2 run camera_follwer clr_follower
