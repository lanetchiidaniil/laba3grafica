# GUI-модуль: создаёт окно, canvas, HUD и обработчики ввода.
import tkinter as tk
from tkinter import ttk

from config import DEFAULT_CENTER, DEFAULT_SCALE, HEIGHT, WIDTH
from fractal import build_fractal_image, screen_to_complex
from palette import Palette


class FractalApp:
    def __init__(self, root, max_iter):
        self.root = root
        self.width = WIDTH
        self.height = HEIGHT
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE
        self.max_iter = max_iter
        self.palette = Palette("Night")
        self.status_var = tk.StringVar()
        self.iteration_var = tk.IntVar(value=self.max_iter)
        self.render_width = 500
        self.render_height = 400

        self.root.title("Коллингвуд / Перпендикулярный Горящий Корабль")
        self.root.geometry(f"{self.width}x{self.height + 170}")
        self.root.resizable(False, False)

        self.control_frame = ttk.LabelFrame(root, text="Управление", padding=(10, 8))
        self.control_frame.pack(fill="x", padx=10, pady=(8, 0))

        self.help_label = ttk.Label(
            self.control_frame,
            text="ЛКМ — увеличить | Скролл — масштаб | R — сброс | +/- — итерации | Q — выход",
            justify="left",
            wraplength=980,
        )
        self.help_label.pack(anchor="w")

        self.options_row = ttk.Frame(self.control_frame)
        self.options_row.pack(anchor="w", pady=(8, 0))

        ttk.Label(self.options_row, text="Цвет: ").pack(side="left")
        self.palette_var = tk.StringVar(value=self.palette.name)
        self.palette_combo = ttk.Combobox(
            self.options_row,
            textvariable=self.palette_var,
            values=list(Palette.PRESETS.keys()),
            state="readonly",
            width=18,
        )
        self.palette_combo.pack(side="left", padx=(0, 8))
        self.palette_combo.bind("<<ComboboxSelected>>", self.on_palette_change)

        ttk.Label(self.options_row, text="Итерации: ").pack(side="left")
        self.iteration_scale = ttk.Scale(
            self.options_row,
            from_=20,
            to=250,
            orient="horizontal",
            variable=self.iteration_var,
            command=self.on_iteration_change,
            length=220,
        )
        self.iteration_scale.pack(side="left", padx=(0, 6))

        self.iteration_entry = ttk.Entry(self.options_row, textvariable=self.iteration_var, width=6)
        self.iteration_entry.pack(side="left")
        self.iteration_entry.bind("<Return>", self.on_iteration_enter)

        self.status = ttk.Label(
            self.control_frame,
            textvariable=self.status_var,
            background="#171b2b",
            foreground="white",
            anchor="w",
            padding=(8, 4),
            justify="left",
        )
        self.status.pack(fill="x", pady=(8, 0))

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.photo = tk.PhotoImage(width=self.render_width, height=self.render_height)
        self.image_id = self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        self.canvas.pack(fill="both", padx=10, pady=10)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", self.on_scroll)
        self.canvas.bind("<Button-4>", self.on_scroll)
        self.canvas.bind("<Button-5>", self.on_scroll)
        self.root.bind("<KeyPress>", self.on_key)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.render()

    @property
    def default_scale(self):
        return DEFAULT_SCALE

    def update_status(self):
        zoom_value = self.default_scale / self.scale
        self.status_var.set(
            f"Zoom: {zoom_value:.2f}x | "
            f"Center: ({self.center_x:.5f}, {self.center_y:.5f}) | "
            f"Iterations: {self.max_iter} | "
            f"Palette: {self.palette.name} | "
            f"R reset | +/- adjust"
        )

    def on_palette_change(self, event=None):
        self.palette.set_palette(self.palette_var.get())
        self.render()

    def on_iteration_change(self, value=None):
        try:
            self.max_iter = max(20, min(250, int(float(self.iteration_var.get()))))
            self.iteration_var.set(self.max_iter)
            self.render()
        except ValueError:
            return

    def on_iteration_enter(self, event=None):
        self.on_iteration_change()

    def render(self):
        self.max_iter = max(20, min(250, int(self.max_iter)))
        self.iteration_var.set(self.max_iter)
        rgb = build_fractal_image(
            self.render_width,
            self.render_height,
            self.center_x,
            self.center_y,
            self.scale,
            self.max_iter,
            self.palette,
        )

        colors = [
            "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
            for r, g, b in rgb.reshape(-1, 3)
        ]
        self.photo = tk.PhotoImage(width=self.render_width, height=self.render_height)
        self.photo.put(colors, to=(0, 0))
        self.photo = self.photo.zoom(2, 2)
        self.canvas.itemconfig(self.image_id, image=self.photo)
        self.update_status()
        self.root.update_idletasks()

    def reset(self):
        self.center_x, self.center_y = DEFAULT_CENTER
        self.scale = DEFAULT_SCALE
        self.render()

    def zoom_at(self, px, py, factor):
        target_cx, target_cy = screen_to_complex(px, py, self.width, self.height, self.center_x, self.center_y, self.scale)
        self.center_x = target_cx
        self.center_y = target_cy
        self.scale /= factor
        self.render()

    def zoom_out(self, px, py, factor):
        target_cx, target_cy = screen_to_complex(px, py, self.width, self.height, self.center_x, self.center_y, self.scale)
        self.center_x = target_cx
        self.center_y = target_cy
        self.scale *= factor
        self.render()

    def close(self):
        self.root.destroy()

    def on_click(self, event):
        self.zoom_at(event.x, event.y, 1.8)

    def on_scroll(self, event):
        delta = getattr(event, "delta", 0)
        if delta > 0 or getattr(event, "num", 0) == 4:
            self.zoom_at(event.x, event.y, 1.5)
        else:
            self.zoom_out(event.x, event.y, 1.5)

    def on_key(self, event):
        key = (event.keysym or "").lower()
        if key in {"escape", "q"}:
            self.close()
            return
        if key == "r":
            self.reset()
            return
        if key in {"equal", "plus", "kp_add"}:
            self.max_iter = max(20, min(250, self.max_iter + 25))
            self.iteration_var.set(self.max_iter)
            self.render()
            return
        if key in {"minus", "kp_subtract"}:
            self.max_iter = max(20, min(250, self.max_iter - 25))
            self.iteration_var.set(self.max_iter)
            self.render()
