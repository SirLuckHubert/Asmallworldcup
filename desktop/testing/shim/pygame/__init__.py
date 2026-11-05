"""A stand-in for pygame, drawn with Pillow. NOT part of the game (copy of the project's
pygame_shim.py, used here only to run the game headless)."""
import math
import os
import sys
import types

from PIL import Image, ImageChops, ImageDraw, ImageFont

IS_SHIM = True

SRCALPHA = 0x00010000
FULLSCREEN = 0x80000000
SCALED = 0x200
RESIZABLE = 0x10
NOFRAME = 0x20
BLEND_RGB_ADD = 0x1
BLEND_RGB_SUB = 0x2
BLEND_RGB_MULT = 0x3
BLEND_RGBA_ADD = 0x6
BLEND_RGBA_MULT = 0x8
QUIT = 256
KEYDOWN = 768
KEYUP = 769
MOUSEMOTION = 1024
MOUSEBUTTONDOWN = 1025
MOUSEBUTTONUP = 1026
MOUSEWHEEL = 1027
FINGERDOWN = 1792
FINGERUP = 1793
FINGERMOTION = 1794
WINDOWFOCUSLOST = 32785
WINDOWFOCUSGAINED = 32784
VIDEORESIZE = 32769
K_BACKSPACE, K_TAB, K_RETURN, K_ESCAPE, K_SPACE = 8, 9, 13, 27, 32
K_LEFT, K_RIGHT, K_UP, K_DOWN = 1073741904, 1073741903, 1073741906, 1073741905
K_LSHIFT, K_RSHIFT, K_LCTRL, K_RCTRL = 1073742049, 1073742053, 1073742048, 1073742052
for _i in range(10):
    globals()["K_%d" % _i] = 48 + _i
for _c in "abcdefghijklmnopqrstuvwxyz":
    globals()["K_" + _c] = ord(_c)
for _i in range(1, 13):
    globals()["K_F%d" % _i] = 1073741881 + _i


class error(Exception):
    pass


def _i(v):
    return int(v)


