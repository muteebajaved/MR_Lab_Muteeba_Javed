"""
waypoint_navigator_dynamic.py  –  Lab 7 Task 3
------------------------------------------------
Extension of Task 2: accepts waypoints as command-line arguments
instead of hardcoding them.

Each group of THREE values on the command line represents one waypoint:
    x   y   orientation_w

Usage examples:
    # Via ros2 run (pass args after --)
    ros2 run lab7_pkg waypoint_navigator_dynamic -- 0.5 0.0 1.0 1.0 0.5 1.0 0.0 0.0 1.0

    # Or run the script directly (during development):
    python3 waypoint_navigator_dynamic.py 0.5 0.0 1.0 1.0 0.5 1.0 0.0 0.0 1.0

Each triplet  <x>  <y>  <orientation_w>  defines one goal pose.
The number of arguments must therefore be a multiple of 3.

Prerequisites:
    • Gazebo simulation running  (turtlebot3_world)
    • Nav2 bringup running with a saved map
    • Initial pose set in RViz via "2D Pose Estimate"
"""

import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped


# ---------------------------------------------------------------------------
# Helper: build a PoseStamped from (x, y, orientation_w)
# ---------------------------------------------------------------------------
def make_pose(x: float, y: float, orientation_w: float) -> PoseStamped:
    """
    Create a PoseStamped message in the 'map' frame.

    Parameters
    ----------
    x, y          : position in metres relative to map origin
    orientation_w : scalar part of quaternion (1.0 → facing +X)
    """
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0
    pose.pose.orientation.x = 0.0
    pose.pose.orientation.y = 0.0
    pose.pose.orientation.z = 0.0
    pose.pose.orientation.w = orientation_w
    return pose


# ---------------------------------------------------------------------------
# Dynamic Waypoint Navigator Node
# ---------------------------------------------------------------------------
class DynamicWaypointNavigator(Node):
    """
    ROS 2 node that reads waypoints from CLI arguments and sends them
    to the Nav2 FollowWaypoints action server.
    """

    def __init__(self):
        super().__init__('dynamic_waypoint_navigator')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

    def send_waypoints(self, waypoints: list):
        """Send the waypoint list and block until the mission completes."""
        self.get_logger().info('Waiting for FollowWaypoints action server...')
        self._client.wait_for_server()

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(
            f'Sending {len(waypoints)} dynamically-defined waypoint(s)...')

        send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self._feedback_callback)
        rclpy.spin_until_future_complete(self, send_goal_future)

        goal_handle = send_goal_future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal was REJECTED by the action server!')
            return

        self.get_logger().info(
            'Goal ACCEPTED. Robot is navigating through waypoints...')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result
        missed = result.missed_waypoints
        if missed:
            self.get_logger().warn(
                f'Mission finished. Missed {len(missed)} waypoint(s): '
                f'{list(missed)}')
        else:
            self.get_logger().info(
                'SUCCESS – All waypoints reached! Mission complete.')

    def _feedback_callback(self, feedback_msg):
        """Log the index of the waypoint currently being navigated to."""
        current = feedback_msg.feedback.current_waypoint
        self.get_logger().info(f'  → Navigating to waypoint #{current}')


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------
def parse_waypoints(raw_args: list) -> list:
    """
    Parse a flat list of strings  [x1, y1, w1, x2, y2, w2, ...]
    into a list of PoseStamped messages.

    Raises
    ------
    ValueError  if the number of arguments is not a multiple of 3,
                or if any argument cannot be converted to float.
    """
    if len(raw_args) == 0:
        raise ValueError(
            'No waypoints provided.\n'
            'Usage: ros2 run lab7_pkg waypoint_navigator_dynamic -- '
            '<x1> <y1> <w1>  <x2> <y2> <w2>  ...')

    if len(raw_args) % 3 != 0:
        raise ValueError(
            f'Expected a multiple of 3 arguments (got {len(raw_args)}).\n'
            'Each waypoint needs exactly 3 values: x  y  orientation_w')

    waypoints = []
    for i in range(0, len(raw_args), 3):
        try:
            x = float(raw_args[i])
            y = float(raw_args[i + 1])
            w = float(raw_args[i + 2])
        except ValueError:
            raise ValueError(
                f'Could not convert argument group [{i}:{i+3}] to floats: '
                f'{raw_args[i:i+3]}')
        waypoints.append(make_pose(x, y, w))

    return waypoints


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(args=None):
    # -----------------------------------------------------------------------
    # Separate ROS arguments from our custom waypoint arguments.
    # When called via `ros2 run`, ROS strips its own args before passing to
    # Python.  When called directly, sys.argv[1:] contains everything.
    # We use rclpy.utilities.remove_ros_args() to be safe.
    # -----------------------------------------------------------------------
    rclpy.init(args=args)

    from rclpy.utilities import remove_ros_args
    # remove_ros_args returns argv with ROS-specific flags stripped
    user_args = remove_ros_args(sys.argv)[1:]  # drop the script name

    try:
        waypoints = parse_waypoints(user_args)
    except ValueError as e:
        print(f'\n[ERROR] {e}\n', file=sys.stderr)
        rclpy.shutdown()
        sys.exit(1)

    navigator = DynamicWaypointNavigator()

    navigator.get_logger().info(
        f'=== Lab 7 Dynamic Waypoint Mission – {len(waypoints)} waypoint(s) ===')
    for i, wp in enumerate(waypoints, 1):
        navigator.get_logger().info(
            f'  WP{i}: x={wp.pose.position.x:.2f}  '
            f'y={wp.pose.position.y:.2f}  '
            f'orientation_w={wp.pose.orientation.w:.2f}')

    navigator.send_waypoints(waypoints)

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
