import pygame
import math
from typing import Optional, Tuple, Dict, List
from game_core import GameOfLife, CellType
from patterns import PatternLibrary
from events import EventSystem, EventType
from stats import StatisticsTracker
import json
import os

class FixedButton:
    def __init__(self, x, y, width, height, text, font, bg_color=(60, 60, 70), hover_color=(80, 80, 90), pressed_color=(100, 100, 110), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.pressed_color = pressed_color
        self.text_color = text_color
        self.is_pressed = False
        self.is_hovered = False
        self.enabled = True
        self.clicked = False
        
    def handle_event(self, event):
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                self.clicked = True
                return True
            self.is_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        return False
    
    def update_position(self, x, y, width=None, height=None):
        if width is not None:
            self.rect.width = width
        if height is not None:
            self.rect.height = height
        self.rect.x = x
        self.rect.y = y
    
    def draw(self, screen):
        if not self.enabled:
            color = (40, 40, 40)
            text_color = (100, 100, 100)
        elif self.is_pressed:
            color = self.pressed_color
            text_color = self.text_color
        elif self.is_hovered:
            color = self.hover_color
            text_color = self.text_color
        else:
            color = self.bg_color
            text_color = self.text_color
            
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2, border_radius=5)
        
        if self.enabled and (self.is_hovered or self.is_pressed):
            overlay = pygame.Surface((self.rect.width, self.rect.height // 2), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 20))
            screen.blit(overlay, self.rect.topleft)
        
        font_size = min(self.rect.height - 8, 20)
        if hasattr(self, '_cached_font_size') and self._cached_font_size != font_size:
            self._cached_font = pygame.font.Font(None, font_size)
            self._cached_font_size = font_size
        elif not hasattr(self, '_cached_font'):
            self._cached_font = pygame.font.Font(None, font_size)
            self._cached_font_size = font_size
            
        text_surface = self._cached_font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class FixedSlider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, font, label="", format_str="{:.1f}"):
        self.rect = pygame.Rect(x, y, width, 24)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.font = font
        self.label = label
        self.format_str = format_str
        self.dragging = False
        self.handle_radius = 10
        
    def update_position(self, x, y, width):
        self.rect.x = x
        self.rect.y = y
        self.rect.width = width
        
    def handle_event(self, event):
        handle_x = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_x - self.handle_radius, self.rect.centery - self.handle_radius, 
                                self.handle_radius * 2, self.handle_radius * 2)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])
            return True
        return False
    
    def update_value(self, mouse_x):
        relative_x = mouse_x - self.rect.x
        relative_x = max(0, min(self.rect.width, relative_x))
        ratio = relative_x / self.rect.width
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
    
    def draw(self, screen):
        track_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(screen, (40, 40, 50), track_rect, border_radius=3)
        pygame.draw.rect(screen, (100, 100, 120), track_rect, 2, border_radius=3)
        
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        filled_width = ratio * self.rect.width
        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.centery - 3, filled_width, 6)
            pygame.draw.rect(screen, (70, 130, 200), filled_rect, border_radius=3)
        
        handle_x = self.rect.x + ratio * self.rect.width
        handle_center = (int(handle_x), self.rect.centery)
        pygame.draw.circle(screen, (200, 200, 200), handle_center, self.handle_radius)
        pygame.draw.circle(screen, (100, 100, 120), handle_center, self.handle_radius, 2)
        pygame.draw.circle(screen, (255, 255, 255), handle_center, self.handle_radius - 3)
        
        value_text = self.format_str.format(self.value)
        small_font = pygame.font.Font(None, 16)
        text_surface = small_font.render(value_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(handle_x, self.rect.centery - 18))
        
        text_bg = pygame.Rect(text_rect.x - 3, text_rect.y - 1, text_rect.width + 6, text_rect.height + 2)
        pygame.draw.rect(screen, (0, 0, 0, 180), text_bg, border_radius=3)
        screen.blit(text_surface, text_rect)

