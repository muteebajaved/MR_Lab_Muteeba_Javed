import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np

class LidarNavigator(Node):
    def __init__(self):
        super().__init__('lidar_navigator')
        self.subscription = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.front_threshold = 0.5   # metres — stop if closer than this
        self.side_threshold  = 0.4   # metres — wall-follow target distance

    def scan_callback(self, msg):
        ranges = np.array(msg.ranges)

        # --- TODO 1: Clean data ---
        ranges = np.where(np.isfinite(ranges), ranges, 3.5)

        # --- TODO 2: Define regions (360-degree scan, index 0 = front) ---
        front = np.concatenate([ranges[0:20], ranges[340:360]])
        left  = ranges[60:120]
        right = ranges[240:300]

        front_dist = float(np.min(front))
        left_dist  = float(np.min(left))
        right_dist = float(np.min(right))

        self.get_logger().info(
            f"F:{front_dist:.2f}  L:{left_dist:.2f}  R:{right_dist:.2f}")

        twist = Twist()

        # --- TODO 3: Obstacle logic ---
        if front_dist < self.front_threshold:
            # --- TODO 4: Turn toward clearer side ---
            if left_dist > right_dist:
                twist.angular.z =  0.5   # turn left
            else:
                twist.angular.z = -0.5   # turn right
            twist.linear.x = 0.0
        else:
            # --- TODO 5: Move forward ---
            twist.linear.x  = 0.15
            twist.angular.z = 0.0

        self.publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = LidarNavigator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
