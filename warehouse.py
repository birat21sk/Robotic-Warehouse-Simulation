import csv
import random
import argparse

from Simulation import Simulation
from WareHouseSpace import WareHouseSpace as Warehouse
from constants import INPUT_TYPE_INT, INPUT_TYPE_FLOAT


def init_interactive_mode():
    """
    Initialize the simulation in interactive mode by prompting the user for parameters.
    """
    print()
    print("=" * 50)
    print("Welcome to the Robotic Warehouse Simulation!")
    print("=" * 50)

    def prompt_input(msg, default, in_type=INPUT_TYPE_INT, positive_only=True):
        """Helper function to prompt for input with validation and default value."""
        inp = input(f" {msg} [default: {default}]: ").strip()
        try:
            if inp == "":
                return default
            val = float(inp) if in_type == INPUT_TYPE_FLOAT else int(inp)
            if positive_only and val < 0:
                print("  Please enter a positive value.")
                return prompt_input(msg, default, in_type, positive_only)
            return val
        except ValueError:
            print("  Invalid input. Please enter a valid number.")
            return prompt_input(msg, default, in_type, positive_only)

    width = prompt_input(
        "Enter Warehouse width (number of columns): ", 20, INPUT_TYPE_INT
    )
    height = prompt_input(
        "Enter Warehouse height (number of rows): ", 15, INPUT_TYPE_INT
    )
    num_robots = prompt_input("Enter number of robots: ", 4, INPUT_TYPE_INT)
    num_goods = prompt_input("Enter number of goods: ", 20, INPUT_TYPE_INT)
    max_time_steps = prompt_input(
        "Enter maximum number of time steps to run the simulation: ",
        float("inf"),
        INPUT_TYPE_INT,
    )
    anim_delay = prompt_input(
        "Enter animation delay in seconds (set to 0 for no animation): ",
        0.05,
        INPUT_TYPE_FLOAT,
    )

    wh = Warehouse.create_from_dimensions(width, height)
    wh.add_goods(num_goods)
    wh.add_robots(num_robots)

    sim = Simulation(wh, max_time_steps, anim_delay, animate=(anim_delay > 0))
    return wh, sim


def init_batch_mode(csv_file, params_file):
    """
    Initialize the simulation in batch mode by reading the warehouse layout and parameters from CSV files.
    """
    wh = Warehouse.generate_from_csv(csv_file)

    params = {}
    with open(params_file, mode="r") as f:
        for line in csv.reader(f):
            if len(line) >= 2:
                params[line[0].strip()] = line[1].strip()
    seed = params.get("seed")
    if seed is not None:
        random.seed(seed)

    num_robots = int(params.get("num_robots", 4))
    num_goods = int(params.get("num_goods", 20))
    max_time_steps = int(params.get("max_time_steps")) or float("inf")
    anim_delay = float(params.get("anim_delay", 0.05))
    animate = params.get("animate", "false").lower() == "true"

    wh.add_robots(num_robots)
    wh.add_goods(num_goods)

    sim = Simulation(wh, max_time_steps, anim_delay, animate=animate)
    return wh, sim


def main():
    """
    Main entry point for the warehouse simulation.
    """
    parser = argparse.ArgumentParser(
        prog="warehouse.py",
        description="Robotic Warehouse Simulation - COMP5005",
    )

    # Ensure that only one of the following options can be provided
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run the simulation with interactive mode (get parameters from input).",
    )

    group.add_argument(
        "-f",
        "--csv-file",
        metavar="CSV_MAP_FILE",
        help="Path to CSV map/terrain file (enables batch mode with parameters read from the specified file).",
    )

    parser.add_argument(
        "-p",
        "--params-file",
        metavar="PARAMS_CSV_FILE",
        help="Path to parameters CSV file (required with -f)",
    )

    parser.add_argument(
        "--save-terrain",
        metavar="OUTPUT_CSV_FILE",
        help="Sace the map grid to a CSV file before running",
    )

    parser.add_argument(
        "--save-stats",
        metavar="STATS_CSV_FILE",
        help="Save the per-timestep simulation statistics to a CSV file after running inside summaries folder",
    )

    parser.add_argument(
        "--no-animation",
        action="store_true",
        help="Disable animation for faster execution (useful for batch mode or when visualization is not needed). Saves final frame as PNG instead.",
    )

    args = parser.parse_args()  # Parse command-line arguments

    if args.interactive:
        wh, sim = init_interactive_mode()
        if args.no_animation:
            sim.animate = False
    else:
        if args.params_file is None:
            parser.error(
                "The -p / --params-file argument is required when using -f / --csv-file."
            )
        wh, sim = init_batch_mode(args.csv_file, args.params_file)
        if args.no_animation:
            sim.animate = False

    if args.save_terrain:
        wh.save_map_to_csv(args.save_terrain)
        print(f"Terrain saved to {args.save_terrain}")

    print(wh)
    for robot in wh.robots:
        print(robot)

    sim.run()

    summary_file = args.save_stats if args.save_stats else "summary.csv"
    sim.save_stats_to_csv(summary_file)
    print(f"Simulation statistics saved to {summary_file}")


if __name__ == "__main__":
    main()
