"""
drone_sprites.py — NEUROCALIPSIS
══════════════════════════════════
Carga el spritesheet del drone y provee get_frame().
Solo afecta al drone — el resto del juego no se toca.

Guardar la imagen como:  images/drone_sprites.png

Animaciones detectadas (spritesheet 1536×1024):
  Fila 1  FLY   (movimiento normal)   — 6 frames,  y=145..354
  Fila 2  SHOOT (disparo / carga)     — 6 frames,  y=400..614
  Fila 3  LASER (láser extendido)     — 6 frames,  y=715..984
"""

import pygame
import os
import sys
import math

def _resource_base():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _resource_base()

# ── Coordenadas en el spritesheet  (x, y, ancho, alto) ───────────────────────
# Medidas automáticamente — ajusta si ves desplazamiento
_FLY_RECTS = [
    ( 85, 145, 218, 210),
    (303, 145, 218, 210),
    (521, 145, 218, 210),
    (739, 145, 218, 210),
    (957, 145, 218, 210),
    (1175, 145, 218, 210),
]
_SHOOT_RECTS = [
    ( 64, 400, 221, 215),
    (285, 400, 221, 215),
    (506, 400, 221, 215),
    (727, 400, 221, 215),
    (948, 400, 221, 215),
    (1169, 400, 221, 215),
]
_LASER_RECTS = [
    ( 72, 715, 231, 270),
    (303, 715, 231, 270),
    (534, 715, 231, 270),
    (765, 715, 231, 270),
    (996, 715, 231, 270),
    (1227, 715, 231, 270),
]

# ── Tamaño final en pantalla ──────────────────────────────────────────────────
# El drone tiene collider 30×22 en el juego; el sprite lo dibujamos más grande
# para que se vea bien. Ajusta a gusto.
RENDER_W = 90
RENDER_H = 62

# ── Estado interno ────────────────────────────────────────────────────────────
_sheet:     pygame.Surface | None = None
_fly:       list = []   # [(frame_right, frame_left), …]
_shoot:     list = []
_laser:     list = []
_ready:     bool = False


# ── Carga y compilación ───────────────────────────────────────────────────────
def _crop(x: int, y: int, w: int, h: int) -> pygame.Surface:
    """Recorta un frame del sheet con clipping defensivo y lo escala."""
    if _sheet is None:
        return pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
    sw, sh = _sheet.get_size()
    x = max(0, min(x, sw - 1));  w = min(w, sw - x)
    y = max(0, min(y, sh - 1));  h = min(h, sh - y)
    if w <= 0 or h <= 0:
        return pygame.Surface((RENDER_W, RENDER_H), pygame.SRCALPHA)
    crop = _sheet.subsurface(pygame.Rect(x, y, w, h)).copy()
    return pygame.transform.smoothscale(crop, (RENDER_W, RENDER_H))


def _build(rects: list) -> list:
    return [(_crop(*r), pygame.transform.flip(_crop(*r), True, False)) for r in rects]


def init() -> None:
    """
    Llama esto una vez, DESPUÉS de pygame.display.set_mode().
    Si la imagen no existe, el drone usa su dibujo procedural original.
    """
    global _sheet, _fly, _shoot, _laser, _ready

    path = os.path.join(BASE_DIR, "images", "drone_sprites.png")
    if not os.path.isfile(path):
        print("⚠️  drone_sprites.png no encontrado — drone usará dibujo procedural")
        return

    try:
        _sheet = pygame.image.load(path).convert_alpha()
        print(f"✅ drone_sprites.png cargado: {_sheet.get_size()}")
    except Exception as exc:
        print(f"⚠️  Error cargando drone_sprites.png: {exc}")
        return

    _fly   = _build(_FLY_RECTS)
    _shoot = _build(_SHOOT_RECTS)
    _laser = _build(_LASER_RECTS)
    _ready = True
    print(f"✅ Drone sprites compilados: fly={len(_fly)}, shoot={len(_shoot)}, laser={len(_laser)}")


# ── API pública ───────────────────────────────────────────────────────────────
def get_frame(anim_t: int, attack_t: int, at_cd: int, facing: int) -> pygame.Surface | None:
    """
    Devuelve el Surface correcto según el estado del drone.
    Retorna None si los sprites no están disponibles.

    Lógica de animación:
      · Si attack_t > at_cd * 0.6  → LASER  (disparo activo, láser extendido)
      · Si attack_t > 0             → SHOOT  (cargando / disparando)
      · En cualquier otro caso      → FLY    (movimiento normal)

    facing: 1 = mira derecha, -1 = mira izquierda
    """
    if not _ready:
        return None

    side = 0 if facing >= 0 else 1  # 0=right, 1=left

    # Selección de animación según estado de ataque
    if attack_t > at_cd * 0.5:
        frames = _laser
        tpf    = 5          # ticks por frame (más rápido al disparar)
    elif attack_t > 0:
        frames = _shoot
        tpf    = 7
    else:
        frames = _fly
        tpf    = 8

    if not frames:
        return None

    idx = (anim_t // tpf) % len(frames)
    return frames[idx][side]