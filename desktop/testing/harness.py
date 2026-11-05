"""Boots the real game on the Pillow stand-in for pygame: no window, no sound, same code.
Everything it writes (saves, screenshots) goes in testing/out, never in the game folder."""
import builtins, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(os.path.dirname(HERE), "game")   # the game folder, next to this one
sys.path.insert(0, os.path.join(HERE, "shim"))
sys.path.insert(1, ROOT)
_print = builtins.print
def _quiet(*a, **k):
    if a and isinstance(a[0], str) and a[0].startswith("[ragdoll_football]"):
        return
    _print(*a, **k)
builtins.print = _quiet
import pygame
assert getattr(pygame, "IS_SHIM", False)
import ragdoll_football as rf
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

class Run:
    def __init__(self, save=None, name="save_test.json", keep=False, headless=False):
        rf.SAVE_PATH = os.path.join(OUT, name)
        if not keep and os.path.exists(rf.SAVE_PATH):
            os.remove(rf.SAVE_PATH)
        if save is not None:
            with open(rf.SAVE_PATH, "w") as fh:
                json.dump(save, fh)
        pygame.init()
        self.screen = pygame.display.set_mode((rf.WIDTH, rf.HEIGHT))
        self.g = rf.Game(headless=headless, screen=self.screen)
        self.g.input_lock = 0.0
    def frames(self, n=1, dt=1 / 60.0, draw=False):
        for _ in range(n):
            pygame.time.advance(dt * 1000.0)
            self.g.handle_events()
            self.g.update(dt)
            if draw:
                self.g.draw()
    def click(self, x, y=None, settle=30):
        if y is None:
            x, y = x
        self.frames(settle)
        pygame.mouse.pos = (int(x), int(y))
        self.g.pointer = (int(x), int(y))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(int(x), int(y)), button=1))
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(int(x), int(y)), button=1))
        self.frames(2)
    def hover(self, x, y):
        pygame.mouse.pos = (int(x), int(y))
        self.g.pointer = (int(x), int(y))
    def key(self, k):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=k, unicode=""))
        pygame.event.post(pygame.event.Event(pygame.KEYUP, key=k))
        self.frames(2)
    def shot(self, name, half=True, toasts=False):
        if not toasts:
            self.g.toasts = []
        self.g.draw()
        path = os.path.join(OUT, name + ".png")
        im = self.screen.im.convert("RGB")
        if half:
            im = im.resize((rf.WIDTH // 2, rf.HEIGHT // 2))
        im.save(path)
        return path
