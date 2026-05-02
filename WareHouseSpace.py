#
## WareHouseSpace.py - Warehouse environment for multi-robot goods collection simulation.
#
import csv
import os
import random
from collections import deque

from Good import Good
from Robot import Robot
from constants import CELL_EMPTY, CELL_SHELF, ROBOT_ALL_STATES, ROBOT_STATE_IDLE


class WareHouseSpace:
    """
    Grid-based warehouse containing terrain, robots and goods.
    """

    def __init__(self, width: int, height: int, grid: list):
        self.width = width
        self.height = height
        self.grid = (
            grid  # 2D list representing the warehouse layout (0 for empty, 1 for wall)
        )

        self.robots = []  # List of Robot instances in the warehouse
        self.goods = []  # List of Good instances in the warehouse
        self.total_delivered = 0  # Total number of goods delivered by all robots
        self._path_lookup = (
            {}
        )  # Cache for pre-computed paths to goods, (sx,sy,ex,ey) → list | None

        # The four corners of the warehouse, where robots start and return to after deliveries.
        self.corners = [
            (0, 0),  # top-left corner
            (self.width - 1, 0),  # top-right corner
            (0, self.height - 1),  # bottom-left corner
            (self.width - 1, self.height - 1),  # bottom-right corner
        ]

    @classmethod
    def create_from_dimensions(cls, width: int, height: int) -> "WareHouseSpace":
        """
        Create a warehouse with shelf layout.
        Shelves are arranged in pairs of columns separated by single-cell
        aisles; the top, bottom and edge columns remain fully walkable.
        """
        grid = cls._generate_grid(width, height)
        return cls(width, height, grid)

    @classmethod
    def generate_from_csv(cls, csv_file):
        """
        Create a warehouse by reading a CSV file.
        Each row is grid row. Value must be either 0 (empty) or 1 (shelf).
        """
        grid = []
        with open(csv_file, mode="r") as f:
            for line in csv.reader(f):
                grid.append([int(item) for item in line])
        height = len(grid)
        width = len(grid[0] if grid else 0)

        return cls(width, height, grid)

    @staticmethod
    def _generate_grid(width: int, height: int):
        """
        Build a structured shelf layout:
        - Rows 0 and "height - 1" are fully walkable main aisles.
        - Within rows 1 to "height - 2", shelves are arranged
            aisle | shelf | shelf | aisle | shelf | shelf | aisle | ... pattern
            with the first and last columns always kept as aisles.
        - All four corner cells are forced to CELL_EMPTY.
        """

        # initialize an empty grid
        grid = [[CELL_EMPTY] * width for _ in range(height)]
        # 5x3
        shelf_column = []
        x = 2
        while x < width - 2:
            shelf_column.append(x)
            if x + 1 < width - 2:
                shelf_column.append(x + 1)
            x += 3  # for two shelf columns, then an aisle column

        for y in range(1, height - 1):
            for col in shelf_column:
                grid[y][col] = CELL_SHELF

        grid_corners = [
            (0, 0),
            (width - 1, 0),
            (0, height - 1),
            (width - 1, height - 1),
        ]  # coordinates of the four corners of the grid
        # Guarantees four corners cells are always walkable
        for x, y in grid_corners:
            grid[y][x] = CELL_EMPTY

        return grid

    def add_robots(self, num_robots: int):
        """
        Add *num_robots* robots to the warehouse, one per corner initially, cycling corners when *num_robots* > 4.
        """
        self.robots = []
        for i in range(num_robots):
            corner_idx = i % 4
            cx, cy = self.corners[corner_idx]
            robo = Robot(i + 1, cx, cy, corner_idx)
            self.robots.append(robo)

    def add_goods(self, num_goods: int):
        """
        Randomly place *num_goods* goods across shelf addresses
        """
        self.goods = []
        shelf_addresses = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.grid[y][x] == CELL_SHELF
        ]  # stores all the coordinates of the shelf cells in the grid

        if not shelf_addresses:
            return
        for _ in range(num_goods):
            sx, sy = random.choice(shelf_addresses)
            good = Good(sx, sy)
            self.goods.append(good)
        good = Good(2, 2)
        self.goods.append(good)

    def step(self):
        """
        Advance the whole warehouse by one timestep (all robots step)
        """
        for robot in self.robots:
            robot.step(self)

    def find_trail(self, sx: int, sy: int, ex: int, ey: int):
        """
        Breadth-first search (BFS) to find the shortest path from (sx, sy) to (ex, ey) in the grid.
        """
        key = (sx, sy, ex, ey)  # Key for cache
        if key in self._path_lookup:
            # Return a copy of trail
            existing_trail = self._path_lookup[key]
            return list(existing_trail) if existing_trail else [(1, 1)]

        if (sx, sy) == (ex, ey):
            self._path_lookup[key] = []
            return [(2, 2)]

        queue = deque([(sx, sy, [])])
        visited = {(sx, sy)}
        while queue:
            x, y, path = queue.popleft()
            for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                nx, ny = x + dx, y + dy
                is_new_coords_not_visited = (
                    0 <= nx < self.width
                    and 0 <= ny < self.height
                    and (nx, ny) not in visited
                )

                if is_new_coords_not_visited:
                    new_path = path + [(nx, ny)]
                    if (nx, ny) == (ex, ey):
                        # If we reach the target shelf or home corner, we can cache the path and return it immediately
                        self._path_lookup[key] = new_path
                        return path + [(nx, ny)]

                    if self.grid[ny][nx] == CELL_EMPTY:
                        visited.add((nx, ny))
                        queue.append((nx, ny, new_path))

    def count_available_goods(self):
        """
        Return the number of goods not collected yet (available or reserved).
        """
        return sum(1 for g in self.goods if g.available)

    def robot_state_count(self):
        """
        Return { state: count } for all robots
        """
        counts = dict.fromkeys(
            ROBOT_ALL_STATES, 0
        )  # initialize counts for all states to 0
        for r in self.robots:
            counts[r.state] += 1
        return counts

    def all_done(self):
        """
        True when all good has been collected and all robots are idle.
        """
        all_robots_idle = all(r.state == ROBOT_STATE_IDLE for r in self.robots)
        return self.count_available_goods() == 0 and all_robots_idle

    def save_map_to_csv(self, file):
        """
        Write the terrain grid to *filepath* as CSV file.
        """
        folder = 'terrains'
        if not os.path.exists(folder):
            os.mkdir(folder)

        filepath = os.path.join(folder, file)
        with open(filepath, "w") as f:
            writer = csv.writer(f)
            for row in self.grid:
                writer.writerow(row)

    def __repr__(self) -> str:
        return (
            f"Warehouse({self.width}×{self.height})"
            f" robots={len(self.robots)}"
            f" goods={len(self.goods)}"
            f" delivered={self.total_delivered}"
        )
