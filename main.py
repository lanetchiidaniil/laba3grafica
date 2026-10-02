#!/usr/bin/env python3
# Точка входа: запускает окно приложения и аргументы командной строки.
import argparse
import sys
import tkinter as tk

from app import FractalApp
from config import DEFAULT_ITERATIONS


def parse_args():
    parser = argparse.ArgumentParser(description="Алгебраический фрактал: Коллингвуд")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, help="Максимальное число итераций")
    parser.add_argument("--headless", action="store_true", help="Запуск без графического окна для проверки")
    return parser.parse_args()


def main():
    args = parse_args()
    root = tk.Tk()
    if args.headless:
        root.withdraw()
        app = FractalApp(root, args.iterations)
        app.render()
        root.update()
        print(
            f"Headless render completed: center=({app.center_x:.5f}, {app.center_y:.5f}), "
            f"scale={app.scale:.5f}, iterations={app.max_iter}"
        )
        root.destroy()
        return 0

    app = FractalApp(root, args.iterations)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
