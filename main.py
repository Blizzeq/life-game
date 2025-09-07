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
        self.CELL_SIZE = max(6, min(12, available_width // 150))  # Adaptive cell size
        
        # Calculate optimal grid size for the screen
        ui_panel_width = int(available_width * 0.25)  # 25% for UI
        game_area_width = available_width - ui_panel_width
        game_area_height = available_height
        
        self.GRID_WIDTH = game_area_width // self.CELL_SIZE
        self.GRID_HEIGHT = game_area_height // self.CELL_SIZE
        
        # Ensure minimum viable grid size
        self.GRID_WIDTH = max(80, self.GRID_WIDTH)
        self.GRID_HEIGHT = max(60, self.GRID_HEIGHT)
        
        # Calculate actual screen size
        self.SCREEN_WIDTH = self.GRID_WIDTH * self.CELL_SIZE + ui_panel_width
        self.SCREEN_HEIGHT = self.GRID_HEIGHT * self.CELL_SIZE
        self.FPS = 60
        
        print(f"Adaptive settings: Grid={self.GRID_WIDTH}x{self.GRID_HEIGHT}, Cell size={self.CELL_SIZE}, Screen={self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")
        
        # Initialize game components
        self.game = GameOfLife(self.GRID_WIDTH, self.GRID_HEIGHT)
        self.visualizer = Visualizer(self.game, self.CELL_SIZE)
        self.ui_controller = UIController(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, self.game)
        self.event_system = EventSystem(self.game)
        self.stats = StatisticsTracker(self.game)
        
        # Pygame setup with resizable window
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Quantum Life - Enhanced Conway's Game of Life")
        self.clock = pygame.time.Clock()
        
        # Initialize visualization surfaces
        self.visualizer.initialize_surfaces(self.screen)
        
        # Timing for simulation updates
        self.last_update_time = time.time()
        self.update_interval = 1.0 / 5.0  # Base 5 updates per second
        
        # Load demo pattern
        self._load_demo_pattern()
        
        print("Quantum Life Game initialized!")
        print("Controls:")
        print("  SPACE - Play/Pause")
        print("  S - Step simulation")
        print("  C - Clear grid")
        print("  H - Toggle UI")
        print("  1-4 - Select cell type (1=Red, 2=Green, 3=Blue, 4=Quantum)")
        print("  0 - Erase mode")
        print("  M - Trigger random meteor")
        print("  Mouse - Draw cells")
        print("  Right click - Place pattern")

    def _load_demo_pattern(self):
        """Load some interesting patterns to start with"""
        pattern_lib = PatternLibrary()
        
        # Place some gliders
        pattern_lib.place_pattern(self.game, "Glider", 10, 10, CellType.RED)
        pattern_lib.place_pattern(self.game, "Glider", 80, 20, CellType.GREEN)
        
        # Place an oscillator
        pattern_lib.place_pattern(self.game, "Pulsar", 40, 30, CellType.BLUE)
        
        # Place some quantum cells
        pattern_lib.place_pattern(self.game, "Quantum Cross", 60, 50, CellType.QUANTUM)
        
        # Place a gun
        pattern_lib.place_pattern(self.game, "Gosper Glider Gun", 10, 50, CellType.RED)

    def handle_events(self):
        """Handle all pygame and UI events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                self.handle_resize(event.w, event.h)
            
            # Handle UI events
            self.ui_controller.handle_event(event, self.event_system, self.stats)
            
            # Handle mouse input for drawing
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if event.button == 1:  # Left click - start drawing
                    self.ui_controller.drawing_mode = True
                elif event.button == 3:  # Right click - place pattern
                    self.ui_controller.handle_pattern_placement(mouse_pos, self.visualizer)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Stop drawing
                    self.ui_controller.drawing_mode = False
            
            # Handle stepping is now handled in ui_controller.handle_event
        
        return True

    def handle_resize(self, new_width: int, new_height: int):
        """Handle window resize"""
        # Update screen dimensions
        self.SCREEN_WIDTH = max(800, new_width)  # Minimum width
        self.SCREEN_HEIGHT = max(600, new_height)  # Minimum height
        
        # Recreate the screen surface
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        
        # Update UI controller for new size
        self.ui_controller.resize(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Reinitialize visualizer surfaces
        self.visualizer.initialize_surfaces(self.screen)
        
        print(f"Window resized to: {self.SCREEN_WIDTH}x{self.SCREEN_HEIGHT}")

    def update(self, dt):
        """Update game state"""
        # Update UI
        self.ui_controller.update(dt)
        
        # Update statistics
        self.stats.update()
        
        # Update events
        self.event_system.update()
        self.event_system.apply_event_effects()
        
        # Handle continuous mouse drawing
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]:  # Left mouse held
            mouse_pos = pygame.mouse.get_pos()
            # Check if mouse is not over UI (use dynamic panel width)
            if mouse_pos[0] < self.SCREEN_WIDTH - self.ui_controller.panel_width:
                self.ui_controller.handle_mouse_input(mouse_pos, mouse_buttons, self.visualizer)
        
        # Update visualizer settings from UI
        self.visualizer.show_grid = self.ui_controller.show_grid
        self.visualizer.show_energy = self.ui_controller.show_energy
        self.visualizer.show_age = self.ui_controller.show_age
        
        # Update simulation based on speed and play state
        current_time = time.time()
        speed_multiplier = self.ui_controller.get_speed_multiplier()
        adjusted_interval = self.update_interval / speed_multiplier
        
        if (self.ui_controller.get_simulation_should_run() and 
            current_time - self.last_update_time >= adjusted_interval):
            self.step_simulation()
            self.last_update_time = current_time
        
        # Update stats display
        if self.ui_controller.show_stats:
            pass  # Stats are drawn directly in the UI

    def step_simulation(self):
        """Advance simulation by one generation"""
        self.game.update()

    def render(self):
        """Render everything to screen"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render game world
        self.visualizer.render(self.screen)
        
        # Render event effects
        self._render_events()
        
        # Render UI
        self.ui_controller.draw(self.screen)
        
        # Draw additional info
        self._draw_debug_info()
        
        # Update display
        pygame.display.flip()

    def _render_events(self):
        """Render visual effects for active events"""
        for event in self.event_system.active_events:
            self._draw_event_effect(event)

    def _draw_event_effect(self, event):
        """Draw visual effect for a specific event"""
        center_x = event.x * self.CELL_SIZE + self.CELL_SIZE // 2
        center_y = event.y * self.CELL_SIZE + self.CELL_SIZE // 2
        
        # Event-specific visual effects
        if event.event_type.value == 'meteor':
            # Draw explosion effect
            radius = int(event.radius * self.CELL_SIZE * event.get_age_factor())
            if radius > 0:
                color = (255, int(200 * (1 - event.get_age_factor())), 0)
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius, 2)
        
        elif event.event_type.value == 'energy_wave':
            # Draw expanding wave
            wave_radius = int(event.radius * self.CELL_SIZE * event.get_age_factor())
            if wave_radius > 0:
                color = (0, 255, 255, int(100 * (1 - event.get_age_factor())))
                pygame.draw.circle(self.screen, color, (center_x, center_y), wave_radius, 3)
        
        elif event.event_type.value == 'quantum_storm':
            # Draw quantum effect
            import random
            import math
            for i in range(10):
                angle = random.random() * 2 * math.pi
                distance = random.random() * event.radius * self.CELL_SIZE
                x = center_x + int(math.cos(angle) * distance)
                y = center_y + int(math.sin(angle) * distance)
                pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 2)
        
        # Draw particles
        for particle in event.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = (*particle['color'], alpha)
                # Create small surface for particle with alpha
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (3, 3), 3)
                self.screen.blit(particle_surface, (int(particle['x'] - 3), int(particle['y'] - 3)))

    def _draw_debug_info(self):
        """Draw debug information"""
        if not hasattr(self, '_debug_font'):
            self._debug_font = pygame.font.Font(None, 20)
        
        # Active events info
        if self.event_system.active_events:
            y_offset = 50
            for i, event in enumerate(self.event_system.active_events[:5]):  # Show max 5 events
                event_text = f"{event.event_type.value}: {event.duration}/{event.max_duration}"
                text_surface = self._debug_font.render(event_text, True, (255, 255, 0))
                self.screen.blit(text_surface, (10, y_offset + i * 20))

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(self.FPS) / 1000.0
            
            # Handle events
            running = self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Render
            self.render()
        
        # Cleanup
        self.quit()

    def quit(self):
        """Clean shutdown"""
        # Export final statistics
        try:
            self.stats.export_data("final_stats.csv")
            print("Final statistics exported to final_stats.csv")
        except Exception as e:
            print(f"Error exporting stats: {e}")
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point"""
    try:
        game = QuantumLifeGame()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()