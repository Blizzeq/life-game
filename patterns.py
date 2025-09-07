from typing import List, Tuple, Dict
from game_core import CellType

class Pattern:
    def __init__(self, name: str, pattern: List[List[int]], 
                 description: str = "", cell_type: CellType = CellType.RED):
        self.name = name
        self.pattern = pattern
        self.description = description
        self.cell_type = cell_type
        self.width = len(pattern[0]) if pattern else 0
        self.height = len(pattern)

    def get_cells(self) -> List[Tuple[int, int]]:
        cells = []
        for y, row in enumerate(self.pattern):
            for x, cell in enumerate(row):
                if cell == 1:
                    cells.append((x, y))
        return cells

class PatternLibrary:
    def __init__(self):
        self.patterns = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        # Still lifes
        self.add_pattern("Block", [
            [1, 1],
            [1, 1]
        ], "A 2x2 square that never changes")

        self.add_pattern("Beehive", [
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [0, 1, 1, 0]
        ], "A stable hexagonal pattern")

        self.add_pattern("Loaf", [
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [0, 1, 0, 1],
            [0, 0, 1, 0]
        ], "A stable asymmetric pattern")

        # Oscillators
        self.add_pattern("Blinker", [
            [1, 1, 1]
        ], "Simplest oscillator, period 2")

        self.add_pattern("Toad", [
            [0, 1, 1, 1],
            [1, 1, 1, 0]
        ], "Period 2 oscillator")

        self.add_pattern("Beacon", [
            [1, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1]
        ], "Period 2 oscillator")

        self.add_pattern("Pulsar", [
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0]
        ], "Period 3 oscillator")

        # Spaceships
        self.add_pattern("Glider", [
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], "The famous glider that travels diagonally")

        self.add_pattern("Lightweight Spaceship", [
            [1, 0, 0, 1, 0],
            [0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [0, 1, 1, 1, 1]
        ], "LWSS - travels horizontally")

        # Methuselahs (patterns that evolve for a long time)
        self.add_pattern("R-Pentomino", [
            [0, 1, 1],
            [1, 1, 0],
            [0, 1, 0]
        ], "Famous methuselah that stabilizes after 1103 generations")

        self.add_pattern("Diehard", [
            [0, 0, 0, 0, 0, 0, 1, 0],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 1, 1, 1]
        ], "Dies completely after 130 generations")

        self.add_pattern("Acorn", [
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [1, 1, 0, 0, 1, 1, 1]
        ], "Small pattern that grows to over 600 cells")

        # Guns
        self.add_pattern("Gosper Glider Gun", [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ], "Produces gliders indefinitely")

        # Multi-species patterns
        self.add_pattern("Species Competition", [
            [1, 1, 1, 0, 0, 0, 2, 2, 2],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [3, 3, 3, 0, 0, 0, 1, 1, 1]
        ], "Four species competing for space", CellType.RED)

        # Quantum patterns
        self.add_pattern("Quantum Glider", [
            [0, 4, 0],
            [0, 0, 4],
            [4, 4, 4]
        ], "Quantum version of the classic glider", CellType.QUANTUM)

        self.add_pattern("Quantum Cross", [
            [0, 0, 4, 0, 0],
            [0, 0, 4, 0, 0],
            [4, 4, 4, 4, 4],
            [0, 0, 4, 0, 0],
            [0, 0, 4, 0, 0]
        ], "Quantum cross pattern with tunneling effects", CellType.QUANTUM)

        # Random patterns for testing
        self.add_pattern("Random Small", self._generate_random_pattern(5, 5, 0.3),
                        "Small random pattern")
        
        self.add_pattern("Random Medium", self._generate_random_pattern(10, 10, 0.2),
                        "Medium random pattern")

    def _generate_random_pattern(self, width: int, height: int, density: float) -> List[List[int]]:
        import random
        pattern = []
        for _ in range(height):
            row = []
            for _ in range(width):
                row.append(1 if random.random() < density else 0)
            pattern.append(row)
        return pattern

    def add_pattern(self, name: str, pattern: List[List[int]], 
                   description: str = "", cell_type: CellType = CellType.RED):
        # Convert multi-species patterns
        converted_pattern = []
        for row in pattern:
            converted_row = []
            for cell in row:
                if cell == 2:
                    # Convert to GREEN
                    converted_row.append(1)
                elif cell == 3:
                    # Convert to BLUE
                    converted_row.append(1)
                elif cell == 4:
                    # Convert to QUANTUM
                    converted_row.append(1)
                else:
                    converted_row.append(cell)
            converted_pattern.append(converted_row)
        
        # Store the original pattern with species info
        pattern_obj = Pattern(name, pattern, description, cell_type)
        self.patterns[name] = pattern_obj

    def get_pattern(self, name: str) -> Pattern:
        return self.patterns.get(name)

    def get_pattern_names(self) -> List[str]:
        return list(self.patterns.keys())

    def get_patterns_by_category(self) -> Dict[str, List[str]]:
        categories = {
            "Still Lifes": ["Block", "Beehive", "Loaf"],
            "Oscillators": ["Blinker", "Toad", "Beacon", "Pulsar"],
            "Spaceships": ["Glider", "Lightweight Spaceship"],
            "Methuselahs": ["R-Pentomino", "Diehard", "Acorn"],
            "Guns": ["Gosper Glider Gun"],
            "Multi-Species": ["Species Competition"],
            "Quantum": ["Quantum Glider", "Quantum Cross"],
            "Random": ["Random Small", "Random Medium"]
        }
        return categories

    def place_pattern(self, game, pattern_name: str, x: int, y: int, 
                     cell_type: CellType = None) -> bool:
        pattern = self.get_pattern(pattern_name)
        if not pattern:
            return False
        
        # Use pattern's default cell type if none specified
        if cell_type is None:
            cell_type = pattern.cell_type
        
        # Place the pattern on the grid
        for py, row in enumerate(pattern.pattern):
            for px, cell_value in enumerate(row):
                if cell_value > 0:
                    grid_x = x + px
                    grid_y = y + py
                    
                    # Determine cell type based on pattern value
                    if cell_value == 1:
                        place_type = cell_type
                    elif cell_value == 2:
                        place_type = CellType.GREEN
                    elif cell_value == 3:
                        place_type = CellType.BLUE
                    elif cell_value == 4:
                        place_type = CellType.QUANTUM
                    else:
                        place_type = cell_type
                    
                    if (0 <= grid_x < game.width and 0 <= grid_y < game.height):
                        game.set_cell(grid_x, grid_y, place_type)
        
        return True

    def create_symmetric_pattern(self, base_pattern: List[List[int]], 
                                symmetry_type: str = "horizontal") -> List[List[int]]:
        if symmetry_type == "horizontal":
            return base_pattern + [row[::-1] for row in reversed(base_pattern)]
        elif symmetry_type == "vertical":
            return base_pattern + [row for row in reversed(base_pattern)]
        elif symmetry_type == "diagonal":
            # Transpose the pattern
            height = len(base_pattern)
            width = len(base_pattern[0]) if height > 0 else 0
            transposed = [[base_pattern[y][x] for y in range(height)] 
                         for x in range(width)]
            return base_pattern + transposed
        else:
            return base_pattern