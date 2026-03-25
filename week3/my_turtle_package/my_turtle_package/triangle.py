import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class Triangle(Node):
    def __init__(self):
        super().__init__('triangle_motion')
        self.pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        time.sleep(2)
        self.draw_triangle()

    def draw_triangle(self):
        msg = Twist()

        for _ in range(3):
            msg.linear.x = 2.0
            msg.angular.z = 0.0
            self.pub.publish(msg)
            time.sleep(2)

            msg.linear.x = 0.0
            msg.angular.z = 2.09
            self.pub.publish(msg)
            time.sleep(1.5)

        self.pub.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = Triangle()
    rclpy.spin_once(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()