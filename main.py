"""
╔══════════════════════════════════════════════════════════╗
║   NEUROCALIPSIS: El Último Fragmento                    ║
║   Metroidvania 2D — Pygame                              ║
║                                                          ║
║   Instalar: pip install pygame                           ║
║   Ejecutar: python neurocalipsis.py                      ║
║                                                          ║
║   CONTROLES:                                             ║
║   A / D         → Mover                                 ║
║   SPACE / W     → Saltar                                ║
║   J             → Katana (combo x3)                     ║
║   K o Click Izq → Pistola (apunta al cursor)            ║
║   L             → Descarga Neural (ralentiza enemigos)   ║
║   R             → Recargar munición                      ║
║   ESC           → Pausa   Q (en pausa) = Salir            ║
║   TAB           → Menú habilidades   F1 = Debug          ║
║   SHIFT         → Dash (si desbloqueado)                  ║
╚══════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import math
import random
import json
import os

import effects
from particles import ParticleSystem
import abilities as ab
import minimap as mm
from data.load_stats import get_enemy_stats
import drone_sprites  # ← sprites del drone

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

DEBUG = False  # F1 para toggle
TILE_CELL = 128  # celdas para grid de colisión de balas
pygame.display.set_caption("NEUROCALIPSIS: El Último Fragmento")

# ─────────────────────────────────────────────────────────
# CONSTANTES GLOBALES
# ─────────────────────────────────────────────────────────
FPS  = 60
GRAV = 0.58
FALL_DEATH_Y = 2000  # Si el jugador cae por debajo de esta Y, muere

# Paleta cyberpunk
BG1      = (4,   4,  14)
CYAN     = (0,  230, 220)
PINK     = (255,  0, 120)
PURPLE   = (170,  0, 255)
WHITE    = (210, 225, 255)
RED      = (255,  55,  55)
ORANGE   = (255, 150,  30)
GOLD     = (255, 205,   0)
GREEN    = (40,  255, 100)
DARKBLUE = (10,  20,  40)
GREY     = (80,  90, 110)
DKGREY   = (20,  25,  35)

# Pantalla completa (resolución nativa del monitor)
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = screen.get_size()
clock  = pygame.time.Clock()

# Inicializar sprites del drone (después de set_mode para que convert_alpha funcione)
drone_sprites.init()

# ─────────────────────────────────────────────────────────
# CARGAR SONIDOS
# ─────────────────────────────────────────────────────────
# Base para recursos: al compilar con PyInstaller los datos están en sys._MEIPASS
def _resource_base():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _resource_base()

print(f"📁 Directorio actual: {BASE_DIR}")
print(f"🔊 Buscando sonido en: {os.path.join(BASE_DIR, 'sounds', 'slash.wav')}")
print(f"🔊 ¿Existe el archivo? {os.path.exists(os.path.join(BASE_DIR, 'sounds', 'slash.wav'))}")

try:
    SND_SLASH = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "slash.wav"))
    SND_SLASH.set_volume(0.6)
    print("✅ Sonido de espada cargado correctamente")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo de sonido: sounds/slash.wav")
    SND_SLASH = None
except Exception as e:
    print(f"⚠️ Error al cargar el sonido: {e}")
    SND_SLASH = None

# Cargar sonido de descarga neural (tecla L)
print(f"🔊 Buscando sonido de descarga en: {os.path.join(BASE_DIR, 'sounds', 'neural.wav')}")
print(f"🔊 ¿Existe el archivo de descarga? {os.path.exists(os.path.join(BASE_DIR, 'sounds', 'neural.wav'))}")

try:
    SND_NEURAL = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "neural.wav"))
    SND_NEURAL.set_volume(0.8)
    print("✅ Sonido de descarga neural cargado correctamente")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo de sonido: sounds/neural.wav")
    SND_NEURAL = None
except Exception as e:
    print(f"⚠️ Error al cargar el sonido de descarga: {e}")
    SND_NEURAL = None

# Cargar sonido de pistola (tecla K)
print(f"🔊 Buscando sonido de pistola en: {os.path.join(BASE_DIR, 'sounds', 'shoot.wav')}")
print(f"🔊 ¿Existe el archivo de pistola? {os.path.exists(os.path.join(BASE_DIR, 'sounds', 'shoot.wav'))}")

try:
    SND_SHOOT = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "shoot.wav"))
    SND_SHOOT.set_volume(0.5)
    print("✅ Sonido de pistola cargado correctamente")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo de sonido: sounds/shoot.wav")
    SND_SHOOT = None
except Exception as e:
    print(f"⚠️ Error al cargar el sonido de pistola: {e}")
    SND_SHOOT = None

# Cargar sonido de recarga (tecla R)
print(f"🔊 Buscando sonido de recarga en: {os.path.join(BASE_DIR, 'sounds', 'reload.wav')}")
print(f"🔊 ¿Existe el archivo de recarga? {os.path.exists(os.path.join(BASE_DIR, 'sounds', 'reload.wav'))}")

try:
    SND_RELOAD = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "reload.wav"))
    SND_RELOAD.set_volume(0.6)
    print("✅ Sonido de recarga cargado correctamente")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo de sonido: sounds/reload.wav")
    SND_RELOAD = None
except Exception as e:
    print(f"⚠️ Error al cargar el sonido de recarga: {e}")
    SND_RELOAD = None

# Cargar sonido de salto (SPACE / W / UP)
print(f"🔊 Buscando sonido de salto en: {os.path.join(BASE_DIR, 'sounds', 'jump.wav')}")
print(f"🔊 ¿Existe el archivo de salto? {os.path.exists(os.path.join(BASE_DIR, 'sounds', 'jump.wav'))}")

try:
    SND_JUMP = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "jump.wav"))
    SND_JUMP.set_volume(0.5)
    print("✅ Sonido de salto cargado correctamente")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo de sonido: sounds/jump.wav")
    SND_JUMP = None
except Exception as e:
    print(f"⚠️ Error al cargar el sonido de salto: {e}")
    SND_JUMP = None

# Cargar sonido de muerte (game over)
print(f"🔊 Buscando sonido de muerte en: {os.path.join(BASE_DIR, 'sounds', 'game_over.wav')}")
print(f"🔊 ¿Existe el archivo? {os.path.exists(os.path.join(BASE_DIR, 'sounds', 'game_over.wav'))}")

try:
    SND_GAME_OVER = pygame.mixer.Sound(os.path.join(BASE_DIR, "sounds", "game_over.wav"))
    SND_GAME_OVER.set_volume(0.7)
    print("✅ Sonido de muerte cargado correctamente")
except FileNotFoundError:
    print("⚠️ No se encontró el archivo de sonido: sounds/game_over.wav")
    SND_GAME_OVER = None
except Exception as e:
    print(f"⚠️ Error al cargar el sonido de muerte: {e}")
    SND_GAME_OVER = None

    # Cargar música de fondo
MUSIC_PATH = os.path.join(BASE_DIR, "sounds", "background_music.wav")
print(f"🔊 Buscando música de fondo en: {MUSIC_PATH}")
print(f"🔊 ¿Existe el archivo? {os.path.exists(MUSIC_PATH)}")

try:
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.set_volume(0.3)  # Volumen más bajo para no tapar efectos
    print("✅ Música de fondo cargada correctamente")
except Exception as e:
    print(f"⚠️ Error al cargar la música de fondo: {e}")

# Imágenes de items (ponlas en una carpeta assets/ o images/)
def load_item_images():
    images = {}
    try:
        img_hp = pygame.image.load(os.path.join(BASE_DIR, "assets", "Health.png")).convert_alpha()
        img_hp = pygame.transform.scale(img_hp, (52, 52))
        images["health"] = img_hp
    except Exception:
        images["health"] = None

    try:
        img_am = pygame.image.load(os.path.join(BASE_DIR, "assets", "Ammo.png")).convert_alpha()
        img_am = pygame.transform.scale(img_am, (52, 52))
        images["ammo"] = img_am
    except Exception:
        images["ammo"] = None

    return images

ITEM_IMAGES = load_item_images()

# ─────────────────────────────────────────────────────────
# SPRITES JUGADOR (reemplaza dibujo procedural)
# ─────────────────────────────────────────────────────────
def _load_image_from_images(*names):
    for n in names:
        p = os.path.join(BASE_DIR, "images", n)
        if os.path.isfile(p):
            return pygame.image.load(p).convert_alpha()
    raise FileNotFoundError(
        f"No encontré el spritesheet en /images. Probé: {names}"
    )

def _make_player_frame(sheet, rect: pygame.Rect, canvas_w: int, canvas_h: int, scale: float, min_alpha: int = 10):
    """
    1) Corta el rect
    2) Encuentra el bounding box real (sin basurita de alpha bajo)
    3) Pega en un CANVAS FIJO alineando al piso (bottom) y centrado
    4) Escala con UN SOLO factor (scale) para que no "respire" ni tiemble
    """
    bounds = sheet.get_rect()
    rect = rect.clip(bounds)
    if rect.width <= 0 or rect.height <= 0:
        out = pygame.Surface((max(1, int(canvas_w * scale)), max(1, int(canvas_h * scale))), pygame.SRCALPHA)
        return out
    crop = sheet.subsurface(rect).copy()

    try:
        br = crop.get_bounding_rect(min_alpha=min_alpha)
    except TypeError:
        br = crop.get_bounding_rect()
    if br.w <= 0 or br.h <= 0:
        br = crop.get_rect()

    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)

    dx = (canvas_w - br.w) // 2          # centrado horizontal
    dy = canvas_h - br.h                  # alineado al piso (bottom)

    canvas.blit(crop, (dx, dy), area=br)

    out_w = max(1, int(canvas_w * scale))
    out_h = max(1, int(canvas_h * scale))
    return pygame.transform.smoothscale(canvas, (out_w, out_h))

# Carga con fallback por si el nombre está mal escrito
_player_sheet = _load_image_from_images("spites.png", "spirtes.png", "sprites.png")

# ─────────────────────────────────────────────────────────
# COORDENADAS PARA EL NUEVO SPRITESHEET (1024x1536)
# Layout detectado:
# RUN   : y 0..324    (6 frames)
# IDLE  : y 325..614  (6 frames)
# SLASH : y 615..937  (3 frames)
# SHOOT : y 938..1254 (5 frames)  (la fila 5 se ignora)
# ─────────────────────────────────────────────────────────

SHEET_W, SHEET_H = _player_sheet.get_width(), _player_sheet.get_height()

RUN_Y0,   RUN_H   = 0,   325
IDLE_Y0,  IDLE_H  = 325, 290
SLASH_Y0, SLASH_H = 615, 323
SHOOT_Y0, SHOOT_H = 938, 317

# Rangos X (x0, x1) por frame — ajustados para NO coger los textos
RUN_X = [
    (73, 201), (201, 379), (379, 537),
    (537, 722), (722, 871), (871, 1003),
]
IDLE_X = [
    (82, 223), (223, 366), (366, 498),
    (498, 632), (632, 769), (769, 982),
]
SLASH_X = [
    (121, 336), (336, 552), (552, 846),
]
# OJO: el frame 1 de SHOOT tiene el arma muy hacia la izquierda, por eso empieza en 110
SHOOT_X = [
    (110, 238), (238, 415), (415, 600),
    (600, 783), (783, 1002),
]

# Canvas fijo (para estabilidad, sin jitter)
_all_widths = [x1 - x0 for (x0, x1) in (RUN_X + IDLE_X + SLASH_X + SHOOT_X)]
SRC_CANVAS_W = max(_all_widths) + 2          # +2 por seguridad
SRC_CANVAS_H = max(RUN_H, IDLE_H, SLASH_H, SHOOT_H)

# Tamaño final del personaje (ajústalo a gusto)
PLAYER_SPRITE_H = 96
SPR_SCALE = PLAYER_SPRITE_H / SRC_CANVAS_H

def _build_frames(x_ranges, y0, h):
    return [
        _make_player_frame(
            _player_sheet,
            pygame.Rect(x0, y0, (x1 - x0), h),
            SRC_CANVAS_W,
            SRC_CANVAS_H,
            SPR_SCALE
        )
        for (x0, x1) in x_ranges
    ]

SPR_RUN_R   = _build_frames(RUN_X,   RUN_Y0,   RUN_H)
SPR_IDLE_R  = _build_frames(IDLE_X,  IDLE_Y0,  IDLE_H)
SPR_SLASH_R = _build_frames(SLASH_X, SLASH_Y0, SLASH_H)
SPR_SHOOT_R = _build_frames(SHOOT_X, SHOOT_Y0, SHOOT_H)

SPR_RUN_L   = [pygame.transform.flip(s, True, False) for s in SPR_RUN_R]
SPR_IDLE_L  = [pygame.transform.flip(s, True, False) for s in SPR_IDLE_R]
SPR_SLASH_L = [pygame.transform.flip(s, True, False) for s in SPR_SLASH_R]
SPR_SHOOT_L = [pygame.transform.flip(s, True, False) for s in SPR_SHOOT_R]

# Dimensiones fijas (ya no cambian entre frames)
PLAYER_FRAME_W = SPR_RUN_R[0].get_width()
PLAYER_FRAME_H = SPR_RUN_R[0].get_height()

try:
    FNT_BIG = pygame.font.SysFont("consolas", 52, bold=True)
    FNT_MED = pygame.font.SysFont("consolas", 30, bold=True)
    FNT_SM  = pygame.font.SysFont("consolas", 19)
    FNT_XS  = pygame.font.SysFont("consolas", 14)
except Exception:
    FNT_BIG = FNT_MED = FNT_SM = FNT_XS = pygame.font.Font(None, 28)


# ─────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────
def lerp(a, b, t):    return a + (b - a) * t
def clamp(v, lo, hi): return max(lo, min(hi, v))

def txt(surf, text, font, color, x, y, shadow=True):
    if shadow:
        s = font.render(text, True, (0, 0, 0))
        surf.blit(s, (x + 2, y + 2))
    surf.blit(font.render(text, True, color), (x, y))

def bar(surf, x, y, w, h, pct, fg, bg=DKGREY, border=CYAN, label=""):
    pct = clamp(pct, 0, 1)
    pygame.draw.rect(surf, bg,     (x, y, w, h),          border_radius=3)
    if pct > 0:
        pygame.draw.rect(surf, fg, (x, y, int(w*pct), h), border_radius=3)
    pygame.draw.rect(surf, border, (x, y, w, h), 1,       border_radius=3)
    if label:
        surf.blit(FNT_XS.render(label, True, WHITE), (x + 3, y + 1))

def glow_circle(surf, color, cx, cy, radius, alpha=70):
    s = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    r, g, b = color
    for i in range(3):
        a   = alpha // (i + 1)
        rad = radius + i * 4
        pygame.draw.circle(s, (r, g, b, a), (radius * 2, radius * 2), rad)
    surf.blit(s, (cx - radius * 2, cy - radius * 2),
              special_flags=pygame.BLEND_RGBA_ADD)
    
def glow_buble(surf, color, cx, cy, radius, alpha=70):
    s = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    r, g, b = color

    # Rellena el centro completamente transparente
    # y dibuja el borde degradado de afuera hacia adentro
    num_rings = 12
    for i in range(num_rings):
        ratio = i / num_rings          # 0 = exterior, 1 = interior
        rad = max(1, int(radius * (1 - ratio * 0.35)))
        a = int(alpha * (1 - ratio))   # alfa va de 'alpha' a 0
        pygame.draw.circle(s, (r, g, b, a),
                           (radius * 2, radius * 2),
                           rad, max(2, radius // num_rings))

    # Sin BLEND_RGBA_ADD para que el alpha funcione correctamente
    surf.blit(s, (cx - radius * 2, cy - radius * 2))


# ─────────────────────────────────────────────────────────
# PARTÍCULAS (sistema encapsulado)
# ─────────────────────────────────────────────────────────
particle_system = ParticleSystem()

def spawn(x, y, col, n=8, sp=3, life=28, sz=4):
    particle_system.spawn(x, y, col, n, sp, life, sz)

def update_particles():
    particle_system.update()

def draw_particles(surf, ox, oy):
    particle_system.draw(surf, ox, oy, W, H)


def build_tile_grid(tiles, cell_size=TILE_CELL):
    """Devuelve dict (cx, cy) -> lista de rects para colisión rápida de balas."""
    grid = {}
    for t in tiles:
        cx_min = t.left // cell_size
        cx_max = t.right // cell_size
        cy_min = t.top // cell_size
        cy_max = t.bottom // cell_size
        for cx in range(cx_min, cx_max + 1):
            for cy in range(cy_min, cy_max + 1):
                key = (cx, cy)
                if key not in grid:
                    grid[key] = []
                grid[key].append(t)
    return grid


# ─────────────────────────────────────────────────────────
# PROYECTILES
# ─────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, dx, dy, dmg, col, speed, owner):
        n = math.hypot(dx, dy) or 1
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = dx/n*speed, dy/n*speed
        self.dmg, self.col, self.owner = dmg, col, owner
        self.alive = True

    def update(self, tile_grid):
        self.x += self.vx
        self.y += self.vy
        if not (-50 < self.x < 9000 and -300 < self.y < 2000):
            self.alive = False
            return
        cx, cy = int(self.x) // TILE_CELL, int(self.y) // TILE_CELL
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                key = (cx + dx, cy + dy)
                for t in tile_grid.get(key, []):
                    if t.collidepoint(self.x, self.y):
                        self.alive = False
                        spawn(self.x, self.y, self.col, 5, 2, 12, 3)
                        return

    def draw(self, surf, ox, oy):
        sx, sy = int(self.x - ox), int(self.y - oy)
        if -12 < sx < W + 12 and -12 < sy < H + 12:
            # Ángulo de la dirección del disparo
            angle = math.degrees(math.atan2(self.vy, self.vx))

            # Dimensiones del rectángulo (largo x ancho)
            bw, bh = 18, 6

            # Crear superficie temporal con alpha para rotar
            bsurf = pygame.Surface((bw + 4, bh + 4), pygame.SRCALPHA)
            r, g, b = self.col

            # Glow suave detrás
            pygame.draw.rect(bsurf, (r, g, b, 60),
                            (0, 0, bw + 4, bh + 4),
                            border_radius=(bh + 4) // 2)

            # Rectángulo principal con puntas redondeadas
            pygame.draw.rect(bsurf, (r, g, b, 220),
                            (2, 2, bw, bh),
                            border_radius=bh // 2)

            # Núcleo blanco brillante en el centro
            pygame.draw.rect(bsurf, (255, 255, 255, 180),
                            (4, 3, bw - 4, bh - 2),
                            border_radius=(bh - 2) // 2)

            # Rotar según dirección
            rotated = pygame.transform.rotate(bsurf, -angle)
            rw, rh = rotated.get_size()
            surf.blit(rotated, (sx - rw // 2, sy - rh // 2))


# ─────────────────────────────────────────────────────────
# EFECTO DE CORTE DE KATANA
# ─────────────────────────────────────────────────────────
class SlashEffect:
    def __init__(self, cx, cy, facing, dmg):
        self.cx, self.cy = cx, cy
        self.facing      = facing
        self.dmg         = dmg
        self.life = self.max_life = 16
        self.alive   = True
        self.hit_ids = set()

    @property
    def rect(self):
        w, h = 68, 52
        ox = self.cx + self.facing * 34 - w / 2
        return pygame.Rect(int(ox), int(self.cy - h/2), w, h)

    def update(self):
        self.life -= 1
        if self.life <= 0: self.alive = False

    def draw(self, surf, ox, oy):
        ratio = self.life / self.max_life
        cx = int(self.cx - ox)
        cy = int(self.cy - oy)

        r_outer = int(62 * ratio)
        r_inner = int(36 * ratio)

        if r_outer < 2 or r_inner < 2:
            return

        # facing=1 = derecha (0°), facing=-1 = izquierda (180°)
        base = 0.0 if self.facing == 1 else math.pi
        spread = math.radians(65)
        n = 18

        outer = []
        for i in range(n + 1):
            ang = base - spread + (2 * spread * i / n)
            outer.append((
                cx + int(math.cos(ang) * r_outer),
                cy + int(math.sin(ang) * r_outer)
            ))

        inner = []
        for i in range(n + 1):
            ang = base + spread - (2 * spread * i / n)
            inner.append((
                cx + int(math.cos(ang) * r_inner),
                cy + int(math.sin(ang) * r_inner)
            ))

        pts = outer + inner
        if len(pts) < 3:
            return

        s = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        alpha = int(200 * ratio)
        r, g, b = CYAN

        pygame.draw.polygon(s, (r, g, b, alpha // 3), pts)
        pygame.draw.lines(s, (r, g, b, alpha), False, outer, 3)
        pygame.draw.lines(s, (r, g, b, alpha // 2), False, inner, 2)

        surf.blit(s, (0, 0))

        glow_circle(surf, CYAN, outer[0][0],      outer[0][1],      7, int(90 * ratio))
        glow_circle(surf, CYAN, outer[-1][0],     outer[-1][1],     7, int(90 * ratio))
        #glow_circle(surf, CYAN, outer[n//2][0],   outer[n//2][1],   7, int(90 * ratio))

# ─────────────────────────────────────────────────────────
# JUGADOR – SAKÍ KISHIMOTO
# ─────────────────────────────────────────────────────────
class Player:
    PW, PH = 30, 52

    def __init__(self, x, y):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.facing      = 1
        self.on_ground   = False

        self.hp = self.max_hp = 150
        self.ammo = self.max_ammo = 30
        self.xp = 0
        self.level = 1
        self.xp_to_next = 100

        self.slash_cd  = 0
        self.shoot_cd  = 0
        self.neural_cd = 0
        self.hurt_t    = 0
        self.inv_t     = 0
        self.neural_t  = 0
        self.levelup_t = 0
        self.combo     = 0
        self.combo_t   = 0
        self.dead      = False

        self.slash_effects = []
        self.walk_t  = 0
        self.walk_fr = 0
        self.abilities = dict(ab.DEFAULT_ABILITIES)
        self.jumps_left = 1
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.on_wall = False
        self.wall_side = 0
        self.show_ability_menu = False
        self.land_t = 0
        self.anim_t = 0
        self.was_on_ground = True
        self.fall_timer = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.PW, self.PH)

    @property
    def cx(self):
        return self.x + self.PW / 2

    @property
    def cy(self):
        return self.y + self.PH / 2

    def take_damage(self, d):
        if self.inv_t > 0 or self.neural_t > 0:
            return
        self.hp = max(0, self.hp - d)
        self.hurt_t = 20
        self.inv_t = 50
        if self.hp == 0:
            self.dead = True
            # Reproducir sonido de muerte
            if 'SND_GAME_OVER' in globals() and SND_GAME_OVER:
                SND_GAME_OVER.play()
                print("💀 ¡Personaje muerto!")

    def gain_xp(self, xp):
        self.xp += xp
        leveled = False
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.6)
            self.max_hp += 25
            self.hp = min(self.hp + 40, self.max_hp)
            self.max_ammo += 5
            spawn(self.cx, self.cy, GOLD, 22, 5, 55, 7)
            self.levelup_t = 130
            leveled = True
        ab.check_unlocks(self.level, self.abilities)
        return leveled

    def do_slash(self):
        if self.slash_cd > 0:
            return
        self.combo = (self.combo % 3) + 1
        self.combo_t = 35
        dmg = int((50 + (self.level-1)*8) * (1.7 if self.combo == 3 else 1.0))
        self.slash_effects.append(SlashEffect(self.cx, self.cy, self.facing, dmg))
        spawn(self.cx + self.facing*42, self.cy, CYAN, 10, 4, 20, 4)
        self.slash_cd = 20

        # Reproducir sonido de espada
        if 'SND_SLASH' in globals() and SND_SLASH:
            SND_SLASH.play()

    def do_shoot(self, wmx, wmy):
        if self.shoot_cd > 0 or self.ammo <= 0:
            return None
        self.ammo -= 1
        self.shoot_cd = 14
        dx = wmx - self.cx
        dy = wmy - self.cy
        spawn(self.cx + self.facing*18, self.cy, CYAN, 4, 3, 10, 3)

        # Reproducir sonido de pistola
        if 'SND_SHOOT' in globals() and SND_SHOOT:
            SND_SHOOT.play()
            print("🔫 ¡Disparo!")

        return Bullet(self.cx, self.cy, dx, dy, 22+(self.level-1)*4, CYAN, 14, "player")

    def do_neural(self):
        if self.neural_cd > 0:
            return
        self.neural_t = 200
        self.neural_cd = 600
        spawn(self.cx, self.cy, PURPLE, 30, 6, 65, 7)

        # Reproducir sonido de descarga neural
        if 'SND_NEURAL' in globals() and SND_NEURAL:
            SND_NEURAL.play()
            print("⚡ ¡Descarga Neural activada!")

    def update(self, keys, tiles):
        for attr in ("slash_cd", "shoot_cd", "neural_cd", "hurt_t", "inv_t",
                     "neural_t", "combo_t", "levelup_t", "dash_timer", "dash_cooldown"):
            setattr(self, attr, max(0, getattr(self, attr, 0) - 1))

        if self.on_ground:
            self.jumps_left = 2 if ab.has_ability(self.abilities, ab.ABILITY_DOUBLE_JUMP) else 1

        self.on_wall = False
        self.wall_side = 0
        r = self.rect
        for t in tiles:
            if r.colliderect(t):
                continue
            if self.vy != 0 or not self.on_ground:
                if self.x + self.PW <= t.left and t.left - (self.x + self.PW) < 8 and t.top < self.y + self.PH and t.bottom > self.y:
                    self.on_wall = True
                    self.wall_side = -1
                if self.x >= t.right and self.x - t.right < 8 and t.top < self.y + self.PH and t.bottom > self.y:
                    self.on_wall = True
                    self.wall_side = 1

        mv = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mv = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mv = 1
        if mv:
            self.facing = mv
            if self.dash_timer <= 0:
                self.vx = lerp(self.vx, mv * 5.6, 0.22)
            self.walk_t += 1
            # Faster animation when dashing, normal otherwise
            step = 4 if self.dash_timer > 0 else 6
            if self.walk_t % step == 0:
                self.walk_fr = (self.walk_fr + 1) % len(SPR_RUN_R)
        else:
            if self.dash_timer <= 0:
                self.vx = lerp(self.vx, 0, 0.18)
            self.walk_t = 0   # reset so run starts cleanly from frame 0

        if self.dash_timer > 0:
            self.vx = self.facing * 14
            self.vy *= 0.5
        elif ab.has_ability(self.abilities, ab.ABILITY_DASH) and self.dash_cooldown <= 0 and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            self.dash_timer = 12
            self.dash_cooldown = 45
            spawn(self.cx, self.cy, PURPLE, 8, 4, 18, 3)

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]):
            if self.on_ground:
                self.vy = -14.2
                self.on_ground = False
                self.jumps_left -= 1
                spawn(self.cx, self.y + self.PH, CYAN, 6, 2, 14, 3)
                # Reproducir sonido de salto
                if 'SND_JUMP' in globals() and SND_JUMP:
                    SND_JUMP.play()
                    print("🦶 ¡Salto!")
            elif ab.has_ability(self.abilities, ab.ABILITY_DOUBLE_JUMP) and self.jumps_left > 0 and self.dash_timer <= 0:
                self.vy = -14.2
                self.jumps_left -= 1
                spawn(self.cx, self.cy, GOLD, 10, 3, 20, 4)
                # Reproducir sonido de doble salto
                if 'SND_JUMP' in globals() and SND_JUMP:
                    SND_JUMP.play()
                    print("🦶 ¡Doble salto!")
            elif ab.has_ability(self.abilities, ab.ABILITY_WALL_JUMP) and self.on_wall and self.dash_timer <= 0:
                self.vy = -13
                self.vx = -self.wall_side * 10
                self.facing = -self.wall_side
                self.on_wall = False
                spawn(self.cx, self.cy, CYAN, 8, 3, 16, 3)
                # Reproducir sonido de salto de pared
                if 'SND_JUMP' in globals() and SND_JUMP:
                    SND_JUMP.play()
                    print("🧱 ¡Salto de pared!")

        self.vy = min(self.vy + GRAV, 18)

        # mover X + colisión
        self.x += self.vx
        r = self.rect
        for t in tiles:
            if r.colliderect(t):
                if self.vx > 0:
                    self.x = t.left - self.PW
                else:
                    self.x = t.right
                self.vx = 0
                r = self.rect

        # mover Y + colisión
        self.y += self.vy
        self.on_ground = False
        r = self.rect
        for t in tiles:
            if r.colliderect(t):
                if self.vy > 0:
                    self.y = t.top - self.PH
                    self.on_ground = True
                else:
                    self.y = t.bottom
                self.vy = 0
                r = self.rect

        # Limitar X para que no salga del mapa
        self.x = max(0.0, min(self.x, 9000 - self.PW))

        # Detectar caída al vacío
        if self.y > FALL_DEATH_Y:
            self.dead = True
            spawn(self.cx, self.y, RED, 20, 8, 40, 8)
            # Reproducir sonido de muerte por caída
            if 'SND_GAME_OVER' in globals() and SND_GAME_OVER:
                SND_GAME_OVER.play()
                print("💀 ¡Caída al vacío!")

        if self.on_ground:
            if not self.was_on_ground and self.vy >= 0:
                self.land_t = 14
            self.land_t = max(0, self.land_t - 1)
        else:
            self.land_t = 0
        self.was_on_ground = self.on_ground
        self.anim_t += 1

        for se in self.slash_effects[:]:
            se.update()
            if not se.alive:
                self.slash_effects.remove(se)

    def draw(self, surf, ox, oy):
        rx, ry = int(self.x - ox), int(self.y - oy)

        # Blink cuando recibe daño
        if self.hurt_t > 0 and (self.hurt_t // 3) % 2 == 0:
            return

        # Selección de animación
        facing_left = self.facing < 0

        # Prioridad: slash > shoot > aire > run > idle
        if self.slash_cd > 0:
            t = 20 - self.slash_cd
            idx = min(len(SPR_SLASH_R) - 1, t // 7)
            frame = (SPR_SLASH_L if facing_left else SPR_SLASH_R)[idx]

        elif self.shoot_cd > 0:
            t = 14 - self.shoot_cd
            idx = min(len(SPR_SHOOT_R) - 1, t // 3)
            frame = (SPR_SHOOT_L if facing_left else SPR_SHOOT_R)[idx]

        elif not self.on_ground:
            # Going up → arms up pose (frame 0), falling → slightly leaned (frame 2)
            air_idx = 0 if self.vy < -2 else (2 if self.vy > 3 else 1)
            frame = (SPR_IDLE_L if facing_left else SPR_IDLE_R)[air_idx]

        elif abs(self.vx) > 0.6:
            frame = (SPR_RUN_L if facing_left else SPR_RUN_R)[self.walk_fr % len(SPR_RUN_R)]

        else:
            idx = (self.anim_t // 10) % len(SPR_IDLE_R)
            frame = (SPR_IDLE_L if facing_left else SPR_IDLE_R)[idx]

        # Aura neural (detrás del sprite)
        if self.neural_t > 0:
            glow_buble(surf, PURPLE, rx + self.PW // 2, ry + self.PH  // 3, 52, 55)

        # Dibujar alineando "pies" con el collider
        px = rx + self.PW // 2 - PLAYER_FRAME_W // 2
        py = ry + self.PH - PLAYER_FRAME_H
        surf.blit(frame, (px, py))

        # Dibujar efectos de slash
        for se in self.slash_effects:
            se.draw(surf, ox, oy)


# ─────────────────────────────────────────────────────────
# ENEMIGOS
# ─────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y, etype, lv=1):
        self.x, self.y   = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.facing      = 1
        self.on_ground   = False
        self.etype       = etype
        self.alive       = True
        self.hurt_t      = 0
        self.attack_t    = 0
        self.shoot_t     = 0
        self.patrol_t    = 0
        self.aggro_r     = 380
        self.phase       = 1
        self.attack_windup = 0
        self.anim_t      = 0
        sc = lv - 1
        stats = get_enemy_stats()
        st = stats.get(etype)

        if st:
            self.w = st.get("w", 30)
            self.h = st.get("h", 40)
            self.hp = self.max_hp = st.get("base_hp", 50) + sc * st.get("hp_per_level", 15)
            self.speed = st.get("speed_base", 2) + sc * st.get("speed_per_level", 0.2)
            self.xp_val = st.get("xp_base", 20) + sc * st.get("xp_per_level", 5)
            self.col = tuple(st.get("color", [100, 100, 100]))
            self.at_r = st.get("at_r", 40)
            self.dmg = st.get("dmg_base", 10) + sc * st.get("dmg_per_level", 2)
            self.at_cd = st.get("at_cd", 60)
            if etype == "drone":
                self.bob = random.uniform(0, math.tau)
        elif etype == "infectado":
            self.w, self.h = 26, 42
            self.hp = self.max_hp = 65 + sc*22
            self.speed = 2.3 + sc*0.3
            self.xp_val = 20 + sc*6
            self.col = (90, 120, 155)   # steel-blue android (was muddy reddish)
            self.at_r = 34
            self.dmg = 12+sc*3
            self.at_cd = 62
        elif etype == "drone":
            self.w, self.h = 30, 22
            self.hp = self.max_hp = 48 + sc*16
            self.speed = 2.8 + sc*0.4
            self.xp_val = 32 + sc*8
            self.col = (90, 90, 245)
            self.at_r = 350
            self.dmg = 14+sc*3
            self.at_cd = 88
            self.bob = random.uniform(0, math.tau)
        elif etype == "mutante":
            self.w, self.h = 44, 64
            self.hp = self.max_hp = 185 + sc*55
            self.speed = 1.05 + sc*0.15
            self.xp_val = 62 + sc*16
            self.col = (120, 60, 28)
            self.at_r = 54
            self.dmg = 28+sc*6
            self.at_cd = 82
        elif etype == "jefe":
            self.w, self.h = 78, 96
            self.hp = self.max_hp = 650 + sc*120
            self.speed = 1.6
            self.xp_val = 350
            self.col = (60, 0, 130)
            self.at_r = 78
            self.dmg = 38+sc*6
            self.at_cd = 68
        else:
            self.w, self.h = 26, 42
            self.hp = self.max_hp = 50 + sc*15
            self.speed = 2.0 + sc*0.2
            self.xp_val = 20 + sc*5
            self.col = (100, 100, 100)
            self.at_r = 40
            self.dmg = 10 + sc*2
            self.at_cd = 60

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def take_damage(self, d):
        self.hp -= d
        self.hurt_t = 14
        spawn(self.cx, self.cy, PINK, 8, 4, 20, 4)
        if self.hp <= 0:
            self.alive = False
            spawn(self.cx, self.cy, self.col, 20, 5, 40, 6)
            return self.xp_val
        return 0

    def update(self, player, tiles, bullets_list):
        self.hurt_t = max(0, self.hurt_t - 1)
        self.attack_t = max(0, self.attack_t - 1)
        self.shoot_t = max(0, self.shoot_t - 1)
        self.anim_t += 1

        dx = player.cx - self.cx
        dy = player.cy - self.cy
        dist = math.hypot(dx, dy)
        self.slowed = player.neural_t > 0 and dist < self.aggro_r
        slow = 0.35 if player.neural_t > 0 else 1.0

        # ── DRONE (flotante) ──────────────────────────────
        if self.etype == "drone":
            t = pygame.time.get_ticks() * 0.002
            self.y += math.sin(t + self.bob) * 0.45
            if dist < self.aggro_r:
                tvx = (dx/dist)*self.speed*slow if dist > 2 else 0
                self.vx = lerp(self.vx, tvx, 0.07)
                self.facing = 1 if dx >= 0 else -1
            else:
                self.vx *= 0.9
            self.x += self.vx
            if dist < self.at_r and self.attack_t <= 0:
                bullets_list.append(
                    Bullet(self.cx, self.cy, dx, dy, self.dmg, (90, 90, 245), 8, "enemy"))
                self.attack_t = self.at_cd
            return

        # ── ENEMIGOS CON GRAVEDAD ─────────────────────────
        self.vy += GRAV

        if dist < self.aggro_r:
            self.facing = 1 if dx >= 0 else -1
            if abs(dx) > self.at_r:
                self.vx = self.facing * self.speed * slow
                self.attack_windup = 0
            else:
                self.vx *= 0.7
                if self.attack_t <= 0 and self.attack_windup <= 0:
                    self.attack_t = self.at_cd
                    self.attack_windup = 22
                if self.attack_windup > 0:
                    self.attack_windup -= 1
                elif self.attack_windup == 0:
                    player.take_damage(self.dmg)
                    effects.trigger_shake(is_melee_hit=True)
                    spawn(player.cx, player.cy, RED, 7, 4, 20)
                    self.attack_windup = -1
                if self.attack_windup == -1 and self.attack_t <= 0:
                    self.attack_windup = 0
            # jefe fase 2: dispara
            if self.etype == "jefe" and self.phase >= 2 and self.shoot_t <= 0:
                bullets_list.append(
                    Bullet(self.cx, self.cy, dx, dy, 18, PURPLE, 9, "enemy"))
                bullets_list.append(
                    Bullet(self.cx, self.cy, dx+60, dy, 18, PURPLE, 9, "enemy"))
                self.shoot_t = 42
        else:
            self.patrol_t += 1
            self.vx = self.facing * self.speed * 0.45
            if self.patrol_t > 160:
                self.patrol_t = 0
                self.facing *= -1

        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.86
        self.on_ground = False

        r = self.rect
        for t in tiles:
            if r.colliderect(t):
                if self.vy > 0 and self.y + self.h - self.vy <= t.y + 5:
                    self.y = t.y - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = t.y + t.h
                    self.vy = 0
                elif self.vx > 0:
                    self.x = t.x - self.w
                    self.vx = -self.vx*0.3
                    self.facing *= -1
                elif self.vx < 0:
                    self.x = t.x + self.w
                    self.vx = -self.vx*0.3
                    self.facing *= -1
                r = self.rect

        # ── Edge detection: don't walk off ledges (ground enemies only) ──────
        if self.on_ground and self.etype != "drone":
            probe_x = (self.x + self.w + 4) if self.vx > 0 else (self.x - 4)
            probe_y = self.y + self.h + 6
            has_floor = any(t.collidepoint(probe_x, probe_y) for t in tiles)
            if not has_floor:
                self.facing *= -1
                self.vx *= -1

        if self.etype == "jefe" and self.hp < self.max_hp * 0.5:
            self.phase = 2

    def draw(self, surf, ox, oy):
        rx, ry = int(self.x - ox), int(self.y - oy)
        if rx < -120 or rx > W + 120:
            return
        col = RED if self.hurt_t > 0 else self.col
        if getattr(self, "slowed", False):
            r, g, b = col
            col = (min(255, r + 80), min(255, g + 20), min(255, b + 120))
            pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01)
            col = (int(col[0] * pulse), int(col[1] * pulse), min(255, int(col[2] * 1.2)))

        t = self.anim_t * 0.08
        atk_raise = 0
        if getattr(self, "attack_windup", 0) > 0:
            atk_raise = (1 - self.attack_windup / 22.0) * 12

        if self.etype == "infectado":
            sway   = int(math.sin(t) * 1.5)
            moving = abs(self.vx) > 0.5
            leg_f  = math.sin(t * 1.9) * 6  if moving else 0
            arm_f  = math.sin(t * 1.9 + math.pi) * 5 if moving else 0
            atk_glow = getattr(self, "attack_windup", 0) > 0

            # Lighter accent colour
            light = (min(255, col[0]+55), min(255, col[1]+55), min(255, col[2]+65))
            dim   = (max(0, col[0]-25),   max(0, col[1]-20),   max(0, col[2]-20))

            # ── Legs ──────────────────────────────────────────
            foot_l = (rx + 5 + int( leg_f), ry + self.h - 2)
            foot_r = (rx + self.w - 5 - int(leg_f), ry + self.h - 2)
            knee_l = (rx + 7 + sway, ry + 28)
            knee_r = (rx + self.w - 7 + sway, ry + 28)
            pygame.draw.line(surf, dim,   knee_l, foot_l, 4)
            pygame.draw.line(surf, dim,   knee_r, foot_r, 4)
            pygame.draw.rect(surf, light, (foot_l[0]-4, foot_l[1]-2, 8, 4), border_radius=2)
            pygame.draw.rect(surf, light, (foot_r[0]-4, foot_r[1]-2, 8, 4), border_radius=2)

            # ── Pelvis / hip connector ─────────────────────────
            pygame.draw.rect(surf, dim, (rx + 5 + sway, ry + 26, self.w - 10, 6), border_radius=2)

            # ── Torso ─────────────────────────────────────────
            pygame.draw.rect(surf, col,  (rx + 4 + sway, ry + 17, self.w - 8, 12), border_radius=3)
            # Chest core crystal (glows when attacking)
            core_c = PINK if atk_glow else (180, 30, 50)
            pygame.draw.rect(surf, core_c, (rx + self.w//2 - 3 + sway, ry + 19, 6, 6), border_radius=2)
            if atk_glow:
                glow_circle(surf, PINK,  rx + self.w//2 + sway, ry + 22, 7, 110)
            else:
                glow_circle(surf, core_c, rx + self.w//2 + sway, ry + 22, 4, 50)
            # Trim line
            pygame.draw.line(surf, light, (rx + 5 + sway, ry + 18), (rx + self.w - 5 + sway, ry + 18), 1)

            # ── Shoulder armour ────────────────────────────────
            pygame.draw.rect(surf, light, (rx      + sway, ry + 16, 7, 8), border_radius=2)
            pygame.draw.rect(surf, light, (rx + self.w - 7 + sway, ry + 16, 7, 8), border_radius=2)

            # ── Arms ──────────────────────────────────────────
            arm_ty = ry + 19
            hand_l = (rx - 1 + sway, arm_ty + 9 + int(arm_f))
            hand_r = (rx + self.w + 1 + sway, arm_ty + 9 - int(arm_f))
            pygame.draw.line(surf, dim, (rx + 3 + sway, arm_ty), hand_l, 3)
            pygame.draw.line(surf, dim, (rx + self.w - 3 + sway, arm_ty), hand_r, 3)
            pygame.draw.circle(surf, light, hand_l, 3)
            pygame.draw.circle(surf, light, hand_r, 3)

            # ── Neck ──────────────────────────────────────────
            pygame.draw.rect(surf, dim, (rx + 10 + sway, ry + 12, 6, 6))

            # ── Head ──────────────────────────────────────────
            head_y = ry + 2 - int(atk_raise)
            pygame.draw.rect(surf, col, (rx + 4 + sway, head_y, self.w - 8, 12), border_radius=4)
            # Visor band
            v_col = (255, 50, 50) if atk_glow else (170, 30, 35)
            pygame.draw.rect(surf, v_col, (rx + 5 + sway, head_y + 4, self.w - 10, 5), border_radius=2)
            # Individual LED eyes
            ex = rx + (7 if self.facing > 0 else self.w - 11) + sway
            pygame.draw.rect(surf, (255, 240, 180), (ex,     head_y + 5, 3, 3))
            pygame.draw.rect(surf, (255, 240, 180), (ex + 4, head_y + 5, 3, 3))
            eye_intensity = 90 if atk_glow else 45
            glow_circle(surf, (255, 80, 50), ex + 1,     head_y + 6, 4, eye_intensity)
            glow_circle(surf, (255, 80, 50), ex + 5,     head_y + 6, 4, eye_intensity)
            # Antenna
            ant_x = rx + self.w // 2 + sway
            pygame.draw.line(surf, CYAN, (ant_x, head_y), (ant_x, head_y - 6), 1)
            pygame.draw.circle(surf, CYAN, (ant_x, head_y - 6), 2)
            glow_circle(surf, CYAN, ant_x, head_y - 6, 3, 50)

        elif self.etype == "drone":
            frame = drone_sprites.get_frame(self.anim_t, self.attack_t, self.at_cd, self.facing)
            if frame is not None:
                # Tinte rojo al recibir daño
                if self.hurt_t > 0 and (self.hurt_t // 3) % 2 == 0:
                    frame = frame.copy()
                    frame.fill((200, 0, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
                # Tinte púrpura cuando está ralentizado (descarga neural)
                if getattr(self, "slowed", False):
                    frame = frame.copy()
                    frame.fill((70, 0, 140, 0), special_flags=pygame.BLEND_RGB_ADD)
                fw, fh = frame.get_size()
                # Centrar sobre el collider del drone
                draw_x = rx + self.w // 2 - fw // 2
                draw_y = ry + self.h // 2 - fh // 2
                surf.blit(frame, (draw_x, draw_y))
            else:
                # Fallback procedural si no hay sprite
                cx2, cy2 = rx + self.w//2, ry + self.h//2
                rot = (self.anim_t * 2) % 360
                pts = [(cx2+int(14*math.cos(math.radians(a+rot))),
                        cy2+int(9 * math.sin(math.radians(a+rot)))) for a in range(0, 360, 60)]
                bob = int(math.sin(t) * 2)
                pts = [(p[0], p[1] + bob) for p in pts]
                col = RED if self.hurt_t > 0 else self.col
                pygame.draw.polygon(surf, col, pts)
                pygame.draw.polygon(surf, CYAN, pts, 2)
                pygame.draw.circle(surf, CYAN, (cx2, cy2 + bob), 4)
                glow_circle(surf, CYAN, cx2, cy2 + bob, 12, 55)

        elif self.etype == "mutante":
            moving = abs(self.vx) > 0.4
            leg_f  = math.sin(t * 1.5) * 8 if moving else 0
            arm_sw = math.sin(t * 1.5 + math.pi) * 10 if moving else 0
            atk_glow = getattr(self, "attack_windup", 0) > 0
            breath = 1.0 + 0.04 * math.sin(t)
            light = (min(255, col[0]+45), min(255, col[1]+35), min(255, col[2]+20))
            dim   = (max(0, col[0]-20),   max(0, col[1]-15),   max(0, col[2]-10))

            # Legs — thick powerful limbs
            pygame.draw.line(surf, dim, (rx+14, ry+self.h-22), (rx+8+int(leg_f),  ry+self.h-2), 7)
            pygame.draw.line(surf, dim, (rx+30, ry+self.h-22), (rx+36-int(leg_f), ry+self.h-2), 7)
            pygame.draw.rect(surf, light, (rx+4+int(leg_f),   ry+self.h-6, 10, 6), border_radius=3)
            pygame.draw.rect(surf, light, (rx+30-int(leg_f),  ry+self.h-6, 10, 6), border_radius=3)

            # Main body
            bw, bh = int((self.w - 6) * breath), self.h - 28
            bx = rx + 3 - (bw - (self.w - 6)) // 2
            pygame.draw.rect(surf, col,  (bx, ry + 28, bw, bh), border_radius=5)
            # Belly segments
            for i in range(3):
                seg_y = ry + 32 + i * 10
                pygame.draw.line(surf, dim, (bx + 3, seg_y), (bx + bw - 3, seg_y), 1)

            # Shoulder pads (wide)
            pygame.draw.rect(surf, light, (rx - 2, ry + 22, 12, 10), border_radius=3)
            pygame.draw.rect(surf, light, (rx + self.w - 10, ry + 22, 12, 10), border_radius=3)

            # Arms (heavy, swinging)
            pygame.draw.line(surf, col, (rx + 4,          ry + 24), (rx - 6,          ry + 38 + int(arm_sw)), 6)
            pygame.draw.line(surf, col, (rx + self.w - 4, ry + 24), (rx + self.w + 6, ry + 38 - int(arm_sw)), 6)
            # Fists / claws
            claw_l = (rx - 8,          ry + 38 + int(arm_sw))
            claw_r = (rx + self.w + 8, ry + 38 - int(arm_sw))
            for dx2, dy2 in [(-3,-3),(0,-4),(3,-3)]:
                pygame.draw.line(surf, ORANGE, claw_l, (claw_l[0]+dx2, claw_l[1]+dy2+(-5 if atk_glow else 0)), 2)
                pygame.draw.line(surf, ORANGE, claw_r, (claw_r[0]-dx2, claw_r[1]+dy2+(-5 if atk_glow else 0)), 2)

            # Head (larger, brutish)
            pygame.draw.circle(surf, col, (rx + self.w // 2, ry + 22), int(18 * breath))
            # Bony spikes on head
            for i, sx2 in enumerate([rx+self.w//2-14, rx+self.w//2, rx+self.w//2+14]):
                h_spk = 8 + i % 2 * 4
                pygame.draw.polygon(surf, ORANGE, [(sx2-4, ry+10),(sx2+4, ry+10),(sx2, ry+10-h_spk)])
            # Eyes — three (creepy)
            ec = RED if atk_glow else (200, 30, 30)
            for ex_off in (-8, 0, 8):
                pygame.draw.circle(surf, ec, (rx + self.w//2 + ex_off, ry + 20), 3)
                if atk_glow:
                    glow_circle(surf, RED, rx + self.w//2 + ex_off, ry + 20, 5, 100)
                else:
                    glow_circle(surf, ec,  rx + self.w//2 + ex_off, ry + 20, 3, 40)
            # Mouth gash
            pygame.draw.line(surf, (200, 0, 0), (rx + self.w//2 - 8, ry + 26), (rx + self.w//2 + 8, ry + 26), 2)

        elif self.etype == "jefe":
            pulse = 0.85 + 0.15 * math.sin(t * 1.5)
            r_glow = int(55 * pulse)
            glow_circle(surf, PURPLE, rx+self.w//2, ry+self.h//2, r_glow, 70)
            breath = 1.0 + 0.03 * math.sin(t)
            pygame.draw.rect(surf, col, (rx, ry+32, self.w, self.h-32), border_radius=8)
            pygame.draw.circle(surf, col, (rx+self.w//2, ry+30), int(32 * breath))
            ec = PURPLE if self.phase < 2 else PINK
            for off in (-12, 12):
                pygame.draw.circle(surf, ec, (rx+self.w//2+off, ry+26), 6)
                glow_circle(surf, ec, rx+self.w//2+off, ry+26, 12, 130)
            for i in range(4):
                cy_ = ry + 44 + i*12
                pygame.draw.line(surf, PURPLE, (rx+8, cy_), (rx+self.w-8, cy_), 1)

        # HP bar — always drawn on top, color-coded by type
        hp_pct  = self.hp / self.max_hp
        bar_col = {
            "jefe":     PURPLE,
            "mutante":  ORANGE,
            "infectado": CYAN,
            "drone":    (90, 90, 245),
        }.get(self.etype, RED)
        bw2 = self.w + 10
        bar(surf, rx - 5, ry - 11, bw2, 6, hp_pct, bar_col)


# ─────────────────────────────────────────────────────────
# ITEMS / PICKUPS
# ─────────────────────────────────────────────────────────
class Item:
    def __init__(self, x, y, itype):
        self.x, self.y = float(x), float(y)
        self.itype = itype
        self.alive = True
        self.bob = random.uniform(0, math.tau)

    def update(self, player):
        self.bob += 0.07
        iy = self.y - math.sin(self.bob) * 5
        if pygame.Rect(int(self.x)-12, int(iy)-12, 24, 24).colliderect(player.rect):
            if self.itype == "health":
                player.hp = min(player.hp + 45, player.max_hp)
                spawn(self.x, self.y, GREEN, 24, 3, 60, 5)
            else:
                player.ammo = min(player.ammo + 12, player.max_ammo)
                spawn(self.x, self.y, CYAN, 24, 3, 60, 5)
            self.alive = False

    def draw(self, surf, ox, oy):
        sx = int(self.x - ox)
        sy = int(self.y - math.sin(self.bob)*5 - oy)
        if -30 < sx < W+30 and -30 < sy < H+30:
            col = GREEN if self.itype == "health" else CYAN
            glow_buble(surf, col, sx, sy, 32, 60)  # glow detrás

            img = ITEM_IMAGES.get(self.itype)
            if img:
                surf.blit(img, (sx - 26, sy - 26))  # centrada
            else:
                # fallback al diseño original
                pygame.draw.rect(surf, col, (sx-9, sy-9, 18, 18), border_radius=4)
                pygame.draw.rect(surf, WHITE, (sx-9, sy-9, 18, 18), 1, border_radius=4)
                surf.blit(FNT_XS.render("+HP" if self.itype == "health" else "+AM", True, WHITE),
                        (sx - 11, sy - 22))


# ─────────────────────────────────────────────────────────
# PLATAFORMAS
# ─────────────────────────────────────────────────────────
class Platform:
    def __init__(self, rect):
        self.rect = rect

    def draw(self, surf, ox, oy):
        rx = self.rect.x - ox
        ry = self.rect.y - oy
        if rx > W + 80 or rx + self.rect.w < -80:
            return
        r2 = pygame.Rect(int(rx), int(ry), self.rect.w, self.rect.h)
        pygame.draw.rect(surf, DARKBLUE, r2, border_radius=3)
        pygame.draw.rect(surf, (0, 55, 80), (r2.x, r2.y, r2.w, 2))
        for gx in range(r2.x, r2.x + r2.w + 28, 28):
            pygame.draw.line(surf, (0, 35, 55), (gx, r2.y), (gx, r2.bottom), 1)
        pygame.draw.rect(surf, (0, 50, 75), r2, 1, border_radius=3)


# ─────────────────────────────────────────────────────────
# CONSTRUCCIÓN DE NIVELES
# ─────────────────────────────────────────────────────────
def build_level(n):
    gy = 610
    ground = [
        (0, gy, 780), (840, gy-50, 420), (1310, gy, 520),
        (1880, gy-50, 430), (2360, gy, 640), (3050, gy-50, 520),
        (3620, gy, 880),
    ]
    plats = [
        (200, 490, 150, 18), (400, 410, 170, 18), (640, 470, 120, 18),
        (870, 440, 190, 18), (1070, 360, 140, 18), (1330, 430, 160, 18),
        (1510, 320, 200, 18), (1760, 440, 155, 18), (1870, 310, 175, 18),
        (2120, 380, 155, 18), (2360, 300, 190, 18), (2600, 450, 125, 18),
        (2810, 370, 160, 18), (3010, 285, 200, 18), (3200, 400, 140, 18),
        (3400, 320, 180, 18), (3610, 240, 165, 18), (3810, 370, 140, 18),
        (4000, 300, 180, 18), (4200, 420, 160, 18),
    ]
    walls = [
        (310, 420, 22, 190), (770, 310, 22, 300), (1260, 220, 22, 390),
        (2060, 350, 22, 260), (2760, 300, 22, 310), (3570, 220, 22, 390),
    ]

    boss_x = 4350 + n*60
    boss_y = gy - 96
    world_w = boss_x + 600

    # Ground segment tops (raised segments at y=560, others at y=610):
    #   0..780=610, 840..1260=560, 1310..1830=610, 1880..2310=560,
    #   2360..3000=610, 3050..3570=560, 3620..4500=610
    def _floor_y(x, h):
        """Correct spawn y so enemy stands exactly on the right ground segment."""
        for sx, sy, sw in [(0,610,780),(840,560,420),(1310,610,520),(1880,560,430),
                           (2360,610,640),(3050,560,520),(3620,610,880)]:
            if sx <= x < sx + sw:
                return sy - h
        return gy - h   # fallback

    _ih, _mh = 42, 64   # infectado/mutante heights

    e_defs = [
        # Seg 1 top=610: infectado y = 610-42 = 568
        (360,  _floor_y(360,  _ih), "infectado"),
        (540,  _floor_y(540,  _ih), "infectado"),
        (730,  _floor_y(730,  _ih), "infectado"),   # was 790 (in gap 780-840!) → 730
        # Seg 2 top=560: infectado y = 560-42 = 518  (was wrong gy-42=568 = inside tile!)
        (960,  _floor_y(960,  _ih), "infectado"),
        (1120, 310,                  "drone"),
        # Seg 3 top=610
        (1400, _floor_y(1400, _ih), "infectado"),
        (1620, 270,                  "drone"),
        (1820, 390,                  "infectado"),   # drops onto platform, ok
        # Seg 4 top=560: infectado y = 518
        (2150, _floor_y(2150, _ih), "infectado"),
        (2280, 250,                  "drone"),
        # Seg 5 top=610: mutante h=64 → y = 546  (gy-42=568 was inside tile!)
        (2500, _floor_y(2500, _mh), "mutante"),
        (2790, _floor_y(2790, _ih), "infectado"),
        (3060, 235,                  "drone"),
        # Seg 6 top=560: infectado y=518, mutante y=496
        (3250, _floor_y(3250, _ih), "infectado"),
        (3440, _floor_y(3440, _mh), "mutante"),
        (3740, 190,                  "drone"),
        (3930, 250,                  "infectado"),   # drops onto platform, ok
        # Seg 7 top=610
        (4100, _floor_y(4100, _ih), "infectado"),
        (4260, 250,                  "mutante"),     # drops onto platform, ok
    ]
    if n >= 2:
        e_defs += [(1750, 290, "mutante"), (2600, 370, "drone"),
                   (3800, _floor_y(3800, _mh), "mutante")]  # was gy-42=568, needs 546
    if n >= 3:
        extras = [(ex+80, ey, "drone") for ex, ey, et in e_defs[::3]]
        e_defs += extras

    i_defs = [
        (260, 468, "health"), (700, 450, "ammo"), (1100, 335, "health"),
        (1720, 415, "ammo"), (2310, 276, "health"), (3060, 260, "ammo"),
        (3830, 346, "health"), (4150, 278, "ammo"),
    ]

    bgs = [(4, 4, 14), (3, 3, 12), (8, 0, 18)]
    zones = ["ZONA I: CIUDAD DESTRUIDA",
             "ZONA II: LABORATORIOS ABANDONADOS",
             "ZONA III: FORTALEZA FINAL"]

    tile_rects = []
    for gx2, gy2, gw in ground:
        tile_rects.append(pygame.Rect(gx2, gy2, gw, 300))
    for px, py, pw, ph in plats:
        tile_rects.append(pygame.Rect(px, py, pw, ph))
    for wx, wy, ww, wh in walls:
        tile_rects.append(pygame.Rect(wx, wy, ww, wh))

    plat_objs = [Platform(r) for r in tile_rects]
    enemies = [Enemy(ex, ey, et, n) for ex, ey, et in e_defs]
    enemies.append(Enemy(boss_x, boss_y, "jefe", n))
    items = [Item(ix, iy, it) for ix, iy, it in i_defs]
    checkpoints = [(80, 530), (1200, 560), (2500, 560), (3800, 560)]

    return tile_rects, plat_objs, enemies, items, world_w, bgs[n-1], zones[n-1], checkpoints


# ─────────────────────────────────────────────────────────
# FONDO PROCEDURAL
# ─────────────────────────────────────────────────────────
def draw_bg(surf, cam_x, cam_y, bg_col, level_num, tick):
    surf.fill(bg_col)
    rng = random.Random(42 + level_num)

    for _ in range(55):
        sx = (rng.randint(0, W*8) - int(cam_x*0.08)) % W
        sy = (rng.randint(0, 700) - int(cam_y*0.05)) % H
        sc = (CYAN, PURPLE, PINK)[rng.randrange(3)]
        pulse = int(70 + 35*math.sin(tick*0.04 + rng.random()*6))
        r2, g2, b2 = sc
        pygame.draw.circle(surf,
                           (r2*pulse//255, g2*pulse//255, b2*pulse//255),
                           (sx, sy), rng.randint(1, 3))

    rng2 = random.Random(77 + level_num)
    if level_num == 1:
        for i in range(16):
            bw = rng2.randint(55, 115)
            bh = rng2.randint(80, 340)
            bx = (rng2.randint(0, 4800) - int(cam_x*0.14)) % W
            by = H - bh
            pygame.draw.rect(surf, (12, 12, 22), (bx, by, bw, bh))
            for wy2 in range(by+10, by+bh-10, 22):
                for wx2 in range(bx+7, bx+bw-7, 15):
                    if rng2.random() > 0.45:
                        wc = rng2.choice([(0, 35, 55), (35, 0, 55), (0, 0, 40)])
                        pygame.draw.rect(surf, wc, (wx2, wy2, 5, 7))
    elif level_num == 2:
        for _ in range(10):
            px2 = (rng2.randint(0, 4800) - int(cam_x*0.12)) % W
            pygame.draw.line(surf, (15, 25, 40), (px2, 0), (px2, H), rng2.randint(2, 5))
    else:
        for i in range(12):
            tw = rng2.randint(20, 50)
            th = rng2.randint(120, 400)
            tx2 = (rng2.randint(0, 5200) - int(cam_x*0.12)) % W
            ty2 = H - th
            pygame.draw.rect(surf, (10, 0, 20), (tx2, ty2, tw, th))
            pygame.draw.line(surf, (180, 0, 255), (tx2+tw//2, ty2), (tx2+tw//2, ty2+th), 1)

    # scanlines
    for sy in range(0, H, 4):
        pygame.draw.line(surf, (0, 0, 0), (0, sy), (W, sy))
    scan_y = (tick * 3) % (H + 60) - 30
    ss = pygame.Surface((W, 3), pygame.SRCALPHA)
    ss.fill((0, 230, 220, 12))
    surf.blit(ss, (0, scan_y))


# ─────────────────────────────────────────────────────────
# HUD
# ─────────────────────────────────────────────────────────
def draw_hud(surf, player, zone_name, score, boss):
    ps = pygame.Surface((248, 130), pygame.SRCALPHA)
    pygame.draw.rect(ps, (0, 10, 28, 185), (0, 0, 248, 130), border_radius=8)
    pygame.draw.rect(ps, (*CYAN, 80), (0, 0, 248, 130), 1, border_radius=8)
    surf.blit(ps, (8, 8))

    txt(surf, "NEUROCALIPSIS", FNT_XS, CYAN, 16, 12)
    txt(surf, f"SAKÍ  ──  LVL {player.level}", FNT_SM, WHITE, 16, 28)
    bar(surf, 16, 54, 180, 15, player.hp/player.max_hp, RED, label=f"HP  {player.hp}/{player.max_hp}")
    bar(surf, 16, 74, 180, 15, player.ammo/player.max_ammo, CYAN, label=f"AMO {player.ammo}/{player.max_ammo}")
    bar(surf, 16, 94, 180, 15, player.xp/player.xp_to_next, GOLD, label=f"XP  {player.xp}/{player.xp_to_next}")
    nc_pct = 1 - player.neural_cd/600
    nc_col = PURPLE if nc_pct >= 1 or player.neural_t > 0 else GREY
    bar(surf, 16, 114, 180, 15, nc_pct, nc_col, label="DESCARGA NEURAL")

    # zona / score
    zt = FNT_SM.render(zone_name, True, CYAN)
    surf.blit(zt, (W//2 - zt.get_width()//2, 7))
    st = FNT_SM.render(f"SCORE: {score}", True, GOLD)
    surf.blit(st, (W - st.get_width() - 12, 7))

    # level up
    if player.levelup_t > 0:
        lt = FNT_BIG.render(f"¡NIVEL {player.level}!", True, GOLD)
        surf.blit(lt, (W//2 - lt.get_width()//2, H//2 - 50))
        #glow_circle(surf, GOLD, W//2, H//2, 140, 55)

    # combo
    if player.combo > 0 and player.combo_t > 0:
        clabels = {1: "SLASH!", 2: "DOBLE SLASH!", 3: "GOLPE FINAL!"}
        ccols = {1: CYAN, 2: PURPLE, 3: GOLD}
        ct = FNT_MED.render(clabels[player.combo], True, ccols[player.combo])
        surf.blit(ct, (18, H//2))

    # boss bar
    if boss and boss.alive:
        bw = 520
        bx = W//2 - bw//2
        by = H - 78
        bp = pygame.Surface((bw+20, 62), pygame.SRCALPHA)
        pygame.draw.rect(bp, (10, 0, 22, 200), (0, 0, bw+20, 62), border_radius=8)
        pygame.draw.rect(bp, (*PURPLE, 90), (0, 0, bw+20, 62), 1, border_radius=8)
        surf.blit(bp, (bx-10, by-6))
        txt(surf, "LA CONCIENCIA DE LA IA", FNT_SM, PURPLE, bx, by)
        pt = FNT_XS.render(f"FASE {boss.phase}", True, PINK)
        surf.blit(pt, (bx + bw - pt.get_width(), by))
        bar(surf, bx, by+22, bw, 20, boss.hp/boss.max_hp, PURPLE,
            label=f"{boss.hp}/{boss.max_hp}")

    # aura neural
    if player.neural_t > 0:
        ns = pygame.Surface((W, H), pygame.SRCALPHA)
        a = int(90 * player.neural_t / 200)
        pygame.draw.rect(ns, (*PURPLE, a), (0, 0, W, H), 7)
        surf.blit(ns, (0, 0))

    hint = "[A/D] Mover  [SPACE] Saltar  [J] Katana  [K/Click] Pistola  [L] Descarga  [R] Recargar"
    ht = FNT_XS.render(hint, True, (80, 100, 130))
    surf.blit(ht, (W//2 - ht.get_width()//2, H - 18))


# ─────────────────────────────────────────────────────────
# PANTALLA TÍTULO
# ─────────────────────────────────────────────────────────
def draw_title(surf, tick):
    surf.fill(BG1)
    for i in range(18):
        ang = i/18 * math.tau + tick*0.012
        px = W//2 + int(math.cos(ang)*360) #Cambios en el radio horizontal
        py = H//2 + int(math.sin(ang)*280) #Cambios en el radio vertical
        glow_circle(surf, (CYAN, PURPLE, PINK)[i % 3], px, py, 20, 40)

    t1 = FNT_BIG.render("NEUROCALIPSIS", True, CYAN)
    t2 = FNT_MED.render("El Último Fragmento", True, WHITE)
    t3 = FNT_SM.render("─" * 44, True, GREY)
    blink = (tick // 28) % 2 == 0
    t4 = FNT_MED.render("Presiona ENTER para comenzar" if blink else "", True, GOLD)
    t5 = FNT_XS.render("ESC = Salir", True, GREY)

    y0 = H//2 - 140
    surf.blit(t1, (W//2 - t1.get_width()//2, y0))
    surf.blit(t2, (W//2 - t2.get_width()//2, y0 + 68))
    surf.blit(t3, (W//2 - t3.get_width()//2, y0 + 108))
    lines = [
        "Año 2090 — Los implantes de IA han corroído la humanidad.",
        "Sakí Kishimoto es la última esperanza.",
        "Katana, pistola y su Descarga Neural son tu única salvación.",
    ]
    for i, l in enumerate(lines):
        lt = FNT_SM.render(l, True, (150, 160, 190))
        surf.blit(lt, (W//2 - lt.get_width()//2, y0 + 136 + i*28))
    surf.blit(t4, (W//2 - t4.get_width()//2, y0 + 236))
    surf.blit(t5, (W//2 - t5.get_width()//2, y0 + 280))
    #glow_circle(surf, CYAN, W//2, H//2, 300, 20)


# ─────────────────────────────────────────────────────────
# MENÚ DE PAUSA
# ─────────────────────────────────────────────────────────
def draw_pause_menu(surf):
    panel = pygame.Surface((360, 320), pygame.SRCALPHA)
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    panel.fill((10, 20, 40, 230))
    ov.fill((0, 0, 0, 160))
    surf.blit(ov, (0, 0))
    surf.blit(panel, (W//2 - panel.get_width()//2, H//2 - panel.get_height()//2))
    pygame.draw.rect(surf, (0, 230, 220), (W//2 - 180, H//2 - 160, 360, 320), 4, border_radius=10)
    txt(surf, "PAUSA", FNT_BIG, CYAN, W//2 - 120, H//2 - 100)
    txt(surf, "ESC = Reanudar", FNT_SM, WHITE, W//2 - 90, H//2 - 20)
    txt(surf, "Q = Salir al título", FNT_SM, WHITE, W//2 - 90, H//2 + 20)
    txt(surf, "F1 = Debug", FNT_SM, WHITE, W//2 - 90, H//2 + 60)

def draw_ability_menu(surf, abilities_dict):
    """Menú de desbloqueos (TAB)."""
    bx, by = W//2 - 180, H//2 - 160
    panel = pygame.Surface((360, 320), pygame.SRCALPHA)
    panel.fill((10, 20, 40, 230))
    surf.blit(panel, (bx, by))
    pygame.draw.rect(surf, CYAN, (bx, by, 360, 320), 2, border_radius=10)
    txt(surf, "HABILIDADES", FNT_MED, CYAN, bx + 90, by + 12)
    txt(surf, "TAB = Cerrar", FNT_XS, GREY, bx + 120, by + 48)
    y = by + 75
    for aid, name in ab.ABILITY_NAMES.items():
        unlocked = abilities_dict.get(aid, False)
        col = GREEN if unlocked else DKGREY
        txt(surf, ("[OK] " if unlocked else "[--] ") + name, FNT_SM, col, bx + 24, y)
        y += 32


# ─────────────────────────────────────────────────────────
# DEBUG (F1): FPS, hitboxes
# ─────────────────────────────────────────────────────────
def draw_debug(surf, player, enemies, ox, oy):
    fps = clock.get_fps()
    txt(surf, f"FPS: {fps:.0f}", FNT_XS, GREEN, W - 80, 8)
    pr = player.rect
    pygame.draw.rect(surf, GREEN, (pr.x - ox, pr.y - oy, pr.w, pr.h), 1)
    for e in enemies:
        if e.alive:
            er = e.rect
            pygame.draw.rect(surf, RED, (er.x - ox, er.y - oy, er.w, er.h), 1)


# ─────────────────────────────────────────────────────────
# OVERLAY GAME OVER / WIN
# ─────────────────────────────────────────────────────────
def draw_overlay(surf, title, sub, col):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.rect(ov, (0, 0, 0, 175), (0, 0, W, H))
    surf.blit(ov, (0, 0))
    glow_circle(surf, col, W//2, H//2, 220, 60)
    t1 = FNT_BIG.render(title, True, col)
    t2 = FNT_MED.render(sub, True, WHITE)
    t3 = FNT_SM.render("R = Reiniciar desde checkpoint   ESC = Salir", True, GREY)
    surf.blit(t1, (W//2 - t1.get_width()//2, H//2 - 90))
    surf.blit(t2, (W//2 - t2.get_width()//2, H//2 - 4))
    surf.blit(t3, (W//2 - t3.get_width()//2, H//2 + 62))


# ─────────────────────────────────────────────────────────
# BUCLE PRINCIPAL
# ─────────────────────────────────────────────────────────
def run():
    tick = 0
    state = "title"
    score = 0
    level_n = 1

    tiles, plat_objs, enemies, items, world_w, bg_col, zone_name, checkpoints = build_level(level_n)
    tile_grid = build_tile_grid(tiles)
    player = Player(80, 530)
    ab.check_unlocks(player.level, player.abilities)
    bullets = []
    boss = next((e for e in enemies if e.etype == "jefe"), None)
    last_checkpoint_idx = 0
    minimap_discovered = set()

    cam_x, cam_y = 0.0, 0.0
    zone_msg_t = 220
    fade_in = 255

    def reset_level(n, p, at_checkpoint_idx=None):
        nonlocal tiles, plat_objs, enemies, items, world_w, bg_col
        nonlocal zone_name, bullets, boss, zone_msg_t, fade_in, tile_grid, checkpoints, last_checkpoint_idx, minimap_discovered
        tiles, plat_objs, enemies, items, world_w, bg_col, zone_name, checkpoints = build_level(n)
        tile_grid = build_tile_grid(tiles)
        bullets.clear()
        particle_system.clear()
        if at_checkpoint_idx is not None:
            last_checkpoint_idx = at_checkpoint_idx
        else:
            last_checkpoint_idx = 0
            minimap_discovered.clear()
        cx, cy = checkpoints[last_checkpoint_idx]
        p.x, p.y = float(cx), float(cy)
        p.vx = p.vy = 0
        p.dead = False
        p.hp = p.max_hp  # Curar completamente al reiniciar
        p.inv_t = 90
        p.ammo = p.max_ammo  # Recargar munición
        boss = next((e for e in enemies if e.etype == "jefe"), None)
        zone_msg_t = 220
        fade_in = 255
        minimap_discovered.clear()
        mm.update_discovered(minimap_discovered, player.x, player.y)

    def restart_game():
        """Reinicia el juego completamente desde el principio"""
        nonlocal level_n, score, player, bullets, enemies, items, boss, last_checkpoint_idx
        level_n = 1
        score = 0
        player = Player(80, 530)
        ab.check_unlocks(player.level, player.abilities)
        reset_level(level_n, player, 0)
        # Reproducir música de fondo en loop infinito
        try:
            pygame.mixer.music.play(-1)  # -1 significa loop infinito
            print("🎵 Música de fondo iniciada")
        except:
            print("⚠️ No se pudo reproducir la música de fondo")

    while True:
        dt = clock.tick(FPS)
        tick += 1
        effects.update_effects()
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        world_mx = mx + int(cam_x)
        world_my = my + int(cam_y)

            # ── EVENTOS ───────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "playing":
                        state = "pause"
                        pygame.mixer.music.pause()  # Pausar música
                        print("🎵 Música pausada")
                    elif state == "pause":
                        state = "playing"
                        pygame.mixer.music.unpause()  # Reanudar música
                        print("🎵 Música reanudada")
                    else:
                        pygame.quit()
                        sys.exit()
                        
                if event.key == pygame.K_F1 and state in ("playing", "pause"):
                    global DEBUG
                    DEBUG = not DEBUG

                if state == "pause" and event.key == pygame.K_q:
                    state = "title"
                    pygame.mixer.music.stop()  # Detener música al salir al título
                    print("🎵 Música detenida")

                if state == "title" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    state = "playing"
                    restart_game()

                    # La música se inicia dentro de restart_game()

                if event.key == pygame.K_r:
                    if state == "dead":
                        state = "playing"
                        # Reiniciar desde el último checkpoint
                        reset_level(level_n, player, last_checkpoint_idx)
                        # Asegurar que la música siga sonando
                        try:
                            pygame.mixer.music.unpause()
                        except:
                            pass
                    elif state == "win":
                        state = "playing"
                        restart_game()
                    elif state == "playing":
                        player.ammo = player.max_ammo
                        # Reproducir sonido de recarga
                        if 'SND_RELOAD' in globals() and SND_RELOAD:
                            SND_RELOAD.play()
                            print("🔄 ¡Munición recargada!")

                if state == "playing":
                    if event.key == pygame.K_j:
                        player.do_slash()
                    if event.key == pygame.K_l:
                        player.do_neural()
                    if event.key == pygame.K_TAB:
                        player.show_ability_menu = not player.show_ability_menu

            if state == "playing" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                b = player.do_shoot(world_mx, world_my)
                if b:
                    bullets.append(b)

        # ── UPDATE ────────────────────────────────────────
        if state == "playing" and not effects.is_hitstop_active():
            # disparar pistola con K (continuo)
            if keys[pygame.K_k]:
                b = player.do_shoot(world_mx, world_my)
                if b:
                    bullets.append(b)

            player.update(keys, tiles)

            # balas (colisión con grid)
            for b in bullets[:]:
                b.update(tile_grid)
                if not b.alive:
                    bullets.remove(b)
                    continue
                if b.owner == "player":
                    for e in enemies:
                        if e.alive and e.rect.collidepoint(b.x, b.y):
                            xp = e.take_damage(b.dmg)
                            effects.trigger_hitstop(frames=2, is_slash=False)
                            effects.trigger_shake(is_slash=False)
                            effects.spawn_damage_number(e.cx, e.cy - 20, b.dmg, (0, 230, 220))
                            if xp:
                                score += xp
                                player.gain_xp(xp)
                                if random.random() < 0.36:
                                    tp = "health" if random.random() < 0.5 else "ammo"
                                    items.append(Item(e.x + e.w/2, e.y, tp))
                            b.alive = False
                            break
                elif b.owner == "enemy":
                    if player.rect.collidepoint(b.x, b.y):
                        player.take_damage(b.dmg)
                        b.alive = False

            # katana vs enemigos + hit feedback
            for se in player.slash_effects:
                for e in enemies:
                    if e.alive and id(e) not in se.hit_ids:
                        if se.rect.colliderect(e.rect):
                            xp = e.take_damage(se.dmg)
                            se.hit_ids.add(id(e))
                            effects.trigger_hitstop()
                            effects.trigger_shake(is_slash=True)
                            effects.spawn_damage_number(e.cx, e.cy - 20, se.dmg, (0, 230, 220))
                            if xp:
                                score += xp
                                player.gain_xp(xp)
                                if random.random() < 0.36:
                                    tp = "health" if random.random() < 0.5 else "ammo"
                                    items.append(Item(e.x + e.w/2, e.y, tp))

            # enemigos
            for e in enemies:
                if e.alive:
                    e.update(player, tiles, bullets)

            # items
            for it in items[:]:
                it.update(player)
                if not it.alive:
                    items.remove(it)

            update_particles()

            mm.update_discovered(minimap_discovered, player.x, player.y)

            # checkpoints: activar si el jugador pasa por uno
            for i, (cx, cy) in enumerate(checkpoints):
                if abs(player.cx - cx) < 100 and abs(player.cy - cy) < 80:
                    if i > last_checkpoint_idx:
                        last_checkpoint_idx = i
                        # Feedback visual al activar checkpoint
                        spawn(cx, cy, GOLD, 15, 3, 30, 5)

            # cámara (shake se aplica al dibujar)
            cam_x = lerp(cam_x, player.cx - W/2, 0.10)
            cam_y = lerp(cam_y, player.cy - H/2 + 70, 0.10)
            cam_x = clamp(cam_x, 0, world_w - W)
            cam_y = clamp(cam_y, 0, 800)

            if player.dead:
                state = "dead"

            # avance de zona
            if boss and not boss.alive and player.x > world_w - 400:
                if level_n < 3:
                    level_n += 1
                    player.hp = min(player.hp + 55, player.max_hp)
                    player.ammo = player.max_ammo
                    reset_level(level_n, player)
                    boss = next((e for e in enemies if e.etype == "jefe"), None)
                else:
                    state = "win"

        # ── DIBUJAR ───────────────────────────────────────
        shake_dx, shake_dy = effects.get_camera_offset()
        draw_ox = int(cam_x) + int(shake_dx)
        draw_oy = int(cam_y) + int(shake_dy)

        if state == "title":
            draw_title(screen, tick)
        else:
            draw_bg(screen, draw_ox, draw_oy, bg_col, level_n, tick)

            for p in plat_objs:
                p.draw(screen, draw_ox, draw_oy)
            for it in items:
                it.draw(screen, draw_ox, draw_oy)
            for e in enemies:
                if e.alive:
                    e.draw(screen, draw_ox, draw_oy)
            for b in bullets:
                b.draw(screen, draw_ox, draw_oy)
            draw_particles(screen, draw_ox, draw_oy)
            if state != "dead":
                player.draw(screen, draw_ox, draw_oy)
            effects.draw_damage_numbers(screen, draw_ox, draw_oy)

            # mensaje de zona
            if zone_msg_t > 0:
                a = min(255, zone_msg_t * 3)
                zt = FNT_MED.render(zone_name, True, CYAN)
                zs = pygame.Surface((zt.get_width()+24, zt.get_height()+12), pygame.SRCALPHA)
                pygame.draw.rect(zs, (0, 0, 0, min(200, a)), zs.get_rect(), border_radius=7)
                screen.blit(zs, (W//2 - zs.get_width()//2, 60))
                zt.set_alpha(a)
                screen.blit(zt, (W//2 - zt.get_width()//2, 66))
                zone_msg_t -= 1

            draw_hud(screen, player, zone_name, score,
                     boss if boss and boss.alive else None)
            mm.draw_minimap(screen, minimap_discovered, player.x, player.y, world_w, 800, W - 200, H - 118)

            if player.show_ability_menu:
                draw_ability_menu(screen, player.abilities)

            if state == "dead":
                draw_overlay(screen, "GAME OVER",
                             f"Has caído...  Checkpoint alcanzado: {last_checkpoint_idx+1}", RED)
            elif state == "win":
                draw_overlay(screen, "¡VICTORIA!",
                             f"La IA fue derrotada  ·  Score: {score}  ·  Nivel: {player.level}", GOLD)
            elif state == "pause":
                draw_pause_menu(screen)

            if DEBUG:
                draw_debug(screen, player, enemies, draw_ox, draw_oy)

            # fade in
            if fade_in > 0:
                fs = pygame.Surface((W, H))
                fs.fill((0, 0, 0))
                fs.set_alpha(fade_in)
                screen.blit(fs, (0, 0))
                fade_in = max(0, fade_in - 9)

        pygame.display.flip()


# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    run()