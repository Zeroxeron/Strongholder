# ----------------------------------------------------
# Minecraft Strongholder
# ----------------------------------------------------
# Copyright (c) 2026 x_Kiva_x
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Any
# tomllib for Python 3.11+, tomli fallback for older versions
try:
    import tomllib as _toml_loader  # type: ignore
except Exception:
    import tomli as _toml_loader  # type: ignore

@dataclass
class Config:
    cfg_path = Path("config.toml")
    # https://minecraft.fandom.com/wiki/Stronghold
    S_RINGS: List[Tuple[int, int]] = (
        (1280, 2816),
        (4352, 5888),
        (7424, 8960),
        (10496, 12032),
        (13568, 15104),
        (16640, 18176),
        (19712, 21248),
        (22784, 24320),
    )
    # top speedruns usually only require the first ring, but this can be extended.
    MAX_RINGS: int = 1
    # listed results length
    MAX_RESULTS: int = 5
    # Allowance distance
    MAX_DISTANCE: int = 2816
    # filter max AVG angle deviation (+multiplies per line to address the input error)
    MAX_MARGIN: float = 1.25
    # input error offset (-0.13 is decent for casual 30 fov pixel center measurement. Use 0 for low sens + AHK tall screen)
    ANGLE_OFFSET: float = 0

def _toml_repr_for_s_rings(rings: List[Tuple[int,int]]) -> str:
    # Format as TOML array-of-arrays: [[min,max],[min,max],...]
    inner = ",".join(f"[{int(a)},{int(b)}]" for a,b in rings)
    return f"[{inner}]"

def write_config_toml(path: Path, cfg: Config) -> None:
    """
    Write a config.toml file at `path` including comments.
    This overwrites the file if present.
    """
    text = f"""#                                                                        
# ██▄  ▄██ ▄█████   ▄█████  ▄▄▄  ▄▄  ▄▄ ▄▄▄▄▄ ▄▄  ▄▄▄▄ 
# ██ ▀▀ ██ ▀▀▀▄▄▄   ██     ██▀██ ███▄██ ██▄▄  ██ ██ ▄▄ 
# ██    ██ █████▀   ▀█████ ▀███▀ ██ ▀██ ██    ██ ▀███▀ 
#                                                     (c) 2026 x_Kiva_x
#
# Stronghold rings list [[min1, max1],[min2,max2], ...] in blocks.
# Each entry has minimum and maximum distance for a ring. Defaults: https://minecraft.fandom.com/wiki/Stronghold
S_RINGS = {_toml_repr_for_s_rings(cfg.S_RINGS)}

# Maximum number of rings to consider (1 = only first ring). 
# Speedruns typically only need the first ring, but this can be changed. [1]
MAX_RINGS = {int(cfg.MAX_RINGS)}

# Number of results to show per query. [5]
MAX_RESULTS = {int(cfg.MAX_RESULTS)}

# Filter maximum average angle deviation (degrees). Used as a tolerance.
# Multiplies per line count to address input errors. [1.25]
MAX_MARGIN = {float(cfg.MAX_MARGIN)}

# Allowance stronghold distance for eye-throw. [3000]
MAX_DISTANCE = {int(cfg.MAX_DISTANCE)}

# Input error offset for 30-FOV pixel-center measurement, in degrees. [0]
# Note: -0.13 is decent for casual 30 fov pixel center measurement, use 0 for low sens + AHK tall screen.
ANGLE_OFFSET = {float(cfg.ANGLE_OFFSET)}
"""
    path.write_text(text, encoding="utf-8")

def _ensure_list_of_pairs(obj: Any) -> List[Tuple[int,int]]:
    """
    Normalise S_RINGS to a list of (int,int) pairs. Accepts:
    - list of lists/tuples
    - string -> raises
    """
    if not isinstance(obj, (list, tuple)):
        raise TypeError("S_RINGS must be a list of pairs")
    out: List[Tuple[int,int]] = []
    for item in obj:
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            raise TypeError("Each entry in S_RINGS must be a pair [min, max]")
        a, b = int(item[0]), int(item[1])
        out.append((a, b))
    return out

def load_config_toml() -> Config:
    """
    Load config.toml and return a Config instance.
    Missing values fall back to defaults defined in Config dataclass.
    """
    path = Path("config.toml")
    # create default config file if missing
    if not path.exists():
        cfg = Config()
        write_config_toml(path, cfg)
        print(f"Wrote default config to {path}")

    raw = {}
    with path.open("rb") as f:
        raw = _toml_loader.load(f)

    defaults = Config()
    # S_RINGS
    if "S_RINGS" in raw:
        s_rings = _ensure_list_of_pairs(raw["S_RINGS"])
    else:
        s_rings = list(defaults.S_RINGS)

    # other keys with defaults
    max_rings = int(raw.get("MAX_RINGS", defaults.MAX_RINGS))
    max_results = int(raw.get("MAX_RESULTS", defaults.MAX_RESULTS))
    max_margin = float(raw.get("MAX_MARGIN", defaults.MAX_MARGIN))
    max_distance = int(raw.get("MAX_DISTANCE", defaults.MAX_DISTANCE))
    angle_offset = float(raw.get("ANGLE_OFFSET", defaults.ANGLE_OFFSET))

    # Basic validation
    if max_rings < 1:
        raise ValueError("MAX_RINGS must be >= 1")
    if max_results < 1:
        raise ValueError("MAX_RESULTS must be >= 1")
    if max_margin < 0:
        raise ValueError("MAX_MARGIN must be non-negative")
    if max_distance < 0:
        raise ValueError("MAX_MARGIN must be non-negative")

    return Config(
        S_RINGS = s_rings,
        MAX_RINGS = max_rings,
        MAX_RESULTS = max_results,
        MAX_MARGIN = max_margin,
        ANGLE_OFFSET = angle_offset,
        MAX_DISTANCE = max_distance,
    )

CFG = load_config_toml()