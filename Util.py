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

import math
import sys

import numpy as np
import pandas as pd
import pyperclip
import re

import os
from pandas import DataFrame

from Config import CFG

LAST_CLIPBOARD = ""

def chunks_from_ring(rmin, rmax) -> list[tuple]:
    # find chunk_x range to search
    cx_min = math.floor(-rmax / 16)
    cx_max = math.floor( rmax / 16)
    positions = []
    for cx in range(cx_min, cx_max + 1):
        bx = cx * 16 + 8 # chunk center
        # compute allowable cz range for this bx to speed up
        # ensure bx^2 + bz^2 between rmin^2 and rmax^2
        # so bz^2 between rmin^2 - bx^2 and rmax^2 - bx^2
        min_bz2 = rmin * rmin - bx * bx
        max_bz2 = rmax * rmax - bx * bx
        if max_bz2 < 0:
            continue
        # compute bounds for bz (block z coordinate)
        if min_bz2 <= 0:
            bz_min = -math.floor(math.sqrt(max_bz2))
            bz_max = math.floor(math.sqrt(max_bz2))
        else:
            bz_min = math.ceil(-math.sqrt(max_bz2))
            bz_max = math.floor(math.sqrt(max_bz2))
        # convert block z bounds to chunk z bounds (bz = 16 * cz + 8)
        cz_low = math.floor((bz_min - 8) / 16)
        cz_high = math.floor((bz_max - 8) / 16)
        for cz in range(cz_low, cz_high + 1):
            bz = cz * 16 + 8
            d = math.hypot(bx, bz)
            if rmin <= d <= rmax:
                positions.append((bx, bz))
    return positions

def line_from_point_angle(point, angle_deg, length=2500.0) -> tuple[tuple,tuple] :
    """
    point: (x, z)
    angle_deg: angle in degrees, 0° = along +x, counter‑clockwise
    length: how long to draw the segment (large -> approximates an infinite line)
    """
    x0, z0 = point
    r = np.radians(angle_deg)
    dx = -length * math.sin(r)
    dz =  length * math.cos(r)
    return (x0, z0), (x0+dx, z0+dz)

def from_rings(rings) -> DataFrame:
    df = pd.concat(
        (pd.DataFrame(lst, columns=["x", "z"]) for lst in rings),
        ignore_index=True
    )
    return df

def point_line_distance(xs, zs, p1, p2) -> np.ndarray:
    """
    xs, zs: arrays of point coordinates
    p1, p2: endpoints of line (x1,z1), (x2,z2)
    returns: distances from each point to infinite line through p1–p2
    """
    x1, z1 = p1
    x2, z2 = p2

    # vector from p1 to p2
    vx = x2 - x1
    vz = z2 - z1

    # vector from p1 to each point
    wx = xs - x1
    wz = zs - z1

    # cross product magnitude / |v|
    num = np.abs(vx * wz - vz * wx)
    den = np.hypot(vx, vz)
    return num / den

def filter_points_to_lines(df, lines) -> pd.DataFrame:
    """
    df: DataFrame with columns 'x', 'z'
    lines: list of ((x0,z0), (x1,z1)) line segments
    margin: max distance to each line

    Returns: df_filtered with a new column 'max_dist' (max distance to all lines)
    """
    xs = df['x'].to_numpy()
    zs = df['z'].to_numpy()

    dists_all = []
    for p1, p2 in lines:
        dists_all.append(point_line_distance(xs, zs, p1, p2))

    # stack -> shape (n_lines, n_points)
    dists_all = np.vstack(dists_all)  # each row = distances to one line
    # for triangulation-like constraint: points must be close to every line (AVG)
    # average distance across lines (fixed: do not divide twice)
    avg_dist = dists_all.mean(axis=0)
    mask_dist = avg_dist <= CFG.MAX_MARGIN * len(lines) # distance mask

    xs_line = [x for (x0, z0), (x1, z1) in lines for x in (x0, x1)]
    zs_line = [z for (x0, z0), (x1, z1) in lines for z in (z0, z1)]
    min_x, max_x = min(xs_line), max(xs_line)
    min_z, max_z = min(zs_line), max(zs_line)
    mask_box = ((xs >= min_x) & (xs <= max_x) & (zs >= min_z) & (zs <= max_z))
    mask = mask_dist & mask_box

    out = df.loc[mask].copy()
    out["dist"] = avg_dist[mask]
    out["overworld"] = (df["x"] - 4).astype(int).astype(str) +" "+ (df["z"] - 4).astype(int).astype(str)
    out["nether"] = (df["x"]//8).astype(int).astype(str) +" "+ (df["z"]//8).astype(int).astype(str)
    return out

def top_n_closest(df_filtered, n=5):
    """
    df_filtered must have 'dist'
    Returns: top n rows with smallest max_dist
    """
    return df_filtered.sort_values("dist").head(n)

def parse_from_clipboard():
    """
    Reads the user's clipboard, expects something like:
    '/execute in minecraft:overworld run tp @s 504.87 64.00 433.54 -444.07 -32.21'
    Returns:
        line_from_point_angle((X, Z), ANGLE, length=length)
    or None if content doesn't look valid.
    """
    global LAST_CLIPBOARD
    text = pyperclip.paste().strip()
    if text == LAST_CLIPBOARD: return None
    if not text: return None
    if str(text).find("execute") == -1: return None
    nums = re.findall(r'-?\d+(?:\.\d+)?', text)
    if len(nums) < 4: return None
    try:
        x = float(nums[0])
        z = float(nums[2])
        angle = ((float(nums[3]) + 180) % 360) - 180 + CFG.ANGLE_OFFSET
        LAST_CLIPBOARD = text
        return line_from_point_angle((x, z), angle)
    except ValueError:
        return None

def get_resource(relative_path):
    """ PyInstaller stuff --onefile"""
    try: base_path = sys._MEIPASS # PyInstaller creates a temp folder and stores path in _MEIPASS
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)