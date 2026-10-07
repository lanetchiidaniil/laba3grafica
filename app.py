import pygame

if __package__ in (None, ""):
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from laba3grafica.config import DEFAULT_CENTER, DEFAULT_ITERATIONS, DEFAULT_SCALE, HEIGHT, WIDTH
    from laba3grafica.fractal import build_fractal_image, screen_to_complex
    from laba3grafica.palette import Palette
else:
    from .config import DEFAULT_CENTER, DEFAULT_ITERATIONS, DEFAULT_SCALE, HEIGHT, WIDTH
    from .fractal import build_fractal_image, screen_to_complex
    from .palette import Palette


class CollingwoodFractalApp:
    def __init__(self, width=None, height=None, max_iter=DEFAULT_ITERATIONS):
        pygame.init()

        info = pygame.display.Info()
        screen_width = max(1, info.current_w or WIDTH)
        screen_height = max(1, info.current_h or HEIGHT)

        if width is None:
            width = int(screen_width * 0.75)
        if height is None:
            height = int(screen_height * 0.75)

        self.width = width
        self.height = height
        self.hud_height = 128
        self.menu_width = 220
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE
        self.initial_max_iter = max_iter
        self.max_iter = max_iter
        self.palette_names = list(Palette.PRESETS.keys())
        self.fractal_palette_name = "Night"
        self.background_palette_name = "Ice"
        self.fractal_palette = Palette(self.fractal_palette_name)
        self.background_palette = Palette(self.background_palette_name)
        effective_width = max(500, min(900, int((self.width - self.menu_width) * 0.85)))
        effective_height = max(350, min(620, int((self.height - self.hud_height) * 0.85)))
        self.render_width = effective_width
        self.render_height = effective_height
        self.running = True
        self._needs_render = True
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 18)
        self.controls_font = pygame.font.SysFont(None, 16)
        self.action_buttons = {}
        self.selected_point = None
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Collingwood Fractal")

    @property
    def palette(self):
        return self.fractal_palette

    @palette.setter
    def palette(self, value):
        self.fractal_palette = value
        self.fractal_palette_name = value.name

    def request_render(self):
        self._needs_render = True

    def reset(self):
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE
        self.max_iter = self.initial_max_iter
        self.selected_point = None
        self.request_render()

    def set_palette(self, name, target="fractal"):
        if target == "fractal":
            if name not in Palette.PRESETS:
                return
            self.fractal_palette_name = name
            self.fractal_palette = Palette(name)
        elif target == "background":
            if name not in Palette.PRESETS:
                return
            self.background_palette_name = name
            self.background_palette = Palette(name)
        self.request_render()

    def cycle_palette(self, target="fractal", step=1):
        names = self.palette_names
        if target == "fractal":
            current = self.fractal_palette_name
        else:
            current = self.background_palette_name
        index = names.index(current)
        self.set_palette(names[(index + step) % len(names)], target)

    def update_zoom_label(self):
        zoom = DEFAULT_SCALE / self.scale
        return f"Zoom: {zoom:.2f}x"

    def draw_hud(self):
        hud_width = self.width - self.menu_width
        hud = pygame.Surface((hud_width, self.hud_height), pygame.SRCALPHA)
        hud.fill((14, 18, 24, 220))
        pygame.draw.rect(hud, (110, 145, 200), (0, 0, hud_width, self.hud_height), 1)

        title = self.font.render("Collingwood Fractal", True, (255, 255, 255))
        hud.blit(title, (18, 8))

        info = [
            self.update_zoom_label(),
            f"Center: ({self.center_x:.5f}, {self.center_y:.5f})",
            f"Iterations: {self.max_iter}",
        ]

        y = 42
        for text in info:
            label = self.small_font.render(text, True, (220, 220, 220))
            hud.blit(label, (18, y))
            y += 18

        controls_1 = self.controls_font.render("LMB zoom in | RMB zoom out | R reset", True, (180, 220, 255))
        controls_2 = self.controls_font.render("+/− iter | Q/E palette | Esc", True, (180, 220, 255))
        hud.blit(controls_1, (18, 96))
        hud.blit(controls_2, (18, 112))

        self.screen.blit(hud, (0, 0))

    def draw_palette_menu(self):
        menu = pygame.Surface((self.menu_width, self.height - self.hud_height), pygame.SRCALPHA)
        menu.fill((14, 18, 24, 220))
        pygame.draw.rect(menu, (110, 145, 200), (0, 0, self.menu_width, self.height - self.hud_height), 1)

        title = self.small_font.render("Palettes", True, (255, 255, 255))
        menu.blit(title, (18, 16))

        block_y = 48
        for idx, name in enumerate(self.palette_names):
            color = (255, 255, 255)
            if name == self.fractal_palette_name:
                color = (120, 215, 255)
            label = self.small_font.render(f"{idx + 1}. {name}", True, color)
            menu.blit(label, (18, block_y + idx * 22))

        fractal_label = self.small_font.render(f"Fractal: {self.fractal_palette_name}", True, (210, 240, 255))
        menu.blit(fractal_label, (18, 48 + len(self.palette_names) * 22 + 10))

        background_label = self.small_font.render(f"Background: {self.background_palette_name}", True, (210, 240, 255))
        menu.blit(background_label, (18, 48 + len(self.palette_names) * 22 + 28))

        self.action_buttons = {}

        nav_title = self.controls_font.render("View", True, (255, 255, 255))
        menu.blit(nav_title, (18, self.height - self.hud_height - 98))

        zoom_rect = pygame.Rect(18, self.height - self.hud_height - 82, self.menu_width - 36, 28)
        self.action_buttons["auto_zoom"] = zoom_rect
        color = (80, 110, 180) if self.selected_point is not None else (58, 68, 82)
        pygame.draw.rect(menu, color, zoom_rect, 0 if self.selected_point is not None else 1)
        label = self.small_font.render("Zoom here", True, (255, 255, 255))
        menu.blit(label, (zoom_rect.x + 10, zoom_rect.y + 6))

        cell = 26
        start_x = 18
        start_y = self.height - self.hud_height - 48
        directions = [
            ("up", (start_x + cell, start_y)),
            ("left", (start_x, start_y + cell)),
            ("center", (start_x + cell, start_y + cell)),
            ("right", (start_x + 2 * cell, start_y + cell)),
            ("down", (start_x + cell, start_y + 2 * cell)),
        ]
        for name, pos in directions:
            rect = pygame.Rect(pos[0], pos[1], cell, cell)
            self.action_buttons[name] = rect
            pygame.draw.rect(menu, (72, 86, 110), rect, 1)
            text = self.small_font.render({"up": "↑", "down": "↓", "left": "←", "right": "→", "center": "○"}[name], True, (200, 220, 255))
            menu.blit(text, (pos[0] + 7, pos[1] + 4))

        note = self.controls_font.render("Q/E = next | 1/2 compare", True, (180, 220, 255))
        menu.blit(note, (18, self.height - self.hud_height - 10))

        self.screen.blit(menu, (self.width - self.menu_width, self.hud_height))

    def render(self):
        if not self._needs_render:
            return

        self.render_width = max(500, min(900, int((self.width - self.menu_width) * 0.85)))
        self.render_height = max(350, min(620, int((self.height - self.hud_height) * 0.85)))

        fractal = build_fractal_image(
            self.render_width,
            self.render_height,
            self.center_x,
            self.center_y,
            self.scale,
            self.max_iter,
            self.fractal_palette,
            self.background_palette,
        )
        surf = pygame.surfarray.make_surface(fractal)

        scaled = pygame.transform.smoothscale(surf, (self.width - self.menu_width, self.height - self.hud_height))

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (0, self.hud_height))

        self.draw_hud()
        self.draw_palette_menu()
        pygame.display.flip()
        self._needs_render = False

    def _view_rect(self):
        return pygame.Rect(0, self.hud_height, self.width - self.menu_width, self.height - self.hud_height)

    def _screen_to_fractal_coordinates(self, px, py):
        view = self._view_rect()
        if not view.collidepoint(px, py):
            return None

        local_x = float(px - view.left)
        local_y = float(py - view.top)
        px_norm = local_x / view.width
        py_norm = local_y / view.height
        render_x = px_norm * self.render_width
        render_y = py_norm * self.render_height
        return px_norm, py_norm, render_x, render_y

    def _apply_zoom(self, px, py, new_scale):
        point = self._screen_to_fractal_coordinates(px, py)
        if point is None:
            return

        px_norm, py_norm, render_x, render_y = point
        target_x, target_y = screen_to_complex(
            render_x,
            render_y,
            self.render_width,
            self.render_height,
            self.center_x,
            self.center_y,
            self.scale,
        )

        self.center_x = target_x - (px_norm - 0.5) * new_scale
        self.center_y = target_y - (py_norm - 0.5) * new_scale * (self.render_height / self.render_width)
        self.scale = new_scale
        self.request_render()

    def zoom_at(self, px, py, factor):
        view = self._view_rect()
        if not view.collidepoint(px, py):
            return

        self._apply_zoom(px, py, self.scale / factor)

    def zoom_out(self, px, py, factor):
        view = self._view_rect()
        if not view.collidepoint(px, py):
            return

        self._apply_zoom(px, py, self.scale * factor)

    def move_center(self, direction, step=None):
        if step is None:
            step = self.scale * 0.18

        if direction == "left":
            self.center_x += step
        elif direction == "right":
            self.center_x -= step
        elif direction == "up":
            self.center_y += step
        elif direction == "down":
            self.center_y -= step
        elif direction == "center":
            self.center_x, self.center_y = DEFAULT_CENTER
            self.scale = DEFAULT_SCALE
        self.request_render()

    def set_selected_point(self, px, py):
        view = self._view_rect()
        if not view.collidepoint(px, py):
            return False
        self.selected_point = (px, py)
        return True

    def auto_zoom_selected(self, factor=2.0):
        if self.selected_point is None:
            return
        px, py = self.selected_point
        self.zoom_at(px, py, factor)

    def trigger_menu_action(self, action):
        if action == "auto_zoom":
            if self.selected_point is None:
                self.selected_point = (self.width // 2, self.hud_height + (self.height - self.hud_height) // 2)
            self.auto_zoom_selected(2.0)
            return
        if action in {"left", "right", "up", "down", "center"}:
            self.move_center(action)

    def change_iterations(self, delta):
        self.max_iter = max(20, min(1500, self.max_iter + delta))
        self.request_render()

    def set_iterations(self, value):
        self.max_iter = max(20, min(1500, int(value)))
        self.request_render()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            key_text = (event.unicode or "").lower()

            if event.key == pygame.K_ESCAPE and not key_text:
                self.running = False
                return
            elif event.key == pygame.K_r or key_text == "r":
                self.reset()
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS) or key_text in ("+", "="):
                self.change_iterations(50)
            elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE, pygame.K_KP_MINUS) or key_text in ("-", "_"):
                self.change_iterations(-50)
            elif key_text == "1":
                self.set_iterations(20)
            elif key_text == "2":
                self.set_iterations(220)
            elif event.key == pygame.K_q or key_text in ("q", "й"):
                self.cycle_palette("fractal")
            elif event.key == pygame.K_e or key_text in ("e", "у"):
                self.cycle_palette("background")

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if x >= self.width - self.menu_width:
                menu_x = x - (self.width - self.menu_width)
                menu_y = y - self.hud_height
                for name, rect in self.action_buttons.items():
                    if rect.collidepoint(menu_x, menu_y):
                        self.trigger_menu_action(name)
                        return
                return

            if event.button == 1:
                self.zoom_at(x, y, 2.0)
                return

            if event.button == 3:
                self.zoom_out(x, y, 2.0)
                return

            if event.button == 4:
                self.zoom_at(x, y, 2.0)
                return

            if event.button == 5:
                self.zoom_out(x, y, 2.0)
                return

    def run(self):
        self.render()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if self._needs_render:
                self.render()
            pygame.time.delay(33)

        pygame.quit()
