import random
import argparse
import csv
import matplotlib.pyplot as plt
import numpy as np
from buzzness import Bee, Flower, Tree, Barrier
from typing import List, Tuple

# --- Command-Line Argument Parsing ---
def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments to determine simulation mode.

    Returns:
        argparse.Namespace: Parsed arguments with interactive, mapfile, and paramfile.
    """
    parser = argparse.ArgumentParser(description="Bee hive simulation")
    parser.add_argument(
        '-i', '--interactive', action='store_true', help="Run in interactive mode"
    )
    parser.add_argument('-f', '--mapfile', type=str, help="Terrain map file (CSV)")
    parser.add_argument('-p', '--paramfile', type=str, help="Parameters file (CSV)")
    return parser.parse_args()


# --- Terrain Loading ---
def load_map(
    mapfile: str, nectar_amount: int
) -> Tuple[List[Flower], List[Tree], List[Barrier], List[List[int]]]:
    """Load terrain data from a CSV file and initialize the world grid.

    Args:
        mapfile (str): Path to the CSV file containing terrain data.
        nectar_amount (int): Amount of nectar each flower initially holds.

    Returns:
        Tuple: Lists of Flower, Tree, Barrier objects, and the world grid (numpy array).
    """
    # Initialize empty lists for terrain objects
    flowers, trees, barriers = [], [], []
    # Create a 40x35 world grid, where each cell represents a terrain type
    world = np.zeros((40, 35), dtype=int)

    # Read the map file and process each row
    with open(mapfile, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            x, y = int(row[1]), int(row[2])
            # Skip positions outside the world boundaries
            if x >= 40 or y >= 35 or x < 0 or y < 0:
                continue
            # Create Flower objects and mark their positions
            if row[0] == 'flower':
                flowers.append(Flower((x, y), row[3], row[4], nectar_amount))
                world[x, y] = 1  # Mark as flower (1)
            # Create Tree objects with associated flowers
            elif row[0] == 'tree':
                tree_flowers = [
                    Flower((x, y), f"flower_{i}", "red", nectar_amount)
                    for i in range(3)
                ]
                trees.append(Tree((x, y), tree_flowers))
                world[x, y] = 2  # Mark as tree (2)
            # Create Barrier objects (water or building)
            elif row[0] in ['water', 'building']:
                barriers.append(Barrier((x, y), row[0]))
                # Mark as water (3) or building (4)
                world[x, y] = 3 if row[0] == 'water' else 4

    return flowers, trees, barriers, world


# --- Parameter Loading ---
def load_parameters(paramfile: str) -> dict:
    """Load simulation parameters from a CSV file.

    Args:
        paramfile (str): Path to the CSV file containing parameters.

    Returns:
        dict: Dictionary of parameter names and their values.

    Raises:
        ValueError: If parameters are invalid (e.g., negative values).
        FileNotFoundError: If the parameter file is not found.
    """
    params = {}
    valid_strategies = ['none', 'random', 'intelligent']

    try:
        with open(paramfile, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row
            for row in reader:
                # Handle communication probability (float between 0 and 1)
                if row[0] == 'comm_prob':
                    params[row[0]] = float(row[1])
                    if not (0.0 <= params[row[0]] <= 1.0):
                        raise ValueError(f"Invalid comm_prob: {params[row[0]]}")
                # Validate strategy type
                elif row[0] == 'strategy_type':
                    if row[1] not in valid_strategies:
                        raise ValueError(
                            f"Invalid strategy_type: {row[1]}, must be one of {valid_strategies}"
                        )
                    params[row[0]] = row[1]
                # Handle other parameters (integers or strings)
                else:
                    params[row[0]] = int(row[1]) if row[1].isdigit() else row[1]
                # Ensure numeric parameters are non-negative
                if isinstance(params[row[0]], (int, float)) and params[row[0]] < 0:
                    raise ValueError(f"Invalid parameter {row[0]}: {params[row[0]]}")
    except FileNotFoundError:
        print(f"Error: {paramfile} not found")
        exit(1)

    return params


# --- Hive Visualization ---
def plot_hive(
    hive: List[List[int]], blist: List[Bee], ax: plt.Axes, bees_only: bool = False
) -> None:
    """Plot the hive view with bees and comb structure.

    Args:
        hive (List[List[int]]): 2D array representing the hive's state.
        blist (List[Bee]): List of Bee objects to plot.
        ax (plt.Axes): Matplotlib axes to plot on.
        bees_only (bool): If True, plot only bees (Task 1); otherwise, include comb.
    """
    # Extract positions of bees inside the hive
    xvalues = [b.get_pos()[0] for b in blist if b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if b.get_inhive()]

    if not bees_only:
        # Create a display array for the hive with comb and honey
        hive_display = np.zeros_like(hive)
        hive_display[:, 10:15] = 10  # Set center stripe as comb (not ready)
        # Add alternating honey cells in the comb
        for i in range(len(hive)):
            for j in range(10, 15, 2):
                hive_display[i, j] = 5  # Full honey cells
        # Plot the hive with a yellow-orange-brown colormap
        ax.imshow(hive_display.T, cmap='YlOrBr', origin='lower', vmin=0, vmax=10)
        # Add a vertical dashed line to indicate comb boundary
        ax.axvline(x=15, color='orange', linestyle='--', linewidth=2)
        ax.set_facecolor('#4A2C2A')  # Set background to dark brown
        ax.set_title('Bee Hive')
    else:
        # For Task 1: Plot only bees on a white background
        ax.set_facecolor('white')
        ax.set_title('Bees in Hive (Task 1)')

    # Scatter plot bees as yellow circles
    ax.scatter(xvalues, yvalues, c='yellow', marker='o', label='Bees')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.legend()


# --- World Visualization ---
def plot_world(
    world: List[List[int]], blist: List[Bee], hive_pos: Tuple[int, int], ax: plt.Axes
) -> None:
    """Plot the world view with terrain, bees, and hive.

    Args:
        world (List[List[int]]): 2D array representing the world grid.
        blist (List[Bee]): List of Bee objects to plot.
        hive_pos (Tuple[int, int]): Position of the hive.
        ax (plt.Axes): Matplotlib axes to plot on.
    """
    # Extract positions of bees outside the hive
    xvalues = [b.get_pos()[0] for b in blist if not b.get_inhive()]
    yvalues = [b.get_pos()[1] for b in blist if not b.get_inhive()]

    # Define a custom colormap for terrain types
    custom_cmap = plt.cm.colors.ListedColormap(
        ['lightgreen', 'green', 'pink', 'blue', 'gray']
    )
    bounds = [0, 1, 2, 3, 4, 5]
    norm = plt.cm.colors.BoundaryNorm(bounds, custom_cmap.N)

    # Plot the world grid with terrain colors
    ax.imshow(world.T, cmap=custom_cmap, norm=norm, origin='lower')

    # Plot the hive as a white square with an orange dot in the center
    ax.scatter(hive_pos[0], hive_pos[1], c='white', marker='s', s=100, label='Hive')
    ax.scatter(hive_pos[0], hive_pos[1], c='orange', marker='o', s=20)

    # Plot bees as yellow circles
    ax.scatter(xvalues, yvalues, c='yellow', marker='o', label='Bees')
    ax.set_title('Property')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.legend()


# --- Hive Initialization ---
def initialize_hive(hive_x: int, hive_y: int) -> np.ndarray:
    """Initialize the hive grid with a comb pattern.

    Args:
        hive_x (int): Width of the hive grid.
        hive_y (int): Height of the hive grid.

    Returns:
        np.ndarray: 2D array representing the initialized hive.
    """
    # Create a hive grid with specified dimensions
    hive = np.zeros((hive_x, hive_y), dtype=int)
    hive[:, 10:15] = 10  # Set center stripe as comb (not ready for honey)
    # Add alternating honey cells in the comb
    for i in range(hive_x):
        for j in range(10, 15, 2):
            hive[i, j] = 5  # Set to full honey (max value)
    return hive


# --- Simulation Class ---
class Simulation:
    """Encapsulate a single bee simulation run with hive and world interactions.

    Attributes:
        num_bees (int): Number of bees in the simulation.
        sim_length (int): Number of timesteps to run.
        mapfile (str): Path to the terrain map file.
        hive_x (int): Width of the hive grid.
        hive_y (int): Height of the hive grid.
        hive_pos (Tuple[int, int]): Position of the hive in the world.
        nectar_amount (int): Initial nectar per flower.
        comm_prob (float): Probability of bees sharing nectar locations.
        strategy_type (str): Strategy for bee movement ('none', 'random', 'intelligent').
        hive_memory (List): Shared nectar locations for intelligent strategy.
    """

    def __init__(
        self,
        num_bees: int,
        sim_length: int,
        mapfile: str,
        hive_x: int,
        hive_y: int,
        hive_pos: Tuple[int, int],
        nectar_amount: int,
        comm_prob: float,
        strategy_type: str
    ):
        """Initialize the simulation with given parameters."""
        self.num_bees = num_bees
        self.sim_length = sim_length
        self.mapfile = mapfile
        self.hive_x = hive_x
        self.hive_y = hive_y
        self.hive_pos = hive_pos
        self.nectar_amount = nectar_amount
        self.comm_prob = comm_prob
        self.strategy_type = strategy_type
        self.hive_memory = []  # Shared memory for intelligent strategy
        self.reset()

    def reset(self) -> None:
        """Reset the simulation state before a new run."""
        # Initialize hive and load terrain
        self.hive = initialize_hive(self.hive_x, self.hive_y)
        self.flowers, self.trees, self.barriers, self.world = load_map(
            self.mapfile, self.nectar_amount
        )
        # Create bees with random positions inside the hive
        self.blist = [
            Bee(
                f"b{i}",
                (random.randint(0, self.hive_x - 1), random.randint(0, self.hive_y - 1))
            )
            for i in range(self.num_bees)
        ]
        self.total_honey = 0
        self.honey_over_time = []
        self.hive_memory = []

    def run(self, interactive: bool = False) -> Tuple[int, List[int]]:
        """Run the simulation for the specified number of timesteps.

        Args:
            interactive (bool): If True, enable interactive visualization.

        Returns:
            Tuple[int, List[int]]: Total honey collected and honey per timestep.
        """
        if interactive:
            plt.ion()  # Enable interactive plotting mode

            # Task 1: Plot bees only in the hive
            fig1, ax1 = plt.subplots(figsize=(6, 5))
            plot_hive(self.hive, self.blist, ax1, bees_only=True)
            fig1.savefig('task1.png')
            plt.close(fig1)

            # Task 2: Plot hive with comb in two columns
            fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))
            plot_hive(self.hive, self.blist, axes2[0])
            plot_hive(self.hive, self.blist, axes2[1])
            fig2.suptitle('Hive Simulation (Task 2)')
            fig2.savefig('task2.png')
            plt.close(fig2)

            # Task 3: Plot the initial world state
            fig3, ax3 = plt.subplots(figsize=(6, 5))
            plot_world(self.world, self.blist, self.hive_pos, ax3)
            fig3.savefig('task3.png')
            plt.close(fig3)

            # Task 4: Set up interactive simulation with pause functionality
            fig4, axes4 = plt.subplots(1, 2, figsize=(12, 5))
            paused = False

            def on_key(event):
                nonlocal paused
                if event.key == 'p':
                    paused = not paused  # Toggle pause state on 'p' key press

            fig4.canvas.mpl_connect('key_press_event', on_key)

        # Run simulation for each timestep
        for t in range(self.sim_length):
            if interactive and paused:
                plt.pause(0.1)  # Pause visualization if toggled
                continue

            # Update each bee and track honey collected in this timestep
            timestep_honey = 0
            for b in self.blist:
                nectar = b.step_change(
                    None,
                    self.world,
                    self.hive_pos,
                    self.flowers,
                    self.trees,
                    self.barriers,
                    self.comm_prob,
                    self.strategy_type,
                    self.hive_memory,
                    self.blist
                )
                timestep_honey += nectar
                # Deposit nectar in the hive if bee is inside
                if b.get_inhive():
                    x, y = min(b.get_pos()[0], self.hive_x - 1), min(
                        b.get_pos()[1], self.hive_y - 1
                    )
                    self.hive[x, y] = min(self.hive[x, y] + nectar, 5)

            self.total_honey += timestep_honey
            self.honey_over_time.append(timestep_honey)

            # Update interactive visualization
            if interactive:
                fig4.suptitle(
                    f'Bee Simulation - Timestep {t}, Strategy: {self.strategy_type}'
                )
                axes4[0].clear()
                axes4[1].clear()
                plot_hive(self.hive, self.blist, axes4[0])
                plot_world(self.world, self.blist, self.hive_pos, axes4[1])
                if t == self.sim_length - 1:
                    fig4.savefig('task4.png')
                plt.pause(1)

        if interactive:
            plt.ioff()  # Disable interactive mode

            # Plot honey collection trend over time
            plt.figure(figsize=(8, 6))
            plt.plot(range(self.sim_length), self.honey_over_time, marker='o')
            plt.title('Honey Collected Over Time')
            plt.xlabel('Timestep')
            plt.ylabel('Honey Units')
            plt.grid(True)
            plt.savefig('honey_trend.png')
            plt.close()

        return self.total_honey, self.honey_over_time


# --- Parameter Sweep for Batch Mode ---
def run_parameter_sweep(mapfile: str, paramfile: str) -> None:
    """Run multiple simulations with varying parameters and save results.

    Args:
        mapfile (str): Path to the terrain map file.
        paramfile (str): Path to the parameters file.
    """
    # Load parameters and set defaults
    params = load_parameters(paramfile)
    sim_length = params.get('sim_length', 10)
    comm_prob = params.get('comm_prob', 0.7)
    hive_x, hive_y = 30, 25
    hive_pos = (20, 20)
    results = []

    # Sweep over different numbers of bees, nectar amounts, and strategies
    for num_bees in [5, 10, 15]:
        for nectar_amount in [50, 100, 200]:
            for strategy_type in ['none', 'random', 'intelligent']:
                sim = Simulation(
                    num_bees,
                    sim_length,
                    mapfile,
                    hive_x,
                    hive_y,
                    hive_pos,
                    nectar_amount,
                    comm_prob,
                    strategy_type
                )
                total_honey, _ = sim.run()
                # Calculate metrics for this run
                avg_honey_per_bee = total_honey / num_bees if num_bees > 0 else 0
                success_rate = sum(
                    1 for b in sim.blist if b.carrying_nectar > 0 or b.total_nectar > 0
                ) / num_bees if num_bees > 0 else 0
                results.append(
                    (
                        num_bees,
                        nectar_amount,
                        strategy_type,
                        total_honey,
                        avg_honey_per_bee,
                        success_rate
                    )
                )

    # Print parameter sweep results
    print("Parameter Sweep Results:")
    print(
        f"{'Bees':<6} {'Nectar':<8} {'Strategy':<12} {'Total Honey':<12} "
        f"{'Avg Honey/Bee':<14} {'Success Rate':<12}"
    )
    for num_bees, nectar_amount, strategy_type, honey, avg_honey, success_rate in results:
        print(
            f"{num_bees:<6} {nectar_amount:<8} {strategy_type:<12} {honey:<12} "
            f"{avg_honey:<14.2f} {success_rate:<12.2f}"
        )

    # Save results to CSV
    with open('parameter_sweep_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                'num_bees',
                'nectar_amount',
                'strategy_type',
                'total_honey',
                'avg_honey_per_bee',
                'success_rate'
            ]
        )
        for row in results:
            writer.writerow(row)

    # Plot honey collected vs. number of bees for each strategy
    plt.figure(figsize=(10, 6))
    for strategy in ['none', 'random', 'intelligent']:
        for na in [50, 100, 200]:
            bees = [r[0] for r in results if r[2] == strategy and r[1] == na]
            honey = [r[3] for r in results if r[2] == strategy and r[1] == na]
            if bees:
                plt.plot(
                    bees,
                    honey,
                    marker='o',
                    label=f'{strategy}, Nectar={na}'
                )
    plt.title('Honey Collected vs. Number of Bees by Strategy')
    plt.xlabel('Number of Bees')
    plt.ylabel('Total Honey')
    plt.legend()
    plt.grid(True)
    plt.savefig('parameter_sweep_plot.png')
    plt.close()

    # Print summary report averaging metrics by strategy and nectar amount
    print("Summary Report:")
    print(f"{'Strategy':<12} {'Nectar':<8} {'Avg Honey/Bee':<14} {'Success Rate':<12}")
    for strategy in ['none', 'random', 'intelligent']:
        for na in [50, 100, 200]:
            avg_honey = [
                r[4] for r in results if r[2] == strategy and r[1] == na
            ]
            success = [
                r[5] for r in results if r[2] == strategy and r[1] == na
            ]
            if avg_honey:
                print(
                    f"{strategy:<12} {na:<8} {sum(avg_honey)/len(avg_honey):<14.2f} "
                    f"{sum(success)/len(success):<12.2f}"
                )


# --- Main Execution ---
def main() -> None:
    """Run the bee hive simulation with visualization and interactivity."""
    # Parse command-line arguments to determine mode
    args = parse_arguments()

    # Set default simulation parameters
    hive_x, hive_y = 30, 25
    world_x, world_y = 40, 35
    sim_length = 10
    num_bees = 5
    mapfile = 'map1.csv'
    paramfile = 'para1.csv'
    hive_pos = (20, 20)
    comm_prob = 0.7
    nectar_amount = 100
    strategy_type = 'random'

    # Handle interactive mode: prompt for user inputs
    if args.interactive:
        try:
            num_bees = int(input("Enter number of bees: "))
            sim_length = int(input("Enter simulation length: "))
            mapfile = input("Enter map file (e.g., map1.csv): ")
            comm_prob = float(input("Enter communication probability (0.0 to 1.0): "))
            nectar_amount = int(input("Enter nectar amount per flower: "))
            strategy_type = input("Enter strategy type (none, random, intelligent): ")
            # Validate inputs
            if comm_prob < 0.0 or comm_prob > 1.0:
                raise ValueError("Communication probability must be between 0.0 and 1.0")
            if num_bees < 0 or sim_length < 0 or nectar_amount < 0:
                raise ValueError("Parameters must be non-negative")
            if strategy_type not in ['none', 'random', 'intelligent']:
                raise ValueError("Strategy type must be none, random, or intelligent")
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)
    # Handle batch mode: load parameters and run parameter sweep
    elif args.mapfile and args.paramfile:
        mapfile = args.mapfile
        paramfile = args.paramfile
        params = load_parameters(paramfile)
        # Override defaults with loaded parameters
        num_bees = params.get('num_bees', num_bees)
        sim_length = params.get('sim_length', sim_length)
        comm_prob = params.get('comm_prob', comm_prob)
        nectar_amount = params.get('nectar_amount', nectar_amount)
        strategy_type = params.get('strategy_type', strategy_type)
        run_parameter_sweep(mapfile, paramfile)

        # Replot results for confirmation
        try:
            with open('parameter_sweep_results.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)
                results = [
                    (int(row[0]), int(row[1]), row[2], int(row[3]), float(row[4]), float(row[5]))
                    for row in reader
                ]
            plt.figure(figsize=(10, 6))
            for strategy in ['none', 'random', 'intelligent']:
                for na in [50, 100, 200]:
                    bees = [r[0] for r in results if r[2] == strategy and r[1] == na]
                    honey = [r[3] for r in results if r[2] == strategy and r[1] == na]
                    if bees:
                        plt.plot(
                            bees,
                            honey,
                            marker='o',
                            label=f'{strategy}, Nectar={na}'
                        )
            plt.title('Honey Collected vs. Number of Bees by Strategy')
            plt.xlabel('Number of Bees')
            plt.ylabel('Total Honey')
            plt.legend()
            plt.grid(True)
            plt.savefig('parameter_sweep_plot.png')
            plt.close()

            # Print summary report
            print("Summary Report:")
            print(
                f"{'Strategy':<12} {'Nectar':<8} {'Avg Honey/Bee':<14} {'Success Rate':<12}"
            )
            for strategy in ['none', 'random', 'intelligent']:
                for na in [50, 100, 200]:
                    avg_honey = [
                        r[4] for r in results if r[2] == strategy and r[1] == na
                    ]
                    success = [
                        r[5] for r in results if r[2] == strategy and r[1] == na
                    ]
                    if avg_honey:
                        print(
                            f"{strategy:<12} {na:<8} {sum(avg_honey)/len(avg_honey):<14.2f} "
                            f"{sum(success)/len(success):<12.2f}"
                        )
        except FileNotFoundError:
            print("Error: parameter_sweep_results.csv not found")
        return
    else:
        print("Error: Specify -i for interactive mode or -f and -p for batch mode")
        exit(1)

    # Run the simulation in interactive mode
    sim = Simulation(
        num_bees,
        sim_length,
        mapfile,
        hive_x,
        hive_y,
        hive_pos,
        nectar_amount,
        comm_prob,
        strategy_type
    )
    total_honey, honey_over_time = sim.run(interactive=True)

    # Calculate and display simulation summary
    avg_honey_per_bee = total_honey / num_bees if num_bees > 0 else 0
    success_rate = sum(
        1 for b in sim.blist if b.carrying_nectar > 0 or b.total_nectar > 0
    ) / num_bees if num_bees > 0 else 0

    print("Simulation Summary:")
    print(f"Total Honey: {total_honey}")
    print(f"Average Honey per Bee: {avg_honey_per_bee:.2f}")
    print(f"Success Rate: {success_rate:.2f}")


if __name__ == "__main__":
    main()