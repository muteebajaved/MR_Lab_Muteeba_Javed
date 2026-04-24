import math
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist


class FollowLeader(Node):

    def __init__(self):
        super().__init__('follow_leader')

        # Store poses
        self.turtle1_pose = None
        self.turtle2_pose = None

        # Subscribers
        self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.turtle1_callback,
            10
        )

        self.create_subscription(
            Pose,
            '/turtle2/pose',
            self.turtle2_callback,
            10
        )

        # Publisher
        self.vel_publisher = self.create_publisher(
            Twist,
            '/turtle2/cmd_vel',
            10
        )

        # Timer loop
        self.create_timer(0.1, self.follow_logic)

    def turtle1_callback(self, msg):
        self.turtle1_pose = msg

    def turtle2_callback(self, msg):
        self.turtle2_pose = msg

    def follow_logic(self):
        if self.turtle1_pose is None or self.turtle2_pose is None:
            return

        # Position difference
        dx = self.turtle1_pose.x - self.turtle2_pose.x
        dy = self.turtle1_pose.y - self.turtle2_pose.y

        # Distance
        distance = math.sqrt(dx**2 + dy**2)

        # Desired angle
        target_theta = math.atan2(dy, dx)

        # Angle error
        angle_error = target_theta - self.turtle2_pose.theta

        # Normalize angle between -pi and pi
        angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

        # Create velocity command
        vel_msg = Twist()

        vel_msg.linear.x = min(2.0, 1.5 * distance)
        vel_msg.angular.z = 4.0 * angle_error

        # Stop if very close
        if distance < 0.5:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.0

        # Publish
        self.vel_publisher.publish(vel_msg)


def main(args=None):
    rclpy.init(args=args)

    node = FollowLeader()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
