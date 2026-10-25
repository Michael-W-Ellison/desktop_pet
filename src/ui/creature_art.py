"""
Pixel-art creatures, drawn in code.

Each species is built from body parts (ellipses, smooth outlines, tapered
limbs) on a small pixel grid (64x64 for a full-grown pet). Shapes are reduced
to hard-edged pixels by coverage; each part is lit as a rounded surface and
quantised to a five-tone colour ramp (cool shadows, warm lights) with light
ordered dithering, and the sprite gets a coloured outline. Callers scale the
grid up with nearest-neighbour resampling for crisp pixels.

Coordinates are in a unit square (0-1), creature facing right, ground at GROUND.
"""
import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw

MASK_SUPERSAMPLE = 4
GROUND = 0.93
LIGHT = np.array([-0.45, -0.7, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = (LIGHT + np.array([0.0, 0.0, 1.0]))
HALF = HALF / np.linalg.norm(HALF)

Color = Tuple[int, int, int]
Point = Tuple[float, float]


# Colour helpers

def rgb(color) -> Color:
    """Colour from '#RRGGBB' or an (r, g, b) tuple."""
    if isinstance(color, str):
        color = color.lstrip('#')
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    return tuple(int(c) for c in color[:3])


def mix(a, b, t: float) -> Color:
    a, b = rgb(a), rgb(b)
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


def lighten(c, t: float) -> Color:
    return mix(c, (255, 255, 255), t)


def darken(c, t: float) -> Color:
    return mix(c, (0, 0, 0), t)


def desaturate(c, t: float) -> Color:
    c = rgb(c)
    grey = int(0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2])
    return mix(c, (grey, grey, grey), t)


# Geometry helpers

def catmull_rom(points: Sequence[Point], closed: bool = True, steps: int = 12) -> List[Point]:
    """Smooth curve through the points."""
    pts = list(points)
    n = len(pts)
    out = []
    segments = n if closed else n - 1
    for i in range(segments):
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[0]
        p1 = pts[i % n]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t
                                    + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    if not closed:
        out.append(pts[-1])
    return out


def ellipse_points(cx, cy, rx, ry, angle=0.0, n=72) -> List[Point]:
    ca, sa = math.cos(angle), math.sin(angle)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = rx * math.cos(t), ry * math.sin(t)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def _value_noise(shape, scale, seed) -> np.ndarray:
    """Smooth random field in 0-1."""
    rng = np.random.default_rng(seed)
    small = (max(2, int(shape[0] / scale)), max(2, int(shape[1] / scale)))
    img = Image.fromarray((rng.random(small) * 255).astype(np.uint8), 'L')
    return np.asarray(img.resize((shape[1], shape[0]), Image.BICUBIC), dtype=np.float32) / 255.0


def _box_blur(a: np.ndarray, r: int, axis: int) -> np.ndarray:
    """Mean over a window of 2r+1 along one axis (edges padded with zeros)."""
    pad = [(0, 0), (0, 0)]
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad), axis=axis, dtype=np.float64)
    hi = np.take(c, np.arange(2 * r + 1, c.shape[axis]), axis=axis)
    lo = np.take(c, np.arange(0, c.shape[axis] - 2 * r - 1), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian-like blur in floating point (three box passes per axis), free of 8-bit banding."""
    r = max(1, int(round((math.sqrt(4 * sigma * sigma + 1) - 1) / 2)))
    for axis in (0, 1):
        for _ in range(3):
            a = _box_blur(a, r, axis)
    return a


# Ordered-dither thresholds (4x4 Bayer matrix, 0-1)
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) + 0.5) / 16

# Tone levels of a colour ramp, darkest to lightest
RAMP = (0.42, 0.62, 0.82, 1.0, 1.18)


def ramp(color) -> List[Color]:
    """Pixel-art colour ramp: shadows shift toward cool purple, lights toward warm yellow."""
    c = rgb(color)
    out = []
    for level in RAMP:
        if level < 1:
            tone = mix(mix(c, (52, 36, 92), 0.35 * (1 - level) / 0.58), (0, 0, 0), (1 - level) * 0.75)
        else:
            tone = mix(c, (255, 244, 214), (level - 1) / 0.18 * 0.45)
        out.append(tone)
    return out


class Painter:
    """
    Builds one pixel-art creature on a grid x grid canvas.

    Shapes are drawn at MASK_SUPERSAMPLE times the grid and reduced to pixels by
    coverage (at least half covered), so outlines are clean and hard-edged.
    Each part is lit as a rounded surface and its brightness is quantised to a
    five-tone ramp with light ordered dithering; part edges are darkened one
    tone, and finish() adds a coloured outline around the whole sprite.
    """

    def __init__(self, size: int, seed: int = 0):
        self.grid = size
        self.n = size * MASK_SUPERSAMPLE
        self.seed = seed
        self._parts = 0
        self.rgb = np.zeros((size, size, 3), dtype=np.float32)
        self.alpha = np.zeros((size, size), dtype=np.float32)
        gy, gx = np.mgrid[0:size, 0:size]
        self._gx, self._gy = gx, gy
        self._bayer = np.tile(BAYER, (size // 4 + 1, size // 4 + 1))[:size, :size]

    # Coordinates (masks use the supersampled resolution)

    def px(self, v: float) -> float:
        return v * self.n

    def pts(self, points: Sequence[Point]) -> List[Tuple[float, float]]:
        return [(x * self.n, y * self.n) for x, y in points]

    def gpx(self, v: float) -> float:
        return v * self.grid

    # Masks

    def _blank(self):
        m = Image.new('L', (self.n, self.n), 0)
        return m, ImageDraw.Draw(m)

    def ellipse_mask(self, cx, cy, rx, ry, angle=0.0) -> Image.Image:
        m, d = self._blank()
        d.polygon(self.pts(ellipse_points(cx, cy, rx, ry, angle)), fill=255)
        return m

    def blob_mask(self, points: Sequence[Point]) -> Image.Image:
        m, d = self._blank()
        d.polygon(self.pts(catmull_rom(points)), fill=255)
        return m

    def poly_mask(self, points: Sequence[Point]) -> Image.Image:
        m, d = self._blank()
        d.polygon(self.pts(points), fill=255)
        return m

    def limb_mask(self, points: Sequence[Point], widths: Sequence[float]) -> Image.Image:
        """Tapered tube along a smooth path; widths are radii at each control point."""
        m, d = self._blank()
        # Stamp circles no further apart than half the thinnest radius, so long thin limbs stay smooth
        length = sum(math.dist(a, b) for a, b in zip(points, points[1:]))
        steps = max(16, int(length / max(1e-4, min(widths) * 0.5) / max(1, len(points) - 1)) + 1)
        path = catmull_rom(points, closed=False, steps=steps)
        k = len(path) - 1
        for i, (x, y) in enumerate(path):
            t = i / k * (len(widths) - 1)
            j = min(int(t), len(widths) - 2)
            r = (widths[j] + (widths[j + 1] - widths[j]) * (t - j)) * self.n
            cx, cy = x * self.n, y * self.n
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        return m

    @staticmethod
    def union(*masks: Image.Image) -> Image.Image:
        out = masks[0]
        for m in masks[1:]:
            out = Image.fromarray(np.maximum(np.asarray(out), np.asarray(m)))
        return out

    @staticmethod
    def subtract(mask: Image.Image, cut: Image.Image) -> Image.Image:
        a = np.asarray(mask).astype(np.int16) - np.asarray(cut).astype(np.int16)
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    @staticmethod
    def intersect(mask: Image.Image, keep: Image.Image) -> Image.Image:
        return Image.fromarray(np.minimum(np.asarray(mask), np.asarray(keep)))

    def coverage(self, mask: Image.Image) -> np.ndarray:
        """Share of each pixel the mask covers (0-1)."""
        return np.asarray(mask.resize((self.grid, self.grid), Image.Resampling.BOX), dtype=np.float32) / 255.0

    # Textures at pixel scale (values around 0, added to the tone level)

    def texture(self, kind: str, scale: float = 1.0, angle: float = 0.0) -> np.ndarray:
        g = self.grid
        seed = self.seed * 31 + self._parts
        rng = np.random.default_rng(seed)
        ca, sa = math.cos(angle), math.sin(angle)
        u = self._gx * ca + self._gy * sa
        v = -self._gx * sa + self._gy * ca
        if kind == 'fur':
            # Short strands: runs of slightly darker pixels along the fur direction
            noise = rng.random((g, g))
            strands = (np.sin(v * 1.7 + noise * 2.0) > 0.75).astype(np.float32)
            return -strands * 0.5 * min(1.5, scale)
        if kind in ('scales', 'feathers', 'scutes'):
            size = max(2.0, (3.0 if kind == 'feathers' else 2.5) * scale * g / 64)
            row = np.floor(v / size)
            uu = u / (size * (1.4 if kind == 'feathers' else 1.0)) + 0.5 * (row % 2)
            fu, fv = uu - np.floor(uu), v / size - row
            edge = ((fv > 0.66) | ((fu < 0.18) & (fv > 0.3))).astype(np.float32)
            return -edge * 0.7
        if kind == 'stone':
            a = _value_noise((g, g), max(2, g / 10), seed) - 0.5
            cracks = (np.abs(_value_noise((g, g), max(2, g / 7), seed + 3) - 0.5) < 0.04).astype(np.float32)
            return a * 1.2 - cracks * 1.0
        if kind == 'skin':
            return (_value_noise((g, g), max(2, g / 12), seed) - 0.5) * 0.2
        return np.zeros((g, g), dtype=np.float32)

    # Compositing

    def _over(self, colors: np.ndarray, alpha: np.ndarray):
        a = alpha[..., None]
        total = self.alpha + alpha * (1 - self.alpha)
        safe = np.where(total > 0, total, 1)[..., None]
        self.rgb = (colors * a + self.rgb * self.alpha[..., None] * (1 - a)) / safe
        self.alpha = total

    def part(self, mask: Image.Image, color, *, color2=None, gradient: float = 0.0,
             gloss: float = 0.25, roundness: float = 1.0, texture: Optional[str] = None,
             texture_scale: float = 1.0, texture_angle: float = 0.0, outline: float = 0.35,
             opacity: float = 1.0, glow: float = 0.0, flat: bool = False):
        """
        Composite one part as pixels.

        Args:
            mask: Part outline
            color: Base colour; color2 with gradient (0-1) blends toward it downward
            gloss: Strength of the lightest highlight pixels
            roundness: How domed the surface looks
            texture: 'fur', 'scales', 'feathers', 'scutes', 'stone', 'skin' or None
            outline: Above zero, the part's edge pixels are drawn one tone darker
            opacity: Overall alpha (translucent wings, spirits), kept to a few steps
            glow: Self-illumination (0-1) for fiery or magical parts
            flat: One tone only (markings drawn on an already shaded part)
        """
        self._parts += 1
        cov = self.coverage(mask)
        solid = cov >= 0.5
        if not solid.any():
            return
        g = self.grid
        rows = np.nonzero(solid.any(axis=1))[0]
        y0, y1 = rows.min(), rows.max()
        c1 = np.array(rgb(color), dtype=np.float32)
        if color2 is not None and gradient > 0:
            c2 = np.array(rgb(color2), dtype=np.float32)
            t = np.clip((self._gy - y0) / max(1, y1 - y0), 0, 1)[..., None] * gradient
            base = c1 + (c2 - c1) * t
        else:
            base = np.broadcast_to(c1, (g, g, 3)).astype(np.float32)

        if flat:
            level = np.full((g, g), 3.0, dtype=np.float32)
        else:
            area = solid.sum()
            r_eq = math.sqrt(area / math.pi)
            h = np.sqrt(np.clip(blur(solid.astype(np.float32), max(0.8, 0.42 * r_eq)), 0, 1))
            gy, gx = np.gradient(h)
            k = r_eq * 0.55 * roundness
            nx, ny, nz = -gx * k, -gy * k, np.ones_like(h)
            norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
            nx, ny, nz = nx / norm, ny / norm, nz / norm
            diffuse = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
            spec = np.clip(nx * HALF[0] + ny * HALF[1] + nz * HALF[2], 0, 1) ** 20
            # Level 0-4 on the ramp; 3 is the base colour
            level = 0.6 + diffuse * 3.0 + glow * 1.5
            if texture:
                level = level + self.texture(texture, texture_scale, texture_angle)
            level = level + (spec > 0.75) * gloss * 3.0
        # Ordered dithering between neighbouring tones
        tone = np.clip(np.floor(level + (self._bayer - 0.5) * 0.35 + 0.5), 0, 4).astype(np.int32)
        if outline > 0 and not flat:
            inner = solid & ~(np.roll(solid, 1, 0) & np.roll(solid, -1, 0) & np.roll(solid, 1, 1) & np.roll(solid, -1, 1))
            tone = np.where(inner, np.maximum(tone - 1, 0), tone)

        ramps = np.zeros((g, g, 3), dtype=np.float32)
        for lv in range(5):
            if color2 is not None and gradient > 0:
                # Per-pixel base: apply the ramp factor to each pixel's own base colour
                factor = np.array(ramp((128, 128, 128))[lv], dtype=np.float32) / 128.0
                layer = np.clip(base * factor, 0, 255)
            else:
                layer = np.broadcast_to(np.array(ramp(c1)[lv], dtype=np.float32), (g, g, 3))
            ramps = np.where((tone == lv)[..., None], layer, ramps)
        alpha = solid.astype(np.float32) * (round(opacity * 4) / 4)
        self._over(ramps, alpha)

    # Line work and details

    def stroke(self, points: Sequence[Point], width: float, color, opacity: float = 1.0, smooth: bool = True):
        g = self.grid
        layer = Image.new('L', (g, g), 0)
        d = ImageDraw.Draw(layer)
        path = catmull_rom(points, closed=False) if smooth and len(points) > 2 else list(points)
        w = max(1, int(round(width * g)))
        d.line([(x * g, y * g) for x, y in path], fill=255, width=w)
        m = np.asarray(layer, dtype=np.float32) / 255.0
        if opacity < 0.6 and w == 1:
            return  # Too faint to show as pixels
        self._over(np.broadcast_to(np.array(rgb(color), dtype=np.float32), (g, g, 3)),
                   (m >= 0.5) * (1.0 if opacity >= 0.6 else 0.5))

    def dot(self, cx, cy, r, color, opacity: float = 1.0, blur: float = 0.0):
        g = self.grid
        rr = max(0.5, r * g)
        dist = np.hypot(self._gx + 0.5 - cx * g, self._gy + 0.5 - cy * g)
        core = (dist <= rr).astype(np.float32)
        col = np.broadcast_to(np.array(rgb(color), dtype=np.float32), (g, g, 3))
        if blur:
            halo = ((dist <= rr + max(1.0, blur * g)) & (core == 0)).astype(np.float32)
            self._over(col, halo * 0.35 * opacity)
        self._over(col, core * (1.0 if opacity >= 0.6 else 0.5))

    def eye(self, cx, cy, r, iris, pupil: str = 'round', sclera=(250, 248, 240),
            look: Point = (0.25, 0.0), lid=None, squash: float = 1.0):
        """Pixel eye: iris, pupil and a highlight pixel, sized from the radius."""
        g = self.grid
        rr = max(1.0, r * g)
        ry = rr * squash
        x, y = cx * g, cy * g
        dx = (self._gx + 0.5 - x) / rr
        dy = (self._gy + 0.5 - y) / max(0.8, ry)
        inside = dx ** 2 + dy ** 2 <= 1.15
        if not inside.any():
            iy, ix = int(y), int(x)
            inside = np.zeros((g, g), bool)
            inside[min(g - 1, iy), min(g - 1, ix)] = True
        lid_c = np.array(rgb(lid) if lid else (28, 20, 26), dtype=np.float32)
        iris_r = np.array(ramp(iris)[3], dtype=np.float32)
        iris_d = np.array(ramp(iris)[1], dtype=np.float32)
        colors = np.where((dy < -0.2)[..., None], iris_d, iris_r)
        if sclera is not None and rr >= 2.5 and pupil not in ('slit', 'goat'):
            colors = np.where(((dx - look[0] * 0.5) ** 2 + dy ** 2 > 0.45)[..., None],
                              np.array(rgb(sclera), dtype=np.float32), colors)
        px, py = x + look[0] * rr * 0.5, y + look[1] * rr * 0.5
        pdx, pdy = self._gx + 0.5 - px, self._gy + 0.5 - py
        if pupil == 'slit':
            pup = (np.abs(pdx) < max(0.5, rr * 0.22)) & (np.abs(pdy) < rr * 0.8)
        elif pupil == 'goat':
            pup = (np.abs(pdy) < max(0.5, rr * 0.2)) & (np.abs(pdx) < rr * 0.7)
        else:
            pup = np.hypot(pdx, pdy) < max(0.7, rr * 0.45)
        colors = np.where(pup[..., None], np.array((16, 12, 18), dtype=np.float32), colors)
        # Top lid line on larger eyes
        if rr >= 2.5:
            top = inside & ~np.roll(inside, 1, 0)
            colors = np.where(top[..., None], lid_c, colors)
        self._over(colors, inside.astype(np.float32))
        # Highlight pixel up and to the left of centre
        hx, hy = int(np.floor(x - rr * 0.35)), int(np.floor(y - ry * 0.35))
        if 0 <= hx < g and 0 <= hy < g:
            hl = np.zeros((g, g), np.float32)
            hl[hy, hx] = 1.0
            self._over(np.broadcast_to(np.array((255, 255, 255), np.float32), (g, g, 3)), hl)

    def shadow(self, cx, width, opacity: float = 0.28, y: float = GROUND):
        """Dithered oval shadow on the ground."""
        g = self.grid
        dx = (self._gx + 0.5 - cx * g) / max(1.0, width * g)
        dy = (self._gy + 0.5 - y * g) / max(1.0, width * g * 0.16)
        d = dx ** 2 + dy ** 2
        m = (d <= 1).astype(np.float32) * np.where(d < 0.45, 1.0, (self._bayer < 0.5).astype(np.float32))
        self._over(np.broadcast_to(np.array((40, 30, 56), np.float32), (g, g, 3)), m * min(0.75, opacity * 1.6))

    def glow(self, mask: Image.Image, color, radius: float, opacity: float = 0.6):
        """Stepped halo of light around a mask."""
        g = self.grid
        cov = self.coverage(mask)
        spread = blur((cov >= 0.5).astype(np.float32), max(1.0, radius * g))
        halo = np.where(spread > 0.25, 0.5, np.where(spread > 0.06, 0.25, 0.0)) * opacity
        halo = np.where((halo > 0) & (halo < 0.3) & (self._bayer > 0.5), 0.0, halo)
        self._over(np.broadcast_to(np.array(lighten(color, 0.2), np.float32), (g, g, 3)), halo)

    def finish(self) -> Image.Image:
        """The pixel canvas with a coloured outline around the whole sprite."""
        solid = self.alpha >= 0.5
        edge = solid & ~(np.roll(solid, 1, 0) & np.roll(solid, -1, 0) & np.roll(solid, 1, 1) & np.roll(solid, -1, 1))
        dark = self.rgb * 0.45 + np.array((30, 18, 40), np.float32) * 0.55 * 0.45
        out = np.where(edge[..., None], dark, self.rgb)
        alpha = np.where(self.alpha >= 0.94, 1.0, np.round(self.alpha * 4) / 4)
        img = np.dstack([np.clip(out, 0, 255), alpha * 255]).astype(np.uint8)
        return Image.fromarray(img, 'RGBA')


# Species

SPECIES: Dict[str, Callable] = {}


def species(name: str):
    def register(fn):
        SPECIES[name] = fn
        return fn
    return register


# Natural colourings for real animals, chosen by the pet's palette:
# (coat, belly, markings or None, eye)
NATURAL_COATS = {
    'cat': [((214, 140, 72), (243, 222, 190), (160, 90, 42), (126, 170, 64)),      # orange tabby
            ((128, 128, 132), (205, 205, 208), (78, 78, 84), (210, 170, 60)),      # grey tabby
            ((44, 40, 44), (70, 64, 66), None, (226, 170, 40)),                    # black
            ((236, 220, 192), (250, 244, 232), (210, 180, 140), (90, 150, 205)),   # cream
            ((140, 100, 66), (210, 180, 140), (80, 55, 35), (150, 175, 60)),       # brown tabby
            ((238, 236, 232), (250, 250, 248), (150, 150, 155), (110, 160, 210))], # white
    'dog': [((212, 160, 84), (240, 214, 160), None, (95, 60, 30)),                 # golden
            ((40, 34, 32), (176, 112, 60), (176, 112, 60), (80, 50, 25)),          # black and tan
            ((132, 82, 48), (190, 140, 96), None, (90, 55, 25)),                   # chocolate
            ((240, 236, 228), (250, 248, 244), (150, 110, 80), (70, 45, 25)),      # white with patches
            ((188, 96, 48), (232, 190, 150), None, (95, 60, 30)),                  # red
            ((150, 150, 156), (220, 220, 222), (90, 90, 96), (60, 110, 160))],     # grey
    'bunny': [((150, 128, 104), (226, 214, 196), None, (60, 40, 30)),             # agouti
              ((246, 244, 240), (252, 250, 248), None, (190, 60, 80)),             # white
              ((52, 48, 50), (90, 84, 86), None, (60, 40, 30)),                    # black
              ((226, 196, 150), (248, 236, 214), None, (70, 45, 30)),              # cream
              ((112, 76, 56), (180, 150, 126), None, (60, 40, 30)),                # chocolate
              ((150, 152, 160), (222, 222, 226), None, (60, 40, 30))],             # blue-grey
    'fox': [((206, 104, 40), (246, 240, 230), (40, 30, 28), (200, 140, 40)),       # red
            ((236, 238, 240), (250, 250, 252), (180, 182, 188), (120, 150, 170)),  # arctic
            ((70, 66, 70), (210, 210, 214), (30, 28, 30), (200, 150, 50)),         # silver
            ((176, 110, 60), (236, 226, 210), (56, 40, 34), (190, 140, 50)),       # cross
            ((226, 190, 136), (248, 240, 224), (150, 110, 70), (120, 80, 40)),     # fennec
            ((150, 140, 132), (230, 226, 220), (60, 52, 50), (190, 150, 60))],     # grey
    'hamster': [((214, 150, 80), (248, 238, 222), None, (20, 15, 15)),
                ((236, 222, 196), (252, 248, 240), None, (150, 40, 50)),
                ((140, 136, 134), (232, 230, 228), None, (20, 15, 15)),
                ((60, 56, 56), (240, 238, 236), None, (20, 15, 15)),
                ((196, 128, 82), (242, 226, 206), None, (120, 40, 50)),
                ((110, 84, 66), (210, 190, 170), None, (20, 15, 15))],
    'bird': [((122, 92, 66), (226, 104, 52), (70, 54, 42), (25, 20, 20)),         # robin
             ((70, 120, 200), (226, 150, 100), (40, 70, 140), (25, 20, 20)),      # bluebird
             ((238, 200, 40), (246, 222, 90), (40, 36, 34), (25, 20, 20)),        # goldfinch
             ((200, 40, 40), (210, 60, 56), (60, 20, 22), (25, 20, 20)),          # cardinal
             ((110, 140, 90), (220, 214, 170), (60, 80, 50), (25, 20, 20)),       # warbler
             ((128, 120, 116), (230, 226, 220), (40, 38, 40), (25, 20, 20))],     # chickadee
    'owl': [((136, 98, 66), (222, 196, 160), (80, 56, 38), (240, 160, 40)),       # tawny
            ((244, 244, 246), (250, 250, 252), (90, 90, 96), (240, 200, 40)),     # snowy
            ((214, 170, 110), (248, 240, 228), (150, 120, 90), (30, 24, 24)),     # barn
            ((140, 138, 136), (214, 210, 204), (70, 68, 66), (240, 190, 40)),     # grey
            ((150, 104, 64), (204, 160, 110), (70, 50, 34), (250, 130, 30)),      # eagle owl
            ((96, 76, 62), (190, 170, 146), (50, 40, 34), (240, 180, 50))],       # dark
    'penguin': [((32, 34, 42), (248, 248, 246), (250, 190, 60), (60, 40, 40)),    # emperor
                ((40, 42, 48), (246, 246, 244), (240, 220, 80), (190, 40, 40)),   # rockhopper
                ((30, 32, 40), (250, 250, 248), (240, 120, 60), (60, 40, 40)),
                ((44, 46, 54), (244, 244, 242), (250, 210, 90), (60, 40, 40)),
                ((36, 38, 46), (248, 248, 246), (230, 160, 60), (60, 40, 40)),
                ((60, 64, 76), (240, 240, 238), (250, 200, 80), (60, 40, 40))],
    'turtle': [((86, 110, 60), (190, 176, 120), (60, 72, 40), (40, 30, 20)),
               ((120, 96, 60), (200, 180, 130), (80, 60, 36), (40, 30, 20)),
               ((70, 100, 90), (180, 190, 150), (44, 66, 60), (40, 30, 20)),
               ((140, 120, 70), (210, 196, 140), (96, 80, 46), (40, 30, 20)),
               ((96, 84, 70), (190, 176, 150), (60, 52, 44), (40, 30, 20)),
               ((90, 120, 70), (200, 190, 130), (120, 90, 40), (40, 30, 20))],
}


def palette_for(name: str, palette: Sequence, index: Optional[int] = None) -> Dict:
    """
    Colours for one creature.

    Real animals take a natural colouring chosen by the palette; the palette's
    colours tint details. Fantasy creatures use the palette directly, slightly
    muted so they do not look like flat cartoon colours.
    """
    cols = [rgb(c) for c in palette] + [rgb(palette[0])] * 3
    if index is None:
        index = sum(sum(c) for c in cols[:3]) % 6
    out = {
        'primary': desaturate(cols[0], 0.18),
        'secondary': desaturate(cols[1], 0.18),
        'accent': desaturate(cols[2], 0.12),
    }
    if name in NATURAL_COATS:
        coat, belly, markings, eye = NATURAL_COATS[name][index % 6]
        out.update(coat=coat, belly=belly, markings=markings, eye=eye)
    else:
        out.update(coat=out['primary'], belly=lighten(out['secondary'], 0.2), markings=darken(out['primary'], 0.3),
                   eye=out['accent'])
    return out


# Shared body parts

def leg(p: Painter, top: Point, knee: Point, foot: Point, w_top: float, w_foot: float, color, **kw):
    p.part(p.limb_mask([top, knee, foot], [w_top, (w_top + w_foot) / 2, w_foot]), color, **kw)


def paw(p: Painter, x, y, w, color):
    p.part(p.ellipse_mask(x, y - w * 0.35, w, w * 0.5), color, gloss=0.08, texture='fur')


def hoof(p: Painter, x, y, w, color):
    p.part(p.poly_mask([(x - w, y), (x - w * 0.8, y - w * 1.1), (x + w * 0.8, y - w * 1.1), (x + w, y)]),
           color, gloss=0.5, roundness=0.6)


def whiskers(p: Painter, x, y, length=0.08, color=(245, 240, 235)):
    for dy in (-0.012, 0.0, 0.012):
        p.stroke([(x, y + dy * 0.4), (x + length * 0.6, y + dy), (x + length, y + dy * 1.6 + 0.004)], 0.0022,
                 color, opacity=0.8)


def membrane_wing(p: Painter, root: Point, joints: Sequence[Point], color, bone, opacity=0.92):
    """Bat-like wing: an arm to the first joint, fingers to the other points, skin between."""
    elbow = joints[0]
    tips = joints[1:]
    skin = [root, elbow] + list(tips) + [(root[0] - 0.04, root[1] + 0.05)]
    m = p.poly_mask(skin)
    # Scalloped trailing edge
    for a, b in zip(tips, tips[1:] + [(root[0] - 0.04, root[1] + 0.05)]):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        out_x, out_y = mx - root[0], my - root[1]
        norm = math.hypot(out_x, out_y) or 1.0
        cut = p.ellipse_mask(mx + out_x / norm * math.dist(a, b) * 0.08, my + out_y / norm * math.dist(a, b) * 0.08,
                             math.dist(a, b) * 0.45, math.dist(a, b) * 0.14,
                             math.atan2(b[1] - a[1], b[0] - a[0]))
        m = p.subtract(m, cut)
    p.part(m, color, roundness=0.35, gloss=0.15, opacity=opacity, outline=0.2, texture='skin')
    p.part(p.limb_mask([root, elbow], [0.016, 0.011]), bone, roundness=0.8)
    for t in tips:
        p.stroke([elbow, t], 0.006, bone)
    p.part(p.ellipse_mask(elbow[0], elbow[1], 0.012, 0.012), bone)


def feather_wing(p: Painter, root: Point, tip: Point, width: float, color, tip_color=None, rows=3, raised=True):
    """Raised bird wing: a solid wing with a row of long flight feathers along the trailing edge."""
    tip_color = tip_color or darken(color, 0.25)
    ang = math.atan2(tip[1] - root[1], tip[0] - root[0])
    # Trailing edge lies on the side away from the body (below-left of the leading edge)
    nx, ny = math.sin(ang), -math.cos(ang)
    if ny < 0:
        nx, ny = -nx, -ny
    # Flight feathers: long, overlapping, fanning from the trailing edge
    count = 9
    for k in range(count):
        t = (k + 0.5) / count
        bx, by = root[0] + (tip[0] - root[0]) * (0.25 + 0.75 * t), root[1] + (tip[1] - root[1]) * (0.25 + 0.75 * t)
        flen = width * (1.3 + 0.9 * t)
        fang = math.atan2(ny, nx) - 0.9 * t * (1 if nx >= 0 else -1) - 0.3
        fx, fy = bx + math.cos(fang) * flen * 0.5, by + math.sin(fang) * flen * 0.5
        p.part(p.ellipse_mask(fx, fy, flen * 0.55, width * 0.3, fang), mix(color, tip_color, 0.5 + 0.5 * t),
               roundness=0.45, gloss=0.15, outline=0.55, texture='skin')
        p.stroke([(bx, by), (bx + math.cos(fang) * flen * 0.95, by + math.sin(fang) * flen * 0.95)], 0.0025,
                 lighten(tip_color, 0.25), opacity=0.5)
    # Coverts over the bases of the feathers
    covert = p.blob_mask([root, (root[0] + (tip[0] - root[0]) * 0.5 - nx * width * 0.15,
                                 root[1] + (tip[1] - root[1]) * 0.5 - ny * width * 0.15), tip,
                          (tip[0] + nx * width * 0.5, tip[1] + ny * width * 0.5),
                          (root[0] + (tip[0] - root[0]) * 0.5 + nx * width * 0.9,
                           root[1] + (tip[1] - root[1]) * 0.5 + ny * width * 0.9),
                          (root[0] + nx * width * 0.7, root[1] + ny * width * 0.7)])
    p.part(covert, color, color2=mix(color, tip_color, 0.4), gradient=0.5, texture='feathers', texture_scale=0.6,
           texture_angle=ang)


def folded_wing(p: Painter, shoulder: Point, tip: Point, depth: float, color, tip_color):
    """Bird wing folded against the body: a covert shape with long primaries at the tip."""
    sx, sy = shoulder
    tx, ty = tip
    mx, my = (sx + tx) / 2, (sy + ty) / 2
    for k in range(4):
        off = 0.012 * k
        p.part(p.ellipse_mask(tx + (mx - tx) * 0.35 + off, ty + (my - ty) * 0.35 - off * 0.6,
                              math.dist(shoulder, tip) * 0.32, depth * 0.17,
                              math.atan2(ty - sy, tx - sx)), darken(tip_color, 0.08 * k), roundness=0.5,
               gloss=0.15, outline=0.45)
    covert = p.blob_mask([(sx + 0.02, sy - 0.01), (mx, my - depth * 0.45), (tx + (mx - tx) * 0.3, ty - depth * 0.1),
                          (mx - 0.02, my + depth * 0.45), (sx, sy + depth * 0.5)])
    p.part(covert, color, color2=tip_color, gradient=0.6, texture='feathers', texture_scale=0.7,
           texture_angle=math.atan2(ty - sy, tx - sx))
    for k in range(3):
        t = 0.35 + 0.18 * k
        x, y = sx + (tx - sx) * t, sy + (ty - sy) * t
        p.stroke([(x, y - depth * 0.3), (x - 0.015, y), (x - 0.01, y + depth * 0.3)], 0.003, darken(color, 0.35),
                 opacity=0.5)


def horn(p: Painter, base: Point, mid: Point, tip: Point, width: float, color, ridged=True):
    p.part(p.limb_mask([base, mid, tip], [width, width * 0.6, width * 0.12]), color, gloss=0.35, roundness=0.8)
    if ridged:
        for t in (0.25, 0.45, 0.65):
            pt = catmull_rom([base, mid, tip], closed=False)[int(t * 24)]
            p.dot(pt[0], pt[1], width * (1 - t) * 0.5, darken(color, 0.3), opacity=0.35)


def flowing_hair(p: Painter, roots: Sequence[Point], drift: Point, length: float, color, width=0.02, waves=1.0,
                 opacity=1.0, glow=0.0):
    """Locks of mane or hair streaming in the drift direction."""
    for i, (x, y) in enumerate(roots):
        w = 0.6 + 0.4 * math.sin(i * 1.7)
        pts = [(x, y)]
        for s in range(1, 4):
            t = s / 3
            pts.append((x + drift[0] * length * t + math.sin(i + t * 3 * waves) * 0.02,
                        y + drift[1] * length * t + math.cos(i * 1.3 + t * 2) * 0.015))
        c = mix(color, darken(color, 0.3), (i % 3) / 3)
        p.part(p.limb_mask(pts, [width * w, width * w * 0.8, width * 0.5 * w, width * 0.12]), c,
               gloss=0.35, roundness=0.7, opacity=opacity, glow=glow, texture='fur', texture_angle=math.atan2(drift[1], drift[0]))


def humanoid_head(p: Painter, cx, cy, r, skin, eye_c, hair=None):
    p.part(p.ellipse_mask(cx, cy, r * 0.92, r), skin, gloss=0.15, texture='skin')
    p.eye(cx + r * 0.38, cy - r * 0.05, r * 0.2, eye_c, look=(0.4, 0.0), squash=1.15)
    p.eye(cx - r * 0.1, cy - r * 0.05, r * 0.18, eye_c, look=(0.4, 0.0), squash=1.15)
    p.stroke([(cx + r * 0.15, cy + r * 0.45), (cx + r * 0.3, cy + r * 0.5)], r * 0.06, darken(skin, 0.45))


# Real animals

@species('cat')
def draw_cat(p: Painter, pal):
    coat, belly, eye_c, markings = pal['coat'], pal['belly'], pal['eye'], pal['markings']
    far = darken(coat, 0.22)
    p.shadow(0.5, 0.33)
    p.part(p.limb_mask([(0.24, 0.66), (0.13, 0.6), (0.1, 0.44), (0.15, 0.31)], [0.034, 0.031, 0.028, 0.022]),
           coat, texture='fur', texture_angle=-1.4)
    leg(p, (0.33, 0.66), (0.36, 0.8), (0.35, 0.905), 0.04, 0.022, far, texture='fur')
    leg(p, (0.62, 0.64), (0.6, 0.79), (0.61, 0.905), 0.034, 0.021, far, texture='fur')
    paw(p, 0.36, 0.915, 0.026, far)
    paw(p, 0.62, 0.915, 0.024, far)
    body = p.blob_mask([(0.22, 0.6), (0.34, 0.5), (0.55, 0.5), (0.7, 0.52), (0.73, 0.66),
                        (0.6, 0.75), (0.4, 0.76), (0.25, 0.71)])
    p.part(body, coat, color2=belly, gradient=0.6, texture='fur')
    if markings:
        for x in (0.34, 0.42, 0.5, 0.58):
            p.part(p.intersect(p.limb_mask([(x, 0.5), (x - 0.012, 0.58), (x + 0.004, 0.66)],
                                           [0.013, 0.01, 0.003]), body), markings, flat=True, opacity=0.5)
    # Haunch and near legs
    p.part(p.ellipse_mask(0.31, 0.64, 0.09, 0.11, -0.3), coat, texture='fur', outline=0.25)
    leg(p, (0.29, 0.7), (0.26, 0.82), (0.29, 0.905), 0.04, 0.024, coat, texture='fur')
    paw(p, 0.305, 0.915, 0.03, coat)
    p.part(p.ellipse_mask(0.66, 0.62, 0.06, 0.08, 0.2), coat, texture='fur', outline=0.25)
    leg(p, (0.67, 0.66), (0.68, 0.8), (0.68, 0.905), 0.036, 0.022, coat, texture='fur')
    paw(p, 0.695, 0.915, 0.028, coat)
    # Neck and head
    p.part(p.limb_mask([(0.66, 0.6), (0.73, 0.52), (0.77, 0.47)], [0.07, 0.065, 0.06]), coat, texture='fur')
    for x0, y0, x1, y1, x2, y2 in ((0.7, 0.42, 0.72, 0.27, 0.78, 0.38), (0.81, 0.37, 0.85, 0.24, 0.885, 0.39)):
        p.part(p.blob_mask([(x0, y0), (x1, y1), (x2, y2)]), coat, texture='fur', roundness=0.6)
        p.part(p.blob_mask([(x0 + 0.017, y0 - 0.006), (x1 + 0.005, y1 + 0.035), (x2 - 0.014, y2 - 0.008)]),
               (222, 158, 158), roundness=0.4, gloss=0.05)
    head = p.blob_mask([(0.68, 0.47), (0.72, 0.38), (0.82, 0.35), (0.91, 0.4), (0.94, 0.49),
                        (0.88, 0.56), (0.76, 0.58), (0.69, 0.54)])
    p.part(head, coat, texture='fur', texture_angle=0.3)
    if markings:
        for dx in (0.0, 0.025):
            p.stroke([(0.8 + dx, 0.36), (0.79 + dx, 0.4)], 0.008, markings, opacity=0.5)
    p.part(p.ellipse_mask(0.895, 0.51, 0.05, 0.038), lighten(belly, 0.25), texture='fur', roundness=0.7)
    p.part(p.blob_mask([(0.915, 0.475), (0.94, 0.478), (0.928, 0.495)]), (196, 112, 120), gloss=0.5)
    p.stroke([(0.927, 0.495), (0.924, 0.515), (0.91, 0.522)], 0.004, (70, 45, 45))
    p.stroke([(0.924, 0.515), (0.936, 0.522)], 0.004, (70, 45, 45))
    p.eye(0.84, 0.445, 0.03, eye_c, pupil='slit', look=(0.4, 0.0), squash=0.85)
    whiskers(p, 0.9, 0.51, 0.09)


@species('dog')
def draw_dog(p: Painter, pal):
    coat, belly, eye_c, patch = pal['coat'], pal['belly'], pal['eye'], pal['markings']
    far = darken(coat, 0.22)
    p.shadow(0.5, 0.36)
    p.part(p.limb_mask([(0.2, 0.52), (0.12, 0.42), (0.14, 0.3)], [0.03, 0.025, 0.016]), coat, texture='fur',
           texture_angle=-1.2)
    leg(p, (0.27, 0.62), (0.3, 0.77), (0.29, 0.9), 0.045, 0.026, far, texture='fur')
    leg(p, (0.62, 0.62), (0.6, 0.77), (0.61, 0.9), 0.04, 0.025, far, texture='fur')
    paw(p, 0.3, 0.912, 0.03, far)
    paw(p, 0.62, 0.912, 0.029, far)
    body = p.blob_mask([(0.18, 0.52), (0.3, 0.44), (0.55, 0.44), (0.7, 0.46), (0.74, 0.6),
                        (0.6, 0.68), (0.42, 0.66), (0.24, 0.66)])
    p.part(body, coat, color2=belly, gradient=0.55, texture='fur')
    if patch and pal['coat'][0] > 200:
        p.part(p.intersect(p.ellipse_mask(0.38, 0.5, 0.09, 0.06, 0.2), body), patch, flat=True, opacity=0.8)
    p.part(p.ellipse_mask(0.25, 0.57, 0.1, 0.11, -0.2), coat, texture='fur', outline=0.25)
    leg(p, (0.24, 0.62), (0.21, 0.77), (0.25, 0.9), 0.05, 0.027, coat, texture='fur')
    paw(p, 0.265, 0.912, 0.033, coat)
    p.part(p.ellipse_mask(0.66, 0.56, 0.07, 0.09, 0.2), coat, texture='fur', outline=0.25)
    leg(p, (0.67, 0.6), (0.69, 0.76), (0.68, 0.9), 0.042, 0.026, coat, texture='fur')
    paw(p, 0.7, 0.912, 0.032, coat)
    if pal['markings'] and pal['coat'][0] < 60:  # tan points
        p.part(p.ellipse_mask(0.69, 0.86, 0.03, 0.045), belly, flat=True, opacity=0.9)
    # Neck, collar, head
    p.part(p.limb_mask([(0.64, 0.54), (0.72, 0.44), (0.76, 0.36)], [0.085, 0.075, 0.07]), coat, texture='fur')
    neck = p.limb_mask([(0.64, 0.54), (0.72, 0.44), (0.76, 0.36)], [0.085, 0.075, 0.07])
    p.part(p.intersect(p.limb_mask([(0.63, 0.41), (0.7, 0.455), (0.77, 0.5)], [0.016, 0.016, 0.016]), neck),
           pal['primary'], gloss=0.5, roundness=0.6)
    p.part(p.ellipse_mask(0.745, 0.51, 0.013, 0.016), (230, 196, 70), gloss=0.9)
    head = p.blob_mask([(0.7, 0.33), (0.78, 0.24), (0.87, 0.26), (0.91, 0.33), (0.97, 0.37),
                        (0.97, 0.42), (0.9, 0.45), (0.78, 0.44), (0.71, 0.4)])
    p.part(head, coat, texture='fur')
    p.part(p.ellipse_mask(0.92, 0.405, 0.05, 0.035), belly, texture='fur', roundness=0.7, opacity=0.9)
    p.part(p.ellipse_mask(0.965, 0.368, 0.02, 0.016), (30, 26, 28), gloss=0.8)
    p.stroke([(0.965, 0.385), (0.95, 0.42), (0.92, 0.428)], 0.004, (60, 40, 36))
    p.part(p.blob_mask([(0.925, 0.425), (0.945, 0.43), (0.94, 0.465), (0.925, 0.46)]), (214, 100, 110), gloss=0.4)
    p.eye(0.855, 0.32, 0.024, eye_c, look=(0.5, 0.0))
    # Floppy ear
    ear = p.blob_mask([(0.76, 0.27), (0.8, 0.26), (0.81, 0.33), (0.79, 0.42), (0.75, 0.4), (0.74, 0.32)])
    p.part(ear, darken(coat, 0.18) if not patch else patch, texture='fur', texture_angle=1.4)


@species('bunny')
def draw_bunny(p: Painter, pal):
    coat, belly, eye_c = pal['coat'], pal['belly'], pal['eye']
    p.shadow(0.48, 0.3)
    # Far ear
    p.part(p.limb_mask([(0.66, 0.38), (0.62, 0.22), (0.6, 0.08)], [0.035, 0.04, 0.02]), darken(coat, 0.2),
           texture='fur', texture_angle=-1.5)
    body = p.blob_mask([(0.22, 0.75), (0.25, 0.58), (0.38, 0.47), (0.55, 0.48), (0.66, 0.58),
                        (0.66, 0.78), (0.55, 0.9), (0.3, 0.9)])
    p.part(body, coat, color2=belly, gradient=0.4, texture='fur', texture_angle=-0.4)
    p.part(p.ellipse_mask(0.2, 0.68, 0.045, 0.045), (250, 250, 248), texture='fur')
    # Big hind leg and long foot
    p.part(p.ellipse_mask(0.36, 0.73, 0.13, 0.14, -0.4), coat, texture='fur', outline=0.25)
    p.part(p.blob_mask([(0.3, 0.86), (0.48, 0.865), (0.53, 0.89), (0.5, 0.915), (0.3, 0.915)]),
           lighten(coat, 0.1), texture='fur')
    # Front legs
    leg(p, (0.6, 0.72), (0.62, 0.83), (0.62, 0.9), 0.03, 0.02, coat, texture='fur')
    paw(p, 0.635, 0.912, 0.025, belly)
    # Head and near ear
    head = p.blob_mask([(0.58, 0.43), (0.64, 0.35), (0.74, 0.33), (0.82, 0.38), (0.84, 0.47),
                        (0.78, 0.53), (0.66, 0.54), (0.59, 0.5)])
    p.part(head, coat, texture='fur')
    p.part(p.ellipse_mask(0.79, 0.48, 0.045, 0.04), belly, texture='fur', roundness=0.6)
    ear = p.limb_mask([(0.7, 0.36), (0.68, 0.2), (0.7, 0.05)], [0.038, 0.045, 0.022])
    p.part(ear, coat, texture='fur', texture_angle=-1.5)
    p.part(p.limb_mask([(0.7, 0.33), (0.687, 0.2), (0.698, 0.08)], [0.018, 0.026, 0.01]), (226, 170, 170),
           roundness=0.5, gloss=0.05)
    p.part(p.blob_mask([(0.83, 0.455), (0.845, 0.46), (0.838, 0.472)]), (210, 140, 150), gloss=0.4)
    p.stroke([(0.838, 0.472), (0.832, 0.49), (0.82, 0.495)], 0.003, (90, 60, 60))
    p.eye(0.75, 0.41, 0.03, eye_c, look=(0.3, 0.0), squash=1.05)
    whiskers(p, 0.82, 0.48, 0.08, (230, 230, 230))


@species('fox')
def draw_fox(p: Painter, pal):
    coat, belly, socks, eye_c = pal['coat'], pal['belly'], pal['markings'], pal['eye']
    p.shadow(0.5, 0.38)
    # Bushy tail with white tip
    tail = p.blob_mask([(0.24, 0.55), (0.14, 0.6), (0.05, 0.7), (0.04, 0.8), (0.1, 0.82), (0.2, 0.74), (0.28, 0.62)])
    p.part(tail, coat, texture='fur', texture_angle=2.2, texture_scale=1.4)
    p.part(p.intersect(p.ellipse_mask(0.06, 0.78, 0.06, 0.06), tail), (248, 246, 242), texture='fur')
    leg(p, (0.3, 0.6), (0.33, 0.76), (0.32, 0.9), 0.034, 0.018, socks, texture='fur')
    leg(p, (0.62, 0.6), (0.6, 0.76), (0.61, 0.9), 0.03, 0.018, socks, texture='fur')
    paw(p, 0.33, 0.912, 0.024, socks)
    paw(p, 0.62, 0.912, 0.023, socks)
    body = p.blob_mask([(0.24, 0.55), (0.34, 0.47), (0.55, 0.47), (0.69, 0.49), (0.71, 0.6),
                        (0.6, 0.66), (0.4, 0.66), (0.26, 0.62)])
    p.part(body, coat, color2=belly, gradient=0.5, texture='fur')
    p.part(p.ellipse_mask(0.31, 0.58, 0.075, 0.09, -0.3), coat, texture='fur', outline=0.25)
    leg(p, (0.28, 0.63), (0.25, 0.77), (0.28, 0.9), 0.04, 0.019, coat, texture='fur')
    p.part(p.limb_mask([(0.262, 0.8), (0.28, 0.9)], [0.02, 0.019]), socks, texture='fur')
    paw(p, 0.29, 0.912, 0.026, socks)
    leg(p, (0.66, 0.6), (0.67, 0.76), (0.67, 0.9), 0.032, 0.018, coat, texture='fur')
    p.part(p.limb_mask([(0.67, 0.76), (0.67, 0.9)], [0.019, 0.018]), socks, texture='fur')
    paw(p, 0.68, 0.912, 0.025, socks)
    # Neck with white chest
    p.part(p.limb_mask([(0.64, 0.55), (0.71, 0.46), (0.74, 0.4)], [0.07, 0.06, 0.055]), coat, texture='fur')
    p.part(p.blob_mask([(0.68, 0.46), (0.75, 0.44), (0.74, 0.56), (0.68, 0.6)]), belly, texture='fur', roundness=0.6)
    # Head: ears with dark backs, long muzzle
    for base in ((0.72, 0.35), (0.79, 0.33)):
        bx, by = base
        p.part(p.blob_mask([(bx - 0.02, by + 0.02), (bx + 0.005, by - 0.13), (bx + 0.035, by + 0.01)]),
               socks, texture='fur', roundness=0.6)
        p.part(p.blob_mask([(bx - 0.008, by + 0.01), (bx + 0.006, by - 0.09), (bx + 0.022, by + 0.005)]),
               coat, roundness=0.4)
    head = p.blob_mask([(0.69, 0.38), (0.75, 0.31), (0.84, 0.32), (0.9, 0.37), (0.98, 0.41),
                        (0.97, 0.44), (0.88, 0.47), (0.76, 0.47)])
    p.part(head, coat, texture='fur', texture_angle=0.2)
    p.part(p.intersect(p.blob_mask([(0.8, 0.44), (0.9, 0.42), (0.98, 0.43), (0.9, 0.48), (0.78, 0.5)]), head),
           belly, texture='fur')
    p.part(p.ellipse_mask(0.973, 0.41, 0.014, 0.012), (24, 20, 22), gloss=0.8)
    p.eye(0.84, 0.37, 0.019, eye_c, pupil='slit', look=(0.5, 0.0), squash=0.8)


@species('hamster')
def draw_hamster(p: Painter, pal):
    coat, belly, eye_c = pal['coat'], pal['belly'], pal['eye']
    p.shadow(0.5, 0.3)
    body = p.blob_mask([(0.22, 0.78), (0.24, 0.62), (0.36, 0.5), (0.55, 0.47), (0.72, 0.52),
                        (0.8, 0.64), (0.78, 0.82), (0.62, 0.91), (0.34, 0.91)])
    p.part(body, coat, texture='fur', texture_angle=-0.3, texture_scale=1.2)
    p.part(p.intersect(p.blob_mask([(0.5, 0.92), (0.58, 0.7), (0.72, 0.62), (0.86, 0.68), (0.82, 0.92)]), body),
           belly, texture='fur')
    # Ears
    for ex, ey in ((0.6, 0.48), (0.69, 0.47)):
        p.part(p.ellipse_mask(ex, ey, 0.032, 0.035), darken(coat, 0.1), texture='fur')
        p.part(p.ellipse_mask(ex + 0.004, ey + 0.004, 0.018, 0.022), (226, 160, 160), roundness=0.4)
    # Cheek pouch and face
    p.part(p.ellipse_mask(0.73, 0.64, 0.085, 0.075), lighten(coat, 0.15), texture='fur', outline=0.2)
    p.part(p.ellipse_mask(0.78, 0.6, 0.06, 0.05), lighten(belly, 0.1), texture='fur', roundness=0.6)
    p.part(p.ellipse_mask(0.835, 0.585, 0.014, 0.011), (214, 140, 150), gloss=0.5)
    p.stroke([(0.833, 0.598), (0.83, 0.612), (0.82, 0.616)], 0.003, (100, 60, 60))
    p.eye(0.715, 0.555, 0.022, eye_c, sclera=eye_c, look=(0.0, 0.0))
    whiskers(p, 0.82, 0.6, 0.07, (240, 236, 230))
    # Paws
    for x in (0.66, 0.72):
        p.part(p.ellipse_mask(x, 0.78, 0.022, 0.018), (232, 172, 170), gloss=0.2)
    p.part(p.ellipse_mask(0.36, 0.9, 0.05, 0.02), (232, 172, 170), gloss=0.2)


@species('bird')
def draw_bird(p: Painter, pal):
    back, breast, dark, eye_c = pal['coat'], pal['belly'], pal['markings'], pal['eye']
    p.shadow(0.48, 0.2)
    for x in (0.44, 0.52):
        p.stroke([(x, 0.72), (x - 0.01, 0.82), (x, 0.91)], 0.009, (150, 110, 80))
        p.stroke([(x - 0.03, 0.915), (x + 0.03, 0.915)], 0.007, (150, 110, 80))
    # Tail feathers
    for k, a in enumerate((-0.2, -0.05, 0.1)):
        p.part(p.ellipse_mask(0.2 + k * 0.01, 0.6 + a * 0.2, 0.13, 0.03, 0.55 + a), darken(back, 0.15 + k * 0.05),
               texture='feathers', texture_angle=0.5, roundness=0.6)
    body = p.blob_mask([(0.26, 0.58), (0.36, 0.46), (0.52, 0.42), (0.66, 0.45), (0.7, 0.58),
                        (0.62, 0.72), (0.45, 0.76), (0.32, 0.7)])
    p.part(body, back, color2=breast, gradient=0.9, texture='feathers', texture_angle=0.2, texture_scale=0.8)
    p.part(p.intersect(p.ellipse_mask(0.6, 0.62, 0.12, 0.13), body), breast, texture='feathers', texture_scale=0.6)
    folded_wing(p, (0.58, 0.5), (0.24, 0.62), 0.16, back, dark)
    head = p.ellipse_mask(0.68, 0.39, 0.085, 0.08)
    p.part(head, back, texture='feathers', texture_scale=0.5)
    if pal['coat'] == (128, 120, 116):  # chickadee cap and bib
        p.part(p.intersect(p.ellipse_mask(0.68, 0.33, 0.1, 0.05), head), dark, flat=True)
    p.part(p.intersect(p.ellipse_mask(0.72, 0.45, 0.06, 0.05), head), breast, texture='feathers', texture_scale=0.5)
    p.part(p.poly_mask([(0.745, 0.37), (0.84, 0.395), (0.745, 0.415)]), (60, 52, 46), gloss=0.6, roundness=0.6)
    p.stroke([(0.75, 0.393), (0.83, 0.395)], 0.002, (20, 18, 16))
    p.eye(0.705, 0.37, 0.018, eye_c, sclera=eye_c, look=(0.3, 0.0))


@species('owl')
def draw_owl(p: Painter, pal):
    plum, face, bars, eye_c = pal['coat'], pal['belly'], pal['markings'], pal['eye']
    p.shadow(0.5, 0.24)
    body = p.blob_mask([(0.32, 0.6), (0.34, 0.4), (0.42, 0.3), (0.58, 0.3), (0.66, 0.4),
                        (0.68, 0.62), (0.62, 0.84), (0.5, 0.89), (0.38, 0.84)])
    p.part(body, plum, color2=face, gradient=0.5, texture='feathers', texture_scale=0.7)
    chest = p.intersect(p.ellipse_mask(0.5, 0.67, 0.13, 0.19), body)
    p.part(chest, face, texture='feathers', texture_scale=0.55)
    for row in range(5):
        for k in range(4):
            x = 0.43 + k * 0.045 + (row % 2) * 0.02
            y = 0.56 + row * 0.055
            p.part(p.intersect(p.ellipse_mask(x, y, 0.013, 0.006), chest), bars, flat=True, opacity=0.55)
    # Folded wings
    for side in (-1, 1):
        x = 0.5 + side * 0.15
        w = p.blob_mask([(x - side * 0.02, 0.42), (x + side * 0.04, 0.5), (x + side * 0.045, 0.7),
                         (x + side * 0.01, 0.84), (x - side * 0.03, 0.7)])
        p.part(w, darken(plum, 0.1), texture='feathers', texture_angle=1.4, texture_scale=0.8)
    # Ear tufts
    for side in (-1, 1):
        p.part(p.blob_mask([(0.5 + side * 0.07, 0.33), (0.5 + side * 0.13, 0.2), (0.5 + side * 0.12, 0.32)]),
               darken(plum, 0.15), texture='feathers')
    # Facial disc
    for side in (-1, 1):
        p.part(p.ellipse_mask(0.5 + side * 0.065, 0.42, 0.075, 0.08), face, roundness=0.6, texture='fur',
               texture_angle=side * 0.8)
        p.eye(0.5 + side * 0.065, 0.42, 0.045, eye_c, sclera=eye_c, look=(0.0, 0.0))
    p.part(p.poly_mask([(0.48, 0.45), (0.52, 0.45), (0.5, 0.51)]), (70, 60, 50), gloss=0.6)
    for x in (0.45, 0.55):
        for dx in (-0.02, 0.0, 0.02):
            p.stroke([(x, 0.875), (x + dx, 0.905), (x + dx * 1.3, 0.915)], 0.006, (60, 50, 44))


@species('penguin')
def draw_penguin(p: Painter, pal):
    black, white, patch, eye_c = pal['coat'], pal['belly'], pal['markings'], pal['eye']
    p.shadow(0.5, 0.22)
    for x in (0.44, 0.56):
        p.part(p.ellipse_mask(x + 0.02, 0.905, 0.05, 0.018), (230, 140, 60), gloss=0.3)
    body = p.blob_mask([(0.34, 0.66), (0.36, 0.42), (0.44, 0.26), (0.56, 0.24), (0.64, 0.36),
                        (0.68, 0.62), (0.62, 0.86), (0.5, 0.9), (0.38, 0.86)])
    p.part(body, black, gloss=0.4, texture='skin')
    belly = p.intersect(p.blob_mask([(0.46, 0.4), (0.58, 0.36), (0.66, 0.5), (0.66, 0.76), (0.56, 0.9), (0.44, 0.86),
                                     (0.42, 0.6)]), body)
    p.part(belly, white, color2=(226, 226, 222), gradient=0.6, gloss=0.2, texture='skin')
    p.part(p.intersect(p.ellipse_mask(0.6, 0.42, 0.07, 0.05), body), patch, roundness=0.5, opacity=0.85)
    p.part(p.limb_mask([(0.4, 0.46), (0.33, 0.6), (0.31, 0.72)], [0.04, 0.035, 0.012]), darken(black, 0.15),
           gloss=0.35)
    p.part(p.blob_mask([(0.6, 0.3), (0.7, 0.315), (0.74, 0.33), (0.68, 0.345), (0.6, 0.34)]), patch, gloss=0.6)
    p.eye(0.57, 0.29, 0.016, eye_c, sclera=eye_c, look=(0.4, 0.0))


@species('turtle')
def draw_turtle(p: Painter, pal):
    shell, skin, rim, eye_c = pal['coat'], pal['belly'], pal['markings'], pal['eye']
    skin_c = mix(skin, (110, 130, 80), 0.5)
    p.shadow(0.5, 0.36)
    leg(p, (0.33, 0.78), (0.31, 0.86), (0.3, 0.905), 0.04, 0.034, darken(skin_c, 0.2), texture='scales', texture_scale=0.5)
    leg(p, (0.64, 0.78), (0.67, 0.86), (0.68, 0.905), 0.04, 0.034, darken(skin_c, 0.2), texture='scales', texture_scale=0.5)
    p.part(p.limb_mask([(0.18, 0.8), (0.12, 0.83)], [0.022, 0.006]), skin_c, texture='scales', texture_scale=0.4)
    p.part(p.limb_mask([(0.68, 0.76), (0.78, 0.7), (0.86, 0.66)], [0.04, 0.036, 0.033]), skin_c,
           texture='scales', texture_scale=0.45)
    p.part(p.ellipse_mask(0.89, 0.64, 0.06, 0.045, -0.15), skin_c, texture='scales', texture_scale=0.35)
    p.stroke([(0.9, 0.665), (0.945, 0.655)], 0.003, (50, 40, 30))
    p.eye(0.9, 0.625, 0.014, eye_c, sclera=eye_c, look=(0.3, 0.0))
    # Shell: dome, rim and plates
    dome = p.blob_mask([(0.18, 0.8), (0.22, 0.62), (0.34, 0.5), (0.5, 0.47), (0.66, 0.51), (0.77, 0.63),
                        (0.8, 0.8), (0.5, 0.83)])
    p.part(dome, shell, gloss=0.45, roundness=1.2)
    plates = [(0.36, 0.58), (0.5, 0.54), (0.64, 0.58), (0.27, 0.72), (0.43, 0.69), (0.57, 0.69), (0.73, 0.72)]
    for x, y in plates:
        hexagon = [(x + 0.072 * math.cos(a), y + 0.062 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]
        p.part(p.intersect(p.poly_mask(hexagon), dome), shell, roundness=0.35, gloss=0.35, outline=0.75,
               texture='stone')
        p.dot(x - 0.01, y - 0.012, 0.022, lighten(shell, 0.35), opacity=0.25, blur=0.01)
    p.part(p.intersect(p.limb_mask([(0.17, 0.79), (0.5, 0.825), (0.81, 0.79)], [0.02, 0.022, 0.02]), dome),
           rim, roundness=0.6)


# Fantasy creatures

def spikes(p: Painter, path: Sequence[Point], size: float, color, count: int = 7, lean: float = -0.4):
    pts = catmull_rom(path, closed=False, steps=12)
    for k in range(count):
        i = int((k + 0.5) / count * (len(pts) - 2))
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        ang = math.atan2(y1 - y0, x1 - x0) - math.pi / 2 + lean
        h = size * (0.6 + 0.4 * math.sin(math.pi * (k + 0.5) / count))
        tip = (x0 + math.cos(ang) * h, y0 + math.sin(ang) * h)
        p.part(p.poly_mask([(x0 - size * 0.25, y0), tip, (x0 + size * 0.35, y0 + size * 0.05)]), color,
               gloss=0.3, roundness=0.6)


def dragon_head(p: Painter, cx, cy, scale, skin, belly, horn_c, eye_c, facing=0.0):
    s = scale
    for k, (hx, hy) in enumerate(((-0.05, -0.12), (-0.08, -0.08))):
        horn(p, (cx - 0.02 * s, cy - 0.03 * s), (cx + hx * s, cy + hy * s * 0.7),
             (cx + (hx - 0.06) * s, cy + (hy - 0.04) * s), 0.022 * s, darken(horn_c, 0.15 * k))
    head = p.blob_mask([(cx - 0.06 * s, cy + 0.02 * s), (cx - 0.04 * s, cy - 0.05 * s), (cx + 0.04 * s, cy - 0.055 * s),
                        (cx + 0.12 * s, cy - 0.02 * s), (cx + 0.16 * s, cy + 0.01 * s), (cx + 0.15 * s, cy + 0.04 * s),
                        (cx + 0.06 * s, cy + 0.06 * s), (cx - 0.03 * s, cy + 0.06 * s)])
    p.part(head, skin, texture='scales', texture_scale=0.6 * s)
    p.part(p.intersect(p.blob_mask([(cx - 0.02 * s, cy + 0.045 * s), (cx + 0.15 * s, cy + 0.03 * s),
                                    (cx + 0.12 * s, cy + 0.065 * s), (cx, cy + 0.07 * s)]), head), belly,
           texture='scales', texture_scale=0.4 * s)
    p.stroke([(cx + 0.02 * s, cy + 0.035 * s), (cx + 0.1 * s, cy + 0.03 * s), (cx + 0.15 * s, cy + 0.025 * s)],
             0.004 * s, darken(skin, 0.5))
    p.dot(cx + 0.14 * s, cy - 0.005 * s, 0.006 * s, darken(skin, 0.6))
    p.part(p.blob_mask([(cx + 0.0 * s, cy - 0.045 * s), (cx + 0.07 * s, cy - 0.05 * s), (cx + 0.06 * s, cy - 0.03 * s)]),
           darken(skin, 0.15), roundness=0.4)
    p.eye(cx + 0.045 * s, cy - 0.02 * s, 0.017 * s, eye_c, pupil='slit', look=(0.4, 0.0), squash=0.75)


@species('dragon')
def draw_dragon(p: Painter, pal):
    skin, belly, wing_c, eye_c = pal['primary'], pal['secondary'], pal['accent'], (250, 200, 40)
    far = darken(skin, 0.25)
    p.shadow(0.48, 0.4)
    membrane_wing(p, (0.46, 0.46), [(0.38, 0.22), (0.12, 0.12), (0.14, 0.3), (0.22, 0.42)], darken(wing_c, 0.25),
                  darken(skin, 0.35), opacity=0.9)
    tail = p.limb_mask([(0.28, 0.66), (0.16, 0.74), (0.09, 0.84), (0.16, 0.9), (0.04, 0.88)],
                       [0.05, 0.04, 0.028, 0.018, 0.008])
    p.part(tail, skin, texture='scales', texture_angle=2.0)
    p.part(p.poly_mask([(0.02, 0.86), (0.07, 0.83), (0.06, 0.9), (0.01, 0.92)]), darken(skin, 0.2), gloss=0.3)
    leg(p, (0.34, 0.68), (0.37, 0.8), (0.35, 0.9), 0.05, 0.025, far, texture='scales')
    leg(p, (0.6, 0.64), (0.58, 0.78), (0.6, 0.9), 0.04, 0.022, far, texture='scales')
    body = p.blob_mask([(0.26, 0.64), (0.34, 0.52), (0.5, 0.48), (0.64, 0.5), (0.7, 0.6),
                        (0.62, 0.73), (0.44, 0.76), (0.3, 0.73)])
    p.part(body, skin, texture='scales', texture_angle=0.1)
    belly_m = p.intersect(p.blob_mask([(0.3, 0.72), (0.5, 0.66), (0.7, 0.62), (0.66, 0.76), (0.4, 0.8)]), body)
    p.part(belly_m, belly, roundness=0.6, gloss=0.2)
    for x in np.linspace(0.36, 0.64, 7):
        p.stroke([(x, 0.69 - (x - 0.36) * 0.2), (x + 0.012, 0.75 - (x - 0.36) * 0.1)], 0.003, darken(belly, 0.3),
                 opacity=0.6)
    spikes(p, [(0.22, 0.68), (0.32, 0.52), (0.5, 0.47), (0.64, 0.48)], 0.045, wing_c, count=6)
    p.part(p.ellipse_mask(0.34, 0.66, 0.09, 0.1, -0.3), skin, texture='scales', outline=0.25)
    leg(p, (0.32, 0.72), (0.28, 0.82), (0.32, 0.9), 0.05, 0.026, skin, texture='scales')
    for dx in (0.0, 0.02, 0.04):
        p.part(p.poly_mask([(0.33 + dx, 0.9), (0.345 + dx, 0.885), (0.355 + dx, 0.915)]), (240, 236, 220), gloss=0.5)
    leg(p, (0.64, 0.62), (0.67, 0.77), (0.66, 0.9), 0.042, 0.024, skin, texture='scales')
    for dx in (0.0, 0.02, 0.04):
        p.part(p.poly_mask([(0.66 + dx, 0.9), (0.675 + dx, 0.885), (0.685 + dx, 0.915)]), (240, 236, 220), gloss=0.5)
    neck = p.limb_mask([(0.62, 0.56), (0.7, 0.46), (0.71, 0.36), (0.75, 0.29)], [0.065, 0.05, 0.042, 0.04])
    p.part(neck, skin, texture='scales', texture_angle=-1.2)
    p.part(p.intersect(p.limb_mask([(0.66, 0.6), (0.74, 0.47), (0.75, 0.37)], [0.035, 0.028, 0.02]), neck), belly,
           roundness=0.5)
    spikes(p, [(0.62, 0.5), (0.66, 0.4), (0.7, 0.3)], 0.035, wing_c, count=4, lean=-0.7)
    membrane_wing(p, (0.54, 0.5), [(0.5, 0.2), (0.28, 0.06), (0.26, 0.24), (0.32, 0.38)], wing_c,
                  darken(skin, 0.2), opacity=0.94)
    dragon_head(p, 0.77, 0.28, 1.0, skin, belly, (236, 226, 200), eye_c)


@species('chimera')
def draw_chimera(p: Painter, pal):
    fur, mane_c, goat_c = pal['primary'], pal['secondary'], pal['accent']
    lion = mix(fur, (200, 150, 80), 0.5)
    mane_col = mix(mane_c, (150, 90, 40), 0.5)
    p.shadow(0.5, 0.4)
    # Serpent tail
    snake = mix(goat_c, (80, 120, 60), 0.5)
    p.part(p.limb_mask([(0.24, 0.6), (0.14, 0.58), (0.08, 0.46), (0.14, 0.34), (0.2, 0.3)],
                       [0.025, 0.024, 0.022, 0.02, 0.018]), snake, texture='scales', texture_angle=-1.4)
    sh = p.blob_mask([(0.17, 0.3), (0.21, 0.26), (0.27, 0.27), (0.29, 0.3), (0.24, 0.33), (0.18, 0.33)])
    p.part(sh, snake, texture='scales', texture_scale=0.5)
    p.eye(0.235, 0.29, 0.008, (240, 200, 40), pupil='slit', sclera=(240, 200, 40))
    p.stroke([(0.29, 0.31), (0.31, 0.32), (0.32, 0.31)], 0.0025, (200, 40, 50))
    far = darken(lion, 0.25)
    leg(p, (0.32, 0.64), (0.35, 0.78), (0.33, 0.9), 0.045, 0.025, far, texture='fur')
    leg(p, (0.62, 0.62), (0.6, 0.77), (0.61, 0.9), 0.045, 0.026, far, texture='fur')
    paw(p, 0.34, 0.912, 0.03, far)
    paw(p, 0.62, 0.912, 0.03, far)
    body = p.blob_mask([(0.24, 0.6), (0.32, 0.5), (0.5, 0.48), (0.66, 0.5), (0.7, 0.62), (0.6, 0.7), (0.4, 0.7), (0.27, 0.68)])
    p.part(body, lion, color2=lighten(lion, 0.25), gradient=0.5, texture='fur')
    p.part(p.ellipse_mask(0.3, 0.62, 0.085, 0.1, -0.3), lion, texture='fur', outline=0.25)
    leg(p, (0.28, 0.68), (0.25, 0.8), (0.28, 0.9), 0.048, 0.027, lion, texture='fur')
    paw(p, 0.29, 0.912, 0.032, lion)
    leg(p, (0.66, 0.62), (0.68, 0.77), (0.67, 0.9), 0.05, 0.028, lion, texture='fur')
    paw(p, 0.685, 0.912, 0.033, lion)
    # Goat head rising from the back: long face, swept-back ridged horns, small beard
    goat = mix(goat_c, (206, 200, 188), 0.6)
    p.part(p.limb_mask([(0.45, 0.52), (0.45, 0.42), (0.48, 0.34)], [0.034, 0.03, 0.026]), goat, texture='fur')
    for k in range(2):
        horn(p, (0.5 - k * 0.012, 0.28), (0.44 - k * 0.012, 0.16), (0.34 - k * 0.014, 0.18), 0.017 - k * 0.003,
             darken(goat_c, 0.35 + 0.1 * k))
    gh = p.blob_mask([(0.46, 0.31), (0.5, 0.26), (0.55, 0.27), (0.6, 0.31), (0.62, 0.35), (0.6, 0.37), (0.54, 0.35),
                      (0.48, 0.36)])
    p.part(gh, goat, texture='fur')
    p.part(p.blob_mask([(0.49, 0.29), (0.47, 0.26), (0.5, 0.275)]), darken(goat, 0.15), roundness=0.4)
    p.part(p.ellipse_mask(0.612, 0.345, 0.008, 0.006), darken(goat, 0.6))
    p.eye(0.53, 0.3, 0.011, (220, 170, 60), pupil='goat', sclera=(220, 170, 60), squash=0.8)
    # Lion head with mane
    for k in range(14):
        a = -math.pi * 0.95 + k * (math.pi * 1.5 / 13)
        p.part(p.limb_mask([(0.76, 0.43), (0.76 + math.cos(a) * 0.09, 0.43 + math.sin(a) * 0.09),
                            (0.75 + math.cos(a) * 0.14, 0.44 + math.sin(a) * 0.14)], [0.04, 0.035, 0.012]),
               darken(mane_col, 0.12 * (k % 3)), texture='fur', texture_angle=a)
    face = p.blob_mask([(0.74, 0.38), (0.8, 0.35), (0.87, 0.39), (0.9, 0.45), (0.86, 0.5), (0.78, 0.5), (0.74, 0.45)])
    p.part(face, lion, texture='fur')
    p.part(p.ellipse_mask(0.865, 0.46, 0.04, 0.03), lighten(lion, 0.3), texture='fur', roundness=0.6)
    p.part(p.blob_mask([(0.875, 0.43), (0.905, 0.435), (0.895, 0.452)]), (80, 50, 44), gloss=0.5)
    p.stroke([(0.89, 0.455), (0.885, 0.475), (0.87, 0.48)], 0.004, (60, 36, 30))
    p.eye(0.815, 0.41, 0.017, (220, 160, 50), look=(0.4, 0.0), squash=0.8)


@species('hydra')
def draw_hydra(p: Painter, pal):
    skin, belly = pal['primary'], pal['secondary']
    p.shadow(0.48, 0.38)
    body = p.blob_mask([(0.14, 0.86), (0.2, 0.7), (0.36, 0.62), (0.56, 0.62), (0.72, 0.7), (0.78, 0.86), (0.5, 0.9)])
    p.part(p.limb_mask([(0.2, 0.84), (0.1, 0.86), (0.04, 0.8)], [0.04, 0.025, 0.008]), darken(skin, 0.1),
           texture='scales')
    necks = [((0.36, 0.66), (0.24, 0.5), (0.26, 0.34), (0.2, 0.24), 0.8),
             ((0.48, 0.64), (0.48, 0.48), (0.55, 0.3), (0.52, 0.18), 1.0),
             ((0.6, 0.66), (0.72, 0.54), (0.74, 0.4), (0.7, 0.3), 0.9)]
    for k, (a, b, c, d, sc) in enumerate(necks):
        shade = darken(skin, 0.18 * (1 - sc))
        p.part(p.limb_mask([a, b, c, d], [0.05, 0.04, 0.034 * sc, 0.03 * sc]), shade, texture='scales',
               texture_angle=-1.3)
        p.part(p.limb_mask([(a[0] + 0.02, a[1]), (b[0] + 0.015, b[1]), (c[0] + 0.012, c[1])], [0.022, 0.018, 0.012]),
               belly, roundness=0.4, opacity=0.8)
        dragon_head(p, d[0] + 0.01, d[1] - 0.005, 0.7 * sc, shade, belly, (230, 220, 200), (240, 190, 40))
    p.part(body, skin, texture='scales')
    p.part(p.intersect(p.ellipse_mask(0.47, 0.84, 0.25, 0.08), body), belly, roundness=0.5)
    for x in (0.28, 0.66):
        leg(p, (x, 0.78), (x + 0.02, 0.86), (x + 0.01, 0.9), 0.04, 0.026, darken(skin, 0.1), texture='scales')
        for dx in (0.0, 0.018, 0.036):
            p.part(p.poly_mask([(x + dx - 0.01, 0.905), (x + dx, 0.89), (x + dx + 0.008, 0.915)]), (236, 230, 214))


@species('basilisk')
def draw_basilisk(p: Painter, pal):
    skin, belly, crest = pal['primary'], pal['secondary'], pal['accent']
    p.shadow(0.5, 0.38)
    coil = [(0.82, 0.86), (0.5, 0.9), (0.18, 0.84), (0.2, 0.72), (0.5, 0.7), (0.74, 0.74), (0.7, 0.62),
            (0.48, 0.58), (0.4, 0.5), (0.48, 0.36), (0.6, 0.3)]
    widths = [0.02, 0.05, 0.055, 0.055, 0.055, 0.05, 0.048, 0.045, 0.042, 0.04, 0.038]
    p.part(p.limb_mask(coil[:6], widths[:6]), darken(skin, 0.15), texture='scales', texture_scale=0.8)
    p.part(p.limb_mask(coil[4:], widths[4:]), skin, texture='scales', texture_scale=0.8)
    p.part(p.limb_mask([(0.46, 0.57), (0.42, 0.5), (0.47, 0.38), (0.56, 0.32)], [0.022, 0.022, 0.02, 0.018]),
           belly, roundness=0.4, opacity=0.85)
    for k in range(5):
        a = -2.4 + k * 0.38
        p.part(p.limb_mask([(0.6, 0.29), (0.6 + math.cos(a) * 0.08, 0.29 + math.sin(a) * 0.08),
                            (0.6 + math.cos(a) * 0.13, 0.29 + math.sin(a) * 0.13)], [0.012, 0.008, 0.002]),
               crest, gloss=0.4, roundness=0.6)
    p.part(p.subtract(p.ellipse_mask(0.56, 0.24, 0.1, 0.07), p.ellipse_mask(0.6, 0.31, 0.06, 0.05)),
           darken(crest, 0.2), roundness=0.4, opacity=0.85)
    head = p.blob_mask([(0.56, 0.27), (0.62, 0.23), (0.72, 0.24), (0.8, 0.28), (0.78, 0.32), (0.66, 0.34), (0.58, 0.33)])
    p.part(head, skin, texture='scales', texture_scale=0.5)
    p.stroke([(0.64, 0.315), (0.72, 0.31), (0.79, 0.295)], 0.003, darken(skin, 0.5))
    p.stroke([(0.79, 0.3), (0.83, 0.31), (0.85, 0.3)], 0.003, (190, 40, 50))
    p.stroke([(0.83, 0.31), (0.85, 0.325)], 0.003, (190, 40, 50))
    p.eye(0.68, 0.265, 0.016, (250, 220, 40), pupil='slit', sclera=(250, 220, 40), squash=0.8)
    p.glow(p.ellipse_mask(0.68, 0.265, 0.016, 0.013), (250, 230, 80), 0.012, 0.6)


@species('salamander')
def draw_salamander(p: Painter, pal):
    skin, spots = pal['primary'], pal['secondary']
    fire = (255, 150, 40)
    p.shadow(0.5, 0.42)
    tail = p.limb_mask([(0.3, 0.76), (0.18, 0.78), (0.08, 0.72), (0.04, 0.62)], [0.045, 0.035, 0.022, 0.008])
    for x, y, r in ((0.05, 0.6, 0.05), (0.38, 0.6, 0.04), (0.55, 0.6, 0.045)):
        flame = p.blob_mask([(x - r * 0.6, y + r), (x - r * 0.5, y), (x, y - r * 1.8), (x + r * 0.5, y - r * 0.2),
                             (x + r * 0.6, y + r)])
        p.glow(flame, fire, 0.03, 0.5)
        p.part(flame, (255, 120, 30), color2=(255, 230, 120), gradient=1.0, glow=0.8, opacity=0.85, roundness=0.5)
    p.part(tail, skin, texture='skin')
    for x, y in ((0.36, 0.84), (0.7, 0.83)):
        leg(p, (x, 0.78), (x - 0.03, 0.85), (x - 0.02, 0.905), 0.03, 0.018, darken(skin, 0.25), texture='skin')
    body = p.blob_mask([(0.28, 0.76), (0.4, 0.68), (0.6, 0.67), (0.76, 0.7), (0.8, 0.78), (0.6, 0.82), (0.4, 0.82)])
    p.part(body, skin, gloss=0.55, texture='skin')
    for x, y in ((0.36, 0.73), (0.46, 0.71), (0.56, 0.72), (0.66, 0.72), (0.2, 0.76), (0.12, 0.73)):
        p.dot(x, y, 0.015, spots, opacity=0.9)
    for x in (0.42, 0.74):
        leg(p, (x, 0.78), (x + 0.04, 0.85), (x + 0.035, 0.905), 0.032, 0.018, skin, texture='skin')
        for dx in (-0.015, 0.0, 0.015):
            p.stroke([(x + 0.035, 0.905), (x + 0.04 + dx, 0.915)], 0.004, skin)
    head = p.blob_mask([(0.76, 0.72), (0.82, 0.66), (0.9, 0.66), (0.96, 0.7), (0.94, 0.75), (0.84, 0.78), (0.77, 0.77)])
    p.part(head, skin, gloss=0.55, texture='skin')
    p.stroke([(0.86, 0.745), (0.92, 0.735), (0.955, 0.72)], 0.003, darken(skin, 0.5))
    p.eye(0.86, 0.69, 0.016, (40, 30, 20), sclera=(40, 30, 20))


@species('phoenix')
def draw_phoenix(p: Painter, pal):
    body_c = mix(pal['primary'], (230, 80, 30), 0.5)
    gold = mix(pal['secondary'], (255, 200, 60), 0.5)
    p.shadow(0.5, 0.25)
    # Long flame plumes sweeping down and back
    for k in range(5):
        y_end = 0.62 + k * 0.07
        pts = [(0.4, 0.58), (0.28, 0.58 + k * 0.03), (0.16, y_end - 0.04), (0.05 + k * 0.02, y_end + 0.05)]
        plume = p.limb_mask(pts, [0.028, 0.03, 0.022, 0.006])
        p.glow(plume, (255, 140, 40), 0.02, 0.35)
        p.part(plume, mix(body_c, gold, k / 4), color2=(255, 236, 150), gradient=0.9, glow=0.45, roundness=0.6)
        ex, ey = pts[2]
        p.part(p.ellipse_mask(ex, ey, 0.022, 0.014, 0.5), (255, 230, 120), glow=0.8, roundness=0.5)
        p.dot(ex, ey, 0.007, darken(body_c, 0.3))
    for x in (0.48, 0.55):
        p.stroke([(x, 0.7), (x - 0.01, 0.8), (x, 0.9)], 0.01, (120, 70, 40))
        for dx in (-0.025, 0.0, 0.025):
            p.stroke([(x, 0.9), (x + dx, 0.915)], 0.006, (120, 70, 40))
    feather_wing(p, (0.52, 0.46), (0.3, 0.12), 0.09, darken(body_c, 0.15), gold)
    body = p.blob_mask([(0.38, 0.56), (0.46, 0.44), (0.58, 0.42), (0.66, 0.48), (0.66, 0.62), (0.56, 0.72), (0.44, 0.68)])
    p.part(body, body_c, color2=gold, gradient=0.8, texture='feathers', texture_scale=0.6, glow=0.15)
    feather_wing(p, (0.56, 0.48), (0.42, 0.14), 0.1, body_c, gold)
    p.part(p.limb_mask([(0.6, 0.48), (0.66, 0.4), (0.7, 0.34)], [0.045, 0.036, 0.032]), body_c, texture='feathers',
           texture_scale=0.5)
    head = p.ellipse_mask(0.71, 0.31, 0.06, 0.055)
    p.part(head, body_c, texture='feathers', texture_scale=0.4, glow=0.15)
    for k in range(4):
        a = -2.0 + k * 0.25
        crest = p.limb_mask([(0.69, 0.27), (0.69 + math.cos(a) * 0.06, 0.27 + math.sin(a) * 0.06),
                             (0.69 + math.cos(a) * 0.11, 0.27 + math.sin(a) * 0.11)], [0.012, 0.01, 0.003])
        p.part(crest, gold, glow=0.6, roundness=0.5)
    p.part(p.blob_mask([(0.75, 0.29), (0.82, 0.31), (0.79, 0.34), (0.75, 0.335)]), (240, 200, 100), gloss=0.6)
    p.eye(0.72, 0.3, 0.013, (250, 220, 80), sclera=(250, 220, 80), look=(0.3, 0.0))


@species('griffin')
def draw_griffin(p: Painter, pal):
    lion = mix(pal['primary'], (196, 150, 90), 0.6)
    eagle = mix(pal['secondary'], (120, 84, 56), 0.6)
    head_c = (244, 242, 236)
    p.shadow(0.5, 0.4)
    feather_wing(p, (0.5, 0.48), (0.24, 0.12), 0.1, darken(eagle, 0.2), darken(eagle, 0.4), rows=3)
    p.part(p.limb_mask([(0.24, 0.6), (0.14, 0.66), (0.08, 0.76)], [0.02, 0.016, 0.012]), lion, texture='fur')
    p.part(p.ellipse_mask(0.075, 0.79, 0.025, 0.035), darken(lion, 0.4), texture='fur')
    far = darken(lion, 0.25)
    leg(p, (0.3, 0.66), (0.34, 0.79), (0.32, 0.9), 0.045, 0.025, far, texture='fur')
    leg(p, (0.62, 0.62), (0.6, 0.77), (0.61, 0.9), 0.035, 0.016, darken((230, 190, 80), 0.25), texture='scales',
        texture_scale=0.5)
    body = p.blob_mask([(0.22, 0.6), (0.32, 0.5), (0.5, 0.47), (0.66, 0.48), (0.72, 0.6), (0.6, 0.7), (0.4, 0.72), (0.25, 0.68)])
    p.part(body, lion, texture='fur')
    p.part(p.intersect(p.blob_mask([(0.5, 0.46), (0.72, 0.46), (0.74, 0.66), (0.56, 0.7)]), body), eagle,
           texture='feathers', texture_scale=0.6)
    p.part(p.ellipse_mask(0.28, 0.63, 0.085, 0.1, -0.3), lion, texture='fur', outline=0.25)
    leg(p, (0.27, 0.68), (0.24, 0.8), (0.27, 0.9), 0.048, 0.027, lion, texture='fur')
    paw(p, 0.28, 0.912, 0.032, lion)
    leg(p, (0.67, 0.6), (0.69, 0.76), (0.68, 0.895), 0.036, 0.016, (230, 190, 80), texture='scales', texture_scale=0.5)
    for dx in (-0.025, 0.0, 0.025):
        p.stroke([(0.68, 0.895), (0.685 + dx, 0.91), (0.69 + dx * 1.3, 0.917)], 0.006, (60, 50, 40))
    feather_wing(p, (0.56, 0.5), (0.36, 0.1), 0.11, eagle, darken(eagle, 0.3), rows=3)
    p.part(p.limb_mask([(0.64, 0.52), (0.7, 0.42), (0.73, 0.35)], [0.06, 0.05, 0.045]), head_c, texture='feathers',
           texture_scale=0.5)
    head = p.ellipse_mask(0.75, 0.31, 0.065, 0.06)
    p.part(head, head_c, texture='feathers', texture_scale=0.4)
    p.part(p.blob_mask([(0.79, 0.28), (0.86, 0.29), (0.885, 0.33), (0.86, 0.35), (0.85, 0.33), (0.8, 0.34)]),
           (236, 190, 60), gloss=0.6)
    p.eye(0.765, 0.29, 0.014, (240, 170, 40), sclera=(240, 170, 40), look=(0.4, 0.0), lid=(60, 50, 40))


@species('unicorn')
def draw_unicorn(p: Painter, pal):
    coat = mix(pal['secondary'], (246, 244, 250), 0.75)
    mane = pal['primary']
    accent = pal['accent']
    far = darken(coat, 0.2)
    p.shadow(0.5, 0.38)
    flowing_hair(p, [(0.24, 0.5), (0.23, 0.52), (0.22, 0.54)], (-0.4, 1.0), 0.3, mane, width=0.03)
    for x0, x1 in ((0.33, 0.35), (0.62, 0.6)):
        leg(p, (x0, 0.6), (x1, 0.76), (x0, 0.88), 0.035, 0.018, far, texture='fur')
        hoof(p, x0 + 0.005, 0.915, 0.022, (180, 160, 130))
    body = p.blob_mask([(0.22, 0.52), (0.32, 0.44), (0.55, 0.44), (0.68, 0.46), (0.7, 0.58), (0.6, 0.64), (0.4, 0.64), (0.25, 0.6)])
    p.part(body, coat, texture='fur', gloss=0.3)
    p.part(p.ellipse_mask(0.29, 0.55, 0.08, 0.09, -0.3), coat, texture='fur', outline=0.25)
    for x0, x1 in ((0.28, 0.25), (0.66, 0.68)):
        leg(p, (x0, 0.6), (x1, 0.76), (x0 + 0.005, 0.88), 0.038, 0.019, coat, texture='fur')
        hoof(p, x0 + 0.008, 0.915, 0.023, (200, 180, 150))
    neck = p.limb_mask([(0.62, 0.52), (0.7, 0.4), (0.74, 0.3)], [0.07, 0.055, 0.045])
    p.part(neck, coat, texture='fur')
    head = p.blob_mask([(0.72, 0.26), (0.78, 0.22), (0.84, 0.25), (0.92, 0.33), (0.93, 0.38), (0.88, 0.39),
                        (0.8, 0.34), (0.73, 0.33)])
    p.part(head, coat, texture='fur', gloss=0.3)
    p.part(p.ellipse_mask(0.905, 0.36, 0.008, 0.006), darken(coat, 0.5))
    p.part(p.blob_mask([(0.76, 0.24), (0.77, 0.17), (0.79, 0.23)]), coat, roundness=0.5)
    # Spiral horn
    hb, ht = (0.81, 0.23), (0.9, 0.06)
    p.part(p.limb_mask([hb, ht], [0.016, 0.003]), mix(accent, (250, 230, 170), 0.5), gloss=0.8, roundness=0.9)
    for k in range(6):
        t = (k + 0.5) / 6
        x, y = hb[0] + (ht[0] - hb[0]) * t, hb[1] + (ht[1] - hb[1]) * t
        p.stroke([(x - 0.012 * (1 - t), y + 0.004), (x + 0.012 * (1 - t), y - 0.006)], 0.0025,
                 darken(accent, 0.3), opacity=0.6)
    p.glow(p.limb_mask([hb, ht], [0.016, 0.003]), lighten(accent, 0.3), 0.02, 0.35)
    p.eye(0.825, 0.29, 0.016, (90, 60, 140), look=(0.4, 0.0), squash=0.85)
    flowing_hair(p, [(0.74, 0.26), (0.72, 0.31), (0.7, 0.36), (0.68, 0.41), (0.66, 0.46)], (-0.6, 0.6), 0.16,
                 mane, width=0.022)


def humanoid_body(p: Painter, cx, top, height, skin, cloth, hair, eye_c, float_y=0.0, legs=True):
    """Slender figure: head, torso in clothing, arms; optional legs."""
    h = height
    hy = top + h * 0.12
    if legs:
        for dx in (-0.025, 0.02):
            leg(p, (cx + dx, top + h * 0.6), (cx + dx * 1.2, top + h * 0.8), (cx + dx * 1.4, top + h * 0.98),
                0.018, 0.011, darken(skin, 0.1), texture='skin')
    torso = p.blob_mask([(cx - 0.05, top + h * 0.3), (cx + 0.05, top + h * 0.3), (cx + 0.07, top + h * 0.5),
                         (cx + 0.09, top + h * 0.68), (cx - 0.09, top + h * 0.68), (cx - 0.07, top + h * 0.5)])
    p.part(torso, cloth, color2=darken(cloth, 0.3), gradient=0.8, gloss=0.3, texture='skin')
    for side in (-1, 1):
        p.part(p.limb_mask([(cx + side * 0.05, top + h * 0.32), (cx + side * 0.09, top + h * 0.45),
                            (cx + side * 0.08, top + h * 0.58)], [0.016, 0.013, 0.01]), skin, texture='skin')
    p.part(p.limb_mask([(cx, top + h * 0.22), (cx, top + h * 0.3)], [0.015, 0.016]), skin)
    humanoid_head(p, cx + 0.005, hy, h * 0.11, skin, eye_c)
    return hy


@species('sprite')
def draw_sprite(p: Painter, pal):
    wing_c, cloth, hair = lighten(pal['accent'], 0.4), pal['primary'], pal['secondary']
    skin = (246, 220, 200)
    p.shadow(0.5, 0.12, opacity=0.18)
    for k, (tx, ty, tw) in enumerate(((0.18, 0.18, 0.08), (0.2, 0.52, 0.06), (0.8, 0.16, 0.08), (0.78, 0.5, 0.06))):
        root = (0.5, 0.42 + (k % 2) * 0.04)
        mx, my = (root[0] + tx) / 2, (root[1] + ty) / 2
        wing = p.ellipse_mask(mx, my, math.dist(root, (tx, ty)) * 0.55, tw, math.atan2(ty - root[1], tx - root[0]))
        p.glow(wing, wing_c, 0.02, 0.3)
        p.part(wing, wing_c, roundness=0.25, gloss=0.6, opacity=0.45, outline=0.6)
        for v in (-0.3, 0.0, 0.3):
            p.stroke([root, (mx + v * tw * 0.4, my + v * tw * 0.6), (tx, ty)], 0.002, lighten(wing_c, 0.5), opacity=0.6)
    hy = 0.26 + 0.56 * 0.12
    flowing_hair(p, [(0.47, hy - 0.05), (0.5, hy - 0.06), (0.46, hy - 0.02)], (-0.6, 0.8), 0.13, hair, width=0.02)
    humanoid_body(p, 0.5, 0.26, 0.56, skin, cloth, hair, (60, 140, 90))
    p.part(p.subtract(p.ellipse_mask(0.505, hy - 0.03, 0.065, 0.045), p.ellipse_mask(0.53, hy + 0.012, 0.06, 0.05)),
           hair, gloss=0.4, texture='fur', texture_angle=0.3)
    for x, y, r in ((0.3, 0.3, 0.008), (0.7, 0.6, 0.006), (0.36, 0.74, 0.007), (0.66, 0.28, 0.005)):
        p.dot(x, y, r * 2.5, lighten(wing_c, 0.6), opacity=0.35, blur=0.01)
        p.dot(x, y, r, (255, 255, 240))


@species('sylph')
def draw_sylph(p: Painter, pal):
    air, cloth = lighten(pal['primary'], 0.35), lighten(pal['secondary'], 0.15)
    skin = mix((232, 230, 244), air, 0.25)
    # Whirlwind instead of legs
    for k in range(6):
        y = 0.6 + k * 0.05
        w = 0.1 - k * 0.012
        ring = p.subtract(p.ellipse_mask(0.5 + math.sin(k) * 0.02, y, w, 0.02 + 0.003 * k),
                          p.ellipse_mask(0.5 + math.sin(k) * 0.02, y - 0.006, w * 0.8, 0.014))
        p.part(ring, air, opacity=0.55, glow=0.4, roundness=0.4)
    for k in range(3):
        p.stroke([(0.3 + k * 0.05, 0.75 - k * 0.1), (0.2 + k * 0.03, 0.6 - k * 0.1), (0.28 + k * 0.05, 0.45 - k * 0.08)],
                 0.004, lighten(air, 0.4), opacity=0.5)
    # Feathery wings
    for side in (-1, 1):
        for k in range(5):
            a = (-2.0 if side < 0 else -1.14) + side * k * 0.18
            p.part(p.ellipse_mask(0.5 + math.cos(a) * 0.12, 0.38 + math.sin(a) * 0.1, 0.1, 0.022, a), air,
                   opacity=0.5, glow=0.3, roundness=0.4)
    hy = 0.2 + 0.5 * 0.12
    flowing_hair(p, [(0.48, hy - 0.05), (0.5, hy - 0.055), (0.47, hy - 0.02), (0.46, hy + 0.01)], (-1.0, 0.25), 0.24,
                 darken(air, 0.1), width=0.02, opacity=0.9, glow=0.2)
    humanoid_body(p, 0.5, 0.2, 0.5, skin, cloth, air, (120, 170, 220), legs=False)
    p.part(p.subtract(p.ellipse_mask(0.505, hy - 0.025, 0.06, 0.04), p.ellipse_mask(0.53, hy + 0.01, 0.055, 0.045)),
           darken(air, 0.1), gloss=0.4, texture='fur', texture_angle=0.3)
    p.glow(p.ellipse_mask(0.5, 0.5, 0.15, 0.3), air, 0.05, 0.25)


@species('undine')
def draw_undine(p: Painter, pal):
    water = mix(pal['accent'], (80, 170, 220), 0.5)
    deep = darken(water, 0.35)
    skin = mix(water, (230, 245, 250), 0.55)
    p.shadow(0.5, 0.25, opacity=0.2)
    p.part(p.ellipse_mask(0.5, 0.9, 0.22, 0.03), lighten(water, 0.3), opacity=0.5, glow=0.3, roundness=0.4)
    # Fish tail curling
    tail = p.limb_mask([(0.5, 0.52), (0.46, 0.66), (0.47, 0.78), (0.56, 0.86), (0.68, 0.83), (0.74, 0.76)],
                       [0.075, 0.07, 0.058, 0.044, 0.028, 0.014])
    p.part(tail, water, color2=deep, gradient=0.8, texture='scales', texture_scale=0.6, gloss=0.6, opacity=0.9)
    fin = p.blob_mask([(0.73, 0.77), (0.8, 0.66), (0.83, 0.72), (0.88, 0.76), (0.8, 0.8)])
    p.part(fin, lighten(water, 0.25), opacity=0.7, gloss=0.6, roundness=0.4)
    hy = 0.2 + 0.5 * 0.12
    flowing_hair(p, [(0.48, hy - 0.05), (0.51, hy - 0.06), (0.47, hy - 0.02), (0.46, hy + 0.01)],
                 (-0.6, 1.0), 0.26, deep, width=0.02, opacity=0.9, glow=0.2)
    humanoid_body(p, 0.5, 0.2, 0.5, skin, water, deep, (30, 90, 140), legs=False)
    p.part(p.subtract(p.ellipse_mask(0.505, hy - 0.025, 0.06, 0.04), p.ellipse_mask(0.53, hy + 0.01, 0.055, 0.045)),
           deep, gloss=0.4, opacity=0.95, texture='fur', texture_angle=0.3)
    for x, y, r in ((0.3, 0.4, 0.012), (0.7, 0.3, 0.01), (0.66, 0.5, 0.008), (0.34, 0.62, 0.009)):
        p.part(p.ellipse_mask(x, y, r, r * 1.3), lighten(water, 0.4), gloss=0.9, opacity=0.75, roundness=0.8)


@species('gnome')
def draw_gnome(p: Painter, pal):
    hat, tunic, beard = pal['primary'], pal['secondary'], (236, 234, 228)
    skin = (232, 188, 160)
    p.shadow(0.5, 0.22)
    for x in (0.44, 0.56):
        leg(p, (x, 0.7), (x, 0.8), (x, 0.86), 0.03, 0.028, (80, 70, 90), texture='skin')
        p.part(p.blob_mask([(x - 0.03, 0.85), (x + 0.03, 0.85), (x + 0.07, 0.89), (x + 0.065, 0.915), (x - 0.035, 0.915)]),
               (96, 64, 44), gloss=0.4)
    body = p.blob_mask([(0.36, 0.72), (0.38, 0.52), (0.5, 0.46), (0.62, 0.52), (0.64, 0.72), (0.5, 0.76)])
    p.part(body, tunic, color2=darken(tunic, 0.25), gradient=0.6, texture='fur', texture_scale=0.5)
    p.part(p.limb_mask([(0.37, 0.68), (0.5, 0.7), (0.63, 0.68)], [0.014, 0.014, 0.014]), (90, 60, 40), gloss=0.4)
    p.part(p.ellipse_mask(0.5, 0.69, 0.018, 0.014), (220, 190, 80), gloss=0.9)
    for side in (-1, 1):
        p.part(p.limb_mask([(0.5 + side * 0.11, 0.54), (0.5 + side * 0.14, 0.62), (0.5 + side * 0.12, 0.68)],
                           [0.025, 0.022, 0.018]), tunic, texture='fur', texture_scale=0.5)
        p.part(p.ellipse_mask(0.5 + side * 0.12, 0.7, 0.02, 0.02), skin)
    # Face and beard
    p.part(p.ellipse_mask(0.5, 0.42, 0.075, 0.07), skin, texture='skin')
    p.part(p.blob_mask([(0.43, 0.43), (0.57, 0.43), (0.6, 0.52), (0.55, 0.64), (0.5, 0.68), (0.45, 0.64), (0.4, 0.52)]),
           beard, texture='fur', texture_angle=1.5, texture_scale=1.3)
    p.part(p.ellipse_mask(0.52, 0.445, 0.022, 0.02), mix(skin, (220, 120, 110), 0.4), gloss=0.4)
    for x in (0.47, 0.55):
        p.eye(x, 0.415, 0.011, (60, 90, 130), look=(0.2, 0.0))
    p.part(p.limb_mask([(0.43, 0.395), (0.5, 0.4), (0.57, 0.395)], [0.006, 0.004, 0.006]), beard, roundness=0.4)
    # Tall pointed hat
    hat_m = p.blob_mask([(0.41, 0.39), (0.44, 0.28), (0.5, 0.12), (0.56, 0.06), (0.57, 0.12), (0.58, 0.28), (0.6, 0.39), (0.5, 0.41)])
    p.part(hat_m, hat, texture='fur', texture_scale=0.6, gloss=0.2)
    p.part(p.limb_mask([(0.4, 0.385), (0.5, 0.405), (0.6, 0.385)], [0.016, 0.018, 0.016]), darken(hat, 0.2))


@species('golem')
def draw_golem(p: Painter, pal):
    stone = desaturate(mix(pal['primary'], (140, 136, 128), 0.6), 0.4)
    moss = mix(pal['secondary'], (90, 130, 60), 0.6)
    rune = lighten(pal['accent'], 0.2)
    p.shadow(0.5, 0.36)
    for x in (0.4, 0.6):
        p.part(p.blob_mask([(x - 0.06, 0.74), (x + 0.06, 0.74), (x + 0.07, 0.915), (x - 0.07, 0.915)]),
               darken(stone, 0.15), texture='stone')
    torso = p.blob_mask([(0.3, 0.42), (0.36, 0.3), (0.64, 0.3), (0.72, 0.42), (0.68, 0.7), (0.6, 0.78), (0.4, 0.78), (0.32, 0.7)])
    p.part(torso, stone, texture='stone', roundness=0.8)
    p.part(p.intersect(p.ellipse_mask(0.42, 0.33, 0.1, 0.05), torso), moss, texture='fur', texture_scale=0.6,
           roundness=0.6)
    for pts in ([(0.46, 0.45), (0.5, 0.52), (0.54, 0.45)], [(0.5, 0.52), (0.5, 0.62)], [(0.44, 0.6), (0.56, 0.6)]):
        p.stroke(pts, 0.008, rune, smooth=False)
    p.glow(p.ellipse_mask(0.5, 0.54, 0.07, 0.1), rune, 0.03, 0.45)
    for side in (-1, 1):
        x = 0.5 + side * 0.22
        p.part(p.ellipse_mask(x, 0.4, 0.08, 0.07), darken(stone, 0.05), texture='stone')
        p.part(p.blob_mask([(x - 0.05, 0.44), (x + 0.05, 0.44), (x + side * 0.03 + 0.05, 0.66),
                            (x + side * 0.03 - 0.05, 0.66)]), stone, texture='stone')
        p.part(p.ellipse_mask(x + side * 0.03, 0.72, 0.065, 0.06), darken(stone, 0.1), texture='stone')
    head = p.blob_mask([(0.42, 0.3), (0.43, 0.2), (0.57, 0.19), (0.59, 0.3), (0.5, 0.32)])
    p.part(head, lighten(stone, 0.05), texture='stone')
    for x in (0.47, 0.54):
        p.dot(x, 0.25, 0.012, rune)
        p.dot(x, 0.25, 0.025, rune, opacity=0.4, blur=0.01)


@species('wisp')
def draw_wisp(p: Painter, pal):
    core = lighten(pal['accent'], 0.4)
    flame = pal['primary']
    p.shadow(0.5, 0.15, opacity=0.15)
    for k in range(5):
        a = -2.3 + k * 0.2
        pts = [(0.5, 0.56), (0.5 + math.cos(a) * 0.12, 0.56 + math.sin(a) * 0.12),
               (0.48 + math.cos(a) * 0.22 + 0.04 * math.sin(k), 0.5 + math.sin(a) * 0.26)]
        trail = p.limb_mask(pts, [0.06 - k * 0.004, 0.035, 0.004])
        p.glow(trail, flame, 0.03, 0.35)
        p.part(trail, flame, color2=core, gradient=0.6, opacity=0.6, glow=0.7, roundness=0.4)
    orb = p.ellipse_mask(0.5, 0.58, 0.13, 0.13)
    p.glow(orb, flame, 0.07, 0.7)
    p.part(orb, mix(flame, core, 0.4), color2=core, gradient=0.5, opacity=0.85, glow=0.6, gloss=0.5)
    p.part(p.ellipse_mask(0.5, 0.6, 0.07, 0.07), (255, 255, 240), opacity=0.7, glow=1.0, roundness=0.4)
    for x in (0.47, 0.54):
        p.part(p.ellipse_mask(x, 0.56, 0.012, 0.018), darken(flame, 0.5), opacity=0.7, roundness=0.3)
    for x, y, r in ((0.3, 0.4, 0.008), (0.72, 0.36, 0.006), (0.68, 0.76, 0.007), (0.32, 0.72, 0.005)):
        p.dot(x, y, r * 3, core, opacity=0.4, blur=0.01)
        p.dot(x, y, r, (255, 255, 240))


@species('kraken')
def draw_kraken(p: Painter, pal):
    skin = mix(pal['primary'], (150, 60, 80), 0.4)
    under = lighten(pal['secondary'], 0.3)
    p.shadow(0.5, 0.4)
    tentacles = [[(0.38, 0.66), (0.22, 0.74), (0.14, 0.86), (0.08, 0.8)],
                 [(0.44, 0.7), (0.36, 0.84), (0.3, 0.9), (0.24, 0.86)],
                 [(0.5, 0.72), (0.5, 0.86), (0.56, 0.92), (0.6, 0.88)],
                 [(0.56, 0.7), (0.66, 0.84), (0.76, 0.9), (0.8, 0.84)],
                 [(0.62, 0.66), (0.78, 0.7), (0.9, 0.78), (0.92, 0.7)]]
    for k, t in enumerate(tentacles):
        c = darken(skin, 0.15 if k % 2 else 0.0)
        p.part(p.limb_mask(t, [0.045, 0.032, 0.02, 0.006]), c, gloss=0.5, texture='skin')
        path = catmull_rom(t, closed=False, steps=8)
        for i in range(2, len(path) - 3, 3):
            x, y = path[i]
            p.dot(x, y + 0.012, 0.007 * (1 - i / len(path)) + 0.003, under)
    mantle = p.blob_mask([(0.34, 0.66), (0.32, 0.5), (0.38, 0.3), (0.5, 0.18), (0.62, 0.3), (0.68, 0.5),
                          (0.66, 0.66), (0.5, 0.72)])
    p.part(mantle, skin, color2=darken(skin, 0.2), gradient=0.5, gloss=0.5, texture='skin')
    for x, y, r in ((0.44, 0.34, 0.025), (0.56, 0.42, 0.02), (0.48, 0.5, 0.018), (0.6, 0.3, 0.015)):
        p.dot(x, y, r, darken(skin, 0.25), opacity=0.5)
    for x in (0.43, 0.57):
        p.eye(x, 0.6, 0.032, (240, 190, 50), pupil='goat', sclera=(240, 190, 50))


@species('manticore')
def draw_manticore(p: Painter, pal):
    lion = mix(pal['primary'], (190, 110, 70), 0.55)
    mane_c = darken(mix(pal['secondary'], (130, 60, 40), 0.5), 0.1)
    wing_c = darken(pal['accent'], 0.3)
    p.shadow(0.5, 0.4)
    membrane_wing(p, (0.48, 0.48), [(0.42, 0.24), (0.2, 0.14), (0.2, 0.3), (0.28, 0.42)], darken(wing_c, 0.2),
                  darken(lion, 0.4))
    # Scorpion tail arching over the back
    seg = [(0.25, 0.58), (0.16, 0.5), (0.14, 0.36), (0.22, 0.24), (0.34, 0.2), (0.42, 0.24)]
    shell = mix(lion, (90, 60, 50), 0.45)
    p.part(p.limb_mask(seg, [0.032, 0.03, 0.027, 0.024, 0.02, 0.016]), shell, gloss=0.6, roundness=0.9)
    path = catmull_rom(seg, closed=False, steps=4)
    for i in range(2, len(path) - 1, 2):
        (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
        a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        r = 0.031 - i * 0.0007
        x, y = path[i]
        p.stroke([(x - math.cos(a) * r, y - math.sin(a) * r), (x + math.cos(a) * r, y + math.sin(a) * r)], 0.004,
                 darken(shell, 0.4), opacity=0.7, smooth=False)
    p.part(p.blob_mask([(0.41, 0.22), (0.47, 0.25), (0.5, 0.31), (0.45, 0.28), (0.41, 0.27)]), (40, 30, 30), gloss=0.8)
    far = darken(lion, 0.25)
    leg(p, (0.3, 0.64), (0.33, 0.78), (0.31, 0.9), 0.045, 0.025, far, texture='fur')
    leg(p, (0.62, 0.62), (0.6, 0.77), (0.61, 0.9), 0.045, 0.026, far, texture='fur')
    paw(p, 0.32, 0.912, 0.03, far)
    paw(p, 0.62, 0.912, 0.03, far)
    body = p.blob_mask([(0.22, 0.6), (0.3, 0.5), (0.5, 0.48), (0.66, 0.5), (0.7, 0.62), (0.6, 0.7), (0.4, 0.7), (0.25, 0.68)])
    p.part(body, lion, texture='fur')
    p.part(p.ellipse_mask(0.28, 0.62, 0.085, 0.1, -0.3), lion, texture='fur', outline=0.25)
    leg(p, (0.26, 0.68), (0.23, 0.8), (0.26, 0.9), 0.048, 0.027, lion, texture='fur')
    paw(p, 0.27, 0.912, 0.032, lion)
    leg(p, (0.66, 0.62), (0.68, 0.77), (0.67, 0.9), 0.05, 0.028, lion, texture='fur')
    paw(p, 0.685, 0.912, 0.033, lion)
    membrane_wing(p, (0.54, 0.5), [(0.5, 0.22), (0.3, 0.1), (0.3, 0.26), (0.36, 0.4)], wing_c, darken(lion, 0.3))
    for k in range(16):
        a = -math.pi * 1.0 + k * (math.pi * 1.6 / 15)
        p.part(p.limb_mask([(0.76, 0.44), (0.76 + math.cos(a) * 0.1, 0.44 + math.sin(a) * 0.1),
                            (0.75 + math.cos(a) * 0.15, 0.45 + math.sin(a) * 0.15)], [0.042, 0.036, 0.012]),
               darken(mane_c, 0.1 * (k % 3)), texture='fur', texture_angle=a)
    face = p.blob_mask([(0.73, 0.38), (0.8, 0.35), (0.87, 0.39), (0.9, 0.46), (0.86, 0.51), (0.77, 0.51), (0.73, 0.45)])
    p.part(face, lion, texture='fur')
    p.part(p.ellipse_mask(0.86, 0.47, 0.04, 0.03), lighten(lion, 0.25), texture='fur', roundness=0.6)
    p.part(p.blob_mask([(0.87, 0.44), (0.9, 0.445), (0.89, 0.462)]), (70, 44, 40), gloss=0.5)
    p.stroke([(0.82, 0.49), (0.86, 0.495), (0.885, 0.485)], 0.004, (60, 30, 30))
    for x in (0.835, 0.865):
        p.part(p.poly_mask([(x, 0.49), (x + 0.008, 0.49), (x + 0.004, 0.508)]), (246, 242, 230), gloss=0.5)
    p.eye(0.81, 0.415, 0.018, (230, 80, 40), pupil='slit', look=(0.4, 0.0), squash=0.75)


def draw_egg(p: Painter):
    """Speckled egg resting on the ground."""
    p.shadow(0.5, 0.2)
    egg = p.blob_mask([(0.5, 0.3), (0.6, 0.36), (0.66, 0.55), (0.64, 0.78), (0.5, 0.88), (0.36, 0.78),
                       (0.34, 0.55), (0.4, 0.36)])
    p.part(egg, (238, 226, 176), color2=(214, 196, 140), gradient=0.6, gloss=0.5, roundness=1.2, texture='skin')
    rng = np.random.default_rng(7)
    for _ in range(14):
        x, y = rng.uniform(0.39, 0.61), rng.uniform(0.4, 0.8)
        p.part(p.intersect(p.ellipse_mask(x, y, rng.uniform(0.008, 0.02), rng.uniform(0.006, 0.014),
                                          rng.uniform(0, 3)), egg), (170, 130, 70), flat=True, opacity=0.55)


def render_creature(name: str, palette: Sequence, grid: int, palette_index: Optional[int] = None) -> Image.Image:
    """Pixel-art creature facing right on a grid x grid canvas with a transparent background."""
    p = Painter(grid, seed=sum(map(ord, name)))
    SPECIES.get(name, SPECIES['cat'])(p, palette_for(name, palette, palette_index))
    return p.finish()


# Items

def draw_ball(p: Painter):
    """Rubber ball with a white band; no ground shadow (it bounces in its own window)."""
    ball = p.ellipse_mask(0.5, 0.5, 0.42, 0.42)
    p.part(ball, (214, 60, 64), gloss=0.8, roundness=1.3)
    band = p.intersect(p.subtract(p.ellipse_mask(0.5, 0.5, 0.5, 0.2, -0.5), p.ellipse_mask(0.5, 0.5, 0.5, 0.11, -0.5)),
                       ball)
    p.part(band, (240, 236, 228), gloss=0.8, roundness=1.3, outline=0.0)
    p.dot(0.35, 0.32, 0.035, (255, 255, 255))


def draw_food(p: Painter):
    """Ceramic bowl heaped with kibble."""
    p.shadow(0.5, 0.36, y=0.86)
    rim_back = p.ellipse_mask(0.5, 0.5, 0.38, 0.1)
    p.part(rim_back, (196, 84, 84), roundness=0.4, gloss=0.3)
    rng = np.random.default_rng(3)
    for _ in range(26):
        x, y = rng.uniform(0.2, 0.8), rng.uniform(0.36, 0.52)
        if ((x - 0.5) / 0.34) ** 2 + ((y - 0.52) / 0.14) ** 2 > 1:
            continue
        c = mix((150, 92, 52), (196, 136, 80), rng.random())
        p.part(p.ellipse_mask(x, y, 0.035, 0.026, rng.uniform(0, 3)), c, gloss=0.35, roundness=0.9, texture='stone')
    bowl = p.blob_mask([(0.12, 0.5), (0.88, 0.5), (0.8, 0.72), (0.66, 0.82), (0.34, 0.82), (0.2, 0.72)])
    p.part(bowl, (214, 96, 96), color2=(170, 60, 64), gradient=0.7, gloss=0.6, roundness=0.9)
    p.part(p.subtract(p.ellipse_mask(0.5, 0.5, 0.38, 0.1), p.ellipse_mask(0.5, 0.47, 0.35, 0.08)),
           (236, 140, 136), gloss=0.7, roundness=0.4)
    p.part(p.ellipse_mask(0.5, 0.83, 0.2, 0.03), (150, 50, 56), roundness=0.4)
    p.dot(0.27, 0.6, 0.03, (255, 236, 230), opacity=0.5, blur=0.015)


def draw_shelter(p: Painter):
    """Small wooden house with a tiled roof, round door and lit window."""
    p.shadow(0.5, 0.4)
    wood = (160, 108, 66)
    walls = p.poly_mask([(0.18, 0.5), (0.82, 0.5), (0.82, 0.92), (0.18, 0.92)])
    p.part(walls, wood, roundness=0.25, gloss=0.1, texture='fur', texture_angle=0.0, texture_scale=1.5)
    for y in np.linspace(0.56, 0.88, 6):
        p.stroke([(0.18, y), (0.82, y)], 0.004, darken(wood, 0.35), opacity=0.6, smooth=False)
    # Window with warm light
    win = p.poly_mask([(0.26, 0.6), (0.4, 0.6), (0.4, 0.73), (0.26, 0.73)])
    p.glow(win, (255, 200, 110), 0.03, 0.5)
    p.part(win, (255, 214, 130), glow=0.8, roundness=0.3)
    p.stroke([(0.33, 0.6), (0.33, 0.73)], 0.008, darken(wood, 0.4), smooth=False)
    p.stroke([(0.26, 0.665), (0.4, 0.665)], 0.008, darken(wood, 0.4), smooth=False)
    p.part(p.subtract(p.poly_mask([(0.245, 0.585), (0.415, 0.585), (0.415, 0.745), (0.245, 0.745)]), win),
           darken(wood, 0.25), roundness=0.4)
    # Arched door
    door = p.union(p.poly_mask([(0.52, 0.7), (0.7, 0.7), (0.7, 0.92), (0.52, 0.92)]), p.ellipse_mask(0.61, 0.7, 0.09, 0.08))
    p.part(door, (96, 60, 40), roundness=0.35, texture='fur', texture_angle=1.57)
    p.dot(0.675, 0.81, 0.012, (220, 190, 90))
    # Chimney, then a roof of overlapping tiles
    p.part(p.poly_mask([(0.64, 0.2), (0.74, 0.2), (0.74, 0.42), (0.64, 0.36)]), (150, 140, 130), texture='stone',
           roundness=0.4)
    p.part(p.poly_mask([(0.625, 0.18), (0.755, 0.18), (0.755, 0.215), (0.625, 0.215)]), (120, 112, 106), roundness=0.4)
    roof = p.poly_mask([(0.06, 0.57), (0.5, 0.15), (0.94, 0.57)])
    p.part(roof, (176, 70, 56), color2=(140, 52, 42), gradient=0.5, gloss=0.25, roundness=0.5,
           texture='scales', texture_scale=2.4)
    p.part(p.limb_mask([(0.06, 0.57), (0.5, 0.15), (0.94, 0.57)], [0.016, 0.018, 0.016]), (120, 44, 36), gloss=0.4)


def render_item(name: str, grid: int) -> Image.Image:
    """Pixel-art item on a grid x grid canvas: 'ball', 'food', 'shelter' or 'egg'."""
    draw = {'ball': draw_ball, 'food': draw_food, 'shelter': draw_shelter, 'egg': draw_egg}[name]
    p = Painter(grid, seed=len(name))
    draw(p)
    return p.finish()


def render_icon(grid: int = 64) -> Image.Image:
    """Application icon: pixel-art portrait of an orange tabby cat in a round badge (grid x grid)."""
    # Draw the whole cat large enough that its head spans the grid
    big = render_creature('cat', ['#FF6B6B', '#FFE66D', '#4ECDC4'], int(grid / 0.5), palette_index=0)
    x0, y0 = int(big.width * 0.52), int(big.height * 0.15)
    head = big.crop((x0, y0, x0 + grid, y0 + grid))
    yy, xx = np.mgrid[0:grid, 0:grid]
    inside = (xx + 0.5 - grid / 2) ** 2 + (yy + 0.5 - grid / 2) ** 2 <= (grid / 2 - 0.5) ** 2
    band = np.clip(np.floor((1 - yy / grid) * 4) / 4, 0, 1)[..., None]
    bg = np.array((70, 120, 150), np.float32) + band * np.array((60, 50, 40), np.float32)
    rim = inside & ~((xx + 0.5 - grid / 2) ** 2 + (yy + 0.5 - grid / 2) ** 2 <= (grid / 2 - 2) ** 2)
    bg = np.where(rim[..., None], np.array((40, 60, 80), np.float32), bg)
    badge = Image.fromarray(np.dstack([bg, inside * 255]).astype(np.uint8), 'RGBA')
    badge = Image.alpha_composite(badge, head)
    badge.putalpha(Image.fromarray((inside * 255).astype(np.uint8)))
    return badge
