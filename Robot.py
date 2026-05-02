#
## Robot.py - Robot class representing an individual robot in the warehouse simulation.
#

from constants import (
    ROBOT_STATE_IDLE,
    ROBOT_STATE_TO_GOOD,
    ROBOT_STATE_COLLECTING,
    ROBOT_STATE_RETURNING,
)


class Robot:
    """
    A class to represent a robot in a 2D grid.
    The robot  follows a four-state cycle:
    idle  →  to_good  →  collecting  →  returning  →  idle  → …

    The robot uses BFS trails pre-computed by the Warehouse instance and
    reserves its target Good to prevent race-conditions with other robots.
    """

    def __init__(self, robot_id: int, home_x: int, home_y: int, corner_idx: int = 0):
        self.robot_id = robot_id  # unique identifier for the robot
        self.x = home_x  # initial x-coordinate (home corner)
        self.y = home_y  # initial y-coordinate (home corner)
        self.home_x = home_x  # x-coordinate of the robot's home corner (where it starts and returns to)
        self.home_y = home_y  # y-coordinate of the robot's home corner (where it starts and returns to)
        self.corner_idx = corner_idx  # index of the robot's home corner (0 to 3, corresponding to the four corners of the grid)
        self.target = None  # current Good being pursued
        self.trail = []  # current trail to target, as a list of (x, y) coordinates
        self.carrying = False  # True if the robot is currently carrying a Good
        self.deliveries = 0  # number of successful deliveries made by the robot
        self.state = ROBOT_STATE_IDLE  # current state of the robot: 'idle', '

    def step(self, warehouse):
        """Advance the robot by one simulation tick"""
        if self.state == ROBOT_STATE_IDLE:
            self._find_and_pick_new_target(warehouse)

        elif self.state == ROBOT_STATE_TO_GOOD:
            if not self._check_is_target_valid():
                self._abandon_the_target()
                return
            self._move_one_step()
            # If the robot has arrived at the target Good's location, transition to the collecting state
            if self.target and (self.x, self.y) == (self.target.x, self.target.y):
                self.state = ROBOT_STATE_COLLECTING

        elif self.state == ROBOT_STATE_COLLECTING:
            # If the target Good is still available and reserved by this robot, collect it and mark the robot as carrying a good.
            if self.target and self.target.is_free(self.robot_id):
                self.target.collect()
                self.carrying = True
            self.target = None

            # Find the trail back to the home corner and transition to the returning state.
            trail_to_home_corner = warehouse.find_trail(
                self.x, self.y, self.home_x, self.home_y
            )
            self.trail = (
                trail_to_home_corner if trail_to_home_corner is not None else []
            )
            self.state = ROBOT_STATE_RETURNING

        elif self.state == ROBOT_STATE_RETURNING:
            self._move_one_step()  # Move one step towards the home corner
            # If the robot has arrived back at the home corner, check if it is carrying a good.
            # If so, increment the deliveries count and update the warehouse's total delivered count.
            if (self.x, self.y) == (self.home_x, self.home_y):
                if self.carrying:
                    self.deliveries += 1
                    warehouse.total_delivered += 1
                self.carrying = False
                self.trail = []
                self.state = ROBOT_STATE_IDLE

    def _move_one_step(self):
        """Move the robot one step along its current trail, if any."""
        if self.trail:
            self.x, self.y = self.trail.pop(0)

    def _check_is_target_valid(self):
        """Check if the robot's current target Good is still available and reserved by this robot."""
        return (
            self.target is not None
            and self.target.available
            and self.target.reserved_by == self.robot_id
        )

    def _abandon_the_target(self):
        """Abandon the current target Good, releasing any reservation and clearing the target and trail."""
        if self.target is not None:
            self.target.release()
        self.target = None
        self.trail = []
        self.state = ROBOT_STATE_IDLE

    def _find_and_pick_new_target(self, warehouse):
        optimal_good = None  # Placeholder for the selected target good
        optimal_trail = None  # Placeholder for the trail to the selected target good
        optimal_steps = float(
            "inf"
        )  # Initialize the minimum steps to infinity to ensure any valid trail will be shorter

        for good in warehouse.goods:
            if good.is_free(self.robot_id):
                manhattan_distance = abs(good.x - self.x) + abs(good.y - self.y)

                if manhattan_distance < optimal_steps:
                    trail = warehouse.find_trail(self.x, self.y, good.x, good.y)
                    # If a valid trail exists and is shorter than the current minimum steps, update the target good, trail, and steps
                    if trail is not None and len(trail) < optimal_steps:
                        optimal_steps = len(trail)
                        optimal_good = good
                        optimal_trail = trail

        if optimal_good is not None:
            optimal_good.reserve(
                self.robot_id
            )  # Reserve the selected good for this robot
            self.target = optimal_good  # Set the target to the selected good
            self.trail = optimal_trail  # Set the trail to the selected good
            self.state = ROBOT_STATE_TO_GOOD  # Update the state to indicate the robot is now heading towards a good

    # Print a human-readable string representation of the robot's current status, including its ID, position, state, and delivery count.
    def __repr__(self) -> str:
        return (
            f"Robot {self.robot_id} @({self.x},{self.y})"
            f" state={self.state} deliveries={self.deliveries}"
        )
