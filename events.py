import random
import math
import numpy as np
from typing import List, Tuple, Optional, Dict
from enum import Enum
from game_core import GameOfLife, CellType, Cell

class EventType(Enum):
    METEOR = "meteor"
    ENERGY_WAVE = "energy_wave"
    MUTATION_BURST = "mutation_burst"
    QUANTUM_STORM = "quantum_storm"
    SPECIES_MIGRATION = "species_migration"
    COSMIC_RADIATION = "cosmic_radiation"
    TEMPORAL_RIFT = "temporal_rift"
    ECOSYSTEM_BLOOM = "ecosystem_bloom"

class Event:
    def __init__(self, event_type: EventType, x: int, y: int, 
                 radius: int, duration: int, intensity: float = 1.0):
        self.event_type = event_type
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.max_duration = duration
        self.intensity = intensity
        self.particles = []

    def update(self) -> bool:
        self.duration -= 1
        self.update_particles()
        return self.duration > 0

    def update_particles(self):
        for particle in self.particles[:]:
            particle['life'] -= 1
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95
            
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def add_particle(self, x: float, y: float, vx: float, vy: float, 
                    color: Tuple[int, int, int], life: int):
        self.particles.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'color': color, 'life': life, 'max_life': life
        })

    def get_age_factor(self) -> float:
        return 1.0 - (self.duration / self.max_duration)

