import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


class ScanWatchdog(Node):
    """Reports basic LiDAR stream health for simulation and hardware runs."""

    def __init__(self) -> None:
        super().__init__("sentinel_scan_watchdog")
        self.declare_parameter("scan_topic", "/scan")
        self.declare_parameter("status_topic", "/sentinel/scan_health")
        self.declare_parameter("min_valid_ratio", 0.35)
        self.declare_parameter("timeout_s", 1.5)
        self._last_scan = None
        self._publisher = self.create_publisher(
            String,
            self.get_parameter("status_topic").value,
            10,
        )
        self.create_subscription(
            LaserScan,
            self.get_parameter("scan_topic").value,
            self._on_scan,
            10,
        )
        self.create_timer(1.0, self._tick)

    def _on_scan(self, msg: LaserScan) -> None:
        valid = [
            reading
            for reading in msg.ranges
            if math.isfinite(reading) and msg.range_min <= reading <= msg.range_max
        ]
        ratio = len(valid) / max(1, len(msg.ranges))
        nearest = min(valid) if valid else math.inf
        self._last_scan = self.get_clock().now()
        state = "ok" if ratio >= float(self.get_parameter("min_valid_ratio").value) else "weak"
        self._publisher.publish(String(data=f"state={state} valid_ratio={ratio:.3f} nearest={nearest:.3f}"))

    def _tick(self) -> None:
        if self._last_scan is None:
            self._publisher.publish(String(data="state=waiting valid_ratio=0.000 nearest=inf"))
            return
        age = (self.get_clock().now() - self._last_scan).nanoseconds / 1_000_000_000
        if age > float(self.get_parameter("timeout_s").value):
            self._publisher.publish(String(data=f"state=timeout age={age:.2f}"))


def main() -> None:
    rclpy.init()
    node = ScanWatchdog()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

