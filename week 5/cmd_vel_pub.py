import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_publisher')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(2.0, self.publish_velocity)
        self.toggle = True

    def publish_velocity(self):
        msg = Twist()
        if self.toggle:
            msg.linear.x = 0.2
        else:
            msg.linear.x = 0.0
        self.publisher_.publish(msg)
        self.toggle = not self.toggle

def main(args=None):
    rclpy.init(args=args)
    node = CmdVelPublisher()
    rclpy.spin(node)
    rclpy.shutdown()
