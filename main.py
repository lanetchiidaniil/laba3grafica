#!/usr/bin/env python3
# Точка входа: запускает окно приложения и аргументы командной строки.
import argparse
import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from laba3grafica.config import DEFAULT_CENTER, DEFAULT_ITERATIONS, DEFAULT_SCALE
    from laba3grafica.fractal import build_fractal_image
    from laba3grafica.palette import Palette
else:
    from .config import DEFAULT_CENTER, DEFAULT_ITERATIONS, DEFAULT_SCALE
    from .fractal import build_fractal_image
    from .palette import Palette


def parse_args():
    parser = argparse.ArgumentParser(description="Фрактал Коллингвуда")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, help="Максимальное число итераций")
    parser.add_argument("--headless", action="store_true", help="Запуск без графического окна для проверки")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.headless:
        image = build_fractal_image(
            480,
            360,
            DEFAULT_CENTER[0],
            DEFAULT_CENTER[1],
            DEFAULT_SCALE,
            args.iterations,
            Palette("Night"),
        )
        print(
            f"Headless render completed: center=({DEFAULT_CENTER[0]:.5f}, {DEFAULT_CENTER[1]:.5f}), "
            f"scale={DEFAULT_SCALE:.5f}, iterations={args.iterations}, shape={image.shape}"
        )
        return 0

    # Import the GUI app only when needed so headless mode works without pygame.
    if __package__ in (None, ""):
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from laba3grafica.app import CollingwoodFractalApp
    else:
        from .app import CollingwoodFractalApp

    app = CollingwoodFractalApp(max_iter=args.iterations)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