class FixedCellButton:
    def __init__(self, x, y, width, height, cell_type, font, colors):
        self.rect = pygame.Rect(x, y, width, height)
        self.cell_type = cell_type
        self.font = font
        self.colors = colors
        self.is_pressed = False
        self.is_hovered = False
        self.is_selected = False
        self.clicked = False
        
    def update_position(self, x, y, width, height):
        self.rect.x = x
        self.rect.y = y
        self.rect.width = width
        self.rect.height = height
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                self.clicked = True
                return True
            self.is_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        return False
    
    def draw(self, screen):
        if self.is_selected:
            bg_color = (100, 100, 100)
            border_color = (255, 255, 0)
            border_width = 3
        elif self.is_pressed:
            bg_color = (80, 80, 80)
            border_color = (200, 200, 200)
            border_width = 2
        elif self.is_hovered:
            bg_color = (70, 70, 70)
            border_color = (180, 180, 180)
            border_width = 2
        else:
            bg_color = (50, 50, 50)
            border_color = (120, 120, 120)
            border_width = 1
            
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=5)
        
        if self.cell_type != CellType.EMPTY:
            indicator_margin = max(3, self.rect.width // 10)
            color_rect = pygame.Rect(
                self.rect.x + indicator_margin, 
                self.rect.y + indicator_margin, 
                self.rect.width - indicator_margin * 2, 
                max(10, self.rect.height - 25)
            )
            cell_color = self.colors.get(self.cell_type, (255, 255, 255))
            pygame.draw.rect(screen, cell_color, color_rect, border_radius=3)
            
            if self.cell_type == CellType.QUANTUM:
                glow_surface = pygame.Surface((color_rect.width + 4, color_rect.height + 4), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*cell_color, 100), (0, 0, color_rect.width + 4, color_rect.height + 4), border_radius=5)
                screen.blit(glow_surface, (color_rect.x - 2, color_rect.y - 2), special_flags=pygame.BLEND_ADD)
        
        label_text = {
            CellType.RED: "Red",
            CellType.GREEN: "Green", 
            CellType.BLUE: "Blue",
            CellType.QUANTUM: "Quantum",
            CellType.EMPTY: "Erase"
        }.get(self.cell_type, "?")
        
        font_size = min(14, max(10, self.rect.width // 6))
        small_font = pygame.font.Font(None, font_size)
        text_surface = small_font.render(label_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.rect.centerx, self.rect.bottom - 8))
        screen.blit(text_surface, text_rect)

class MiniMap:
    def __init__(self, x, y, width, height, game):
        self.rect = pygame.Rect(x, y, width, height)
        self.game = game
        self.surface = pygame.Surface((width, height))
        
    def update_position(self, x, y, width, height):
        self.rect.x = x
        self.rect.y = y
        self.rect.width = width
        self.rect.height = height
        self.surface = pygame.Surface((width, height))
        
    def update(self):
        self.surface.fill((0, 0, 0))
        
        if self.rect.width <= 0 or self.rect.height <= 0:
            return
            
        x_scale = self.rect.width / self.game.width
        y_scale = self.rect.height / self.game.height
        
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell = self.game.get_cell(x, y)
                if cell and cell.cell_type != CellType.EMPTY:
                    color = {
                        CellType.RED: (255, 100, 100),
                        CellType.GREEN: (100, 255, 100),
                        CellType.BLUE: (100, 100, 255),
                        CellType.QUANTUM: (255, 255, 255)
                    }.get(cell.cell_type, (128, 128, 128))
                    
                    pixel_x = int(x * x_scale)
                    pixel_y = int(y * y_scale)
                    
                    if 0 <= pixel_x < self.rect.width and 0 <= pixel_y < self.rect.height:
                        pixel_size = max(1, int(min(x_scale, y_scale)))
                        for dx in range(pixel_size):
                            for dy in range(pixel_size):
                                px, py = pixel_x + dx, pixel_y + dy
                                if 0 <= px < self.rect.width and 0 <= py < self.rect.height:
                                    self.surface.set_at((px, py), color)
    
    def draw(self, screen):
        screen.blit(self.surface, self.rect.topleft)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)