class Rect:
    __slots__ = ("x", "y", "w", "h")

    def __init__(self, *a):
        if len(a) == 1:
            a = a[0]
            if isinstance(a, Rect):
                a = (a.x, a.y, a.w, a.h)
            elif hasattr(a, "rect"):
                r = a.rect
                a = (r.x, r.y, r.w, r.h)
        if len(a) == 2:
            a = (a[0][0], a[0][1], a[1][0], a[1][1])
        self.x, self.y, self.w, self.h = _i(a[0]), _i(a[1]), _i(a[2]), _i(a[3])

    width = property(lambda s: s.w, lambda s, v: setattr(s, "w", _i(v)))
    height = property(lambda s: s.h, lambda s, v: setattr(s, "h", _i(v)))
    left = property(lambda s: s.x, lambda s, v: setattr(s, "x", _i(v)))
    top = property(lambda s: s.y, lambda s, v: setattr(s, "y", _i(v)))
    right = property(lambda s: s.x + s.w, lambda s, v: setattr(s, "x", _i(v) - s.w))
    bottom = property(lambda s: s.y + s.h, lambda s, v: setattr(s, "y", _i(v) - s.h))
    centerx = property(lambda s: s.x + s.w // 2, lambda s, v: setattr(s, "x", _i(v) - s.w // 2))
    centery = property(lambda s: s.y + s.h // 2, lambda s, v: setattr(s, "y", _i(v) - s.h // 2))

    def _pair(getx, gety, setx, sety):
        def get(s):
            return (getattr(s, getx), getattr(s, gety))

        def put(s, v):
            setattr(s, setx, v[0])
            setattr(s, sety, v[1])
        return property(get, put)

    topleft = _pair("left", "top", "left", "top")
    topright = _pair("right", "top", "right", "top")
    bottomleft = _pair("left", "bottom", "left", "bottom")
    bottomright = _pair("right", "bottom", "right", "bottom")
    midtop = _pair("centerx", "top", "centerx", "top")
    midbottom = _pair("centerx", "bottom", "centerx", "bottom")
    midleft = _pair("left", "centery", "left", "centery")
    midright = _pair("right", "centery", "right", "centery")
    center = _pair("centerx", "centery", "centerx", "centery")
    size = _pair("w", "h", "width", "height")
    del _pair

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    def move(self, dx, dy=None):
        if dy is None:
            dx, dy = dx
        return Rect(self.x + _i(dx), self.y + _i(dy), self.w, self.h)

    def move_ip(self, dx, dy=None):
        if dy is None:
            dx, dy = dx
        self.x += _i(dx)
        self.y += _i(dy)

    def inflate(self, dx, dy=None):
        if dy is None:
            dx, dy = dx
        dx, dy = _i(dx), _i(dy)
        return Rect(self.x - int(dx / 2), self.y - int(dy / 2), self.w + dx, self.h + dy)

    def inflate_ip(self, dx, dy=None):
        r = self.inflate(dx, dy)
        self.x, self.y, self.w, self.h = r.x, r.y, r.w, r.h

    def collidepoint(self, px, py=None):
        if py is None:
            px, py = px
        return self.x <= px < self.x + self.w and self.y <= py < self.y + self.h

    def colliderect(self, o):
        o = Rect(o)
        return (self.x < o.x + o.w and o.x < self.x + self.w and
                self.y < o.y + o.h and o.y < self.y + self.h)

    def contains(self, o):
        o = Rect(o)
        return (self.x <= o.x and self.y <= o.y and o.x + o.w <= self.x + self.w and
                o.y + o.h <= self.y + self.h and self.x + self.w > o.x and self.y + self.h > o.y)

    def clip(self, o):
        o = Rect(o)
        x0, y0 = max(self.x, o.x), max(self.y, o.y)
        x1, y1 = min(self.right, o.right), min(self.bottom, o.bottom)
        if x1 <= x0 or y1 <= y0:
            return Rect(self.x, self.y, 0, 0)
        return Rect(x0, y0, x1 - x0, y1 - y0)

    def union(self, o):
        o = Rect(o)
        x0, y0 = min(self.x, o.x), min(self.y, o.y)
        x1, y1 = max(self.right, o.right), max(self.bottom, o.bottom)
        return Rect(x0, y0, x1 - x0, y1 - y0)

    def union_ip(self, o):
        r = self.union(o)
        self.x, self.y, self.w, self.h = r.x, r.y, r.w, r.h

    def clamp(self, o):
        o = Rect(o)
        r = self.copy()
        if r.w >= o.w:
            r.x = o.x + o.w // 2 - r.w // 2
        elif r.x < o.x:
            r.x = o.x
        elif r.right > o.right:
            r.x = o.right - r.w
        if r.h >= o.h:
            r.y = o.y + o.h // 2 - r.h // 2
        elif r.y < o.y:
            r.y = o.y
        elif r.bottom > o.bottom:
            r.y = o.bottom - r.h
        return r

    def clamp_ip(self, o):
        r = self.clamp(o)
        self.x, self.y = r.x, r.y

    def normalize(self):
        if self.w < 0:
            self.x += self.w
            self.w = -self.w
        if self.h < 0:
            self.y += self.h
            self.h = -self.h

    def scale_by(self, k, ky=None):
        ky = k if ky is None else ky
        r = Rect(0, 0, self.w * k, self.h * ky)
        r.center = self.center
        return r

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

    def __getitem__(self, i):
        return (self.x, self.y, self.w, self.h)[i]

    def __len__(self):
        return 4

    def __eq__(self, o):
        try:
            o = Rect(o)
        except Exception:
            return False
        return (self.x, self.y, self.w, self.h) == (o.x, o.y, o.w, o.h)

    def __ne__(self, o):
        return not self.__eq__(o)

    __hash__ = None

    def __bool__(self):
        return self.w != 0 and self.h != 0

    def __repr__(self):
        return "<rect(%d, %d, %d, %d)>" % (self.x, self.y, self.w, self.h)


class Vector2:
    __slots__ = ("x", "y")

    def __init__(self, x=0.0, y=None):
        if y is None:
            if isinstance(x, (int, float)):
                x, y = x, x
            else:
                x, y = x[0], x[1]
        self.x, self.y = float(x), float(y)

    xy = property(lambda s: Vector2(s.x, s.y), lambda s, v: s.update(v))

    def update(self, x=0.0, y=None):
        if y is None:
            if isinstance(x, (int, float)):
                x, y = x, x
            else:
                x, y = x[0], x[1]
        self.x, self.y = float(x), float(y)

    def copy(self):
        return Vector2(self.x, self.y)

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, i):
        return (self.x, self.y)[i]

    def __setitem__(self, i, v):
        if i in (0, -2):
            self.x = float(v)
        else:
            self.y = float(v)

    def __len__(self):
        return 2

    def __repr__(self):
        return "<Vector2(%g, %g)>" % (self.x, self.y)

    def __eq__(self, o):
        try:
            return abs(self.x - o[0]) < 1e-6 and abs(self.y - o[1]) < 1e-6
        except Exception:
            return False

    def __ne__(self, o):
        return not self.__eq__(o)

    __hash__ = None

    def __bool__(self):
        return self.x != 0.0 or self.y != 0.0

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __pos__(self):
        return Vector2(self.x, self.y)

    def __add__(self, o):
        return Vector2(self.x + o[0], self.y + o[1])

    __radd__ = __add__

    def __sub__(self, o):
        return Vector2(self.x - o[0], self.y - o[1])

    def __rsub__(self, o):
        return Vector2(o[0] - self.x, o[1] - self.y)

    def __mul__(self, o):
        if isinstance(o, (int, float)):
            return Vector2(self.x * o, self.y * o)
        return self.x * o[0] + self.y * o[1]

    __rmul__ = __mul__

    def __truediv__(self, k):
        return Vector2(self.x / k, self.y / k)

    def __floordiv__(self, k):
        return Vector2(self.x // k, self.y // k)

    def __iadd__(self, o):
        self.x += o[0]
        self.y += o[1]
        return self

    def __isub__(self, o):
        self.x -= o[0]
        self.y -= o[1]
        return self

    def __imul__(self, k):
        self.x *= k
        self.y *= k
        return self

    def __itruediv__(self, k):
        self.x /= k
        self.y /= k
        return self

    def length(self):
        return math.hypot(self.x, self.y)

    magnitude = length

    def length_squared(self):
        return self.x * self.x + self.y * self.y

    magnitude_squared = length_squared

    def normalize(self):
        n = self.length()
        if n == 0:
            raise ValueError("Can't normalize Vector of length zero")
        return Vector2(self.x / n, self.y / n)

    def normalize_ip(self):
        n = self.length()
        if n == 0:
            raise ValueError("Can't normalize Vector of length zero")
        self.x /= n
        self.y /= n

    def is_normalized(self):
        return abs(self.length_squared() - 1.0) < 1e-6

    def scale_to_length(self, n):
        cur = self.length()
        if cur == 0:
            raise ValueError("Cannot scale a vector with zero length")
        self.x *= n / cur
        self.y *= n / cur

    def dot(self, o):
        return self.x * o[0] + self.y * o[1]

    def cross(self, o):
        return self.x * o[1] - self.y * o[0]

    def rotate(self, deg):
        r = math.radians(deg)
        c, s = math.cos(r), math.sin(r)
        return Vector2(self.x * c - self.y * s, self.x * s + self.y * c)

    def rotate_ip(self, deg):
        v = self.rotate(deg)
        self.x, self.y = v.x, v.y

    def rotate_rad(self, r):
        return self.rotate(math.degrees(r))

    def lerp(self, o, t):
        return Vector2(self.x + (o[0] - self.x) * t, self.y + (o[1] - self.y) * t)

    def distance_to(self, o):
        return math.hypot(self.x - o[0], self.y - o[1])

    def distance_squared_to(self, o):
        return (self.x - o[0]) ** 2 + (self.y - o[1]) ** 2

    def angle_to(self, o):
        return math.degrees(math.atan2(o[1], o[0]) - math.atan2(self.y, self.x))

    def as_polar(self):
        return (self.length(), math.degrees(math.atan2(self.y, self.x)))

    def reflect(self, n):
        n = Vector2(n).normalize()
        d = self.dot(n)
        return Vector2(self.x - 2 * d * n.x, self.y - 2 * d * n.y)

    def elementwise(self):
        return self


def _rgba(c, opaque=False):
    if isinstance(c, int):
        c = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    c = tuple(max(0, min(255, int(v))) for v in c)
    if len(c) == 3:
        c = c + (255,)
    if opaque:
        c = c[:3] + (255,)
    return c


class Surface:
    def __init__(self, size, flags=0, depth=0, _im=None, _alpha=None):
        w, h = max(0, int(size[0])), max(0, int(size[1]))
        self.alpha = bool(flags & SRCALPHA) or depth == 32 if _alpha is None else _alpha
        if _im is not None:
            self.im = _im
        else:
            self.im = Image.new("RGBA", (max(1, w), max(1, h)), (0, 0, 0, 0 if self.alpha else 255))
        self._w, self._h = w, h
        self._surf_alpha = None
        self._clip = None
        self._colorkey = None

    def get_size(self):
        return (self._w, self._h)

    def get_width(self):
        return self._w

    def get_height(self):
        return self._h

    def get_rect(self, **kw):
        r = Rect(0, 0, self._w, self._h)
        for k, v in kw.items():
            setattr(r, k, v)
        return r

    def get_flags(self):
        return SRCALPHA if self.alpha else 0

    def get_bitsize(self):
        return 32

    def get_bounding_rect(self, min_alpha=1):
        bb = self.im.split()[3].point(lambda a: 255 if a >= min_alpha else 0).getbbox()
        if bb is None:
            return Rect(0, 0, 0, 0)
        return Rect(bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1])

    def _like(self, im, alpha=None):
        s = Surface(im.size, _im=im, _alpha=self.alpha if alpha is None else alpha)
        return s

    def copy(self):
        s = self._like(self.im.copy())
        s._surf_alpha = self._surf_alpha
        return s

    def convert(self, *a):
        im = self.im.copy()
        if self.alpha:
            bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
            bg.alpha_composite(im)
            im = bg
        return self._like(im, alpha=False)

    def convert_alpha(self, *a):
        return self._like(self.im.copy(), alpha=True)

    def subsurface(self, *a):
        r = Rect(*a) if len(a) != 1 else Rect(a[0])
        if r.x < 0 or r.y < 0 or r.right > self._w or r.bottom > self._h:
            raise ValueError("subsurface rectangle outside surface area")
        return self._like(self.im.crop((r.x, r.y, r.right, r.bottom)))

    def set_alpha(self, a=None, flags=0):
        self._surf_alpha = None if a is None else max(0, min(255, int(a)))

    def get_alpha(self):
        return self._surf_alpha

    def set_colorkey(self, c=None, flags=0):
        self._colorkey = c

    def get_colorkey(self):
        return self._colorkey

    def set_clip(self, r=None):
        if r is None:
            self._clip = None
        else:
            self._clip = Rect(r).clip(Rect(0, 0, self._w, self._h))

    def get_clip(self):
        return self._clip.copy() if self._clip is not None else Rect(0, 0, self._w, self._h)

    def lock(self):
        pass

    def unlock(self):
        pass

    def get_at(self, pos):
        x, y = int(pos[0]), int(pos[1])
        if not (0 <= x < self._w and 0 <= y < self._h):
            raise IndexError("pixel index out of range")
        return self.im.getpixel((x, y))

    def set_at(self, pos, c):
        x, y = int(pos[0]), int(pos[1])
        if 0 <= x < self._w and 0 <= y < self._h:
            self.im.putpixel((x, y), _rgba(c, not self.alpha))

    def fill(self, color, rect=None, special_flags=0):
        r = Rect(0, 0, self._w, self._h) if rect is None else Rect(rect).clip(Rect(0, 0, self._w, self._h))
        if self._clip is not None:
            r = r.clip(self._clip)
        if r.w <= 0 or r.h <= 0:
            return r
        box = (r.x, r.y, r.right, r.bottom)
        c = _rgba(color, not self.alpha and not special_flags)
        if not special_flags:
            self.im.paste(c, box)
            return r
        part = self.im.crop(box)
        rgb, a = part.convert("RGB"), part.split()[3]
        flat = Image.new("RGB", part.size, c[:3])
        if special_flags in (BLEND_RGB_MULT, BLEND_RGBA_MULT):
            rgb = ImageChops.multiply(rgb, flat)
            if special_flags == BLEND_RGBA_MULT:
                a = a.point(lambda v, k=c[3]: v * k // 255)
        elif special_flags in (BLEND_RGB_ADD, BLEND_RGBA_ADD):
            rgb = ImageChops.add(rgb, flat)
        elif special_flags == BLEND_RGB_SUB:
            rgb = ImageChops.subtract(rgb, flat)
        rgb.putalpha(a)
        self.im.paste(rgb, box)
        return r

    def blit(self, source, dest, area=None, special_flags=0):
        if isinstance(dest, Rect):
            dx, dy = dest.x, dest.y
        else:
            dx, dy = int(dest[0]), int(dest[1])
        src = source.im
        sw, sh = source._w, source._h
        sx0, sy0 = 0, 0
        if area is not None:
            a = Rect(area).clip(Rect(0, 0, sw, sh))
            sx0, sy0, sw, sh = a.x, a.y, a.w, a.h
        clip = self._clip if self._clip is not None else Rect(0, 0, self._w, self._h)
        x0, y0 = max(dx, clip.x), max(dy, clip.y)
        x1, y1 = min(dx + sw, clip.right), min(dy + sh, clip.bottom)
        out = Rect(dx, dy, sw, sh)
        if x1 <= x0 or y1 <= y0:
            return out
        box = (sx0 + x0 - dx, sy0 + y0 - dy, sx0 + x1 - dx, sy0 + y1 - dy)
        piece = src.crop(box) if box != (0, 0) + src.size else src
        if special_flags in (BLEND_RGB_ADD, BLEND_RGBA_ADD, BLEND_RGB_MULT, BLEND_RGBA_MULT):
            under = self.im.crop((x0, y0, x1, y1))
            rgb, al = under.convert("RGB"), under.split()[3]
            if special_flags in (BLEND_RGB_ADD, BLEND_RGBA_ADD):
                rgb = ImageChops.add(rgb, piece.convert("RGB"))
            else:
                rgb = ImageChops.multiply(rgb, piece.convert("RGB"))
                if special_flags == BLEND_RGBA_MULT:       # real pygame multiplies alpha too
                    pa = piece.split()[3] if piece.mode == "RGBA" else Image.new("L", piece.size, 255)
                    al = ImageChops.multiply(al, pa)
            rgb.putalpha(al)
            self.im.paste(rgb, (x0, y0))
            return out
        if source._surf_alpha is not None and source._surf_alpha < 255:
            piece = piece.copy()
            k = source._surf_alpha
            if source.alpha:
                piece.putalpha(piece.split()[3].point(lambda v: v * k // 255))
            else:
                piece.putalpha(k)
            self.im.alpha_composite(piece, (x0, y0))
        elif source.alpha:
            self.im.alpha_composite(piece, (x0, y0))
        else:
            self.im.paste(piece, (x0, y0))
        return out

    def blits(self, seq, doreturn=True):
        return [self.blit(*item) for item in seq]

    def scroll(self, dx=0, dy=0):
        self.im = ImageChops.offset(self.im, dx, dy)

    def save_png(self, path):
        self.im.convert("RGB").save(path)


SurfaceType = Surface


class _Draw:
    @staticmethod
    def _begin(surface):
        keep = None
        if surface._clip is not None and (surface._clip.w, surface._clip.h) != (surface._w, surface._h):
            keep = surface.im.copy()
        return ImageDraw.Draw(surface.im), keep

    @staticmethod
    def _end(surface, keep):
        if keep is not None:
            c = surface._clip
            inside = surface.im.crop((c.x, c.y, c.right, c.bottom))
            surface.im = keep
            surface.im.paste(inside, (c.x, c.y))

    @staticmethod
    def _col(surface, color):
        return _rgba(color, not surface.alpha)

    def rect(self, surface, color, rect, width=0, border_radius=0, **kw):
        r = Rect(rect)
        if r.w <= 0 or r.h <= 0:
            return r
        d, keep = self._begin(surface)
        c = self._col(surface, color)
        box = [r.x, r.y, r.right - 1, r.bottom - 1]
        rad = max(0, int(border_radius))
        rad = min(rad, r.w // 2, r.h // 2)
        w = int(width)
        if rad > 0:
            if w > 0:
                d.rounded_rectangle(box, rad, outline=c, width=min(w, max(1, min(r.w, r.h) // 2)))
            else:
                d.rounded_rectangle(box, rad, fill=c)
        else:
            if w > 0:
                d.rectangle(box, outline=c, width=min(w, max(1, min(r.w, r.h) // 2)))
            else:
                d.rectangle(box, fill=c)
        self._end(surface, keep)
        return r

    def circle(self, surface, color, center, radius, width=0, **kw):
        cx, cy, rad = int(center[0]), int(center[1]), int(radius)
        if rad <= 0:
            return Rect(cx, cy, 0, 0)
        d, keep = self._begin(surface)
        c = self._col(surface, color)
        box = [cx - rad, cy - rad, cx + rad - 1, cy + rad - 1]
        if width and int(width) > 0:
            d.ellipse(box, outline=c, width=min(int(width), rad))
        else:
            d.ellipse(box, fill=c)
        self._end(surface, keep)
        return Rect(cx - rad, cy - rad, rad * 2, rad * 2)

    def ellipse(self, surface, color, rect, width=0):
        r = Rect(rect)
        if r.w <= 0 or r.h <= 0:
            return r
        d, keep = self._begin(surface)
        c = self._col(surface, color)
        box = [r.x, r.y, r.right - 1, r.bottom - 1]
        if width and int(width) > 0:
            d.ellipse(box, outline=c, width=min(int(width), max(1, min(r.w, r.h) // 2)))
        else:
            d.ellipse(box, fill=c)
        self._end(surface, keep)
        return r

    def arc(self, surface, color, rect, start, stop, width=1):
        r = Rect(rect)
        if r.w <= 0 or r.h <= 0:
            return r
        d, keep = self._begin(surface)
        d.arc([r.x, r.y, r.right - 1, r.bottom - 1], -math.degrees(stop), -math.degrees(start),
              fill=self._col(surface, color), width=max(1, int(width)))
        self._end(surface, keep)
        return r

    def polygon(self, surface, color, points, width=0):
        pts = [(float(p[0]), float(p[1])) for p in points]
        if len(pts) < 3:
            raise ValueError("points argument must contain more than 2 points")
        d, keep = self._begin(surface)
        c = self._col(surface, color)
        if width and int(width) > 0:
            d.line(pts + [pts[0]], fill=c, width=int(width), joint="curve")
        else:
            d.polygon(pts, fill=c)
        self._end(surface, keep)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)

    def line(self, surface, color, a, b, width=1):
        d, keep = self._begin(surface)
        d.line([(float(a[0]), float(a[1])), (float(b[0]), float(b[1]))], fill=self._col(surface, color),
               width=max(1, int(width)))
        self._end(surface, keep)
        return Rect(min(a[0], b[0]), min(a[1], b[1]), abs(a[0] - b[0]) + 1, abs(a[1] - b[1]) + 1)

    def lines(self, surface, color, closed, points, width=1):
        pts = [(float(p[0]), float(p[1])) for p in points]
        if len(pts) < 2:
            raise ValueError("points argument must contain 2 or more points")
        if closed:
            pts = pts + [pts[0]]
        d, keep = self._begin(surface)
        d.line(pts, fill=self._col(surface, color), width=max(1, int(width)))
        self._end(surface, keep)
        return Rect(0, 0, 0, 0)

    aaline = line
    aalines = lines


draw = _Draw()


class _Transform:
    @staticmethod
    def _sized(surface, size, how, dest=None):
        w, h = max(0, int(size[0])), max(0, int(size[1]))
        im = surface.im.resize((max(1, w), max(1, h)), how)
        if dest is not None:
            if dest.get_size() != (w, h):
                raise ValueError("Destination surface not the given width or height.")
            dest.im = im
            dest.alpha = surface.alpha
            return dest
        s = Surface((w, h), _im=im, _alpha=surface.alpha)
        s._w, s._h = w, h
        return s

    def scale(self, surface, size, dest_surface=None):
        return self._sized(surface, size, Image.NEAREST, dest_surface)

    def smoothscale(self, surface, size, dest_surface=None):
        w, h = max(1, int(size[0])), max(1, int(size[1]))
        shrink = w < surface._w or h < surface._h
        return self._sized(surface, size, Image.BOX if shrink else Image.BILINEAR, dest_surface)

    def scale_by(self, surface, k):
        return self.scale(surface, (surface._w * k, surface._h * k))

    def rotate(self, surface, angle):
        im = surface.im
        if not surface.alpha:
            im = im.copy()
        out = im.rotate(angle, resample=Image.NEAREST, expand=True,
                        fillcolor=(0, 0, 0, 0) if surface.alpha else (0, 0, 0, 255))
        return Surface(out.size, _im=out, _alpha=surface.alpha)

    def rotozoom(self, surface, angle, scale):
        s = self.smoothscale(surface, (surface._w * scale, surface._h * scale))
        out = s.im.rotate(angle, resample=Image.BILINEAR, expand=True)
        return Surface(out.size, _im=out, _alpha=True)

    def flip(self, surface, xbool, ybool):
        im = surface.im
        if xbool:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        if ybool:
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
        if not (xbool or ybool):
            im = im.copy()
        return Surface(im.size, _im=im, _alpha=surface.alpha)


transform = _Transform()

_FACE = None
for _p in ("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    if os.path.exists(_p):
        _FACE = _p
        break


class Font:
    def __init__(self, name=None, size=20):
        self._px = max(1, int(int(size) * 0.6875)) if name is None else max(1, int(size))
        self._f = ImageFont.truetype(_FACE, self._px) if _FACE else ImageFont.load_default()
        try:
            self._asc, self._desc = self._f.getmetrics()
        except Exception:
            self._asc, self._desc = self._px, self._px // 4
        self.bold = False

    def set_bold(self, b):
        self.bold = bool(b)

    def get_height(self):
        return self._asc + self._desc

    def get_linesize(self):
        return int((self._asc + self._desc) * 1.15)

    def get_ascent(self):
        return self._asc

    def get_descent(self):
        return -self._desc

    def size(self, text):
        return (int(math.ceil(self._f.getlength(str(text)))) + (1 if self.bold else 0), self.get_height())

    def render(self, text, antialias=True, color=(255, 255, 255), background=None):
        text = str(text)
        w, h = self.size(text)
        s = Surface((max(1, w), h), SRCALPHA)
        if background is not None:
            s.im.paste(_rgba(background), (0, 0, s.im.width, s.im.height))
        if text:
            d = ImageDraw.Draw(s.im)
            d.text((0, 0), text, font=self._f, fill=_rgba(color))
            if self.bold:
                d.text((1, 0), text, font=self._f, fill=_rgba(color))
        return s

    def metrics(self, text):
        return [(0, int(self._f.getlength(ch)), -self._desc, self._asc, int(self._f.getlength(ch))) for ch in text]


class _FontModule:
    Font = Font

    @staticmethod
    def init():
        pass

    @staticmethod
    def get_init():
        return True

    @staticmethod
    def SysFont(name, size, bold=False, italic=False):
        f = Font(None, size)
        f.set_bold(bold)
        return f

    @staticmethod
    def get_default_font():
        return "freesansbold.ttf"

    @staticmethod
    def match_font(*a, **k):
        return _FACE


font = _FontModule()


class _ImageModule:
    @staticmethod
    def load(path, namehint=""):
        if not isinstance(path, (str, bytes, os.PathLike)):
            im = Image.open(path)
        else:
            if not os.path.exists(path):
                raise FileNotFoundError("No file '%s' found in working directory." % path)
            im = Image.open(path)
        im = im.convert("RGBA")
        return Surface(im.size, _im=im, _alpha=True)

    @staticmethod
    def save(surface, path):
        surface.im.save(path)

    @staticmethod
    def get_extended():
        return True


image = _ImageModule()


class _Time:
    def __init__(self):
        self.ms = 0.0

    def get_ticks(self):
        return int(self.ms)

    def advance(self, ms):
        self.ms += ms

    def wait(self, ms):
        self.ms += ms
        return ms

    delay = wait

    def Clock(self):
        return _Clock(self)


class _Clock:
    def __init__(self, t):
        self._t = t
        self._last = 16.0

    def tick(self, fps=0):
        step = 1000.0 / fps if fps else 1000.0 / 60.0
        self._t.ms += step
        self._last = step
        return int(round(step))

    tick_busy_loop = tick

    def get_time(self):
        return int(self._last)

    def get_fps(self):
        return 1000.0 / self._last


time = _Time()


class Event:
    def __init__(self, type, dict=None, **kw):
        self.type = type
        d = {}
        d.update(dict or {})
        d.update(kw)
        self.__dict__.update(d)

    @property
    def dict(self):
        return {k: v for k, v in self.__dict__.items() if k != "type"}

    def __repr__(self):
        return "<Event(%s %s)>" % (self.type, self.dict)


class _EventModule:
    Event = Event

    def __init__(self):
        self.queue = []

    def get(self, *a, **k):
        q, self.queue = self.queue, []
        return q

    def post(self, e):
        self.queue.append(e)

    def pump(self):
        pass

    def clear(self, *a):
        self.queue = []

    def set_allowed(self, *a):
        pass

    def set_blocked(self, *a):
        pass


event = _EventModule()


class _Mouse:
    def __init__(self):
        self.pos = (0, 0)
        self.down = (False, False, False)

    def get_pos(self):
        return self.pos

    def set_pos(self, *a):
        self.pos = tuple(a[0]) if len(a) == 1 else (a[0], a[1])

    def get_pressed(self, num_buttons=3):
        return self.down

    def set_visible(self, v):
        return True

    def get_rel(self):
        return (0, 0)

    def set_cursor(self, *a):
        pass


mouse = _Mouse()


class _Keys(dict):
    def __missing__(self, k):
        return False


class _Key:
    def __init__(self):
        self.held = _Keys()

    def get_pressed(self):
        return self.held

    def get_mods(self):
        return 0

    def set_repeat(self, *a):
        pass

    def name(self, k):
        return chr(k) if 0 < k < 256 else str(k)

    def start_text_input(self):
        pass

    def stop_text_input(self):
        pass


key = _Key()


class _Display:
    def __init__(self):
        self.surface = None
        self.caption = ""

    def set_mode(self, size=(0, 0), flags=0, depth=0, display=0, vsync=0):
        self.surface = Surface(size)
        return self.surface

    def get_surface(self):
        return self.surface

    def flip(self):
        pass

    update = flip

    def set_caption(self, title, icon=""):
        self.caption = title

    def get_caption(self):
        return (self.caption, self.caption)

    def toggle_fullscreen(self):
        return 1

    def set_icon(self, s):
        pass

    def init(self):
        pass

    def quit(self):
        pass

    def get_init(self):
        return True

    def Info(self):
        return types.SimpleNamespace(current_w=1920, current_h=1080)

    def get_window_size(self):
        return self.surface.get_size() if self.surface else (0, 0)


display = _Display()


class Sound:
    played = []

    def __init__(self, file=None, buffer=None):
        self.file = file
        self._vol = 1.0

    def play(self, loops=0, maxtime=0, fade_ms=0):
        Sound.played.append(self.file)
        return None

    def stop(self):
        pass

    def fadeout(self, ms):
        pass

    def set_volume(self, v):
        self._vol = v

    def get_volume(self):
        return self._vol

    def get_length(self):
        return 1.0

    def get_num_channels(self):
        return 0


class _Music:
    def __init__(self):
        self.track = None
        self.playing = False

    def load(self, path):
        if not os.path.exists(path):
            raise error("No file '%s'" % path)
        self.track = path

    def play(self, loops=0, start=0.0, fade_ms=0):
        self.playing = True

    def stop(self):
        self.playing = False

    def pause(self):
        pass

    def unpause(self):
        pass

    def fadeout(self, ms):
        self.playing = False

    def set_volume(self, v):
        pass

    def get_volume(self):
        return 1.0

    def get_busy(self):
        return self.playing

    def get_pos(self):
        return 0

    def set_pos(self, p):
        pass

    def unload(self):
        self.track = None

    def set_endevent(self, *a):
        pass


class _Mixer:
    Sound = Sound

    def __init__(self):
        self.music = _Music()

    def pre_init(self, *a, **k):
        pass

    def init(self, *a, **k):
        pass

    def quit(self):
        pass

    def get_init(self):
        return (44100, -16, 2)

    def set_num_channels(self, n):
        pass

    def get_num_channels(self):
        return 8

    def stop(self):
        pass

    def pause(self):
        pass

    def unpause(self):
        pass

    def find_channel(self, force=False):
        return None


mixer = _Mixer()

math_module = types.SimpleNamespace(Vector2=Vector2)
version = types.SimpleNamespace(ver="2.6.0-shim", vernum=(2, 6, 0), SDL=(2, 0, 0))
Color = lambda *a: _rgba(a[0] if len(a) == 1 else a)


def init():
    return (6, 0)


def quit():
    pass


def get_init():
    return True


def get_sdl_version():
    return (2, 0, 0)


sys.modules.setdefault("pygame.math", types.SimpleNamespace(Vector2=Vector2))
