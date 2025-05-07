import random
from dataclasses import dataclass
from typing import Tuple, List, Optional


# --- Flower Class ---
@dataclass
class Flower:
    """Represents a flower with nectar in the simulation.

    Attributes:
        position (Tuple[int, int]): (x, y) coordinates of the flower.
        name (str): Name of the flower (e.g., 'rose').
        color (str): Color of the flower (e.g., 'red').
        nectar (int): Amount of nectar the flower currently holds.
    """

    position: Tuple[int, int]
    name: str
    color: str
    nectar: int  # Initial nectar amount

    def collect_nectar(self) -> int:
        """Collect nectar from the flower if available.

        Reduces the flower's nectar by the amount collected (up to 10 units).

        Returns:
            int: Amount of nectar collected (0 if none available).
        """
        if self.nectar > 0:
            # Bees can collect up to 10 units of nectar at a time
            collected = min(10, self.nectar)
            self.nectar -= collected
            return collected
        return 0


# --- Tree Class ---
@dataclass
class Tree:
    """Represents a tree grouping multiple flowers.

    Attributes:
        position (Tuple[int, int]): (x, y) coordinates of the tree.
        flowers (List[Flower]): List of Flower objects associated with the tree.
    """

    position: Tuple[int, int]
    flowers: List[Flower]

    def collect_nectar(self) -> int:
        """Collect nectar from a randomly chosen flower in the tree.

        Returns:
            int: Amount of nectar collected (0 if none available).
        """
        if self.flowers:
            # Randomly select a flower from the tree to collect nectar
            flower = random.choice(self.flowers)
            return flower.collect_nectar()
        return 0


# --- Barrier Class ---
@dataclass
class Barrier:
    """Represents a barrier (e.g., water, building) that bees cannot cross.

    Attributes:
        position (Tuple[int, int]): (x, y) coordinates of the barrier.
        type (str): Type of barrier (e.g., 'water', 'building').
    """

    position: Tuple[int, int]
    type: str  # e.g., 'water', 'building'


