"""Fixed-size vector cat annotations and efficient single-colour paw markers.

The SVG reader intentionally supports only the paths, circles and ellipses in
our bundled illustrations. It is not a general purpose SVG import function.
"""
from functools import lru_cache
from importlib.resources import files
from itertools import count
import math
import re
import xml.etree.ElementTree as ET
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Ellipse
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.transforms import Affine2D

COMPANIONS = ("mochi", "beans", "nugget", "tofu")
MOODS = ("happy", "sleepy", "surprised")
_ids = count()

def _path(data):
    tokens = re.findall(r"[a-zA-Z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?", data)
    vertices, codes = [], []
    p = np.zeros(2); start = p.copy(); i = 0; command = None
    lengths = {"M": 2, "L": 2, "H": 1, "V": 1, "Q": 4, "C": 6}
    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]; i += 1
            if command.upper() == "Z":
                vertices.append(start.copy()); codes.append(Path.CLOSEPOLY); p = start.copy(); command = None
                continue
        if command is None or command.upper() not in lengths:
            raise ValueError(f"Unsupported bundled SVG path command: {command!r}")
        upper = command.upper(); n = lengths[upper]
        args = np.array([float(v) for v in tokens[i:i+n]]); i += n
        relative = command.islower()
        if upper in ("H", "V"):
            q = p.copy(); axis = 0 if upper == "H" else 1
            q[axis] = args[0] + (p[axis] if relative else 0)
            vertices.append(q.copy()); codes.append(Path.LINETO); p = q
        else:
            points = args.reshape(-1, 2) + (p if relative else 0)
            code = {"M": Path.MOVETO, "L": Path.LINETO, "Q": Path.CURVE3, "C": Path.CURVE4}[upper]
            vertices.extend(points.copy()); codes.extend([code] * len(points)); p = points[-1].copy()
            if upper == "M":
                start = p.copy(); command = "l" if relative else "L"
    return Path(vertices, codes)

def _transform(raw):
    matrix = np.eye(3)
    for name, values in re.findall(r"(translate|scale|rotate)\(([^)]*)\)", raw):
        a = [float(v) for v in re.split(r"[\s,]+", values.strip())]
        m = np.eye(3)
        if name == "translate": m[:2, 2] = (a[0], a[1] if len(a) > 1 else 0)
        elif name == "scale": m[0, 0], m[1, 1] = a[0], a[1] if len(a) > 1 else a[0]
        else:
            t = Affine2D().rotate_deg_around(a[1], a[2], a[0]) if len(a) == 3 else Affine2D().rotate_deg(a[0])
            m = t.get_matrix()
        matrix = matrix @ m
    return matrix

@lru_cache(maxsize=12)
def _components(companion, mood):
    if companion not in COMPANIONS: raise ValueError(f"companion must be one of {COMPANIONS}")
    if mood not in MOODS: raise ValueError(f"mood must be one of {MOODS}")
    root = ET.fromstring((files("catplotlib") / "assets" / f"{companion}-{mood}.svg").read_text())
    return _read_components(root)

def _read_components(root):
    """Read the supported primitives of a trusted, bundled cat illustration."""
    parts = []
    def visit(el, inherited, matrix):
        attrs = {**inherited, **{k: v for k, v in el.attrib.items() if k in ("fill", "stroke", "stroke-width", "opacity", "stroke-linecap", "stroke-linejoin")}}
        matrix = matrix @ _transform(el.get("transform", ""))
        tag = el.tag.rsplit("}", 1)[-1]
        if tag == "path": parts.append(("path", _path(el.attrib["d"]), attrs, matrix))
        elif tag in ("circle", "ellipse"):
            rx = float(el.get("rx", el.get("r", 0))); ry = float(el.get("ry", el.get("r", 0)))
            parts.append(("ellipse", (float(el.get("cx", 0)), float(el.get("cy", 0)), rx, ry), attrs, matrix))
        elif tag not in ("svg", "g", "title", "desc"): raise ValueError(f"Unexpected bundled SVG element: {tag}")
        for child in el: visit(child, attrs, matrix)
    visit(root, {"fill": "black", "stroke": "none", "stroke-width": "1", "opacity": "1"}, np.eye(3))
    return tuple(parts)

