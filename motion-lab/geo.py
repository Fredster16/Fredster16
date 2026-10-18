"""World land data -> dot-matrix map (Natural Earth 110m via world-atlas, ISC licence)."""
import json
import os

import numpy as np
from PIL import Image, ImageDraw

from engine import ROOT

LAND_JSON = os.path.join(ROOT, "assets", "land-110m.json")
RES = 4  # mask pixels per degree


def _decode_arcs(topo):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for arc in topo["arcs"]:
        a = np.cumsum(np.array(arc, float), axis=0)
        arcs.append(np.column_stack([a[:, 0] * sx + tx, a[:, 1] * sy + ty]))
    return arcs


def _ring(arcs, idxs):
    pts = []
    for i in idxs:
        seg = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(seg[1:] if pts else seg)
    return np.array(pts)


def land_mask():
    """Boolean array [lat, lon] at RES px/degree, row 0 = 90N, col 0 = 180W."""
    topo = json.load(open(LAND_JSON))
    arcs = _decode_arcs(topo)
    img = Image.new("L", (360 * RES, 180 * RES), 0)
    draw = ImageDraw.Draw(img)
    geoms = topo["objects"]["land"]
    geoms = geoms["geometries"] if geoms["type"] == "GeometryCollection" else [geoms]
    for g in geoms:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        for poly in polys:
            for k, ring_idx in enumerate(poly):
                r = _ring(arcs, ring_idx)
                if r[:, 1].mean() < -60:  # Antarctica wraps the pole; never on screen
                    continue
                # unwrap rings that cross the date line, then draw at -360/0/+360 so both halves land
                lon = r[:, 0].copy()
                d = np.diff(lon)
                lon[1:] -= 360 * np.cumsum(np.round(d / 360))
                for shift in (-360, 0, 360):
                    xy = [((x + shift + 180) * RES, (90 - y) * RES) for x, y in zip(lon, r[:, 1])]
                    draw.polygon(xy, fill=0 if k else 1)
    return np.array(img, bool)


def dot_grid(spacing_deg, lon_range=(-180, 180), lat_range=(-58, 80)):
    """(lon, lat) of every grid point that falls on land, rows offset like halftone."""
    mask = land_mask()
    dots = []
    lat = lat_range[1]
    row = 0
    while lat >= lat_range[0]:
        lon = lon_range[0] + (spacing_deg / 2 if row % 2 else 0)
        while lon <= lon_range[1]:
            y = int((90 - lat) * RES)
            x = int((lon + 180) * RES) % (360 * RES)
            if 0 <= y < mask.shape[0] and mask[y, x]:
                dots.append((lon, lat))
            lon += spacing_deg
        lat -= spacing_deg
        row += 1
    return dots
