# Robotic Warehouse Simulation
---

## Files
.
├── Good.py - defines the `Good` class representing items to be collected and delivered.
├── README - this file, providing an overview of the project, instructions, and design notes.
├── Robot.py - defines the `Robot` class representing the autonomous agents that collect and deliver goods.
├── Simulation.py - contains the main `Simulation` class that orchestrates the warehouse simulation.
├── WareHouseSpace.py - defines the `WarehouseSpace` class representing the grid-based warehouse environment.
├── compare_summaries.py - script to generate a comparison chart from multiple summary CSV files.
├── constants.py - defines constant values used across the simulation (e.g. robot states, colors).
├── params - directory containing parameter CSV files for different simulation scenarios.
│       ├── params1.csv
│       ├── params2.csv
│       └── params3.csv
├── summaries - directory for output statistics and visualisations from simulations.
│       ├── comparison.png
│       ├── summary.csv
│       ├── summary1.csv
│       ├── summary2.csv
│       └── summary3.csv
├── terrains - directory containing terrain CSV files defining the warehouse layouts.
│       ├── map1.csv
│       └── map2.csv
├── warehouse.py - main script to run the warehouse simulation, supporting both interactive and batch modes.
└── warehouse_final.png - final frame of the simulation when run.

3 directories, 19 files

---

## Dependencies

- Python 3.10 or newer
- `csv` (standard library)
- `os` (standard library)
- `random` (standard library)
- `collection` (standard library)
- `matplotlib` (`pip install matplotlib`)
- `numpy` (`pip install numpy`)  *(used implicitly by matplotlib)*

---

## How to Run

### Interactive Mode
Prompts you for all parameters at the terminal:

```
python3 warehouse.py -i
```

You will be asked for:
- Warehouse width and height (number of columns / rows)
- Number of robots  (any positive integer; >4 robots share corners)
- Number of goods
- Maximum simulation ticks
- Animation delay in seconds (e.g. `0.05`)

### Batch Mode
Load terrain and parameters from CSV files:

```
python3 warehouse.py -f ./terrains/map1.csv -p ./params/params1.csv
```

### Optional Flags (both modes)

| Flag                          | Description                                                          |
|-------------------------------|----------------------------------------------------------------------|
| `--save-terrain  output.csv`  | Save the generated terrain grid to CSV before running                |
| `--save-stats stats.csv`      | Save per-tick statistics to CSV after running                        |
| `--no-animation`              | Skip real-time animation; saves final frame as `warehouse_final.png` |

### Reproducing the Three Showcase Scenarios

```bash
# Simulation 1 – standard, 4 robots, 20 goods on a 20×15 map
python3 warehouse.py -f ./terrains/map1.csv -p ./params/params1.csv --save-stats summary1.csv --no-anim

# Simulation 2 – high load, 8 robots, 40 goods on a 20×15 map
python3 warehouse.py -f ./terrains/map1.csv -p ./params/params2.csv --save-stats summary2.csv --no-anim

# Simulation 3 – sparse, 2 robots, 30 goods on a compact 12×10 map
python3 warehouse.py -f ./terrains/map2.csv -p ./params/params3.csv --save-stats summary3.csv --no-anim

# Generate comparison chart of all three scenarios
python3 compare_summaries.py
```

### Parameter CSV Format

Each row has two columns: `key, value`.  Recognised keys:

| Key              | Default | Description                                        |
|------------------|---------|----------------------------------------------------|
| `num_robots`     | 4       | Number of robots                                   |
| `num_goods`      | 20      | Number of goods to place                           |
| `max_time_steps` | 300     | Maximum simulation ticks                           |
| `anim_delay`     | 0.05    | Seconds between animated frames                    |
| `animate`        | false   | `true` to enable real-time animation in batch mode |
| `seed`           | —       | Integer random seed for reproducibility            |

### Map CSV Format

Rows correspond to grid rows (y=0 is the top row in the file).
Values: `0` = walkable cell, `1` = shelf (obstacle).

To generate and save a fresh terrain grid:

```bash
python3 warehouse.py -i --save-terrain my_map.csv
```

---

## Visualisation

The simulation window shows three subplots:

1. **Warehouse map** (left): grid with brown shelves, gold goods (circles),
   and coloured robots (triangles = empty-handed, squares = carrying).
   Home corners are shaded in the robot's colour.
2. **Goods over time** (top right): cumulative deliveries (green) and
   remaining available goods (orange dashed).
3. **Robot states over time** (bottom right): stacked area chart of how
   many robots are in each state (idle / to_good / collecting / returning)
   each timestep.

---

## Design Notes

- **Pathfinding**: BFS on the static terrain grid.  Results are cached by
  `(start, end)` so each unique route is computed at most once.
- **Reservation**: When a robot selects a target good it sets
  `good.reserved_by = robot_id`.  Other robots skip reserved goods.
  If a robot's path is abandoned, the reservation is released.
- **Overlap**: Robots may occupy the same cell simultaneously.
- **Multiple goods per cell**: represented as separate `Good` objects with
  identical coordinates.
- **Robots > 4**: extra robots share corners; up to `n_robots // 4` robots
  can start at each corner.
