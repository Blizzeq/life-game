import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import deque
import pygame
import math
from game_core import GameOfLife, CellType

class StatisticsTracker:
    def __init__(self, game: GameOfLife, max_history: int = 1000):
        self.game = game
        self.max_history = max_history
        
        self.population_history = {
            CellType.RED: deque(maxlen=max_history),
            CellType.GREEN: deque(maxlen=max_history),
            CellType.BLUE: deque(maxlen=max_history),
            CellType.QUANTUM: deque(maxlen=max_history)
        }
        
        self.total_population_history = deque(maxlen=max_history)
        self.entropy_history = deque(maxlen=max_history)
        self.energy_history = deque(maxlen=max_history)
        self.diversity_index_history = deque(maxlen=max_history)
        
        self.birth_rate_history = deque(maxlen=max_history)
        self.death_rate_history = deque(maxlen=max_history)
        self.stability_index_history = deque(maxlen=max_history)
        self.fractal_dimension_history = deque(maxlen=max_history)
        
        self.prev_population = {cell_type: 0 for cell_type in CellType if cell_type != CellType.EMPTY}
        self.prev_total_population = 0
        
        self.analysis_window = 50
        self.update_frequency = 1

    def update(self):
        if self.game.generation % self.update_frequency == 0:
            self._calculate_basic_stats()
            self._calculate_derived_stats()
            self._calculate_advanced_stats()

    def _calculate_basic_stats(self):
        counts = self.game.get_population_counts()
        
        for cell_type in self.population_history.keys():
            self.population_history[cell_type].append(counts[cell_type])
        
        total_pop = sum(counts[cell_type] for cell_type in self.population_history.keys())
        self.total_population_history.append(total_pop)
        
        entropy = self.game.calculate_entropy()
        self.entropy_history.append(entropy)
        
        self.energy_history.append(self.game.total_energy)

    def _calculate_derived_stats(self):
        counts = self.game.get_population_counts()
        total = sum(counts[cell_type] for cell_type in self.population_history.keys())
        
        if total > 0:
            diversity = 0.0
            for cell_type in self.population_history.keys():
                if counts[cell_type] > 0:
                    p = counts[cell_type] / total
                    diversity -= p * math.log(p)
            self.diversity_index_history.append(diversity)
        else:
            self.diversity_index_history.append(0.0)
        
        current_total = self.total_population_history[-1] if self.total_population_history else 0
        birth_rate = max(0, current_total - self.prev_total_population)
        death_rate = max(0, self.prev_total_population - current_total)
        
        self.birth_rate_history.append(birth_rate)
        self.death_rate_history.append(death_rate)
        
        self.prev_total_population = current_total
        for cell_type in self.population_history.keys():
            self.prev_population[cell_type] = self.population_history[cell_type][-1] if self.population_history[cell_type] else 0

    def _calculate_advanced_stats(self):
        if len(self.total_population_history) >= self.analysis_window:
            recent_populations = list(self.total_population_history)[-self.analysis_window:]
            variance = np.var(recent_populations)
            stability = 1.0 / (1.0 + variance) if variance >= 0 else 0.0
            self.stability_index_history.append(stability)
        else:
            self.stability_index_history.append(0.0)
        
        fractal_dim = self._estimate_fractal_dimension()
        self.fractal_dimension_history.append(fractal_dim)

    def _estimate_fractal_dimension(self) -> float:
        scales = [1, 2, 4, 8]
        counts = []
        
        for scale in scales:
            count = 0
            for y in range(0, self.game.height, scale):
                for x in range(0, self.game.width, scale):
                    has_life = False
                    for dy in range(min(scale, self.game.height - y)):
                        for dx in range(min(scale, self.game.width - x)):
                            if self.game.get_cell(x + dx, y + dy).cell_type != CellType.EMPTY:
                                has_life = True
                                break
                        if has_life:
                            break
                    if has_life:
                        count += 1
            counts.append(count)
        
        if len(counts) >= 2 and all(c > 0 for c in counts):
            log_scales = [math.log(1.0/s) for s in scales]
            log_counts = [math.log(c) for c in counts]
            
            n = len(log_scales)
            sum_x = sum(log_scales)
            sum_y = sum(log_counts)
            sum_xy = sum(x*y for x, y in zip(log_scales, log_counts))
            sum_x2 = sum(x*x for x in log_scales)
            
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                return max(0.0, min(2.0, slope))
        
        return 1.0

    def get_current_stats(self) -> Dict:
        if not self.total_population_history:
            return {}
        
        return {
            'generation': self.game.generation,
            'total_population': self.total_population_history[-1],
            'populations': {
                'red': self.population_history[CellType.RED][-1] if self.population_history[CellType.RED] else 0,
                'green': self.population_history[CellType.GREEN][-1] if self.population_history[CellType.GREEN] else 0,
                'blue': self.population_history[CellType.BLUE][-1] if self.population_history[CellType.BLUE] else 0,
                'quantum': self.population_history[CellType.QUANTUM][-1] if self.population_history[CellType.QUANTUM] else 0
            },
            'entropy': self.entropy_history[-1] if self.entropy_history else 0,
            'energy': self.energy_history[-1] if self.energy_history else 0,
            'diversity_index': self.diversity_index_history[-1] if self.diversity_index_history else 0,
            'birth_rate': self.birth_rate_history[-1] if self.birth_rate_history else 0,
            'death_rate': self.death_rate_history[-1] if self.death_rate_history else 0,
            'stability_index': self.stability_index_history[-1] if self.stability_index_history else 0,
            'fractal_dimension': self.fractal_dimension_history[-1] if self.fractal_dimension_history else 0
        }

    def get_moving_average(self, data: deque, window: int = None) -> float:
        if not data:
            return 0.0
        if window is None:
            window = self.analysis_window
        
        recent_data = list(data)[-window:]
        return sum(recent_data) / len(recent_data) if recent_data else 0.0

    def get_trend(self, data: deque, window: int = None) -> float:
        if not data:
            return 0.0
        if window is None:
            window = min(self.analysis_window, len(data))
        
        if window < 2:
            return 0.0
        
        recent_data = list(data)[-window:]
        x = list(range(len(recent_data)))
        y = recent_data
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            return slope
        return 0.0

    def get_analysis_summary(self) -> Dict:
        if not self.total_population_history:
            return {'error': 'No data available'}
        
        summary = {
            'population_trends': {},
            'system_health': {},
            'complexity_measures': {}
        }
        
        for cell_type in self.population_history.keys():
            data = self.population_history[cell_type]
            if data:
                summary['population_trends'][cell_type.name.lower()] = {
                    'current': data[-1],
                    'average': self.get_moving_average(data),
                    'trend': self.get_trend(data),
                    'peak': max(data),
                    'min': min(data)
                }
        
        summary['system_health'] = {
            'stability': self.get_moving_average(self.stability_index_history),
            'diversity': self.get_moving_average(self.diversity_index_history),
            'energy_efficiency': self.energy_history[-1] / max(1, self.total_population_history[-1]) if self.energy_history and self.total_population_history else 0,
            'birth_death_ratio': self.birth_rate_history[-1] / max(1, self.death_rate_history[-1]) if self.birth_rate_history and self.death_rate_history else 1
        }
        
        summary['complexity_measures'] = {
            'entropy': self.get_moving_average(self.entropy_history),
            'fractal_dimension': self.get_moving_average(self.fractal_dimension_history),
            'entropy_trend': self.get_trend(self.entropy_history)
        }
        
        return summary

    def detect_patterns(self) -> List[str]:
        patterns = []
        
        if len(self.total_population_history) < 20:
            return patterns
        
        recent_populations = list(self.total_population_history)[-20:]
        
        if self._detect_oscillation(recent_populations):
            patterns.append("Population oscillation detected")
        
        if self._detect_exponential_growth(recent_populations):
            patterns.append("Exponential growth pattern")
        
        if self._detect_extinction_risk():
            patterns.append("Species extinction risk")
        
        if self._detect_stability(recent_populations):
            patterns.append("Population stability achieved")
        
        if self._detect_chaos():
            patterns.append("Chaotic dynamics detected")
        
        return patterns

    def _detect_oscillation(self, data: List[float]) -> bool:
        if len(data) < 6:
            return False
        
        peaks = []
        valleys = []
        
        for i in range(1, len(data) - 1):
            if data[i] > data[i-1] and data[i] > data[i+1]:
                peaks.append(i)
            elif data[i] < data[i-1] and data[i] < data[i+1]:
                valleys.append(i)
        
        if len(peaks) >= 3:
            intervals = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((interval - avg_interval) ** 2 for interval in intervals) / len(intervals)
            return variance < avg_interval * 0.1
        
        return False

    def _detect_exponential_growth(self, data: List[float]) -> bool:
        if len(data) < 5:
            return False
        
        growth_rates = []
        for i in range(1, len(data)):
            if data[i-1] > 0:
                growth_rate = data[i] / data[i-1]
                growth_rates.append(growth_rate)
        
        if growth_rates:
            avg_growth = sum(growth_rates) / len(growth_rates)
            return avg_growth > 1.1 and all(rate > 1.05 for rate in growth_rates[-3:])
        
        return False

    def _detect_extinction_risk(self) -> bool:
        for cell_type in self.population_history.keys():
            if self.population_history[cell_type]:
                current = self.population_history[cell_type][-1]
                if current > 0 and current < 5:
                    recent_trend = self.get_trend(self.population_history[cell_type], 10)
                    if recent_trend < -0.1:
                        return True
        return False

    def _detect_stability(self, data: List[float]) -> bool:
        if len(data) < 10:
            return False
        
        mean_pop = sum(data) / len(data)
        variance = sum((x - mean_pop) ** 2 for x in data) / len(data)
        coefficient_of_variation = (variance ** 0.5) / mean_pop if mean_pop > 0 else float('inf')
        
        return coefficient_of_variation < 0.05

    def _detect_chaos(self) -> bool:
        if len(self.entropy_history) < 20:
            return False
        
        recent_entropy = list(self.entropy_history)[-20:]
        entropy_variance = np.var(recent_entropy) if recent_entropy else 0
        fractal_dim = self.fractal_dimension_history[-1] if self.fractal_dimension_history else 1
        
        return entropy_variance > 0.5 and fractal_dim > 1.5

    def export_data(self, filename: str = "game_stats.csv"):
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['generation', 'total_pop', 'red', 'green', 'blue', 'quantum', 
                         'entropy', 'energy', 'diversity', 'birth_rate', 'death_rate', 
                         'stability', 'fractal_dim']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            max_len = max(len(self.total_population_history), 
                         len(list(self.population_history.values())[0]),
                         len(self.entropy_history))
            
            for i in range(max_len):
                row = {
                    'generation': i,
                    'total_pop': self.total_population_history[i] if i < len(self.total_population_history) else 0,
                    'red': self.population_history[CellType.RED][i] if i < len(self.population_history[CellType.RED]) else 0,
                    'green': self.population_history[CellType.GREEN][i] if i < len(self.population_history[CellType.GREEN]) else 0,
                    'blue': self.population_history[CellType.BLUE][i] if i < len(self.population_history[CellType.BLUE]) else 0,
                    'quantum': self.population_history[CellType.QUANTUM][i] if i < len(self.population_history[CellType.QUANTUM]) else 0,
                    'entropy': self.entropy_history[i] if i < len(self.entropy_history) else 0,
                    'energy': self.energy_history[i] if i < len(self.energy_history) else 0,
                    'diversity': self.diversity_index_history[i] if i < len(self.diversity_index_history) else 0,
                    'birth_rate': self.birth_rate_history[i] if i < len(self.birth_rate_history) else 0,
                    'death_rate': self.death_rate_history[i] if i < len(self.death_rate_history) else 0,
                    'stability': self.stability_index_history[i] if i < len(self.stability_index_history) else 0,
                    'fractal_dim': self.fractal_dimension_history[i] if i < len(self.fractal_dimension_history) else 0
                }
                writer.writerow(row)

    def clear_history(self):
        for history in self.population_history.values():
            history.clear()
        self.total_population_history.clear()
        self.entropy_history.clear()
        self.energy_history.clear()
        self.diversity_index_history.clear()
        self.birth_rate_history.clear()
        self.death_rate_history.clear()
        self.stability_index_history.clear()
        self.fractal_dimension_history.clear()