class UIController:
    def __init__(self, screen_width: int, screen_height: int, game: GameOfLife):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game = game
        
        self.min_panel_width = 240
        self.max_panel_width = 320
        self.panel_width_ratio = 0.22
        
        calculated_width = int(screen_width * self.panel_width_ratio)
        self.panel_width = max(self.min_panel_width, min(self.max_panel_width, calculated_width))
        self.panel_rect = pygame.Rect(screen_width - self.panel_width, 0, self.panel_width, screen_height)
        
        base_font_size = max(16, min(22, screen_height // 35))
        pygame.font.init()
        self.title_font = pygame.font.Font(None, base_font_size + 4)
        self.font = pygame.font.Font(None, base_font_size)
        self.small_font = pygame.font.Font(None, base_font_size - 2)
        
        self.show_ui = True
        self.current_cell_type = CellType.RED
        self.drawing_mode = True
        self.brush_size = 1
        self.show_stats = False
        self.show_patterns = False
        self.show_events = False
        self.show_grid = False
        self.show_energy = False
        self.show_age = False
        
        self.is_running = False
        self.speed_multiplier = 1.0
        
        self.pattern_library = PatternLibrary()
        self.selected_pattern = None
        
        self.colors = {
            CellType.RED: (255, 100, 100),
            CellType.GREEN: (100, 255, 100),
            CellType.BLUE: (100, 100, 255),
            CellType.QUANTUM: (255, 255, 255),
            CellType.EMPTY: (80, 80, 80)
        }
        
        self._create_ui_elements()

    def _create_ui_elements(self):
        margin = 12
        x = self.panel_rect.x + margin
        y = 35
        button_width = self.panel_width - 2 * margin
        button_height = 35
        spacing = 10
        
        self.buttons = {
            'play_pause': FixedButton(x, y, button_width, button_height, 'Play', self.font, 
                                    bg_color=(70, 120, 70), hover_color=(90, 150, 90), pressed_color=(110, 170, 110)),
            'step': FixedButton(x, y + button_height + spacing, button_width // 2 - 3, button_height, 'Step', self.font),
            'clear': FixedButton(x + button_width // 2 + 3, y + button_height + spacing, button_width // 2 - 3, button_height, 'Clear', self.font,
                               bg_color=(120, 70, 70), hover_color=(150, 90, 90), pressed_color=(170, 110, 110)),
        }
        
        slider_y = y + (button_height + spacing) * 2 + 25
        self.sliders = {
            'speed': FixedSlider(x, slider_y, button_width, 0.1, 10.0, 1.0, self.small_font, "Speed", "{:.1f}x"),
            'brush': FixedSlider(x, slider_y + 55, button_width, 1, 10, 1, self.small_font, "Brush Size", "{:.0f}"),
        }
        
        cell_y = slider_y + 130
        cell_cols = 2
        cell_rows = 2
        cell_width = (button_width - 8) // cell_cols
        cell_height = 55
        
        self.cell_buttons = {}
        cell_types = [CellType.RED, CellType.GREEN, CellType.BLUE, CellType.QUANTUM]
        
        for i, cell_type in enumerate(cell_types):
            col = i % cell_cols
            row = i // cell_cols
            button_x = x + col * (cell_width + 8)
            button_y = cell_y + row * (cell_height + 8)
            
            self.cell_buttons[cell_type] = FixedCellButton(
                button_x, button_y, cell_width, cell_height, cell_type, self.small_font, self.colors
            )
        
        erase_y = cell_y + cell_rows * (cell_height + 8) + 15
        self.cell_buttons[CellType.EMPTY] = FixedButton(
            x, erase_y, button_width, button_height, 'Erase Mode', self.font,
            bg_color=(80, 50, 50), hover_color=(100, 70, 70), pressed_color=(120, 90, 90)
        )
        
        toggle_y = erase_y + button_height + 25
        toggle_cols = 2
        toggle_width = (button_width - 8) // toggle_cols
        toggle_height = 32
        
        toggle_buttons_info = [
            ('stats', 'Stats'), ('patterns', 'Patterns'),
            ('events', 'Events'), ('grid', 'Grid'),
            ('energy', 'Energy'), ('age', 'Age'),
        ]
        
        self.toggle_buttons = {}
        for i, (key, label) in enumerate(toggle_buttons_info):
            col = i % toggle_cols
            row = i // toggle_cols
            button_x = x + col * (toggle_width + 8)
            button_y = toggle_y + row * (toggle_height + 6)
            
            self.toggle_buttons[key] = FixedButton(
                button_x, button_y, toggle_width, toggle_height, label, self.small_font
            )
        
        file_y = toggle_y + 3 * (toggle_height + 6) + 20
        file_width = (button_width - 8) // 2
        
        self.file_buttons = {
            'save': FixedButton(x, file_y, file_width, button_height, 'Save', self.font),
            'load': FixedButton(x + file_width + 8, file_y, file_width, button_height, 'Load', self.font),
        }

    def resize(self, new_width: int, new_height: int):
        self.screen_width = new_width
        self.screen_height = new_height
        
        calculated_width = int(new_width * self.panel_width_ratio)
        self.panel_width = max(self.min_panel_width, min(self.max_panel_width, calculated_width))
        self.panel_rect = pygame.Rect(new_width - self.panel_width, 0, self.panel_width, new_height)
        
        self._create_ui_elements()

    def handle_event(self, event, event_system: EventSystem, stats: StatisticsTracker):
        if not self.show_ui:
            return False
        
        if self.show_stats or self.show_patterns or self.show_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_overlay_clicks(event, event_system)
            return False
        
        for name, button in self.buttons.items():
            if button.handle_event(event):
                return self._handle_button_click(name, event_system, stats)
        
        for name, slider in self.sliders.items():
            if slider.handle_event(event):
                if name == 'speed':
                    self.speed_multiplier = slider.value
                elif name == 'brush':
                    self.brush_size = int(slider.value)
        
        for cell_type, button in self.cell_buttons.items():
            if isinstance(button, FixedCellButton):
                if button.handle_event(event):
                    self.current_cell_type = cell_type
                    self._update_cell_button_selection()
            elif isinstance(button, FixedButton):
                if button.handle_event(event):
                    self.current_cell_type = CellType.EMPTY
                    self._update_cell_button_selection()
        
        for name, button in self.toggle_buttons.items():
            if button.handle_event(event):
                self._handle_toggle_button(name)
        
        for name, button in self.file_buttons.items():
            if button.handle_event(event):
                if name == 'save':
                    self.save_state()
                elif name == 'load':
                    self.load_state()
        
        if event.type == pygame.KEYDOWN:
            return self._handle_keyboard(event, event_system)
        
        return False

    def _handle_overlay_clicks(self, event, event_system):
        mouse_pos = event.pos
        
        if self.show_events and hasattr(self, 'event_buttons_rects'):
            for event_type, button_rect in self.event_buttons_rects.items():
                if button_rect.collidepoint(mouse_pos):
                    import random
                    x = random.randint(0, self.game.width - 1)
                    y = random.randint(0, self.game.height - 1)
                    event_system.force_event(event_type, x, y)
                    return
        
        if self.show_patterns:
            pattern_rect = pygame.Rect(50, 100, min(350, self.screen_width - 100), 300)
            if pattern_rect.collidepoint(mouse_pos):
                self._handle_pattern_selection(mouse_pos, pattern_rect)
                return
        
        self.show_stats = False
        self.show_patterns = False
        self.show_events = False

    def _handle_pattern_selection(self, mouse_pos, pattern_rect):
        relative_y = mouse_pos[1] - pattern_rect.y - 40
        if relative_y < 0:
            return
        
        pattern_categories = self.pattern_library.get_patterns_by_category()
        current_y = 0
        
        for category, patterns in pattern_categories.items():
            if current_y <= relative_y < current_y + 25:
                return
            current_y += 25
            
            for pattern in patterns[:3]:
                if current_y <= relative_y < current_y + 18:
                    self.selected_pattern = pattern
                    return
                current_y += 18
            
            current_y += 10

    def _update_cell_button_selection(self):
        for cell_type, button in self.cell_buttons.items():
            if isinstance(button, FixedCellButton):
                button.is_selected = (cell_type == self.current_cell_type)

    def _handle_button_click(self, button_name: str, event_system: EventSystem, stats: StatisticsTracker):
        if button_name == 'play_pause':
            self.toggle_simulation()
        elif button_name == 'step':
            return True
        elif button_name == 'clear':
            self.game.clear_grid()
        return False

    def _handle_toggle_button(self, button_name: str):
        if button_name == 'stats':
            self.show_stats = not self.show_stats
            self.show_patterns = False
            self.show_events = False
        elif button_name == 'patterns':
            self.show_patterns = not self.show_patterns
            self.show_stats = False
            self.show_events = False
        elif button_name == 'events':
            self.show_events = not self.show_events
            self.show_stats = False
            self.show_patterns = False
        elif button_name == 'grid':
            self.show_grid = not self.show_grid
        elif button_name == 'energy':
            self.show_energy = not self.show_energy
        elif button_name == 'age':
            self.show_age = not self.show_age

    def _handle_keyboard(self, event, event_system):
        if event.key == pygame.K_SPACE:
            self.toggle_simulation()
        elif event.key == pygame.K_s:
            return True
        elif event.key == pygame.K_c:
            self.game.clear_grid()
        elif event.key == pygame.K_h:
            self.show_ui = not self.show_ui
        elif event.key == pygame.K_1:
            self.current_cell_type = CellType.RED
            self._update_cell_button_selection()
        elif event.key == pygame.K_2:
            self.current_cell_type = CellType.GREEN
            self._update_cell_button_selection()
        elif event.key == pygame.K_3:
            self.current_cell_type = CellType.BLUE
            self._update_cell_button_selection()
        elif event.key == pygame.K_4:
            self.current_cell_type = CellType.QUANTUM
            self._update_cell_button_selection()
        elif event.key == pygame.K_0:
            self.current_cell_type = CellType.EMPTY
            self._update_cell_button_selection()
        elif event.key == pygame.K_g:
            self.show_grid = not self.show_grid
        elif event.key == pygame.K_m:
            import random
            x = random.randint(0, self.game.width - 1)
            y = random.randint(0, self.game.height - 1)
            event_system.force_event(EventType.METEOR, x, y)
        
        return False

    def handle_mouse_input(self, mouse_pos: Tuple[int, int], mouse_buttons: Tuple[bool, bool, bool], visualizer):
        if self.show_stats or self.show_patterns or self.show_events:
            return
            
        if not self.drawing_mode or not mouse_buttons[0]:
            return
        
        if mouse_pos[0] >= self.screen_width - self.panel_width:
            return
        
        grid_x, grid_y = visualizer.world_to_grid(mouse_pos[0], mouse_pos[1])
        
        for dy in range(-self.brush_size + 1, self.brush_size):
            for dx in range(-self.brush_size + 1, self.brush_size):
                target_x = grid_x + dx
                target_y = grid_y + dy
                
                if (0 <= target_x < self.game.width and 0 <= target_y < self.game.height):
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance < self.brush_size:
                        if self.current_cell_type == CellType.EMPTY:
                            self.game.set_cell(target_x, target_y, CellType.EMPTY)
                        else:
                            energy = 1.0 + (self.brush_size - distance) * 0.2
                            self.game.set_cell(target_x, target_y, self.current_cell_type, energy)

    def handle_pattern_placement(self, mouse_pos: Tuple[int, int], visualizer):
        if not self.selected_pattern or self.show_stats or self.show_patterns or self.show_events:
            return
        
        grid_x, grid_y = visualizer.world_to_grid(mouse_pos[0], mouse_pos[1])
        self.pattern_library.place_pattern(self.game, self.selected_pattern, 
                                          grid_x, grid_y, self.current_cell_type)
        print(f"Placed pattern: {self.selected_pattern} at ({grid_x}, {grid_y})")

    def toggle_simulation(self):
        self.is_running = not self.is_running
        self.buttons['play_pause'].text = 'Pause' if self.is_running else 'Play'

    def update(self, dt: float):
        pass

    def draw(self, screen):
        if not self.show_ui:
            self._draw_minimal_status(screen)
            return
        
        panel_surface = pygame.Surface((self.panel_width, self.screen_height), pygame.SRCALPHA)
        panel_surface.fill((25, 25, 35, 240))
        screen.blit(panel_surface, (self.screen_width - self.panel_width, 0))
        
        pygame.draw.rect(screen, (80, 80, 100), self.panel_rect, 2)
        
        title_text = self.title_font.render("Quantum Life", True, (255, 255, 255))
        screen.blit(title_text, (self.panel_rect.x + 10, 8))
        
        for button in self.buttons.values():
            button.draw(screen)
        
        slider_labels = {"speed": "Speed", "brush": "Brush Size"}
        for name, slider in self.sliders.items():
            label_y = slider.rect.y - 18
            label_text = self.small_font.render(slider_labels[name], True, (200, 200, 200))
            screen.blit(label_text, (slider.rect.x, label_y))
            slider.draw(screen)
        
        first_cell_button = list(self.cell_buttons.values())[0]
        cell_title = self.small_font.render("Cell Types", True, (200, 200, 200))
        screen.blit(cell_title, (self.panel_rect.x + 10, first_cell_button.rect.y - 18))
        
        for button in self.cell_buttons.values():
            button.draw(screen)
        
        first_toggle = list(self.toggle_buttons.values())[0]
        display_title = self.small_font.render("Display", True, (200, 200, 200))
        screen.blit(display_title, (self.panel_rect.x + 10, first_toggle.rect.y - 18))
        
        toggle_states = {
            'stats': self.show_stats, 'patterns': self.show_patterns, 'events': self.show_events,
            'grid': self.show_grid, 'energy': self.show_energy, 'age': self.show_age
        }
        
        for name, button in self.toggle_buttons.items():
            if toggle_states.get(name, False):
                button.bg_color = (70, 100, 140)
                button.hover_color = (90, 120, 160)
            else:
                button.bg_color = (60, 60, 70)
                button.hover_color = (80, 80, 90)
            button.draw(screen)
        
        file_title = self.small_font.render("Save/Load", True, (200, 200, 200))
        first_file = list(self.file_buttons.values())[0]
        screen.blit(file_title, (self.panel_rect.x + 10, first_file.rect.y - 18))
        
        for button in self.file_buttons.values():
            button.draw(screen)
        
        self._draw_stats_info(screen)
        
        if self.show_stats:
            self._draw_stats_overlay(screen)
        if self.show_patterns:
            self._draw_patterns_overlay(screen)
        if self.show_events:
            self._draw_events_overlay(screen)

    def _draw_minimal_status(self, screen):
        status_text = f"Gen: {self.game.generation} | Pop: {sum(self.game.get_population_counts().values()) - self.game.get_population_counts()[CellType.EMPTY]} | Speed: {self.speed_multiplier:.1f}x | H to show UI"
        text_surface = self.font.render(status_text, True, (255, 255, 255))
        
        text_bg = pygame.Rect(5, 5, text_surface.get_width() + 10, text_surface.get_height() + 6)
        pygame.draw.rect(screen, (0, 0, 0, 180), text_bg, border_radius=3)
        screen.blit(text_surface, (10, 8))

    def _draw_stats_info(self, screen):
        file_buttons_bottom = max(button.rect.bottom for button in self.file_buttons.values())
        stats_y = file_buttons_bottom + 25
        
        stats_title = self.small_font.render("Game Info", True, (200, 200, 200))
        screen.blit(stats_title, (self.panel_rect.x + 12, stats_y))
        stats_y += 25
        
        gen_text = self.small_font.render(f"Generation: {self.game.generation}", True, (255, 255, 255))
        screen.blit(gen_text, (self.panel_rect.x + 12, stats_y))
        
        counts = self.game.get_population_counts()
        total_pop = sum(count for cell_type, count in counts.items() if cell_type != CellType.EMPTY)
        pop_text = self.small_font.render(f"Total Population: {total_pop}", True, (255, 255, 255))
        screen.blit(pop_text, (self.panel_rect.x + 12, stats_y + 18))
        
        species_y = stats_y + 45
        for i, cell_type in enumerate([CellType.RED, CellType.GREEN, CellType.BLUE, CellType.QUANTUM]):
            if species_y + i * 18 > self.panel_rect.bottom - 30:
                break
                
            count = counts.get(cell_type, 0)
            color = self.colors[cell_type]
            
            color_rect = pygame.Rect(self.panel_rect.x + 12, species_y + i * 18, 12, 12)
            pygame.draw.rect(screen, color, color_rect, border_radius=2)
            pygame.draw.rect(screen, (150, 150, 150), color_rect, 1, border_radius=2)
            
            text = self.small_font.render(f"{cell_type.name}: {count:,}", True, (255, 255, 255))
            screen.blit(text, (self.panel_rect.x + 28, species_y + i * 18))
        
        if self.selected_pattern:
            pattern_y = species_y + 90
            if pattern_y < self.panel_rect.bottom - 40:
                pattern_title = self.small_font.render("Selected Pattern:", True, (200, 200, 200))
                screen.blit(pattern_title, (self.panel_rect.x + 12, pattern_y))
                pattern_text = self.small_font.render(self.selected_pattern, True, (255, 255, 100))
                screen.blit(pattern_text, (self.panel_rect.x + 12, pattern_y + 16))
                
                instr_text = self.small_font.render("Right-click to place", True, (150, 150, 150))
                screen.blit(instr_text, (self.panel_rect.x + 12, pattern_y + 32))

    def _draw_stats_overlay(self, screen):
        overlay_width = min(450, self.screen_width - 100)
        overlay_rect = pygame.Rect(50, 50, overlay_width, 400)
        
        overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay_surface.fill((20, 20, 30, 230))
        screen.blit(overlay_surface, overlay_rect.topleft)
        
        pygame.draw.rect(screen, (100, 100, 120), overlay_rect, 2, border_radius=5)
        
        title = self.title_font.render("Statistics", True, (255, 255, 255))
        screen.blit(title, (overlay_rect.x + 10, overlay_rect.y + 10))
        
        y_offset = 45
        counts = self.game.get_population_counts()
        total_pop = sum(count for cell_type, count in counts.items() if cell_type != CellType.EMPTY)
        
        gen_text = self.font.render(f"Generation: {self.game.generation}", True, (255, 255, 255))
        screen.blit(gen_text, (overlay_rect.x + 10, overlay_rect.y + y_offset))
        y_offset += 25
        
        pop_text = self.font.render(f"Total Population: {total_pop:,}", True, (255, 255, 255))
        screen.blit(pop_text, (overlay_rect.x + 10, overlay_rect.y + y_offset))
        y_offset += 25
        
        energy_text = self.font.render(f"Total Energy: {self.game.total_energy:.1f}", True, (255, 255, 255))
        screen.blit(energy_text, (overlay_rect.x + 10, overlay_rect.y + y_offset))
        y_offset += 30
        
        species_title = self.font.render("Species Breakdown:", True, (200, 200, 200))
        screen.blit(species_title, (overlay_rect.x + 10, overlay_rect.y + y_offset))
        y_offset += 25
        
        for cell_type in [CellType.RED, CellType.GREEN, CellType.BLUE, CellType.QUANTUM]:
            count = counts.get(cell_type, 0)
            percentage = (count / total_pop * 100) if total_pop > 0 else 0
            color = self.colors[cell_type]
            
            color_rect = pygame.Rect(overlay_rect.x + 15, overlay_rect.y + y_offset, 12, 12)
            pygame.draw.rect(screen, color, color_rect, border_radius=2)
            
            text = self.small_font.render(f"{cell_type.name}: {count:,} ({percentage:.1f}%)", True, (255, 255, 255))
            screen.blit(text, (overlay_rect.x + 35, overlay_rect.y + y_offset))
            y_offset += 20
        
        y_offset += 15
        entropy = self.game.calculate_entropy()
        entropy_text = self.small_font.render(f"Entropy: {entropy:.3f}", True, (200, 200, 255))
        screen.blit(entropy_text, (overlay_rect.x + 10, overlay_rect.y + y_offset))
        y_offset += 18
        
        if len(self.game.population_history[CellType.RED]) > 1:
            prev_total = sum(self.game.population_history[cell_type][-2] for cell_type in [CellType.RED, CellType.GREEN, CellType.BLUE, CellType.QUANTUM])
            growth_rate = ((total_pop - prev_total) / prev_total * 100) if prev_total > 0 else 0
            growth_text = self.small_font.render(f"Growth Rate: {growth_rate:+.1f}%", True, (255, 200, 200))
            screen.blit(growth_text, (overlay_rect.x + 10, overlay_rect.y + y_offset))
        
        close_text = self.font.render("Click anywhere to close", True, (180, 180, 180))
        screen.blit(close_text, (overlay_rect.x + 10, overlay_rect.bottom - 30))

    def _draw_patterns_overlay(self, screen):
        overlay_width = min(350, self.screen_width - 100)
        overlay_rect = pygame.Rect(50, 100, overlay_width, 300)
        
        overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay_surface.fill((20, 20, 30, 230))
        screen.blit(overlay_surface, overlay_rect.topleft)
        
        pygame.draw.rect(screen, (100, 100, 120), overlay_rect, 2, border_radius=5)
        
        title = self.title_font.render("Pattern Library", True, (255, 255, 255))
        screen.blit(title, (overlay_rect.x + 10, overlay_rect.y + 10))
        
        pattern_categories = self.pattern_library.get_patterns_by_category()
        y_offset = 40
        
        for category, patterns in pattern_categories.items():
            if y_offset > overlay_rect.height - 60:
                break
                
            cat_text = self.font.render(f"▼ {category}", True, (200, 200, 100))
            screen.blit(cat_text, (overlay_rect.x + 15, overlay_rect.y + y_offset))
            y_offset += 25
            
            for pattern in patterns[:3]:
                if y_offset > overlay_rect.height - 60:
                    break
                    
                color = (255, 255, 100) if pattern == self.selected_pattern else (180, 180, 180)
                pattern_text = self.small_font.render(f"  • {pattern}", True, color)
                screen.blit(pattern_text, (overlay_rect.x + 25, overlay_rect.y + y_offset))
                y_offset += 18
            
            y_offset += 10

    def _draw_events_overlay(self, screen):
        overlay_width = min(300, self.screen_width - 100)
        overlay_rect = pygame.Rect(50, 150, overlay_width, 280)
        
        overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay_surface.fill((20, 20, 30, 230))
        screen.blit(overlay_surface, overlay_rect.topleft)
        
        pygame.draw.rect(screen, (100, 100, 120), overlay_rect, 2, border_radius=5)
        
        title = self.title_font.render("Events", True, (255, 255, 255))
        screen.blit(title, (overlay_rect.x + 10, overlay_rect.y + 10))
        
        if not hasattr(self, 'event_buttons_rects'):
            self.event_buttons_rects = {}
        
        event_types = list(EventType)[:7]
        for i, event_type in enumerate(event_types):
            button_rect = pygame.Rect(overlay_rect.x + 15, overlay_rect.y + 50 + i * 30, overlay_width - 30, 25)
            self.event_buttons_rects[event_type] = button_rect
            
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = button_rect.collidepoint(mouse_pos)
            
            button_color = (80, 80, 100) if is_hovering else (60, 60, 80)
            border_color = (150, 150, 170) if is_hovering else (120, 120, 140)
            
            pygame.draw.rect(screen, button_color, button_rect, border_radius=3)
            pygame.draw.rect(screen, border_color, button_rect, 1, border_radius=3)
            
            event_name = event_type.value.replace('_', ' ').title()
            text = self.small_font.render(event_name, True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
        
        instruction = self.small_font.render("Click event to trigger", True, (180, 180, 180))
        screen.blit(instruction, (overlay_rect.x + 15, overlay_rect.bottom - 25))

    def save_state(self):
        state = {
            'generation': self.game.generation,
            'width': self.game.width,
            'height': self.game.height,
            'cells': []
        }
        
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell = self.game.get_cell(x, y)
                if cell and cell.cell_type != CellType.EMPTY:
                    state['cells'].append({
                        'x': x, 'y': y,
                        'type': cell.cell_type.value,
                        'energy': cell.energy,
                        'age': cell.age
                    })
        
        filename = f"game_state_gen_{self.game.generation}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
            print(f"State saved to {filename}")
        except Exception as e:
            print(f"Error saving state: {e}")

    def load_state(self):
        save_files = [f for f in os.listdir('.') if f.startswith('game_state_') and f.endswith('.json')]
        if not save_files:
            print("No save files found")
            return
        
        latest_file = max(save_files, key=lambda f: os.path.getmtime(f))
        
        try:
            with open(latest_file, 'r') as f:
                state = json.load(f)
            
            self.game.clear_grid()
            
            for cell_data in state.get('cells', []):
                cell_type = CellType(cell_data['type'])
                self.game.set_cell(cell_data['x'], cell_data['y'], cell_type, cell_data.get('energy', 1.0))
            
            print(f"State loaded from {latest_file}")
        except Exception as e:
            print(f"Error loading state: {e}")

    def get_simulation_should_run(self) -> bool:
        return self.is_running

    def get_speed_multiplier(self) -> float:
        return self.speed_multiplier