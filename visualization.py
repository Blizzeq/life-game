import pygame
import numpy as np
import colorsys
import math
from typing import Tuple, List, Optional
from game_core import GameOfLife, CellType, Cell

class Visualizer:
    def __init__(self, game: GameOfLife, cell_size: int = 8):
        self.game = game
        self.cell_size = cell_size
        self.screen_width = game.width * cell_size
        self.screen_height = game.height * cell_size
        
        # Colors for different cell types
        self.colors = {
            CellType.EMPTY: (0, 0, 0),
            CellType.RED: (255, 100, 100),
            CellType.GREEN: (100, 255, 100),
            CellType.BLUE: (100, 100, 255),
            CellType.QUANTUM: (255, 255, 255)
        }
        
        # Visual effects
        self.particle_system = ParticleSystem()
        self.glow_surfaces = {}
        self.trail_surface = None
        self.show_energy = False
        self.show_age = False
        self.show_grid = False
        
        # Animation
        self.time = 0.0
        
    def initialize_surfaces(self, screen):
        # Initialize glow surfaces for each cell type
        for cell_type in CellType:
            if cell_type != CellType.EMPTY:
                self.glow_surfaces[cell_type] = pygame.Surface(
                    (self.cell_size * 3, self.cell_size * 3), pygame.SRCALPHA
                )
                self.create_glow_surface(cell_type)
        
        self.trail_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

    def create_glow_surface(self, cell_type: CellType):
        if cell_type == CellType.EMPTY or cell_type not in self.glow_surfaces:
            return
        
        surface = self.glow_surfaces[cell_type]
        center = (self.cell_size * 3 // 2, self.cell_size * 3 // 2)
        base_color = self.colors[cell_type]
        
        # Create radial gradient for glow effect
        for radius in range(self.cell_size * 3 // 2, 0, -1):
            alpha = int(255 * (1 - radius / (self.cell_size * 1.5)) ** 2)
            if alpha > 0:
                color = (*base_color, min(alpha, 100))
                pygame.draw.circle(surface, color, center, radius)

    def get_cell_color(self, cell: Cell, x: int, y: int) -> Tuple[int, int, int]:
        if cell.cell_type == CellType.EMPTY:
            return self.colors[CellType.EMPTY]
        
        base_color = list(self.colors[cell.cell_type])
        
        # Energy-based brightness
        if self.show_energy:
            energy_factor = min(1.0, cell.energy / 2.0)
            base_color = [int(c * (0.3 + 0.7 * energy_factor)) for c in base_color]
        
        # Age-based color shift
        if self.show_age and cell.age > 0:
            age_factor = min(1.0, cell.age / 50.0)
            # Shift towards white for older cells
            base_color = [int(c + (255 - c) * age_factor * 0.3) for c in base_color]
        
        # Quantum phase-based color cycling
        if cell.cell_type == CellType.QUANTUM:
            phase_offset = math.sin(cell.quantum_phase + self.time) * 0.3
            hsv = colorsys.rgb_to_hsv(base_color[0]/255, base_color[1]/255, base_color[2]/255)
            hsv = ((hsv[0] + phase_offset) % 1.0, hsv[1], hsv[2])
            rgb = colorsys.hsv_to_rgb(*hsv)
            base_color = [int(c * 255) for c in rgb]
        
        return tuple(base_color)

    def draw_cell(self, screen, x: int, y: int, cell: Cell):
        pixel_x = x * self.cell_size
        pixel_y = y * self.cell_size
        
        if cell.cell_type == CellType.EMPTY:
            return
        
        color = self.get_cell_color(cell, x, y)
        
        pygame.draw.rect(screen, color, 
                        (pixel_x, pixel_y, self.cell_size, self.cell_size))
        
        if (cell.cell_type == CellType.QUANTUM or 
            (self.show_energy and cell.energy > 1.5)):
            glow_surface = self.glow_surfaces.get(cell.cell_type)
            if glow_surface:
                glow_x = pixel_x - self.cell_size
                glow_y = pixel_y - self.cell_size
                screen.blit(glow_surface, (glow_x, glow_y), special_flags=pygame.BLEND_ADD)
        
        if self.show_energy and cell.energy > 0:
            energy_height = int(self.cell_size * 0.8 * min(1.0, cell.energy / 2.0))
            energy_rect = pygame.Rect(pixel_x + self.cell_size - 2, 
                                    pixel_y + self.cell_size - energy_height,
                                    2, energy_height)
            pygame.draw.rect(screen, (255, 255, 0), energy_rect)

    def draw_grid_lines(self, screen):
        if not self.show_grid:
            return
        
        grid_color = (40, 40, 50)
        
        major_grid_color = (60, 60, 80)
        
        for x in range(0, self.screen_width + 1, self.cell_size):
            cell_x = x // self.cell_size
            if cell_x % 10 == 0:
                pygame.draw.line(screen, major_grid_color, (x, 0), (x, self.screen_height), 2)
            else:
                pygame.draw.line(screen, grid_color, (x, 0), (x, self.screen_height), 1)
        
        for y in range(0, self.screen_height + 1, self.cell_size):
            cell_y = y // self.cell_size
            if cell_y % 10 == 0:
                pygame.draw.line(screen, major_grid_color, (0, y), (self.screen_width, y), 2)
            else:
                pygame.draw.line(screen, grid_color, (0, y), (self.screen_width, y), 1)

    def add_birth_effect(self, x: int, y: int, cell_type: CellType):
        pixel_x = x * self.cell_size + self.cell_size // 2
        pixel_y = y * self.cell_size + self.cell_size // 2
        color = self.colors[cell_type]
        
        for _ in range(5):
            self.particle_system.add_particle(
                x=pixel_x, y=pixel_y,
                vx=np.random.uniform(-2, 2),
                vy=np.random.uniform(-2, 2),
                color=color,
                life=30
            )

    def add_death_effect(self, x: int, y: int, cell_type: CellType):
        pixel_x = x * self.cell_size + self.cell_size // 2
        pixel_y = y * self.cell_size + self.cell_size // 2
        color = self.colors[cell_type]
        
        for _ in range(8):
            self.particle_system.add_particle(
                x=pixel_x, y=pixel_y,
                vx=np.random.uniform(-3, 3),
                vy=np.random.uniform(-3, 3),
                color=color,
                life=20
            )

    def render(self, screen) -> None:
        self.time += 0.05
        
        screen.fill((0, 0, 0))
        
        fade_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 5))
        self.trail_surface.blit(fade_surface, (0, 0))
        
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell = self.game.grid[y, x]
                self.draw_cell(screen, x, y, cell)
                
                if cell.cell_type == CellType.QUANTUM:
                    trail_color = (*self.colors[CellType.QUANTUM], 30)
                    pygame.draw.circle(self.trail_surface, trail_color,
                                     (x * self.cell_size + self.cell_size // 2,
                                      y * self.cell_size + self.cell_size // 2),
                                     self.cell_size // 3)
        
        screen.blit(self.trail_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
        self.particle_system.update()
        self.particle_system.draw(screen)
        
        self.draw_grid_lines(screen)

    def world_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        return screen_x // self.cell_size, screen_y // self.cell_size

    def toggle_energy_display(self):
        self.show_energy = not self.show_energy

    def toggle_age_display(self):
        self.show_age = not self.show_age

    def toggle_grid_display(self):
        self.show_grid = not self.show_grid


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color: Tuple[int, int, int], life: int):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        self.vy += 0.1
        self.vx *= 0.98
        self.vy *= 0.98

    def draw(self, screen):
        if self.life <= 0:
            return
        
        alpha = int(255 * (self.life / self.max_life))
        color = (*self.color, alpha)
        
        particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color, (2, 2), 2)
        screen.blit(particle_surface, (int(self.x - 2), int(self.y - 2)))

    def is_alive(self) -> bool:
        return self.life > 0


class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []

    def add_particle(self, x: float, y: float, vx: float, vy: float,
                    color: Tuple[int, int, int], life: int):
        self.particles.append(Particle(x, y, vx, vy, color, life))

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

    def clear(self):
        self.particles.clear()