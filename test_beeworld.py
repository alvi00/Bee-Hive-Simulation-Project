import unittest
from buzzness import Bee, Flower, Tree, Barrier
from beeworld import load_map, initialize_hive


# --- Test Class Definition ---
class TestBeeWorld(unittest.TestCase):
    """Test suite for the bee world simulation components."""

    def setUp(self):
        """Set up initial conditions for each test case.

        Initializes a hive position, a 50x50 world grid, a flower, a tree, a barrier,
        and a bee to use across tests. This ensures a consistent starting state.
        """
        self.hive_pos = (25, 25)
        self.world = [[0 for _ in range(50)] for _ in range(50)]
        self.flowers = [Flower((10, 10), "rose", "red", 100)]
        self.trees = [Tree((20, 20), [Flower((20, 20), "tree_flower", "red", 100)])]
        self.barriers = [Barrier((30, 30), "water")]
        self.bee = Bee("b1", (25, 25))

    # --- Test Cases ---

    def test_bee_movement(self):
        """Test bee movement outside the hive.

        Verifies that a bee moves to a new position when on a mission, stays within
        the world boundaries (50x50), and avoids barriers.
        """
        self.bee.inhive = False  # Move bee outside the hive
        self.bee.on_mission = True  # Start a mission
        initial_pos = self.bee.pos  # Store initial position
        # Simulate one timestep with 'none' strategy and no communication
        self.bee.step_change(
            None, self.world, self.hive_pos, self.flowers, self.trees, self.barriers, 0.0, 'none'
        )
        new_pos = self.bee.pos  # Get new position after movement
        # Assert the bee has moved to a different position
        self.assertNotEqual(initial_pos, new_pos, "Bee should move")
        # Assert the new position is within the 50x50 world boundaries
        self.assertTrue(
            0 <= new_pos[0] < 50 and 0 <= new_pos[1] < 50,
            "Bee should stay in bounds"
        )

    def test_nectar_collection(self):
        """Test bee's ability to collect nectar from a flower.

        Verifies that a bee collects 10 units of nectar when positioned on a flower,
        and that the flower's nectar decreases accordingly.
        """
        self.bee.pos = (10, 10)  # Position bee on the flower
        self.bee.inhive = False  # Move bee outside the hive
        self.bee.on_mission = True  # Start a mission
        # Simulate one timestep with 'none' strategy and no communication
        nectar = self.bee.step_change(
            None, self.world, self.hive_pos, self.flowers, self.trees, self.barriers, 0.0, 'none'
        )
        # Assert the bee is carrying 10 units of nectar
        self.assertEqual(self.bee.carrying_nectar, 10, "Bee should collect 10 nectar")
        # Assert the flower's nectar has decreased by 10 units
        self.assertEqual(self.flowers[0].nectar, 90, "Flower nectar should decrease")

    def test_communication(self):
        """Test bee communication and strategy behavior.

        Verifies that:
        - A bee targets a known nectar location with 'random' strategy.
        - The 'intelligent' strategy updates the hive memory with shared locations.
        - The bee accumulates total_nectar after collecting nectar.
        """
        self.bee.known_nectar = [(10, 10)]  # Set a known nectar location
        self.bee.inhive = True  # Place bee in the hive
        self.bee.age = 4  # Ensure bee is eligible to start a mission
        # Simulate timestep with 'random' strategy and 100% communication probability
        self.bee.step_change(
            None, self.world, self.hive_pos, self.flowers, self.trees, self.barriers, 1.0, 'random'
        )
        # Assert the bee targets the known nectar location
        self.assertEqual(self.bee.target, (10, 10), "Bee should target known nectar with random strategy")
        
        # Simulate nectar collection and return to hive to trigger sharing
        hive_memory = []  # Initialize empty hive memory
        self.bee.inhive = False  # Move bee outside the hive
        self.bee.on_mission = True  # Start a mission
        self.bee.pos = (10, 10)  # Position bee on the flower to collect nectar
        self.bee.step_change(
            None, self.world, self.hive_pos, self.flowers, self.trees, self.barriers, 1.0, 'intelligent',
            hive_memory, [self.bee]
        )  # Bee collects nectar
        # Simulate return to hive
        self.bee.pos = self.hive_pos  # Move bee back to hive position
        self.bee.step_change(
            None, self.world, self.hive_pos, self.flowers, self.trees, self.barriers, 1.0, 'intelligent',
            hive_memory, [self.bee]
        )  # This should trigger sharing to hive_memory
        # Assert the known nectar location is added to hive memory
        self.assertIn((10, 10), hive_memory, "Intelligent strategy should update hive memory")

        # Test nectar accumulation with random strategy
        self.bee.pos = (10, 10)  # Position bee on the flower again
        self.bee.inhive = False  # Move bee outside the hive
        self.bee.on_mission = True  # Start a mission
        self.bee.carrying_nectar = 0  # Reset carrying nectar
        self.bee.total_nectar = 0  # Reset total nectar
        # Ensure nectar collection by calling step_change
        nectar_collected = self.bee.step_change(
            None, self.world, self.hive_pos, self.flowers, self.trees, self.barriers, 1.0, 'random'
        )
        # Assert the bee has accumulated nectar in its total
        self.assertGreater(self.bee.total_nectar, 0, "Bee should accumulate total_nectar after collecting")
        self.assertEqual(nectar_collected, 10, "Bee should collect 10 nectar from the flower")


if __name__ == '__main__':
    """Run the unit tests when the script is executed directly."""
    unittest.main()