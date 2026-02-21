"""
Sistema de efectos de "game feel": hitstop, camera shake, números de daño.
"""
import pygame
import math
import random

# Configuración tuneable
HITSTOP_FRAMES = 4          # pausa en frames al acertar katana (2-6 recomendado)
HITSTOP_FRAMES_SHOOT = 2    # al acertar disparo
SHAKE_STRENGTH_SLASH = 4    # desplazamiento máx. en px (katana)
SHAKE_STRENGTH_SHOOT = 2
SHAKE_STRENGTH_MELEE = 6    # cuando el jugador recibe melee
SHAKE_DECAY = 0.85          # reducción por frame

# Estado global (actualizado por el juego)
hitstop_remaining = 0
shake_x = 0.0
shake_y = 0.0
shake_strength = 0.0

# Números de daño flotantes
class DamageNumber:
    __slots__ = ("x", "y", "text", "life", "max_life", "vy", "col")
    def __init__(self, x, y, value, col=(255, 55, 55)):
        self.x, self.y = float(x), float(y)
        self.text = str(int(value))
        self.life = self.max_life = 45
        self.vy = -1.8
        self.col = col

    def update(self):
        self.life -= 1
        self.y += self.vy
        self.vy *= 0.92

    def draw(self, surf, ox, oy, font):
        if self.life <= 0:
            return False
        ratio = self.life / self.max_life
        sx = int(self.x - ox)
        sy = int(self.y - oy)
        alpha = int(255 * ratio)
        if alpha <= 0:
            return self.life <= 0
        txt_surf = font.render(self.text, True, self.col)
        txt_surf.set_alpha(alpha)
        surf.blit(txt_surf, (sx - txt_surf.get_width()//2, sy - txt_surf.get_height()//2))
        return True


damage_numbers = []
_damage_font = None

def get_damage_font():
    global _damage_font
    if _damage_font is None:
        try:
            _damage_font = pygame.font.SysFont("consolas", 22, bold=True)
        except Exception:
            _damage_font = pygame.font.Font(None, 24)
    return _damage_font


def trigger_hitstop(frames=None, is_slash=True):
    """Activa hitstop (pausa breve al acertar)."""
    global hitstop_remaining
    f = frames if frames is not None else (HITSTOP_FRAMES if is_slash else HITSTOP_FRAMES_SHOOT)
    hitstop_remaining = max(hitstop_remaining, f)


def trigger_shake(strength=None, is_slash=True, is_melee_hit=False):
    """Activa sacudida de cámara."""
    global shake_strength
    if strength is not None:
        s = strength
    elif is_melee_hit:
        s = SHAKE_STRENGTH_MELEE
    else:
        s = SHAKE_STRENGTH_SLASH if is_slash else SHAKE_STRENGTH_SHOOT
    shake_strength = max(shake_strength, s)


def spawn_damage_number(x, y, value, col=(255, 55, 55)):
    """Añade un número de daño flotante (opcional)."""
    damage_numbers.append(DamageNumber(x, y, value, col))


def update_effects():
    """Llamar cada frame. Actualiza hitstop, shake y números."""
    global hitstop_remaining, shake_x, shake_y, shake_strength
    if hitstop_remaining > 0:
        hitstop_remaining -= 1
    if shake_strength > 0.1:
        angle = random.uniform(0, math.tau)
        shake_x = math.cos(angle) * shake_strength
        shake_y = math.sin(angle) * shake_strength
        shake_strength *= SHAKE_DECAY
    else:
        shake_x = shake_y = 0.0
        shake_strength = 0.0
    for i in range(len(damage_numbers) - 1, -1, -1):
        damage_numbers[i].update()
        if damage_numbers[i].life <= 0:
            damage_numbers.pop(i)


def get_camera_offset():
    """Devuelve (dx, dy) para aplicar a la cámara (shake)."""
    return (shake_x, shake_y)


def is_hitstop_active():
    """True si el juego debe pausar la lógica (hitstop)."""
    return hitstop_remaining > 0


def draw_damage_numbers(surf, ox, oy):
    """Dibuja todos los números de daño."""
    font = get_damage_font()
    for d in damage_numbers[:]:
        if not d.draw(surf, ox, oy, font) or d.life <= 0:
            if d in damage_numbers:
                damage_numbers.remove(d)
