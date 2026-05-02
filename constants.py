#
## constants.py - Constants for warehouse simulation, including cell types, robot states and color palette.
#

# --- Cell type constants
CELL_EMPTY = 0  # walkable aisle cell
CELL_SHELF = 1  # obstacle / shelf unit

# --- Robot state constants
ROBOT_STATE_IDLE = "idle"  # no current assignment
ROBOT_STATE_TO_GOOD = "to_good"  # travelling toward a targeted good
ROBOT_STATE_COLLECTING = "collecting"  # arrived; picking up the good this tick
ROBOT_STATE_RETURNING = "returning"  # carrying a good back to home corner

# --- Colour palette
ROBOT_COLOURS = ["dodgerblue", "tomato", "limegreen", "orchid"]
SHELF_COLOUR = (0.55, 0.35, 0.10)  # dark brown
GOOD_COLOUR = (1.00, 0.85, 0.00)  # gold
EMPTY_COLOUR = (0.95, 0.95, 0.95)  # off-white

STATE_COLOURS = {
    ROBOT_STATE_IDLE: "lightgrey",
    ROBOT_STATE_TO_GOOD: "dodgerblue",
    ROBOT_STATE_COLLECTING: "gold",
    ROBOT_STATE_RETURNING: "tomato",
}

ROBOT_ALL_STATES = (
    ROBOT_STATE_IDLE,
    ROBOT_STATE_TO_GOOD,
    ROBOT_STATE_COLLECTING,
    ROBOT_STATE_RETURNING,
)

INPUT_TYPE_INT = 'int'
INPUT_TYPE_FLOAT = 'float'