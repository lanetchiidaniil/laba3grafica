# Палитра: задаёт плавную цветовую градацию для внешней области фрактала.
class Palette:
    PRESETS = {
        "Night": [(5, 5, 20), (25, 70, 140), (232, 150, 30), (255, 245, 220)],
        "Sunset": [(20, 12, 40), (128, 32, 74), (255, 128, 60), (255, 235, 170)],
        "Ice": [(5, 10, 30), (22, 82, 125), (89, 176, 219), (227, 245, 255)],
        "Neon": [(15, 10, 30), (80, 0, 120), (0, 200, 170), (255, 255, 120)],
    }

    def __init__(self, name="Night"):
        self.name = name
        self.stops = list(self.PRESETS[name])

    def set_palette(self, name):
        if name in self.PRESETS:
            self.name = name
            self.stops = list(self.PRESETS[name])

    def color_hex(self, t):
        t = max(0.0, min(1.0, t))
        if t <= 0.0:
            rgb = self.stops[0]
        elif t >= 1.0:
            rgb = self.stops[-1]
        else:
            scaled = t * (len(self.stops) - 1)
            index = int(scaled)
            fraction = scaled - index
            c1 = self.stops[index]
            c2 = self.stops[min(index + 1, len(self.stops) - 1)]
            rgb = tuple(
                int(c1[i] + (c2[i] - c1[i]) * fraction)
                for i in range(3)
            )
        return "#{:02x}{:02x}{:02x}".format(*rgb)
