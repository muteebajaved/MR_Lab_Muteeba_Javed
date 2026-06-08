"""
waypoint_navigator.py  –  Lab 7 Task 2
---------------------------------------
Hardcoded 5-waypoint mission navigator for the TurtleBot3 world map.

Waypoints are chosen to be valid free-space positions inside the
turtlebot3_world environment.  Adjust x / y values if your map origin
differs from the default (-1.88, -3.18).

Prerequisites:
    • Gazebo simulation running  (turtlebot3_world)
    • Nav2 bringup running with the saved map:
          ros2 launch turtlebot3_navigation2 navigation2.launch.py \\
              use_sim_time:=True map:=$HOME/maps/my_map.yaml
    • Initial pose set in RViz via "2D Pose Estimate"

Usage:
    ros2 run lab7_pkg waypoint_navigator
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
import time


# ---------------------------------------------------------------------------
# Helper: build a PoseStamped from (x, y, orientation_w)
# ---------------------------------------------------------------------------
def make_pose(x: float, y: float, orientation_w: float) -> PoseStamped:
    """
    Create a PoseStamped message in the 'map' frame.

    Parameters
    ----------
    x, y          : position in metres relative to map origin
    orientation_w : scalar part of quaternion  (1.0 → facing +X axis,
                    0.0 → facing -X axis,  ~0.707 → facing +Y axis)
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
# Waypoint Navigator Node
# ---------------------------------------------------------------------------
class WaypointNavigator(Node):
    """
    ROS 2 node that sends a hardcoded list of 5 waypoints to the
    Nav2 FollowWaypoints action server and waits for mission completion.
    """

    def __init__(self):
        super().__init__('waypoint_navigator')
        self._client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

    def send_waypoints(self, waypoints: list):
        """Send the waypoint list and block until the mission completes."""
        self.get_logger().info('Waiting for FollowWaypoints action server...')
        self._client.wait_for_server()

        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints

        self.get_logger().info(
            f'Sending {len(waypoints)} hardcoded waypoint(s)...')

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
                f'Mission finished with {len(missed)} missed waypoint(s): '
                f'{list(missed)}')
        else:
            self.get_logger().info(
                'SUCCESS – All waypoints reached! Mission complete.')

    def _feedback_callback(self, feedback_msg):
        """Log the index of the waypoint currently being navigated to."""
        current = feedback_msg.feedback.current_waypoint
        self.get_logger().info(f'  → Navigating to waypoint #{current}')


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main(args=None):
    rclpy.init(args=args)
    navigator = WaypointNavigator()

    # -----------------------------------------------------------------------
    # Task 2 – 5 Waypoints within the turtlebot3_world map
    #
    # Coordinate reference (map frame, resolution 0.05 m/px):
    #   Origin offset: (-1.88, -3.18) m  (from my_map.yaml)
    #   All poses are in free space within the walled arena.
    #
    # Waypoint  X(m)   Y(m)   orient_w   Description
    # -------   -----  -----  --------   -----------
    #   WP1     0.50   0.00   1.0        Right of start, facing +X
    #   WP2     1.50   0.50   0.707      Top-right corner area
    #   WP3     1.50  -0.50   0.707      Bottom-right corner area
    #   WP4     0.00  -0.80   1.0        Bottom-left open area
    #   WP5     0.00   0.00   1.0        Return to origin
    # -----------------------------------------------------------------------
    waypoints = [
        make_pose(0.50,  0.00, 1.0),    # Waypoint 1 – right of start
        make_pose(1.50,  0.50, 0.707),  # Waypoint 2 – top-right area
        make_pose(1.50, -0.50, 0.707),  # Waypoint 3 – bottom-right area
        make_pose(0.00, -0.80, 1.0),    # Waypoint 4 – bottom-left open area
        make_pose(0.00,  0.00, 1.0),    # Waypoint 5 – return to origin
    ]

    navigator.get_logger().info(
        '=== Lab 7 Task 2 – Hardcoded 5-Waypoint Mission ===')
    for i, wp in enumerate(waypoints, 1):
        navigator.get_logger().info(
            f'  WP{i}: x={wp.pose.position.x:.2f}  '
            f'y={wp.pose.position.y:.2f}  '
            f'orientation_w={wp.pose.orientation.w:.3f}')

    navigator.send_waypoints(waypoints)

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
