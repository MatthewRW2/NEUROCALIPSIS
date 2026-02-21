"""
Carga niveles desde JSON. Si no existe el JSON o falla, usa build_level del main.
"""
import json
import os
import pygame

def load_level_json(level_n, EnemyClass, ItemClass, PlatformClass):
    """Carga nivel desde data/levels/level{N}.json. Devuelve None si no existe."""
    path = os.path.join(os.path.dirname(__file__), "data", "levels", f"level{level_n}.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    tile_rects = []
    gy = data.get("ground_y", 610)
    for g in data.get("ground", []):
        x, y_off, w = g.get("x", 0), g.get("y_off", 0), g.get("w", 200)
        tile_rects.append(pygame.Rect(x, gy + y_off, w, 300))
    for p in data.get("plats", []):
        tile_rects.append(pygame.Rect(p["x"], p["y"], p["w"], p["h"]))
    for w in data.get("walls", []):
        tile_rects.append(pygame.Rect(w["x"], w["y"], w["w"], w["h"]))

    plat_objs = [PlatformClass(r) for r in tile_rects]
    enemies = []
    for e in data.get("enemies", []):
        enemies.append(
            EnemyClass(e["x"], e["y"], e["type"], data.get("level_num", level_n))
        )
    boss_x = data.get("boss_x", 4350 + level_n * 60)
    boss_y = data.get("boss_y", gy - 96)
    if EnemyClass is not None:
        boss = next((ee for ee in enemies if getattr(ee, "etype", None) == "jefe"), None)
        if boss is None:
            enemies.append(EnemyClass(boss_x, boss_y, "jefe", data.get("level_num", level_n)))

    items = []
    for it in data.get("items", []):
        items.append(ItemClass(it["x"], it["y"], it["type"]))

    world_w = data.get("world_w", boss_x + 600)
    bgs = data.get("bg_colors", [(4, 4, 14), (3, 3, 12), (8, 0, 18)])
    zones = data.get("zones", ["ZONA I", "ZONA II", "ZONA III"])
    bg_col = bgs[(level_n - 1) % len(bgs)]
    zone_name = zones[(level_n - 1) % len(zones)]

    checkpoints = data.get("checkpoints", [])

    return tile_rects, plat_objs, enemies, items, world_w, bg_col, zone_name, checkpoints
