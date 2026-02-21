"""
Sistema de partículas encapsulado (sustituye _PARTS global).
"""
import pygame
import math
import random


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "col", "life", "ml", "sz")

    def __init__(self, x, y, vx, vy, col, life, sz):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.col, self.life, self.ml, self.sz = col, life, life, sz

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.13
        self.vx *= 0.93
        self.life -= 1

    def draw(self, surf, ox, oy, W, H):
        if self.life <= 0:
            return
        ratio = self.life / self.ml
        sz = max(1, int(self.sz * ratio))
        sx, sy = int(self.x - ox), int(self.y - oy)
        if -16 < sx < W + 16 and -16 < sy < H + 16:
            rc, gc, bc = self.col
            pygame.draw.circle(
                surf,
                (int(rc * ratio), int(gc * ratio), int(bc * ratio)),
                (sx, sy),
                sz,
            )


class ParticleSystem:
    def __init__(self):
        self._parts = []

    def spawn(self, x, y, col, n=8, sp=3, life=28, sz=4):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            s = random.uniform(sp * 0.3, sp)
            self._parts.append(
                Particle(x, y, math.cos(ang) * s, math.sin(ang) * s, col, life, sz)
            )

    def update(self):
        for i in range(len(self._parts) - 1, -1, -1):
            self._parts[i].update()
            if self._parts[i].life <= 0:
                self._parts.pop(i)

    def draw(self, surf, ox, oy, W, H):
        for p in self._parts:
            p.draw(surf, ox, oy, W, H)

    def clear(self):
        self._parts.clear()
