# Модуль вычислений: содержит формулу Коллингвуда и генерацию изображения фрактала.
import math

import numpy as np

if __package__ in (None, ""):
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from laba3grafica.config import ESCAPE_RADIUS
    from laba3grafica.palette import Palette
else:
    from .config import ESCAPE_RADIUS
    from .palette import Palette


def screen_to_complex(px, py, width, height, center_x, center_y, scale):
    y_scale = scale * (height / width)
    cx = (px / width - 0.5) * scale + center_x
    cy = (py / height - 0.5) * y_scale + center_y
    return cx, cy


def collingwood_escape(cx, cy, max_iter):
    x = 0.0
    y = 0.0
    for i in range(max_iter):
        x_new = abs(x * x - y * y) + cx
        y_new = 2.0 * abs(x * y) + cy
        x, y = x_new, y_new
        if x * x + y * y > ESCAPE_RADIUS * ESCAPE_RADIUS:
            abs_z = math.sqrt(x * x + y * y)
            if abs_z > 1.0 and math.isfinite(abs_z):
                smooth = i + 1.0 - math.log(math.log(abs_z), 2.0)
                return i, smooth
            return i, float(i)
    return max_iter, float(max_iter)


def build_fractal_image(width, height, center_x, center_y, scale, max_iter, palette=None):
    if palette is None:
        palette = Palette("Night")

    x_scale = scale
    y_scale = scale * (height / width)
    x_coords = np.linspace(-0.5, 0.5, width, dtype=np.float64) * x_scale + center_x
    y_coords = np.linspace(-0.5, 0.5, height, dtype=np.float64) * y_scale + center_y
    grid_x, grid_y = np.meshgrid(x_coords, y_coords)

    x = np.zeros_like(grid_x, dtype=np.float64)
    y = np.zeros_like(grid_y, dtype=np.float64)
    escape_counts = np.full(grid_x.shape, max_iter, dtype=np.int32)
    smooth_values = np.zeros(grid_x.shape, dtype=np.float64)
    active = np.ones(grid_x.shape, dtype=bool)

    for iteration in range(max_iter):
        if not np.any(active):
            break

        mask = active
        x_vals = x[mask]
        y_vals = y[mask]

        x_new = np.abs(x_vals * x_vals - y_vals * y_vals) + grid_x[mask]
        y_new = 2.0 * np.abs(x_vals * y_vals) + grid_y[mask]

        x[mask] = x_new
        y[mask] = y_new

        escaped = np.where(mask & ((x * x + y * y) > ESCAPE_RADIUS * ESCAPE_RADIUS))
        if escaped[0].size > 0:
            values = np.sqrt(x[escaped] * x[escaped] + y[escaped] * y[escaped])
            valid = np.isfinite(values) & (values > 1.0)
            smooth_values[escaped] = np.where(valid, iteration + 1.0 - np.log(np.log(values)) / np.log(2.0), iteration)
            escape_counts[escaped] = iteration
            active[escaped] = False

    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    rgb[escape_counts == max_iter] = (0, 0, 0)

    escaped_idx = escape_counts < max_iter
    if np.any(escaped_idx):
        t = np.clip(smooth_values[escaped_idx] / max_iter, 0.0, 1.0)
        palette_values = np.array(palette.stops, dtype=np.float64)
        scaled = t * (len(palette_values) - 1)
        index = np.floor(scaled).astype(int)
        fraction = scaled - index
        idx_next = np.clip(index + 1, 0, len(palette_values) - 1)
        c1 = palette_values[index]
        c2 = palette_values[idx_next]
        rgb[escaped_idx] = (c1 + (c2 - c1) * fraction[:, None]).astype(np.uint8)

    return rgb