class EventSystem:
    def __init__(self, game: GameOfLife):
        self.game = game
        self.active_events: List[Event] = []
        self.event_probability = 0.002
        self.last_event_time = 0
        self.min_event_interval = 300
        
        self.event_weights = {
            EventType.METEOR: 20,
            EventType.ENERGY_WAVE: 15,
            EventType.MUTATION_BURST: 10,
            EventType.QUANTUM_STORM: 8,
            EventType.SPECIES_MIGRATION: 12,
            EventType.COSMIC_RADIATION: 5,
            EventType.TEMPORAL_RIFT: 3,
            EventType.ECOSYSTEM_BLOOM: 7
        }

    def update(self):
        for event in self.active_events[:]:
            if not event.update():
                self.active_events.remove(event)

        self.last_event_time += 1
        if (self.last_event_time >= self.min_event_interval and 
            random.random() < self.event_probability):
            self.spawn_random_event()
            self.last_event_time = 0

    def spawn_random_event(self):
        event_types = list(self.event_weights.keys())
        weights = list(self.event_weights.values())
        event_type = random.choices(event_types, weights=weights)[0]
        
        x = random.randint(0, self.game.width - 1)
        y = random.randint(0, self.game.height - 1)
        
        self.spawn_event(event_type, x, y)

    def spawn_event(self, event_type: EventType, x: int, y: int):
        if event_type == EventType.METEOR:
            self.spawn_meteor(x, y)
        elif event_type == EventType.ENERGY_WAVE:
            self.spawn_energy_wave(x, y)
        elif event_type == EventType.MUTATION_BURST:
            self.spawn_mutation_burst(x, y)
        elif event_type == EventType.QUANTUM_STORM:
            self.spawn_quantum_storm(x, y)
        elif event_type == EventType.SPECIES_MIGRATION:
            self.spawn_species_migration(x, y)
        elif event_type == EventType.COSMIC_RADIATION:
            self.spawn_cosmic_radiation(x, y)
        elif event_type == EventType.TEMPORAL_RIFT:
            self.spawn_temporal_rift(x, y)
        elif event_type == EventType.ECOSYSTEM_BLOOM:
            self.spawn_ecosystem_bloom(x, y)

    def spawn_meteor(self, x: int, y: int):
        radius = random.randint(3, 8)
        event = Event(EventType.METEOR, x, y, radius, 60, 2.0)
        
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            event.add_particle(x * 8, y * 8, vx, vy, (255, 100, 0), 30)
        
        self.active_events.append(event)
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                distance = math.sqrt(dx*dx + dy*dy)
                if distance <= radius:
                    target_x = (x + dx) % self.game.width
                    target_y = (y + dy) % self.game.height
                    
                    destruction_chance = 1.0 - (distance / radius) ** 2
                    if random.random() < destruction_chance:
                        self.game.set_cell(target_x, target_y, CellType.EMPTY)

    def spawn_energy_wave(self, x: int, y: int):
        radius = random.randint(8, 15)
        event = Event(EventType.ENERGY_WAVE, x, y, radius, 120, 1.5)
        
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            vx = math.cos(rad) * 2
            vy = math.sin(rad) * 2
            event.add_particle(x * 8, y * 8, vx, vy, (0, 255, 255), 40)
        
        self.active_events.append(event)

    def spawn_mutation_burst(self, x: int, y: int):
        radius = random.randint(4, 10)
        event = Event(EventType.MUTATION_BURST, x, y, radius, 90, 3.0)
        
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            event.add_particle(x * 8, y * 8, vx, vy, (255, 255, 0), 25)
        
        self.active_events.append(event)

    def spawn_quantum_storm(self, x: int, y: int):
        radius = random.randint(6, 12)
        event = Event(EventType.QUANTUM_STORM, x, y, radius, 150, 2.5)
        
        for _ in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            event.add_particle(x * 8, y * 8, vx, vy, (255, 255, 255), 35)
        
        self.active_events.append(event)

    def spawn_species_migration(self, x: int, y: int):
        radius = random.randint(5, 12)
        event = Event(EventType.SPECIES_MIGRATION, x, y, radius, 200, 1.0)
        
        species = random.choice([CellType.RED, CellType.GREEN, CellType.BLUE])
        
        for i in range(20):
            trail_x = x + random.randint(-radius, radius)
            trail_y = y + random.randint(-radius, radius)
            if (0 <= trail_x < self.game.width and 0 <= trail_y < self.game.height):
                if self.game.get_cell(trail_x, trail_y).cell_type == CellType.EMPTY:
                    self.game.set_cell(trail_x, trail_y, species, energy=0.8)
        
        self.active_events.append(event)

    def spawn_cosmic_radiation(self, x: int, y: int):
        radius = random.randint(10, 20)
        event = Event(EventType.COSMIC_RADIATION, x, y, radius, 300, 1.0)
        self.active_events.append(event)

    def spawn_temporal_rift(self, x: int, y: int):
        radius = random.randint(3, 6)
        event = Event(EventType.TEMPORAL_RIFT, x, y, radius, 180, 4.0)
        
        stored_cells = {}
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx*dx + dy*dy <= radius*radius:
                    target_x = (x + dx) % self.game.width
                    target_y = (y + dy) % self.game.height
                    cell = self.game.get_cell(target_x, target_y)
                    stored_cells[(target_x, target_y)] = Cell(
                        cell_type=cell.cell_type,
                        energy=cell.energy,
                        age=cell.age,
                        mutation_rate=cell.mutation_rate,
                        quantum_phase=cell.quantum_phase
                    )
        
        event.stored_cells = stored_cells
        self.active_events.append(event)

    def spawn_ecosystem_bloom(self, x: int, y: int):
        radius = random.randint(6, 15)
        event = Event(EventType.ECOSYSTEM_BLOOM, x, y, radius, 100, 2.0)
        
        species_list = [CellType.RED, CellType.GREEN, CellType.BLUE, CellType.QUANTUM]
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                distance = math.sqrt(dx*dx + dy*dy)
                if distance <= radius and random.random() < 0.4:
                    target_x = (x + dx) % self.game.width
                    target_y = (y + dy) % self.game.height
                    
                    species = random.choice(species_list)
                    bloom_chance = 1.0 - (distance / radius)
                    if random.random() < bloom_chance:
                        self.game.set_cell(target_x, target_y, species, energy=1.5)
        
        self.active_events.append(event)

    def apply_event_effects(self):
        for event in self.active_events:
            self.apply_event_to_cells(event)

    def apply_event_to_cells(self, event: Event):
        age_factor = event.get_age_factor()
        
        if event.event_type == EventType.ENERGY_WAVE:
            wave_radius = event.radius * age_factor
            for dy in range(-event.radius, event.radius + 1):
                for dx in range(-event.radius, event.radius + 1):
                    distance = math.sqrt(dx*dx + dy*dy)
                    if abs(distance - wave_radius) < 2:
                        target_x = (event.x + dx) % self.game.width
                        target_y = (event.y + dy) % self.game.height
                        cell = self.game.get_cell(target_x, target_y)
                        
                        if cell.cell_type != CellType.EMPTY:
                            new_energy = min(3.0, cell.energy + event.intensity * 0.5)
                            self.game.set_cell(target_x, target_y, cell.cell_type, new_energy)

        elif event.event_type == EventType.MUTATION_BURST:
            for dy in range(-event.radius, event.radius + 1):
                for dx in range(-event.radius, event.radius + 1):
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= event.radius:
                        target_x = (event.x + dx) % self.game.width
                        target_y = (event.y + dy) % self.game.height
                        cell = self.game.get_cell(target_x, target_y)
                        
                        if cell.cell_type != CellType.EMPTY:
                            mutation_boost = event.intensity * (1.0 - distance / event.radius) * 0.05
                            if random.random() < mutation_boost:
                                new_species = random.choice([CellType.RED, CellType.GREEN, 
                                                           CellType.BLUE, CellType.QUANTUM])
                                self.game.set_cell(target_x, target_y, new_species, cell.energy)

        elif event.event_type == EventType.QUANTUM_STORM:
            for dy in range(-event.radius, event.radius + 1):
                for dx in range(-event.radius, event.radius + 1):
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= event.radius:
                        target_x = (event.x + dx) % self.game.width
                        target_y = (event.y + dy) % self.game.height
                        cell = self.game.get_cell(target_x, target_y)
                        
                        quantum_chance = event.intensity * (1.0 - distance / event.radius) * 0.1
                        if (cell.cell_type != CellType.EMPTY and 
                            cell.cell_type != CellType.QUANTUM and 
                            random.random() < quantum_chance):
                            self.game.set_cell(target_x, target_y, CellType.QUANTUM, cell.energy)

        elif event.event_type == EventType.COSMIC_RADIATION:
            for dy in range(-event.radius, event.radius + 1):
                for dx in range(-event.radius, event.radius + 1):
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= event.radius and random.random() < 0.02:
                        target_x = (event.x + dx) % self.game.width
                        target_y = (event.y + dy) % self.game.height
                        cell = self.game.get_cell(target_x, target_y)
                        
                        effect = random.choice(['energy_boost', 'mutation', 'death', 'birth'])
                        
                        if effect == 'energy_boost' and cell.cell_type != CellType.EMPTY:
                            new_energy = min(3.0, cell.energy + 0.5)
                            self.game.set_cell(target_x, target_y, cell.cell_type, new_energy)
                        elif effect == 'mutation' and cell.cell_type != CellType.EMPTY:
                            new_species = random.choice([CellType.RED, CellType.GREEN, 
                                                       CellType.BLUE, CellType.QUANTUM])
                            self.game.set_cell(target_x, target_y, new_species, cell.energy)
                        elif effect == 'death':
                            self.game.set_cell(target_x, target_y, CellType.EMPTY)
                        elif effect == 'birth' and cell.cell_type == CellType.EMPTY:
                            new_species = random.choice([CellType.RED, CellType.GREEN, CellType.BLUE])
                            self.game.set_cell(target_x, target_y, new_species, 1.0)

        elif event.event_type == EventType.TEMPORAL_RIFT:
            if event.duration <= 10 and hasattr(event, 'stored_cells'):
                for (target_x, target_y), stored_cell in event.stored_cells.items():
                    self.game.grid[target_y, target_x] = stored_cell

    def get_event_info(self, event: Event) -> Dict:
        return {
            'type': event.event_type.value,
            'x': event.x,
            'y': event.y,
            'radius': event.radius,
            'duration': event.duration,
            'max_duration': event.max_duration,
            'intensity': event.intensity,
            'age_factor': event.get_age_factor(),
            'particles': len(event.particles)
        }

    def clear_events(self):
        self.active_events.clear()

    def force_event(self, event_type: EventType, x: int, y: int):
        self.spawn_event(event_type, x, y)

    def set_event_probability(self, probability: float):
        self.event_probability = max(0.0, min(0.1, probability))