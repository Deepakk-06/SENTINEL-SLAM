import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class VelocityGuard(Node):
    """Filters velocity commands when LiDAR reports an obstacle in front."""

    def __init__(self) -> None:
        super().__init__("sentinel_velocity_guard")
        self.declare_parameter("input_topic", "/cmd_vel_raw")
        self.declare_parameter("output_topic", "/cmd_vel")
        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("stop_distance_m", 0.38)
        self.declare_parameter("slow_distance_m", 0.75)
        self.declare_parameter("front_arc_deg", 42.0)
        self.declare_parameter("scan_timeout_s", 0.8)

        self._nearest_front = math.inf
        self._last_scan = self.get_clock().now()
        self._publisher = self.create_publisher(
            Twist,
            self.get_parameter("output_topic").value,
            10,
        )
        self.create_subscription(
            Twist,
            self.get_parameter("input_topic").value,
            self._on_cmd,
            10,
        )
        self.create_subscription(
            LaserScan,
            self.get_parameter("scan_topic").value,
            self._on_scan,
            10,
        )

    def _on_scan(self, msg: LaserScan) -> None:
        arc = math.radians(float(self.get_parameter("front_arc_deg").value))
        ranges = []
        for idx, distance in enumerate(msg.ranges):
            angle = msg.angle_min + idx * msg.angle_increment
            if abs(angle) <= arc / 2.0 and math.isfinite(distance):
                if msg.range_min <= distance <= msg.range_max:
                    ranges.append(distance)
        self._nearest_front = min(ranges) if ranges else math.inf
        self._last_scan = self.get_clock().now()

    def _on_cmd(self, msg: Twist) -> None:
        guarded = Twist()
        guarded.linear.x = msg.linear.x
        guarded.angular.z = msg.angular.z

        if self._scan_is_stale():
            guarded.linear.x = min(0.0, guarded.linear.x)
            self.get_logger().warn("LiDAR scan stale; blocking forward motion", throttle_duration_sec=2.0)
        elif guarded.linear.x > 0.0:
            stop_distance = float(self.get_parameter("stop_distance_m").value)
            slow_distance = float(self.get_parameter("slow_distance_m").value)
            if self._nearest_front <= stop_distance:
                guarded.linear.x = 0.0
            elif self._nearest_front <= slow_distance:
                scale = (self._nearest_front - stop_distance) / (slow_distance - stop_distance)
                guarded.linear.x *= max(0.15, min(1.0, scale))

        self._publisher.publish(guarded)

    def _scan_is_stale(self) -> bool:
        age = (self.get_clock().now() - self._last_scan).nanoseconds / 1_000_000_000
        return age > float(self.get_parameter("scan_timeout_s").value)


def main() -> None:
    rclpy.init()
    node = VelocityGuard()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

