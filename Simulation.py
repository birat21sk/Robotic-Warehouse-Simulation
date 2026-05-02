#
## Simulation.py - Main simulation loop for multi-robot goods collection in a warehouse environment.
#
import csv
import os.path

import matplotlib.pyplot as plt
import matplotlib.patches as pltpatch

from WareHouseSpace import WareHouseSpace as Warehouse
from constants import (
    ROBOT_ALL_STATES,
    EMPTY_COLOUR,
    SHELF_COLOUR,
    ROBOT_COLOURS,
    GOOD_COLOUR,
    STATE_COLOURS,
    CELL_SHELF,
)


class Simulation:
    """
    Main simulation loop for multi-robot goods collection in a warehouse environment.
    """

    def __init__(
        self,
        warehouse: Warehouse,
        max_steps: int = 300,
        delay: float = 0.05,
        animate: bool = True,
    ):
        self.warehouse = warehouse
        self.max_time_steps = max_steps
        self.delay = delay
        self.animate = animate
        self.step = 0

        self.hist_steps = []
        self.hist_delivered = []
        self.hist_available = []
        self.hist_states = {state: [] for state in ROBOT_ALL_STATES}

    def run(self):
        """
        Run the simulation until max time steps are reached or all goods are delivered.
        """
        if self.animate:
            plt.ion()  # Enable interactive mode for real-time rendering

        fig = self._create_fig()

        while self.step < self.max_time_steps and not self.warehouse.all_done():
            self.warehouse.step()  # Advance the simulation by one time step
            self.step += 1
            self._record_step()
            if self.animate:
                self._redraw(fig)
                plt.pause(self.delay)

        self._redraw(fig)
        self._summary()

        if self.animate:
            plt.ioff()
            plt.show()
        else:
            fig.savefig("warehouse_final.png")
            print("Final frame saved to warehouse_final.png")

    def _summary(self):
        wh = self.warehouse
        print()
        print("=" * 50)
        print("SIMULATION SUMMARY")
        print("=" * 50)
        print(f"Robots              : {len(wh.robots)}")
        print(f"Goods               : {len(wh.goods)}")
        print(f"Total time steps    : {self.step}")
        print(f"Total delivered     : {wh.total_delivered}")
        print(f"Remaining goods     : {wh.count_available_goods()}")
        print("*" * 50)
        for rob in wh.robots:
            print(f"{rob}")
        print("=" * 50)

    def _record_step(self):
        """
        Add current stat to the history lists for plotting.
        """
        warehouse = self.warehouse
        self.hist_steps.append(self.step)  # Record the current time step
        self.hist_delivered.append(
            warehouse.total_delivered
        )  # Record the total number of goods delivered so far
        self.hist_available.append(
            warehouse.count_available_goods()
        )  # Record the number of goods that are still available (not collected yet)

        for state, lst in self.hist_states.items():
            lst.append(
                warehouse.robot_state_count()[state]
            )  # Record the count of robots in each state at the current time step

    def _create_fig(self):
        """Initialise figure."""
        fig = plt.figure(figsize=(15, 7))
        fig.suptitle("Warehouse simulation", fontsize=12, fontweight="bold")
        return fig

    def _redraw(self, fig):
        """Redraw the figure with the current state of the warehouse and the history plots."""
        fig.clf()  # Clear the figure to redraw

        warehouse = self.warehouse

        plt_grid = fig.add_gridspec(2, 3, wspace=0.5, hspace=0.5)

        map = fig.add_subplot(plt_grid[:, :2])  # Spans both rows, first two columns
        deliveries = fig.add_subplot(
            plt_grid[0, 2]
        )  # Delivery stat, First row, third column
        stat = fig.add_subplot(plt_grid[1, 2])  # Robot state, Second row, third column

        self._draw_map(map, warehouse)
        self._draw_deliveries(deliveries)
        self._draw_states(stat)

    def _draw_map(self, ax, wh):
        """
        Draw warehouse grid map with shelves, goods and robots.
        """
        ax.set_xlim(-0.5, wh.width - 0.5)
        ax.set_ylim(-0.5, wh.height - 0.5)
        ax.set_aspect("equal")
        ax.set_facecolor(EMPTY_COLOUR)
        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        ax.set_title(
            f"Step {self.step} - Delivered ${wh.total_delivered} - Remaining ${wh.count_available_goods()}",
            fontsize=10,
        )

        # Draw shelf cells
        for y in range(wh.height):
            for x in range(wh.width):
                if wh.grid[y][x] == CELL_SHELF:
                    ax.add_patch(
                        plt.Rectangle(
                            (x - 0.5, y - 0.5), 1, 1, color=SHELF_COLOUR, zorder=1
                        )
                    )

        # Mark home corners
        for idx, (cx, cy) in enumerate(wh.corners):
            ax.add_patch(
                plt.Rectangle(
                    (cx - 0.5, cy - 0.5),
                    1,
                    1,
                    color=ROBOT_COLOURS[idx % 4],
                    alpha=0.25,
                    zorder=2,
                )
            )

        # Draw Good
        for good in wh.goods:
            if good.available:
                ax.plot(
                    good.x,
                    good.y,
                    "o",
                    color=GOOD_COLOUR,
                    markersize=7,
                    markeredgecolor="darkorange",
                    zorder=3,
                )

        # Draw Robots
        for robot in wh.robots:
            color = ROBOT_COLOURS[robot.corner_idx % 4]
            marker = "s" if robot.carrying else "^"
            ax.plot(
                robot.x,
                robot.y,
                marker=marker,
                color=color,
                zorder=4,
                markersize=11,
                markeredgewidth=0.6,
                markeredgecolor="black",
            )
            ax.text(
                robot.x,
                robot.y + 0.3,
                str(robot.robot_id),
                ha="center",
                va="bottom",
                fontsize=6,
                color="black",
                zorder=5,
            )

        legend_elements = [
            pltpatch.Patch(facecolor=SHELF_COLOUR, label="Shelf"),
            pltpatch.Patch(facecolor=GOOD_COLOUR, label="Goods"),
        ]
        for idx, _ in enumerate(wh.corners):
            legend_elements.append(
                pltpatch.Patch(
                    facecolor=ROBOT_COLOURS[idx % 4], label=f"Robot - corner {idx}"
                )
            )
        ax.legend(
            handles=legend_elements, loc="upper right", fontsize=6, framealpha=0.8
        )

    def _draw_deliveries(self, ax: plt.Axes):
        """
        Draw the line plot of total deliveries and goods over time.
        """
        ax.set_title("Goods over time", fontsize=8)
        ax.set_xlabel("Time", fontsize=8)
        ax.set_ylabel("Count", fontsize=8)
        ax.tick_params(labelsize=6)
        ax.grid(True, alpha=0.2)

        if self.hist_steps:
            ax.plot(
                self.hist_steps,
                self.hist_delivered,
                label="Delivered",
                color="green",
                linewidth=2,
            )
            ax.plot(
                self.hist_steps,
                self.hist_available,
                label="Available",
                color="orange",
                linewidth=1.5,
                linestyle="--",
            )
            ax.legend(fontsize=6)

    def _draw_states(self, ax: plt.Axes) -> None:
        """Stacked area chart of robot state counts over time."""
        ax.set_title("Robot state over time", fontsize=8)
        ax.set_xlabel("Timestep", fontsize=8)
        ax.set_ylabel("Robots", fontsize=8)
        ax.tick_params(labelsize=6)
        ax.grid(True, alpha=0.2)

        if not self.hist_steps:
            return

        timestep = self.hist_steps
        bottom = [0.0] * len(timestep)

        for state in ROBOT_ALL_STATES:
            vals = self.hist_states[state]
            top = [b + v for b, v in zip(bottom, vals)]
            ax.fill_between(
                timestep,
                bottom,
                top,
                alpha=0.5,
                color=STATE_COLOURS[state],
                label=state,
            )
            bottom = top
        ax.legend(fontsize=6, loc="upper left")

    def save_stats_to_csv(self, file):
        """
        Write per-timestamp stat to *filepath* as a csv file.
        """
        if not os.path.exists("summaries"):
            os.makedirs("summaries")

        filepath = os.path.join("summaries", file)
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["timestep", "delivered", "available"] + list(ROBOT_ALL_STATES)
            )

            for i in range(self.step):
                writer.writerow(
                    [
                        i + 1,
                        self.hist_delivered[i],
                        (self.hist_available[i]),
                        *[self.hist_states[s][i] for s in ROBOT_ALL_STATES],
                    ]
                )
