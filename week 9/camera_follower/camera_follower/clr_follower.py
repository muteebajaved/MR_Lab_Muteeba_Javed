import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
import math


class ObjectTracking(Node):
    """Track colored objects (Red > Blue > Green priority), approach, and stop at safe distance.
    If object disappears, rotate 360° to search, then stop if nothing found."""

    def __init__(self):
        super().__init__('object_tracking')
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.bridge = CvBridge()

        # --- HSV Thresholds (priority order: RED > BLUE > GREEN) ---
        self.colors = [
            ('RED', [
                (np.array([0, 150, 70]),   np.array([10, 255, 255])),
                (np.array([160, 150, 70]), np.array([180, 255, 255])),
            ], (0, 0, 255)),

            ('BLUE', [
                (np.array([100, 100, 50]), np.array([130, 255, 255])),
            ], (255, 0, 0)),

            ('GREEN', [
                (np.array([40, 50, 50]), np.array([80, 255, 255])),
            ], (0, 255, 0)),
        ]

        # --- Control Parameters ---
        self.kp = 0.0005
        self.center_threshold = 3
        self.min_contour_area = 500
        self.search_speed = 0.3
        self.forward_speed = 0.15
        self.stop_percent = 65.0

        # --- 360° Search State ---
        self.search_start_time = None
        self.had_detection = False
        self.search_exhausted = False
        self.full_rotation_time = (2.0 * math.pi) / self.search_speed

        # --- Goal Achieved State ---
        self.goal_achieved = False

        # Morphological kernel
        self.kernel = np.ones((7, 7), np.uint8)

        # Error tracking for GUI display
        self.last_error = None

        self.get_logger().info('object_tracking node started')
        self.get_logger().info(f'  Priority: RED > BLUE > GREEN')
        self.get_logger().info(f'  360 search timeout: {self.full_rotation_time:.1f}s')

    def detect_color(self, hsv, label, hsv_ranges):
        """Create mask for a single color and return (mask, largest_contour, area) or None."""
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for lower, upper in hsv_ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area < self.min_contour_area:
            return None

        M = cv2.moments(largest)
        if M['m00'] == 0:
            return None

        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        return (largest, cx, cy, area, mask)

    def draw_label_box(self, frame, text, pos, text_color, bg_color, font_scale=0.9, thickness=2):
        """Draw text with a filled background box for better readability."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        x, y = pos
        cv2.rectangle(frame, (x - 6, y - th - 8), (x + tw + 6, y + baseline + 4), bg_color, -1)
        cv2.putText(frame, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Image conversion error: {e}')
            return

        h, w, _ = frame.shape
        image_center_x = w // 2

        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        twist = Twist()

        # Try to detect colors in priority order: RED > BLUE > GREEN
        detection = None
        detected_label = None
        detected_color = None
        for label, hsv_ranges, draw_color in self.colors:
            result = self.detect_color(hsv, label, hsv_ranges)
            if result:
                detection = result
                detected_label = label
                detected_color = draw_color
                break

        # Prepare a combined mask image to show in second window
        display_mask = np.zeros((h, w), dtype=np.uint8)

        if detection:
            largest_contour, cx, cy, area, color_mask = detection
            display_mask = color_mask.copy()

            total_pixels = w * h
            color_pixels = cv2.countNonZero(color_mask)
            fill_percent = (color_pixels / total_pixels) * 100.0

            self.had_detection = True
            self.search_start_time = None
            self.search_exhausted = False

            error_x = cx - image_center_x
            self.last_error = error_x

            # --- STEERING ---
            if abs(error_x) > self.center_threshold:
                twist.angular.z = -self.kp * float(error_x)
            else:
                twist.angular.z = 0.0

            # --- APPROACH & SAFE DISTANCE ---
            if fill_percent >= self.stop_percent:
                # GOAL ACHIEVED — full green overlay
                self.goal_achieved = True
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                status = f'GOAL ACHIEVED — {detected_label} REACHED!'
                status_color = (0, 255, 0)

                # Draw green overlay on entire frame
                overlay = frame.copy()
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 220, 0), -1)
                cv2.addWeighted(overlay, 0.18, frame, 0.82, 0, frame)

                # Draw thick green border
                cv2.rectangle(frame, (0, 0), (w - 1, h - 1), (0, 255, 0), 6)

                # Big centered success text
                success_text = 'POINT ACHIEVED'
                font = cv2.FONT_HERSHEY_SIMPLEX
                (tw, th), _ = cv2.getTextSize(success_text, font, 1.2, 3)
                tx = (w - tw) // 2
                ty = h // 2 + th // 2
                cv2.rectangle(frame, (tx - 10, ty - th - 12), (tx + tw + 10, ty + 10), (0, 80, 0), -1)
                cv2.putText(frame, success_text, (tx, ty), font, 1.2, (0, 255, 0), 3, cv2.LINE_AA)

            elif abs(error_x) <= self.center_threshold:
                self.goal_achieved = False
                twist.linear.x = self.forward_speed
                status = f'{detected_label} APPROACHING ({fill_percent:.1f}%)'
                status_color = (0, 255, 255)
            else:
                self.goal_achieved = False
                twist.linear.x = 0.0
                status = f'{detected_label} ALIGNING | err={error_x:+d}px'
                status_color = (0, 165, 255)

            # Draw contour & centroid
            cv2.drawContours(frame, [largest_contour], -1, detected_color, 2)
            cv2.circle(frame, (cx, cy), 8, detected_color, -1)
            cv2.line(frame, (image_center_x, 0), (image_center_x, h), (200, 200, 200), 1)
            cv2.line(frame, (image_center_x, cy), (cx, cy), (0, 255, 255), 2)

            # Status label (top-left)
            self.draw_label_box(frame, status, (10, 36), (255, 255, 255), status_color, font_scale=0.9, thickness=2)

            # Error info (top-right area)
            err_text = f'err={error_x:+d}px'
            self.draw_label_box(frame, err_text, (w - 200, 36), (255, 255, 255), (50, 50, 50), font_scale=0.8, thickness=2)

            # Fill % info
            fill_text = f'Fill: {fill_percent:.1f}% / {self.stop_percent:.0f}%'
            self.draw_label_box(frame, fill_text, (10, 80), (255, 255, 255), (30, 30, 30), font_scale=0.75, thickness=2)

            self.get_logger().info(status, throttle_duration_sec=0.5)

        else:
            # No color detected
            self.goal_achieved = False

            if self.search_exhausted:
                twist.angular.z = 0.0
                twist.linear.x = 0.0
                self.draw_label_box(frame, 'NO OBJECT FOUND — STOPPED', (10, 36),
                                    (255, 255, 255), (0, 0, 200), font_scale=0.9, thickness=2)
                self.get_logger().info('360 search complete -> stopped', throttle_duration_sec=2.0)

            elif self.had_detection:
                if self.search_start_time is None:
                    self.search_start_time = time.time()

                elapsed = time.time() - self.search_start_time
                remaining = self.full_rotation_time - elapsed

                if elapsed >= self.full_rotation_time:
                    self.search_exhausted = True
                    twist.angular.z = 0.0
                else:
                    twist.angular.z = self.search_speed

                self.draw_label_box(frame, f'SEARCHING... {remaining:.1f}s left', (10, 36),
                                    (255, 255, 255), (0, 100, 200), font_scale=0.9, thickness=2)
                self.get_logger().info(f'Searching... {remaining:.1f}s remaining', throttle_duration_sec=1.0)

            else:
                twist.angular.z = self.search_speed
                self.draw_label_box(frame, 'SEARCHING FOR OBJECTS...', (10, 36),
                                    (255, 255, 255), (0, 0, 180), font_scale=0.9, thickness=2)
                self.get_logger().info('Initial search...', throttle_duration_sec=2.0)

            # Show last known error if available
            if self.last_error is not None:
                err_text = f'last err={self.last_error:+d}px'
                self.draw_label_box(frame, err_text, (w - 220, 36),
                                    (200, 200, 200), (40, 40, 40), font_scale=0.8, thickness=2)

        # Publish velocity command
        self.publisher.publish(twist)

        # Resize and display — Camera window
        frame_small = cv2.resize(frame, (0, 0), fx=0.6, fy=0.6)
        cv2.imshow('Camera View — CLR Follower', frame_small)

        # Show color mask in a second window (colorized for visibility)
        mask_colored = cv2.cvtColor(display_mask, cv2.COLOR_GRAY2BGR)
        # Show active pixels as white
        mask_colored[display_mask > 0] = (255, 255, 255)
        mask_small = cv2.resize(mask_colored, (0, 0), fx=0.6, fy=0.6)
        # Label the mask window
        cv2.putText(mask_small, 'COLOR MASK', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow('Color Mask — CLR Follower', mask_small)

        cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ObjectTracking()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        twist = Twist()
        node.publisher.publish(twist)
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
