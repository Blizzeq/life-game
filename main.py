import pygame
import sys
import time
from game_core import GameOfLife, CellType
from visualization import Visualizer
from ui_controller import UIController
from events import EventSystem
from stats import StatisticsTracker
from patterns import PatternLibrary

class QuantumLifeGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()
        
        # Get screen info for responsive design
        screen_info = pygame.display.Info()
        available_width = screen_info.current_w - 100  # Leave some margin
        available_height = screen_info.current_h - 150  # Leave margin for taskbar/titlebar
        
        # Game settings - adaptive to screen size
        self.CELL_SIZE = max(6, min(12, available_width // 150))
        self.MIN_CELL_SIZE = 3
        self.MAX_CELL_SIZE = 20
        
        # Calculate optimal grid and screen size
        ui_panel_width = int(available_width * 0.22)
        ui_panel_width = max(240, min(320, ui_panel_width))
        
        game_area_width = available_width - ui_panel_width
        game_area_height = available_height
        
        self.GRID_WIDTH = game_area_width // self.CELL_SIZE
        self.GRID_HEIGHT = game_area_height // self.CELL_SIZE
        
        self.GRID_WIDTH = max(80, self.GRID_WIDTH)
        self.GRID_HEIGHT = max(60, self.GRID_HEIGHT)
        
        self.SCREEN_WIDTH = self.GRID_WIDTH * self.CELL_SIZE + ui_panel_width
        self.SCREEN_HEIGHT = self.GRID_HEIGHT * self.CELL_SIZE
        self.FPS = 60
        
        self.game = GameOfLife(self.GRID_WIDTH, self.GRID_HEIGHT)
        self.visualizer = Visualizer(self.game, self.CELL_SIZE)
        self.ui_controller = UIController(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game)
        self.event_system = EventSystem(self.game)
        self.stats = StatisticsTracker(self.game)
        
        # Pygame setup with resizable window
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Quantum Life - Enhanced Conway's Game of Life")
        self.clock = pygame.time.Clock()
        
        self.visualizer.initialize_surfaces(self.screen)
        self.last_update_time = time.time()
        self.update_interval = 1.0 / 5.0
        
        self._load_demo_pattern()

    def _load_demo_pattern(self):
        pattern_lib = PatternLibrary()
        pattern_lib.place_pattern(self.game, "Glider", 10, 10, CellType.RED)
        pattern_lib.place_pattern(self.game, "Glider", 80, 20, CellType.GREEN)
        pattern_lib.place_pattern(self.game, "Pulsar", 40, 30, CellType.BLUE)
        pattern_lib.place_pattern(self.game, "Quantum Cross", 60, 50, CellType.QUANTUM)
        pattern_lib.place_pattern(self.game, "Gosper Glider Gun", 10, 50, CellType.RED)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
            
            should_step = self.ui_controller.handle_event(event, self.event_system, self.stats)
            if should_step:
                self.step_simulation()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:
                    self.ui_controller.drawing_mode = True
                elif event.button == 3:
                    self.ui_controller.handle_pattern_placement(mouse_pos, self.visualizer)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.ui_controller.drawing_mode = False
                    self.ui_controller.drawing_started = False
            elif event.type == pygame.MOUSEWHEEL:
                self.handle_zoom(event.y)
        
        return True

    def handle_resize(self, new_width: int, new_height: int):
        self.SCREEN_WIDTH = max(800, new_width)
        self.SCREEN_HEIGHT = max(600, new_height)
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        
        ui_panel_width = int(self.SCREEN_WIDTH * 0.22)
        ui_panel_width = max(240, min(320, ui_panel_width))
        
        game_area_width = self.SCREEN_WIDTH - ui_panel_width
        game_area_height = self.SCREEN_HEIGHT
        
        new_grid_width = game_area_width // self.CELL_SIZE
        new_grid_height = game_area_height // self.CELL_SIZE
        
        new_grid_width = max(40, new_grid_width)
        new_grid_height = max(30, new_grid_height)
        
        if new_grid_width != self.GRID_WIDTH or new_grid_height != self.GRID_HEIGHT:
            self.GRID_WIDTH = new_grid_width
            self.GRID_HEIGHT = new_grid_height
            self.game.resize_grid(self.GRID_WIDTH, self.GRID_HEIGHT)
        
        self.ui_controller.resize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.visualizer.initialize_surfaces(self.screen)

    def handle_zoom(self, zoom_direction: int):
        if zoom_direction > 0:
            new_cell_size = min(self.MAX_CELL_SIZE, self.CELL_SIZE + 1)
        else:
            new_cell_size = max(self.MIN_CELL_SIZE, self.CELL_SIZE - 1)
        
        if new_cell_size != self.CELL_SIZE:
            self.CELL_SIZE = new_cell_size
            self.visualizer.cell_size = self.CELL_SIZE
            
            ui_panel_width = int(self.SCREEN_WIDTH * 0.22)
            ui_panel_width = max(240, min(320, ui_panel_width))
            game_area_width = self.SCREEN_WIDTH - ui_panel_width
            game_area_height = self.SCREEN_HEIGHT
            
            new_grid_width = game_area_width // self.CELL_SIZE
            new_grid_height = game_area_height // self.CELL_SIZE
            new_grid_width = max(40, new_grid_width)
            new_grid_height = max(30, new_grid_height)
            
            if new_grid_width != self.GRID_WIDTH or new_grid_height != self.GRID_HEIGHT:
                self.GRID_WIDTH = new_grid_width
                self.GRID_HEIGHT = new_grid_height
                self.game.resize_grid(self.GRID_WIDTH, self.GRID_HEIGHT)
            
            self.visualizer.screen_width = self.GRID_WIDTH * self.CELL_SIZE
            self.visualizer.screen_height = self.GRID_HEIGHT * self.CELL_SIZE
            self.visualizer.initialize_surfaces(self.screen)

    def update(self, dt):
        self.ui_controller.update(dt)
        self.stats.update()
        self.event_system.update()
        self.event_system.apply_event_effects()
        
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.SCREEN_WIDTH - self.ui_controller.panel_width:
                self.ui_controller.handle_mouse_input(mouse_pos, mouse_buttons, self.visualizer)
        
        self.visualizer.show_grid = self.ui_controller.show_grid
        self.visualizer.show_energy = self.ui_controller.show_energy
        self.visualizer.show_age = self.ui_controller.show_age
        
        current_time = time.time()
        speed_multiplier = self.ui_controller.get_speed_multiplier()
        adjusted_interval = self.update_interval / speed_multiplier
        
        if (self.ui_controller.get_simulation_should_run() and 
            current_time - self.last_update_time >= adjusted_interval):
            self.step_simulation()
            self.last_update_time = current_time

    def step_simulation(self):
        self.game.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.visualizer.render(self.screen)
        self._render_events()
        self.ui_controller.draw(self.screen)
        self._draw_debug_info()
        pygame.display.flip()

    def _render_events(self):
        for event in self.event_system.active_events:
            self._draw_event_effect(event)

    def _draw_event_effect(self, event):
        center_x = event.x * self.CELL_SIZE + self.CELL_SIZE // 2
        center_y = event.y * self.CELL_SIZE + self.CELL_SIZE // 2
        
        if event.event_type.value == 'meteor':
            radius = int(event.radius * self.CELL_SIZE * event.get_age_factor())
            if radius > 0:
                color = (255, int(200 * (1 - event.get_age_factor())), 0)
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius, 2)
        
        elif event.event_type.value == 'energy_wave':
            wave_radius = int(event.radius * self.CELL_SIZE * event.get_age_factor())
            if wave_radius > 0:
                color = (0, 255, 255, int(100 * (1 - event.get_age_factor())))
                pygame.draw.circle(self.screen, color, (center_x, center_y), wave_radius, 3)
        
        elif event.event_type.value == 'quantum_storm':
            import random
            import math
            for i in range(10):
                angle = random.random() * 2 * math.pi
                distance = random.random() * event.radius * self.CELL_SIZE
                x = center_x + int(math.cos(angle) * distance)
                y = center_y + int(math.sin(angle) * distance)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)
        
        for particle in event.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = (*particle['color'], alpha)
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (3, 3), 3)
                self.screen.blit(particle_surface, (int(particle['x'] - 3), int(particle['y'] - 3)))

    def _draw_debug_info(self):
        if not hasattr(self, '_debug_font'):
            self._debug_font = pygame.font.Font(None, 20)
        
        if self.event_system.active_events:
            y_offset = 50
            for i, event in enumerate(self.event_system.active_events[:5]):
                event_text = f"{event.event_type.value}: {event.duration}/{event.max_duration}"
                text_surface = self._debug_font.render(event_text, True, (255, 255, 0))
                self.screen.blit(text_surface, (10, y_offset + i * 20))

    def run(self):
        running = True
        
        while running:
            dt = self.clock.tick(self.FPS) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.render()
        
        self.quit()

    def quit(self):
        try:
            self.stats.export_data("final_stats.csv")
        except Exception:
            pass
        pygame.quit()
        sys.exit()

def main():
    try:
        game = QuantumLifeGame()
        game.run()
    except Exception:
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()