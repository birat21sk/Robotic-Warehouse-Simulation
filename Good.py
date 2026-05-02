#
## Good.py - Definition of the Good class representing collectable items in the warehouse.
#

class Good:
    """
    A single collectable good in the warehouse, located at a specific (x, y) coordinate.
    """

    def __init__(self, x: int, y: int):
        self.x = x  # x-coordinate of the good's location in the grid
        self.y = y  # y-coordinate of the good's location in the grid
        self.available = True  # True if the good is available for collection, False if it has been reserved or collected
        self.reserved_by = None  # robot_id of the robot that has reserved this good, or None if it is not reserved

    def reserve(self, robot_id: int):
        """Reserve this good for a specific robot_id, marking it as unavailable."""
        self.reserved_by = robot_id

    def release(self):
        """Cancel a reservation without collecting (robot abandoned target)."""
        self.reserved_by = None

    def collect(self):
        """Mark this good as collected, making it unavailable and clearing any reservation."""
        self.available = False
        self.reserved_by = None

    def is_free(self, robot_id: int):
        """Check if this good is available for collection by a specific robot_id."""
        not_or_self_reserved = self.reserved_by is None or self.reserved_by == robot_id
        return self.available and not_or_self_reserved

    def __repr__(self):
        status = "available" if self.available else "collected"
        return f"Good @ ({self.x},{self.y}) is {status}, reserved by{self.reserved_by})"