def cat(ax, xy=(.91, .9), *, companion="mochi", mood="happy", size=40,
        coords="axes fraction", offset=(0, 0), zorder=10, clip=False):
    """Place a multicolour vector cat, sized in points, on any Matplotlib Axes.

    Use coords='data' to follow a 2D data point through zoom/pan/log transforms.
    For 3D axes, use axes-fraction decorations; data-attached 3D cats are not
    implemented. Returns a removable AnnotationBbox.
    """
    if not math.isfinite(size) or size <= 0: raise ValueError("size must be finite and positive")
    if getattr(ax, "name", "") == "3d" and coords == "data":
        raise ValueError("3D cats support coords='axes fraction', not data coordinates")
    area = DrawingArea(size, size * .94, 0, 0)
    flip = Affine2D().scale(size / 100, -size / 100).translate(0, size * .94)
    for kind, geometry, a, matrix in _components(companion, mood):
        kw = dict(facecolor=a.get("fill", "none"), edgecolor=a.get("stroke", "none"),
                  linewidth=float(a["stroke-width"]) * size / 100,
                  alpha=float(a.get("opacity", 1)), capstyle="round", joinstyle="round")
        artist = PathPatch(geometry, **kw) if kind == "path" else Ellipse(geometry[:2], geometry[2]*2, geometry[3]*2, **kw)
        artist.set_transform(Affine2D(matrix) + flip + area.get_transform())
        area.add_artist(artist)
    box = AnnotationBbox(area, xy, xybox=offset, xycoords=coords, boxcoords="offset points",
                         frameon=False, pad=0, annotation_clip=clip, zorder=zorder)
    box.set_gid(f"catplotlib-cat-{next(_ids)}")
    box.set_in_layout(False)
    ax.add_artist(box)
    return box

def catify(line, *, companion="mochi", mood="happy", size=28, every=1, max_cats=80):
    """Attach vector cats to an existing 2D Line2D; return removable artists.

    Data are sampled explicitly with every; refuse excessive artist counts so
    large data sets do not silently become expensive or misleading. If the
    line's data later changes, remove/recreate these annotations.
    """
    if isinstance(every, bool) or not isinstance(every, (int, np.integer)) or every < 1:
        raise ValueError("every must be a positive integer")
    if isinstance(max_cats, bool) or not isinstance(max_cats, (int, np.integer)) or max_cats < 1:
        raise ValueError("max_cats must be a positive integer")
    if line.axes is None: raise ValueError("line must belong to an Axes")
    if getattr(line.axes, "name", "") == "3d": raise ValueError("catify supports 2D lines only")
    data = line.get_xydata()[::every]
    data = data[np.isfinite(data).all(axis=1)]
    if len(data) > max_cats: raise ValueError(f"{len(data)} cats exceeds max_cats={max_cats}; increase every or use paw_marker()")
    return [cat(line.axes, p, coords="data", companion=companion, mood=mood, size=size) for p in data]

def paw_marker():
    """A real Matplotlib Path marker suitable for plot/scatter and large datasets."""
    parts = [_path("M13 23q7-13 14 0c2 3 7 8 2 11-4 3-6-1-9-1c-3 0-5 3-9 0c-5-3-1-7 2-10Z")]
    for x, y, angle in [(9, 13, -25), (17, 7, -10), (26, 8, 12), (33, 15, 26)]:
        t = Affine2D().scale(4, 5.4).rotate_deg(angle).translate(x, y)
        parts.append(Path.unit_circle().transformed(t))
    return Path.make_compound_path(*parts).transformed(Affine2D().translate(-21, -20).scale(1/42, -1/42))

def perch(bars, *, companion="mochi", size=30, max_cats=80):
    """Perch vector cats at bar endpoints, including negative/horizontal bars."""
    if len(bars.patches) > max_cats: raise ValueError("Too many bars; decorate a subset explicitly with cat()")
    output = []
    horizontal = getattr(bars, "orientation", "vertical") == "horizontal"
    for bar in bars.patches:
        if horizontal:
            x, y = bar.get_x() + bar.get_width(), bar.get_y() + bar.get_height()/2
            offset = (math.copysign(size*.48, bar.get_width()), 0)
        else:
            x, y = bar.get_x() + bar.get_width()/2, bar.get_y() + bar.get_height()
            offset = (0, math.copysign(size*.44, bar.get_height()))
        output.append(cat(bar.axes, (x, y), coords="data", offset=offset, size=size, companion=companion))
    return output
