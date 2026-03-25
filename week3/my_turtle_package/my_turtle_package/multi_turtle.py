import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn


class TurtleController(Node):

    def __init__(self):
        super().__init__('three_turtles_controller')

        # Spawn turtles
        self.spawn_turtles()

        # Publishers
        self.pub_circle = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub_triangle = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.pub_square = self.create_publisher(Twist, '/turtle3/cmd_vel', 10)

        # Circle motion
        self.circle_speed = Twist()
        self.circle_speed.linear.x = 2.0
        self.circle_speed.angular.z = 2.0

        # Triangle motion steps
        self.triangle_steps = [
            (1.0, 0.0, 20),
            (0.0, 2.09, 10),
            (1.0, 0.0, 20),
            (0.0, 2.09, 10),
            (1.0, 0.0, 20),
            (0.0, 2.09, 10),
        ]
        self.triangle_index = 0
        self.triangle_counter = 0
        self.triangle_msg = Twist()

        # Square motion steps
        self.square_steps = [
            (1.0, 0.0, 20),
            (0.0, 1.57, 10),
            (1.0, 0.0, 20),
            (0.0, 1.57, 10),
            (1.0, 0.0, 20),
            (0.0, 1.57, 10),
            (1.0, 0.0, 20),
            (0.0, 1.57, 10),
        ]
        self.square_index = 0
        self.square_counter = 0
        self.square_msg = Twist()

        # Timers
        self.create_timer(0.1, self.circle_callback)
        self.create_timer(0.1, self.triangle_callback)
        self.create_timer(0.1, self.square_callback)

    # -------------------------
    def spawn_turtles(self):
        client = self.create_client(Spawn, '/spawn')

        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for spawn service...')

        # turtle2
        req2 = Spawn.Request()
        req2.x = 4.0
        req2.y = 2.0
        req2.theta = 0.0
        req2.name = 'turtle2'
        future2 = client.call_async(req2)
        rclpy.spin_until_future_complete(self, future2)

        # turtle3
        req3 = Spawn.Request()
        req3.x = 7.0
        req3.y = 8.0
        req3.theta = 0.0
        req3.name = 'turtle3'
        future3 = client.call_async(req3)
        rclpy.spin_until_future_complete(self, future3)

    # -------------------------
    def circle_callback(self):
        self.pub_circle.publish(self.circle_speed)

    # -------------------------
    def triangle_callback(self):
        linear, angular, duration = self.triangle_steps[self.triangle_index]

        self.triangle_msg.linear.x = linear
        self.triangle_msg.angular.z = angular
        self.pub_triangle.publish(self.triangle_msg)

        self.triangle_counter += 1
        if self.triangle_counter >= duration:
            self.triangle_counter = 0
            self.triangle_index = (self.triangle_index + 1) % len(self.triangle_steps)

    # -------------------------
    def square_callback(self):
        linear, angular, duration = self.square_steps[self.square_index]

        self.square_msg.linear.x = linear
        self.square_msg.angular.z = angular
        self.pub_square.publish(self.square_msg)

        self.square_counter += 1
        if self.square_counter >= duration:
            self.square_counter = 0
            self.square_index = (self.square_index + 1) % len(self.square_steps)


# -------------------------
def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()