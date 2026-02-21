"""Carga stats de enemigos desde data/enemy_stats.json."""
import json
import os

_loaded = None

def get_enemy_stats():
    global _loaded
    if _loaded is not None:
        return _loaded
    path = os.path.join(os.path.dirname(__file__), "enemy_stats.json")
    if not os.path.isfile(path):
        _loaded = {}
        return _loaded
    try:
        with open(path, "r", encoding="utf-8") as f:
            _loaded = json.load(f)
        return _loaded
    except (json.JSONDecodeError, IOError):
        _loaded = {}
        return _loaded
