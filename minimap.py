"""
Minimapa con celdas descubiertas y posición del jugador.
El mundo se discretiza en celdas (ej. 400x300 px). Al entrar en una celda se marca como descubierta.
"""
import pygame
from typing import Set, Tuple

# Tamaño de celda en mundo (px)
CELL_W = 400
CELL_H = 300

# Tamaño del minimapa en pantalla
MINIMAP_W = 180
MINIMAP_H = 100


def world_to_cell(x: float, y: float) -> Tuple[int, int]:
    cx = int(x) // CELL_W
    cy = int(y) // CELL_H
    return (cx, cy)


def update_discovered(discovered: Set[Tuple[int, int]], player_x: float, player_y: float) -> None:
    """Añade la celda actual del jugador a descubiertas."""
    discovered.add(world_to_cell(player_x, player_y))


def draw_minimap(
    surf: pygame.Surface,
    discovered: Set[Tuple[int, int]],
    player_x: float,
    player_y: float,
    world_w: int,
    world_h: int,
    x: int,
    y: int,
    border_col=(0, 230, 220),
    bg_col=(10, 20, 40),
    discovered_col=(0, 80, 100),
    player_col=(255, 55, 55),
) -> None:
    """
    Dibuja el minimapa en (x, y) con ancho MINIMAP_W y alto MINIMAP_H.
    world_h puede ser 800 o el alto máximo del nivel.
    """
    cells_x = max(1, (world_w + CELL_W - 1) // CELL_W)
    cells_y = max(1, (world_h + CELL_H - 1) // CELL_H)
    cell_screen_w = MINIMAP_W / cells_x
    cell_screen_h = MINIMAP_H / cells_y

    # Fondo
    pygame.draw.rect(surf, bg_col, (x, y, MINIMAP_W, MINIMAP_H), border_radius=4)
    pygame.draw.rect(surf, border_col, (x, y, MINIMAP_W, MINIMAP_H), 1, border_radius=4)

    # Celdas descubiertas
    for (cx, cy) in discovered:
        if 0 <= cx < cells_x and 0 <= cy < cells_y:
            sx = x + cx * cell_screen_w
            sy = y + cy * cell_screen_h
            pygame.draw.rect(
                surf,
                discovered_col,
                (sx + 1, sy + 1, max(1, cell_screen_w - 1), max(1, cell_screen_h - 1)),
                border_radius=1,
            )

    # Jugador
    pcx, pcy = world_to_cell(player_x, player_y)
    if 0 <= pcx < cells_x and 0 <= pcy < cells_y:
        px = x + (pcx + 0.5) * cell_screen_w
        py = y + (pcy + 0.5) * cell_screen_h
        pygame.draw.circle(surf, player_col, (int(px), int(py)), 4)
        pygame.draw.circle(surf, (255, 255, 255), (int(px), int(py)), 2)