# --- Bee Class ---
class Bee:
    """Represents a worker bee in the simulation with mission-based behavior.

    Attributes:
        id (str): Unique identifier for the bee (e.g., 'b1').
        pos (Tuple[int, int]): Current (x, y) position of the bee.
        age (int): Age of the bee in timesteps.
        inhive (bool): Whether the bee is currently in the hive.
        on_mission (bool): Whether the bee is on a nectar collection mission.
        carrying_nectar (int): Amount of nectar the bee is currently carrying.
        target (Optional[Tuple[int, int]]): Target nectar source position.
        known_nectar (List[Tuple[int, int]]): Known nectar source positions.
        wait_steps (int): Timesteps the bee must wait in the hive.
        energy (int): Energy level of the bee (depletes over time).
        lifespan (int): Maximum age of the bee in timesteps.
        alive (bool): Whether the bee is alive.
        total_nectar (int): Total nectar collected over the bee's lifetime.
        steps_outside_hive (int): Number of timesteps spent outside the hive.
    """

    def __init__(self, id: str, pos: Tuple[int, int]):
        """Initialize a bee with a given ID and starting position.

        Args:
            id (str): Unique identifier for the bee.
            pos (Tuple[int, int]): Initial (x, y) position in the hive.
        """
        self.id = id
        self.pos = pos
        self.age = 0
        self.inhive = True  # Bee starts in the hive
        self.on_mission = False  # Not on a mission initially
        self.carrying_nectar = 0  # No nectar at start
        self.target = None  # No target initially
        self.known_nectar = []  # List of known nectar locations
        self.wait_steps = 0  # No waiting initially
        self.energy = 100  # Starting energy
        self.lifespan = 50  # Maximum lifespan in timesteps
        self.alive = True  # Bee starts alive
        self.total_nectar = 0  # Total nectar collected over lifetime
        self.steps_outside_hive = 0  # Track steps outside the hive

    def step_change(
        self,
        subgrid: Optional[List[List[int]]],
        world: List[List[int]],
        hive_pos: Tuple[int, int],
        flowers: List[Flower],
        trees: List[Tree],
        barriers: List[Barrier],
        comm_prob: float = 0.7,
        strategy_type: str = 'random',
        hive_memory: List[Tuple[int, int]] = None,
        blist: List['Bee'] = None
    ) -> int:
        """Update the bee's state and position for one timestep.

        Handles aging, energy, mission logic, movement, and nectar collection.

        Args:
            subgrid (Optional[List[List[int]]]): Unused subgrid (for future use).
            world (List[List[int]]): World grid with terrain markers.
            hive_pos (Tuple[int, int]): Position of the hive.
            flowers (List[Flower]): List of flowers in the world.
            trees (List[Tree]): List of trees in the world.
            barriers (List[Barrier]): List of barriers in the world.
            comm_prob (float): Probability of sharing nectar locations.
            strategy_type (str): Strategy for movement ('none', 'random', 'intelligent').
            hive_memory (List[Tuple[int, int]]): Shared nectar locations (intelligent strategy).
            blist (List[Bee]): List of all bees (for intelligent strategy).

        Returns:
            int: Amount of nectar deposited in the hive (0 if none).
        """
        # Skip updates if the bee is not alive
        if not self.alive:
            return 0

        # Update energy and lifespan
        self.energy -= 1  # Deplete energy each timestep
        self.age += 1
        if self.energy <= 0 or self.age >= self.lifespan:
            self.alive = False  # Bee dies if energy or lifespan runs out
            return 0

        # Handle waiting period in the hive
        deposited_nectar = 0
        if self.wait_steps > 0:
            self.wait_steps -= 1
            self.energy = min(self.energy + 5, 100)  # Recharge energy while waiting
            return 0

        # Handle bee behavior inside the hive
        if self.inhive:
            # Start a mission after 4 timesteps
            if self.age >= 4 and not self.on_mission:
                self.on_mission = True
                self.inhive = False
                self.steps_outside_hive = 0  # Reset counter for steps outside
                # Set target based on strategy type
                if strategy_type == 'none':
                    self.target = None  # No target, move randomly
                elif strategy_type == 'random' and self.known_nectar and random.random() < comm_prob:
                    # Choose a known nectar location with probability comm_prob
                    self.target = random.choice(self.known_nectar)
                elif strategy_type == 'intelligent' and hive_memory:
                    # Choose a target with fewer than 2 bees already targeting it
                    valid_targets = [
                        loc for loc in hive_memory
                        if sum(1 for b in blist if b.target == loc and b.alive) < 2
                    ]
                    self.target = random.choice(valid_targets) if valid_targets else None
                else:
                    self.target = None
                # Decay known nectar locations (max 5, 90% retention chance)
                if self.known_nectar:
                    self.known_nectar = [
                        loc for loc in self.known_nectar if random.random() < 0.9
                    ][:5]
            else:
                self.age += 1  # Increment age while in hive
                return 0
        # Handle bee behavior outside the hive
        else:
            self.steps_outside_hive += 1  # Increment steps outside counter
            # Define possible moves in a 3x3 Moore neighborhood (excluding current position)
            valid_moves = [
                (dx, dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1] if dx != 0 or dy != 0
            ]
            random.shuffle(valid_moves)
            new_pos = self.pos

            # Force return to hive after 5 steps outside, even without nectar
            if self.steps_outside_hive >= 5:
                # Calculate direction toward the hive
                dx = hive_pos[0] - self.pos[0]
                dy = hive_pos[1] - self.pos[1]
                move = (0 if dx == 0 else dx // abs(dx), 0 if dy == 0 else dy // abs(dy))
                new_pos = (self.pos[0] + move[0], self.pos[1] + move[1])
                # Check if bee has reached the hive
                if new_pos == hive_pos:
                    self.inhive = True
                    self.on_mission = False
                    self.wait_steps = 4  # Wait 4 timesteps in hive
                    print(f"{self.id} returned to hive after {self.steps_outside_hive} steps.")
                    self.steps_outside_hive = 0
            # Return to hive if carrying nectar
            elif self.carrying_nectar > 0:
                # Calculate direction toward the hive
                dx = hive_pos[0] - self.pos[0]
                dy = hive_pos[1] - self.pos[1]
                move = (0 if dx == 0 else dx // abs(dx), 0 if dy == 0 else dy // abs(dy))
                new_pos = (self.pos[0] + move[0], self.pos[1] + move[1])
                # Deposit nectar if hive is reached
                if new_pos == hive_pos:
                    self.inhive = True
                    self.on_mission = False
                    deposited_nectar = self.carrying_nectar
                    print(f"{self.id} returned to hive with {self.carrying_nectar} nectar.")
                    self.carrying_nectar = 0
                    self.wait_steps = 4  # Wait 4 timesteps in hive
                    self.steps_outside_hive = 0
                    # Share nectar locations with hive (intelligent strategy)
                    if strategy_type == 'intelligent' and hive_memory is not None:
                        for loc in self.known_nectar:
                            if loc not in hive_memory:
                                print(f"{self.id} shared nectar location {loc} with the hive.")
                                hive_memory.append(loc)
            # Search for nectar if not carrying any
            else:
                # Check a 3x3 area around the bee's position for nectar sources
                x, y = self.pos
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        test_pos = (x + dx, y + dy)
                        # Ensure the test position is within world boundaries
                        if 0 <= test_pos[0] < len(world) and 0 <= test_pos[1] < len(world[0]):
                            # Check for flowers at the test position
                            for flower in flowers:
                                if flower.position == test_pos:
                                    nectar = flower.collect_nectar()
                                    if nectar > 0:
                                        self.carrying_nectar = nectar
                                        self.total_nectar += nectar
                                        # Add flower position to known nectar locations
                                        if flower.position not in self.known_nectar:
                                            self.known_nectar.append(flower.position)
                                        self.target = None  # Clear target after collecting
                                        break
                            # Check for trees at the test position
                            for tree in trees:
                                if tree.position == test_pos:
                                    nectar = tree.collect_nectar()
                                    if nectar > 0:
                                        self.carrying_nectar = nectar
                                        self.total_nectar += nectar
                                        # Add tree position to known nectar locations
                                        if tree.position not in self.known_nectar:
                                            self.known_nectar.append(tree.position)
                                        self.target = None  # Clear target after collecting
                                    break
                            # Stop searching if nectar is collected
                            if self.carrying_nectar > 0:
                                break
                        if self.carrying_nectar > 0:
                            break
                    if self.carrying_nectar > 0:
                        break

                # Move randomly if no nectar is collected
                if self.carrying_nectar == 0:
                    for dx, dy in valid_moves:
                        test_pos = (self.pos[0] + dx, self.pos[1] + dy)
                        # Check if the new position is valid (within bounds, no barriers)
                        if (0 <= test_pos[0] < len(world) and
                                0 <= test_pos[1] < len(world[0]) and
                                not any(b.position == test_pos for b in barriers)):
                            new_pos = test_pos
                            break  # Take the first valid random move

            # Update position if the new position is valid
            if (0 <= new_pos[0] < len(world) and
                    0 <= new_pos[1] < len(world[0]) and
                    not any(b.position == new_pos for b in barriers)):
                self.pos = new_pos

        return deposited_nectar

    def get_pos(self) -> Tuple[int, int]:
        """Get the bee's current position.

        Returns:
            Tuple[int, int]: The (x, y) coordinates of the bee.
        """
        return self.pos

    def get_inhive(self) -> bool:
        """Check if the bee is currently in the hive.

        Returns:
            bool: True if the bee is in the hive, False otherwise.
        """
        return self.inhive

    def set_inhive(self, value: bool) -> None:
        """Set the bee's in-hive status.

        Args:
            value (bool): True to place the bee in the hive, False to place it outside.
        """
        self.inhive = value