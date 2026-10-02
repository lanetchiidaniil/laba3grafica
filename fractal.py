# Модуль вычислений: содержит формулу Коллингвуда и генерацию изображения фрактала.
import math

import numpy as np

from config import ESCAPE_RADIUS
from palette import Palette


def screen_to_complex(px, py, width, height, center_x, center_y, scale):
    y_scale = scale * (height / width)
    cx = (px / width - 0.5) * scale + center_x
    cy = (py / height - 0.5) * y_scale + center_y
    return cx, cy


def collingwood_escape(cx, cy, max_iter):
    x = 0.0
    y = 0.0
    for i in range(max_iter):
        ax = abs(x)
        ay = abs(y)
        x_new = abs(ax * ax - ay * ay) + cx
        y_new = abs(2.0 * ax * ay) + cy
        x, y = x_new, y_new
        if x * x + y * y > ESCAPE_RADIUS * ESCAPE_RADIUS:
            abs_z = math.sqrt(x * x + y * y)
            if abs_z > 1.0 and math.isfinite(abs_z):
                smooth = i + 1.0 - math.log2(math.log2(abs_z))
                return i, smooth
            return i, float(i)
    return max_iter, float(max_iter)


def build_fractal_image(width, height, center_x, center_y, scale, max_iter, palette=None):
    if palette is None:
        palette = Palette()

    x_coords = (np.arange(width, dtype=np.float64) / width - 0.5) * scale + center_x
    y_scale = scale * (height / width)
    y_coords = (np.arange(height, dtype=np.float64) / height - 0.5) * y_scale + center_y
    grid_x, grid_y = np.meshgrid(x_coords, y_coords)

    x = np.zeros_like(grid_x)
    y = np.zeros_like(grid_y)
    escape_counts = np.full(grid_x.shape, max_iter, dtype=np.int32)
    smooth_values = np.zeros(grid_x.shape, dtype=np.float64)
    active = np.ones(grid_x.shape, dtype=bool)

    for iteration in range(max_iter):
        if not np.any(active):
            break
        ax = np.abs(x[active])
        ay = np.abs(y[active])
        x_new = np.abs(ax * ax - ay * ay) + grid_x[active]
        y_new = np.abs(2.0 * ax * ay) + grid_y[active]
        x[active] = x_new
        y[active] = y_new

        escaped = np.where(active & ((x * x + y * y) > ESCAPE_RADIUS * ESCAPE_RADIUS))
        if escaped[0].size > 0:
            values = np.sqrt(x[escaped] * x[escaped] + y[escaped] * y[escaped])
            valid = np.isfinite(values) & (values > 1.0)
            smooth_values[escaped] = np.where(valid, iteration + 1.0 - np.log2(np.log2(values)), iteration)
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
