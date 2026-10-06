import math

import numpy as np
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
    def __init__(self, width=WIDTH, height=HEIGHT, max_iter=DEFAULT_ITERATIONS):
        pygame.init()

        self.width = width
        self.height = height
        self.hud_height = 110
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE
        self.max_iter = max_iter
        self.palette = Palette("Night")
        self.render_width = 440
        self.render_height = 300
        self.running = True
        self._needs_render = True
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Collingwood Fractal")

    def request_render(self):
        self._needs_render = True

    def reset(self):
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE
        self.max_iter = DEFAULT_ITERATIONS
        self.request_render()

    def update_zoom_label(self):
        zoom = DEFAULT_SCALE / self.scale
        return f"Zoom: {zoom:.2f}x"

    def draw_hud(self):
        hud = pygame.Surface((self.width, self.hud_height), pygame.SRCALPHA)
        hud.fill((18, 18, 22, 220))
        pygame.draw.rect(hud, (70, 70, 90), (0, 0, self.width, self.hud_height), 2)

        title = self.font.render("Collingwood Fractal", True, (255, 255, 255))
        hud.blit(title, (20, 16))

        info = [
            self.update_zoom_label(),
            f"Center: ({self.center_x:.5f}, {self.center_y:.5f})",
            f"Iterations: {self.max_iter}",
        ]

        for idx, text in enumerate(info):
            label = self.small_font.render(text, True, (220, 220, 220))
            hud.blit(label, (20, 48 + idx * 22))

        controls = self.small_font.render("LMB: zoom in  |  RMB: zoom out  |  R: reset  |  +/-: iterations  |  ESC: exit", True, (180, 220, 255))
        hud.blit(controls, (20, 88))

        self.screen.blit(hud, (0, 0))

    def render(self):
        if not self._needs_render:
            return

        fractal = build_fractal_image(
            self.render_width,
            self.render_height,
            self.center_x,
            self.center_y,
            self.scale,
            self.max_iter,
            self.palette,
        )
        surf = pygame.surfarray.make_surface(fractal)
        scaled = pygame.transform.smoothscale(surf, (self.width, self.height - self.hud_height))

        self.screen.fill((0, 0, 0))
        self.screen.blit(scaled, (0, self.hud_height))
        self.draw_hud()
        pygame.display.flip()
        self._needs_render = False

    def zoom_at(self, px, py, factor):
        render_x = px * (self.render_width / self.width)
        render_y = (py - self.hud_height) * (self.render_height / (self.height - self.hud_height))
        target_x, target_y = screen_to_complex(render_x, render_y, self.render_width, self.render_height, self.center_x, self.center_y, self.scale)
        self.center_x = target_x
        self.center_y = target_y
        self.scale /= factor
        self.request_render()

    def zoom_out(self, px, py, factor):
        render_x = px * (self.render_width / self.width)
        render_y = (py - self.hud_height) * (self.render_height / (self.height - self.hud_height))
        target_x, target_y = screen_to_complex(render_x, render_y, self.render_width, self.render_height, self.center_x, self.center_y, self.scale)
        self.center_x = target_x
        self.center_y = target_y
        self.scale *= factor
        self.request_render()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_r:
                self.reset()
                self.request_render()
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                self.max_iter = min(1500, self.max_iter + 50)
                self.request_render()
            elif event.key in (pygame.K_MINUS, pygame.K_UNDERSCORE):
                self.max_iter = max(50, self.max_iter - 50)
                self.request_render()
            elif event.key == pygame.K_h:
                self.palette = Palette("Night")
                self.request_render()
            elif event.key == pygame.K_j:
                self.palette = Palette("Sunset")
                self.request_render()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1:
                self.zoom_at(x, y, 1.8)
            elif event.button == 3:
                self.zoom_out(x, y, 1.8)

    def run(self):
        self.render()
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            if self._needs_render:
                self.render()
            pygame.time.delay(33)

        pygame.quit()
