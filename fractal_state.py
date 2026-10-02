from dataclasses import dataclass, field

from config import DEFAULT_CENTER, DEFAULT_ITERATIONS, DEFAULT_SCALE, HEIGHT, WIDTH
from palette import Palette


@dataclass
class FractalState:
    """Состояние фрактала и его визуализации."""

    center_x: float = DEFAULT_CENTER[0]
    center_y: float = DEFAULT_CENTER[1]
    scale: float = DEFAULT_SCALE
    max_iter: int = DEFAULT_ITERATIONS
    palette: Palette = field(default_factory=lambda: Palette("Inferno"))
    render_width: int = WIDTH
    render_height: int = HEIGHT

    def reset(self):
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE

    def clamp_iterations(self):
        self.max_iter = max(20, min(250, self.max_iter))
        return self.max_iter
