import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist

from cv_bridge import CvBridge

import cv2
import numpy as np


SEARCH   = 'SEARCH'
ALIGN    = 'ALIGN'
APPROACH = 'APPROACH'
STOP     = 'STOP'


class CameraFollower(Node):

    def __init__(self):
        super().__init__('camera_follower')

        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.bridge = CvBridge()

        # =========================
        # 🔧 SLOW & STABLE ALIGNMENT
        # =========================
        self.kp_ang       = 0.0012     # 🔻 reduced (important fix)
        self.max_ang      = 0.35       # 🔻 slower turning
        self.min_ang      = 0.03

        self.align_thresh = 12         # pixels tolerance
        self.align_hold   = 20         # more stability frames

        # linear movement (VERY IMPORTANT)
        self.linear_speed = 0.18       # 🔻 slower forward
        self.slow_spd     = 0.08       # creeping mode

        # stop condition
        self.stop_area = 1600000
        self.slow_area = 500000

        self.min_area = 500

        # search
        self.spin_spd = 0.25           # 🔻 slower scan

        # state
        self.state = SEARCH
        self._align_cnt = 0

        self.get_logger().info("CameraFollower started (SLOW + STABLE ALIGNMENT)")

    # =========================
    def image_callback(self, msg):
    # =========================

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        h, w, _ = frame.shape
        cx_frame = w // 2

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.bitwise_or(
            cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255])),
            cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        )

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

                if M['m00'] != 0:

                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])

                    err = cx_frame - cx

                    # =========================
                    # STATE CONTROL
                    # =========================

                    if self.state in (SEARCH, ALIGN):

                        if abs(err) <= self.align_thresh:
                            self._align_cnt += 1
                        else:
                            self._align_cnt = 0
                            self.state = ALIGN

                        if self._align_cnt >= self.align_hold:
                            self.state = APPROACH
                            self._align_cnt = 0
                            self.get_logger().info("LOCKED → APPROACH")

                    elif self.state == APPROACH:

                        # drift protection
                        if abs(err) > self.align_thresh * 2:
                            self.state = ALIGN

                    elif self.state == STOP:
                        pass

                    # =========================
                    # CONTROL (SLOW ALIGNMENT FIX)
                    # =========================

                    if self.state == ALIGN:

                        # 🔥 SOFT proportional control (no jerks)
                        ang = self.kp_ang * err

                        # extra smoothing near center
                        if abs(err) < 25:
                            ang *= 0.5

                        # saturation
                        ang = max(-self.max_ang, min(self.max_ang, ang))

                        cmd.linear.x = 0.0
                        cmd.angular.z = ang

                    elif self.state == APPROACH:

                        # PERFECT FIX:
                        # centered → straight slow
                        # off-center → slow correction

                        if abs(err) <= self.align_thresh:

                            cmd.linear.x = self.linear_speed
                            cmd.angular.z = 0.0

                        else:

                            ang = self.kp_ang * err
                            ang = max(-self.max_ang, min(self.max_ang, ang))

                            cmd.linear.x = self.slow_spd
                            cmd.angular.z = ang

                        if area >= self.stop_area:
                            self.state = STOP
                            self.get_logger().info("STOP reached")

                    elif self.state == STOP:

                        cmd.linear.x = 0.0
                        cmd.angular.z = 0.0

                    # =========================
                    # VISUALS
                    # =========================

                    cv2.drawContours(frame, [biggest], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)

                    cv2.line(frame, (cx_frame, 0), (cx_frame, h), (255, 255, 255), 1)

                    cv2.putText(frame,
                                f'{self.state} err={err} area={int(area)}',
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (0, 255, 0),
                                2)

                    self.pub.publish(cmd)
                    cv2.imshow("Camera View", frame)
                    cv2.imshow("Mask", mask)
                    cv2.waitKey(1)
                    return

        # =========================
        # NO OBJECT → SLOW SEARCH
        # =========================
        cmd.linear.x = 0.0
        cmd.angular.z = self.spin_spd
        self.state = SEARCH

        self.pub.publish(cmd)
        cv2.imshow("Camera View", frame)
        cv2.imshow("Mask", mask)
        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = CameraFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
