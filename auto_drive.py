import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def angle_diff(target, current):
    return math.atan2(
        math.sin(target - current),
        math.cos(target - current)
    )


class AutoDrive(Node):
    def __init__(self):
        super().__init__('auto_drive')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10
        )

        self.position = None
        self.start_position = None

        # 出発地点を基準にした巡回地点（単位：メートル）
        self.waypoints = [
            (0.8, 0.0),
            (0.8, 0.8),
            (0.0, 0.8),
            (0.0, 0.0),
        ]

        self.index = 0
        self.finished = False
        self.timer = self.create_timer(0.1, self.control)

    def odom_callback(self, msg):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation

        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

        self.position = (p.x, p.y, yaw)

        if self.start_position is None:
            self.start_position = (p.x, p.y)
            self.get_logger().info('Starting autonomous navigation')

    def control(self):
        if self.position is None or self.finished:
            return

        x, y, yaw = self.position
        sx, sy = self.start_position

        gx, gy = self.waypoints[self.index]
        gx += sx
        gy += sy

        distance = math.hypot(gx - x, gy - y)
        command = Twist()

        if distance < 0.09:
            self.get_logger().info(
                f'Waypoint {self.index + 1} reached'
            )
            self.index += 1

            if self.index >= len(self.waypoints):
                self.finished = True
                self.get_logger().info('TASK COMPLETED')
            self.publisher.publish(command)
            return

        target_yaw = math.atan2(gy - y, gx - x)
        error = angle_diff(target_yaw, yaw)

        if abs(error) > 0.15:
            command.angular.z = max(
                -0.6, min(0.6, 1.8 * error)
            )
        else:
            command.linear.x = min(0.15, 0.7 * distance)
            command.angular.z = max(
                -0.6, min(0.6, 1.8 * error)
            )

        self.publisher.publish(command)


def main():
    rclpy.init()
    node = AutoDrive()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
