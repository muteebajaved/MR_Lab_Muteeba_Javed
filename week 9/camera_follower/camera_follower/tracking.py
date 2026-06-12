import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

from cv_bridge import CvBridge

import cv2
import numpy as np


class CameraTracker(Node):

    def __init__(self):
        super().__init__('camera_tracker')

        self.sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        self.kp = 0.003
        self.max_ang = 0.8
        self.spin_speed = 0.4
        self.min_area = 500

        self.get_logger().info("tracker node started")

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        h, w, _ = frame.shape
        cx_frame = w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # red has two hue ranges in HSV
        m1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        m2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        mask = m1 + m2

        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cmd = Twist()

        if contours:
            biggest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(biggest)

            if area > self.min_area:
                M = cv2.moments(biggest)

                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    err = cx_frame - cx
                    ang = self.kp * err
                    ang = max(-self.max_ang, min(self.max_ang, ang))

                    cmd.linear.x = 0.0
                    cmd.angular.z = ang

                    cv2.drawContours(frame, [biggest], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)
                    cv2.line(frame, (cx_frame, 0), (cx_frame, h), (255, 255, 255), 1)
                    cv2.putText(frame, f'err: {err}', (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        else:
            cmd.angular.z = self.spin_speed

        self.pub.publish(cmd)

        cv2.imshow("Camera View", frame)
        cv2.imshow("Red Mask", mask)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = CameraTracker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
