import numpy as np
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

class CellType(Enum):
    EMPTY = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    QUANTUM = 4

@dataclass
class Cell:
    cell_type: CellType = CellType.EMPTY
    energy: float = 0.0
    age: int = 0
    mutation_rate: float = 0.01
    quantum_phase: float = 0.0

class GameOfLife:
    def __init__(self, width: int = 120, height: int = 80):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=object)
        self.next_grid = np.zeros((height, width), dtype=object)
        self.generation = 0
        self.total_energy = 0.0
        self.population_history = {
            CellType.RED: [],
            CellType.GREEN: [],
            CellType.BLUE: [],
            CellType.QUANTUM: []
        }
        
        for y in range(height):
            for x in range(width):
                self.grid[y, x] = Cell()
                self.next_grid[y, x] = Cell()
        
        self.interaction_matrix = {
            (CellType.RED, CellType.GREEN): 0.1,
            (CellType.RED, CellType.BLUE): -0.05,
            (CellType.GREEN, CellType.BLUE): 0.05,
            (CellType.RED, CellType.QUANTUM): 0.2,
            (CellType.GREEN, CellType.QUANTUM): 0.2,
            (CellType.BLUE, CellType.QUANTUM): 0.2,
        }

    def get_neighbors(self, x: int, y: int) -> List[Cell]:
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                neighbors.append(self.grid[ny, nx])
        return neighbors

    def count_neighbors_by_type(self, x: int, y: int) -> Dict[CellType, int]:
        neighbors = self.get_neighbors(x, y)
        counts = {cell_type: 0 for cell_type in CellType}
        for neighbor in neighbors:
            counts[neighbor.cell_type] += 1
        return counts

    def calculate_interaction_bonus(self, cell: Cell, neighbors: List[Cell]) -> float:
        bonus = 0.0
        for neighbor in neighbors:
            if neighbor.cell_type == CellType.EMPTY:
                continue
            
            interaction_key = (cell.cell_type, neighbor.cell_type)
            reverse_key = (neighbor.cell_type, cell.cell_type)
            
            if interaction_key in self.interaction_matrix:
                bonus += self.interaction_matrix[interaction_key]
            elif reverse_key in self.interaction_matrix:
                bonus += self.interaction_matrix[reverse_key]
        
        return bonus

    def apply_quantum_effects(self, cell: Cell, x: int, y: int) -> Cell:
        new_cell = Cell()
        new_cell.cell_type = cell.cell_type
        new_cell.energy = cell.energy
        new_cell.age = cell.age
        new_cell.mutation_rate = cell.mutation_rate
        
        if cell.cell_type == CellType.QUANTUM:
            if random.random() < 0.05:
                tunnel_x = (x + random.randint(-2, 2)) % self.width
                tunnel_y = (y + random.randint(-2, 2)) % self.height
                if self.grid[tunnel_y, tunnel_x].cell_type == CellType.EMPTY:
                    self.next_grid[tunnel_y, tunnel_x] = Cell(
                        cell_type=CellType.QUANTUM,
                        energy=cell.energy * 0.7,
                        quantum_phase=random.random() * 2 * np.pi
                    )
            
            new_cell.quantum_phase = (cell.quantum_phase + 0.1) % (2 * np.pi)
        
        return new_cell

    def apply_species_rules(self, cell: Cell, neighbor_counts: Dict[CellType, int], 
                          neighbors: List[Cell], x: int, y: int) -> Cell:
        alive_neighbors = sum(count for cell_type, count in neighbor_counts.items() 
                            if cell_type != CellType.EMPTY)
        
        new_cell = Cell()
        
        if cell.cell_type == CellType.EMPTY:
            red_neighbors = neighbor_counts[CellType.RED]
            green_neighbors = neighbor_counts[CellType.GREEN]
            blue_neighbors = neighbor_counts[CellType.BLUE]
            quantum_neighbors = neighbor_counts[CellType.QUANTUM]
            
            if alive_neighbors == 3:
                if red_neighbors >= green_neighbors and red_neighbors >= blue_neighbors:
                    new_cell.cell_type = CellType.RED if quantum_neighbors == 0 else (
                        CellType.QUANTUM if random.random() < 0.3 else CellType.RED)
                elif green_neighbors >= blue_neighbors:
                    new_cell.cell_type = CellType.GREEN if quantum_neighbors == 0 else (
                        CellType.QUANTUM if random.random() < 0.3 else CellType.GREEN)
                else:
                    new_cell.cell_type = CellType.BLUE if quantum_neighbors == 0 else (
                        CellType.QUANTUM if random.random() < 0.3 else CellType.BLUE)
                
                new_cell.energy = 1.0
                new_cell.age = 0
        
        else:
            interaction_bonus = self.calculate_interaction_bonus(cell, neighbors)
            energy_factor = min(2.0, cell.energy + interaction_bonus)
            
            survival_threshold_low = 2
            survival_threshold_high = 3
            
            if cell.cell_type == CellType.RED:
                survival_threshold_high = 4
            elif cell.cell_type == CellType.GREEN:
                survival_threshold_low = 1
            elif cell.cell_type == CellType.BLUE:
                pass
            elif cell.cell_type == CellType.QUANTUM:
                phase_factor = (np.sin(cell.quantum_phase) + 1) / 2
                survival_threshold_low = int(1 + phase_factor)
                survival_threshold_high = int(3 + phase_factor)
            
            if (survival_threshold_low <= alive_neighbors <= survival_threshold_high and 
                energy_factor > 0.1):
                new_cell = Cell(
                    cell_type=cell.cell_type,
                    energy=min(2.0, cell.energy + interaction_bonus - 0.1),
                    age=cell.age + 1,
                    mutation_rate=cell.mutation_rate,
                    quantum_phase=cell.quantum_phase
                )
                
                if random.random() < cell.mutation_rate * (cell.age / 100):
                    species_list = [CellType.RED, CellType.GREEN, CellType.BLUE]
                    if random.random() < 0.1:
                        new_cell.cell_type = CellType.QUANTUM
                        new_cell.quantum_phase = random.random() * 2 * np.pi
                    else:
                        new_cell.cell_type = random.choice(species_list)
        
        return new_cell

    def update(self):
        self.generation += 1
        self.total_energy = 0.0
        
        for y in range(self.height):
            for x in range(self.width):
                self.next_grid[y, x] = Cell()
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y, x]
                neighbor_counts = self.count_neighbors_by_type(x, y)
                neighbors = self.get_neighbors(x, y)
                
                new_cell = self.apply_species_rules(cell, neighbor_counts, neighbors, x, y)
                
                if new_cell.cell_type != CellType.EMPTY or cell.cell_type == CellType.QUANTUM:
                    new_cell = self.apply_quantum_effects(new_cell, x, y)
                
                self.next_grid[y, x] = new_cell
                self.total_energy += new_cell.energy
        
        self.grid, self.next_grid = self.next_grid, self.grid
        
        self.update_population_history()

    def update_population_history(self):
        counts = {cell_type: 0 for cell_type in CellType if cell_type != CellType.EMPTY}
        
        for y in range(self.height):
            for x in range(self.width):
                cell_type = self.grid[y, x].cell_type
                if cell_type != CellType.EMPTY:
                    counts[cell_type] += 1
        
        for cell_type in counts:
            self.population_history[cell_type].append(counts[cell_type])
            if len(self.population_history[cell_type]) > 1000:
                self.population_history[cell_type] = self.population_history[cell_type][-1000:]

    def set_cell(self, x: int, y: int, cell_type: CellType, energy: float = 1.0):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = Cell(
                cell_type=cell_type,
                energy=energy,
                quantum_phase=random.random() * 2 * np.pi if cell_type == CellType.QUANTUM else 0.0
            )

    def get_cell(self, x: int, y: int) -> Optional[Cell]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x]
        return None

    def clear_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y, x] = Cell()
        self.generation = 0
        self.population_history = {cell_type: [] for cell_type in CellType if cell_type != CellType.EMPTY}

    def get_population_counts(self) -> Dict[CellType, int]:
        counts = {cell_type: 0 for cell_type in CellType}
        for y in range(self.height):
            for x in range(self.width):
                counts[self.grid[y, x].cell_type] += 1
        return counts

    def calculate_entropy(self) -> float:
        counts = self.get_population_counts()
        total = sum(counts.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in counts.values():
            if count > 0:
                p = count / total
                entropy -= p * np.log2(p)
        return entropy