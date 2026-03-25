import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute

class MoveTurtle(Node):

    def __init__(self):
        super().__init__('move_turtle_node')

        # Create client for teleport service
        self.client = self.create_client(TeleportAbsolute, 'turtle1/teleport_absolute')

        # Wait until service is available
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for teleport service...')

    def move_to(self, x, y, theta=0.0):
        # Create request
        request = TeleportAbsolute.Request()
        request.x = x
        request.y = y
        request.theta = theta

        # Call service
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)

        self.get_logger().info(f'Moved to x={x}, y={y}, theta={theta}')


def main(args=None):
    rclpy.init(args=args)

    node = MoveTurtle()

    node.move_to(5.0, 5.0, 0.0)   # center
    node.move_to(8.0, 8.0, 1.57)  # top right
    node.move_to(2.0, 3.0, 0.0)   # another position

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()