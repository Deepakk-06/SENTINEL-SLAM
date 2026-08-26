import rclpy
from nav_msgs.msg import OccupancyGrid
from rclpy.node import Node
from std_msgs.msg import String


class MapQualityMonitor(Node):
    """Publishes compact map coverage statistics from an OccupancyGrid."""

    def __init__(self) -> None:
        super().__init__("sentinel_map_quality_monitor")
        self.declare_parameter("map_topic", "/map")
        self.declare_parameter("status_topic", "/sentinel/map_quality")
        self.declare_parameter("occupied_threshold", 55)
        self._publisher = self.create_publisher(
            String,
            self.get_parameter("status_topic").value,
            10,
        )
        self.create_subscription(
            OccupancyGrid,
            self.get_parameter("map_topic").value,
            self._on_map,
            10,
        )

    def _on_map(self, msg: OccupancyGrid) -> None:
        cells = max(1, len(msg.data))
        unknown = sum(1 for value in msg.data if value < 0)
        occupied = sum(
            1
            for value in msg.data
            if value >= int(self.get_parameter("occupied_threshold").value)
        )
        free = cells - unknown - occupied
        explored = free + occupied
        status = (
            f"explored={explored / cells:.3f} "
            f"free={free / cells:.3f} "
            f"occupied={occupied / cells:.3f} "
            f"unknown={unknown / cells:.3f} "
            f"resolution={msg.info.resolution:.3f}"
        )
        self._publisher.publish(String(data=status))


def main() -> None:
    rclpy.init()
    node = MapQualityMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()

