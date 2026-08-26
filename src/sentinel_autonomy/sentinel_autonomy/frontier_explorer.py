import math
from dataclasses import dataclass
from typing import Iterable, Optional

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import OccupancyGrid
from rclpy.action import ActionClient
from rclpy.node import Node


@dataclass(frozen=True)
class Cell:
    x: int
    y: int


class FrontierExplorer(Node):
    """Selects useful map frontiers and sends them as Nav2 goals."""

    def __init__(self) -> None:
        super().__init__("sentinel_frontier_explorer")
        self.declare_parameter("map_topic", "/map")
        self.declare_parameter("goal_frame", "map")
        self.declare_parameter("min_frontier_cells", 8)
        self.declare_parameter("goal_period_s", 8.0)
        self.declare_parameter("occupied_threshold", 55)
        self.declare_parameter("unknown_value", -1)

        self._map: Optional[OccupancyGrid] = None
        self._active_goal = False
        self._navigator = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.create_subscription(
            OccupancyGrid,
            self.get_parameter("map_topic").value,
            self._on_map,
            10,
        )
        self.create_timer(float(self.get_parameter("goal_period_s").value), self._tick)

    def _on_map(self, msg: OccupancyGrid) -> None:
        self._map = msg

    def _tick(self) -> None:
        if self._map is None or self._active_goal:
            return
        if not self._navigator.server_is_ready():
            self.get_logger().info("Waiting for Nav2 navigate_to_pose action server")
            return

        frontier = self._best_frontier(self._map)
        if frontier is None:
            self.get_logger().info("No usable frontier found yet")
            return

        goal = self._cell_to_pose(self._map, frontier)
        nav_goal = NavigateToPose.Goal()
        nav_goal.pose = goal
        self._active_goal = True
        self.get_logger().info(
            f"Exploring frontier at x={goal.pose.position.x:.2f}, y={goal.pose.position.y:.2f}"
        )
        future = self._navigator.send_goal_async(nav_goal)
        future.add_done_callback(self._on_goal_accepted)

    def _on_goal_accepted(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self._active_goal = False
            self.get_logger().warn("Frontier goal was rejected")
            return
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_goal_finished)

    def _on_goal_finished(self, future) -> None:
        self._active_goal = False
        status = future.result().status
        self.get_logger().info(f"Frontier goal finished with status {status}")

    def _best_frontier(self, grid: OccupancyGrid) -> Optional[Cell]:
        width = grid.info.width
        height = grid.info.height
        data = grid.data
        unknown_value = int(self.get_parameter("unknown_value").value)
        min_size = int(self.get_parameter("min_frontier_cells").value)

        frontiers: list[tuple[list[Cell], list[Cell]]] = []
        visited: set[Cell] = set()
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                start = Cell(x, y)
                if start in visited or not self._is_frontier_cell(data, width, start, unknown_value):
                    continue
                cluster = self._grow_frontier(data, width, height, start, visited, unknown_value)
                goal_cells = self._free_neighbors(data, width, height, cluster)
                if len(cluster) >= min_size and goal_cells:
                    frontiers.append((cluster, goal_cells))

        if not frontiers:
            return None

        origin_x = grid.info.origin.position.x
        origin_y = grid.info.origin.position.y
        resolution = grid.info.resolution

        def score(frontier: tuple[list[Cell], list[Cell]]) -> float:
            cluster, goal_cells = frontier
            centroid = self._centroid(goal_cells)
            wx = origin_x + (centroid.x + 0.5) * resolution
            wy = origin_y + (centroid.y + 0.5) * resolution
            distance_penalty = math.hypot(wx, wy) * 0.15
            return len(cluster) - distance_penalty

        _, best_goal_cells = max(frontiers, key=score)
        return self._centroid(best_goal_cells)

    def _grow_frontier(
        self,
        data: Iterable[int],
        width: int,
        height: int,
        start: Cell,
        visited: set[Cell],
        unknown_value: int,
    ) -> list[Cell]:
        cluster: list[Cell] = []
        queue = [start]
        while queue:
            cell = queue.pop()
            if cell in visited:
                continue
            visited.add(cell)
            if not self._is_frontier_cell(data, width, cell, unknown_value):
                continue
            cluster.append(cell)
            for neighbor in self._neighbors4(cell):
                if 0 < neighbor.x < width - 1 and 0 < neighbor.y < height - 1:
                    queue.append(neighbor)
        return cluster

    def _is_frontier_cell(
        self,
        data: Iterable[int],
        width: int,
        cell: Cell,
        unknown_value: int,
    ) -> bool:
        idx = cell.y * width + cell.x
        if data[idx] != unknown_value:
            return False
        return any(data[n.y * width + n.x] == 0 for n in self._neighbors4(cell))

    def _free_neighbors(
        self,
        data: Iterable[int],
        width: int,
        height: int,
        cluster: list[Cell],
    ) -> list[Cell]:
        free: set[Cell] = set()
        for cell in cluster:
            for neighbor in self._neighbors4(cell):
                if 0 < neighbor.x < width - 1 and 0 < neighbor.y < height - 1:
                    if data[neighbor.y * width + neighbor.x] == 0:
                        free.add(neighbor)
        return list(free)

    @staticmethod
    def _neighbors4(cell: Cell) -> tuple[Cell, Cell, Cell, Cell]:
        return (
            Cell(cell.x + 1, cell.y),
            Cell(cell.x - 1, cell.y),
            Cell(cell.x, cell.y + 1),
            Cell(cell.x, cell.y - 1),
        )

    @staticmethod
    def _centroid(cells: list[Cell]) -> Cell:
        return Cell(
            round(sum(cell.x for cell in cells) / len(cells)),
            round(sum(cell.y for cell in cells) / len(cells)),
        )

    def _cell_to_pose(self, grid: OccupancyGrid, cell: Cell) -> PoseStamped:
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self.get_parameter("goal_frame").value
        pose.pose.position.x = grid.info.origin.position.x + (cell.x + 0.5) * grid.info.resolution
        pose.pose.position.y = grid.info.origin.position.y + (cell.y + 0.5) * grid.info.resolution
        pose.pose.orientation.w = 1.0
        return pose


def main() -> None:
    rclpy.init()
    node = FrontierExplorer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
