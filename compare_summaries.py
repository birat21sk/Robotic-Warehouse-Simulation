#
## compare_summaries.py
#
import os
import csv

from matplotlib import pyplot as plt


def main():
    folder = "summaries"

    if not os.path.exists(folder):
        print(
            "No summaries folder found. Please run simulations with --save-stats option to generate summary CSV files."
        )
        return

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for i, file in enumerate(os.listdir(folder)):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path) and file_path.endswith(".csv"):
            with open(file_path, "r") as csvfile:
                x, y1, y2 = [], [], []
                for line in csv.DictReader(csvfile, delimiter=","):
                    x.append(int(line["timestep"]))
                    y1.append(int(line["delivered"]))
                    y2.append(int(line["available"]))
                ax[0].plot(x, y1, label=f"Simulation {i+1}: {file}")
                ax[0].set_title("Delivered Goods over timestep")
                ax[0].set_xlabel("Timestep")
                ax[0].set_ylabel("Delivered Goods")

                ax[1].plot(x, y2, label=f"Simulation {i+1}: {file}")
                ax[1].set_title("Available Goods over timestep")
                ax[1].set_xlabel("Timestep")
                ax[1].set_ylabel("Available Goods")

    ax[1].legend()
    ax[1].grid(True)
    ax[0].legend()
    ax[0].grid(True)

    plt.suptitle("Simulation comparison", fontsize=14, fontweight="bold")
    plt.savefig(f"{folder}/comparison.png", bbox_inches="tight")


if __name__ == "__main__":
    main()
