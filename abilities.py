"""
Sistema de habilidades desbloqueables tipo metroidvania.
Habilidades: doble_salto, dash, wall_jump, keycard_1, keycard_2, gancho (opcional).
Obstáculos en el nivel requieren estas habilidades para pasar.
"""
from typing import Dict, Any

# IDs de habilidades (desbloqueables por nivel o por item)
ABILITY_DOUBLE_JUMP = "doble_salto"
ABILITY_DASH = "dash"
ABILITY_WALL_JUMP = "wall_jump"
ABILITY_KEYCARD_1 = "keycard_1"
ABILITY_KEYCARD_2 = "keycard_2"

DEFAULT_ABILITIES: Dict[str, bool] = {
    ABILITY_DOUBLE_JUMP: False,
    ABILITY_DASH: False,
    ABILITY_WALL_JUMP: False,
    ABILITY_KEYCARD_1: False,
    ABILITY_KEYCARD_2: False,
}

# Descripción para menú de desbloqueos
ABILITY_NAMES: Dict[str, str] = {
    ABILITY_DOUBLE_JUMP: "Doble salto",
    ABILITY_DASH: "Dash",
    ABILITY_WALL_JUMP: "Salto en pared",
    ABILITY_KEYCARD_1: "Keycard Nivel 1",
    ABILITY_KEYCARD_2: "Keycard Nivel 2",
}

# Requisito para desbloquear (por nivel del jugador o por evento)
# Se puede ampliar: {"type": "level", "value": 2} o {"type": "item", "id": "keycard"}
UNLOCK_BY_LEVEL: Dict[str, int] = {
    ABILITY_DOUBLE_JUMP: 2,   # al llegar a nivel 2
    ABILITY_DASH: 3,
    ABILITY_WALL_JUMP: 4,
    ABILITY_KEYCARD_1: 0,     # por item/puerta
    ABILITY_KEYCARD_2: 0,
}


def check_unlocks(level: int, abilities: Dict[str, bool]) -> None:
    """Desbloquea habilidades según nivel del jugador."""
    for ab_id, req_level in UNLOCK_BY_LEVEL.items():
        if req_level > 0 and level >= req_level:
            abilities[ab_id] = True


def has_ability(abilities: Dict[str, bool], ability_id: str) -> bool:
    return abilities.get(ability_id, False)


def can_pass_obstacle(obstacle_type: str, abilities: Dict[str, bool]) -> bool:
    """True si el jugador puede pasar un obstáculo (puerta, zona bloqueada)."""
    if obstacle_type == "keycard_1":
        return has_ability(abilities, ABILITY_KEYCARD_1)
    if obstacle_type == "keycard_2":
        return has_ability(abilities, ABILITY_KEYCARD_2)
    if obstacle_type == "double_jump_required":
        return has_ability(abilities, ABILITY_DOUBLE_JUMP)
    if obstacle_type == "dash_required":
        return has_ability(abilities, ABILITY_DASH)
    if obstacle_type == "wall_jump_required":
        return has_ability(abilities, ABILITY_WALL_JUMP)
    return True
