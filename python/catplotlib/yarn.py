"""Curled stem plots and fixed-size, fully vector balls of yarn."""
from dataclasses import dataclass
from itertools import count
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Circle, PathPatch
from matplotlib.transforms import Affine2D
from mpl_toolkits.mplot3d import proj3d
from .artists import _path

_ids = count()


def _mix(colour, target, fraction):
    return tuple((1 - fraction) * np.array(to_rgb(colour))
                 + fraction * np.array(to_rgb(target)))


def _ball_drawing(colour, size):
    area = DrawingArea(size, size, 0, 0)
    transform = Affine2D().scale(size / 100) + area.get_transform()
    ink = _mix(colour, "#49423f", .49)
    light = _mix(colour, "#fff9e9", .35)
    circle = Circle((50, 50), 46, facecolor=colour, edgecolor="none",
                    transform=transform)
    area.add_artist(circle)

    def curve(data, *, fill="none", stroke=ink, width=3.2):
        patch = PathPatch(_path(data), facecolor=fill, edgecolor=stroke,
                          linewidth=width * size / 100, capstyle="round",
                          joinstyle="round", transform=transform)
        patch.set_clip_path(circle)
        area.add_artist(patch)

    # Continuous nested wraps underneath a crossing band. The circular clip
    # keeps every thread inside the ball, including in SVG/PDF exports.
    curve("M 8 26 C 22 -2 70 -4 91 24 C 68 10 31 11 8 26 Z",
          fill=_mix(colour, ink, .14), stroke="none")
    for data in (
        "M -2 65 C 25 108 87 99 103 39",
        "M -4 51 C 22 97 82 90 99 28",
        "M -3 37 C 26 84 76 78 92 14",
        "M 4 21 C 32 71 68 65 78 1",
        "M 22 6 C 42 54 58 50 61 -4",
    ):
        curve(data)
    curve("M 4 21 C 44 29 70 58 80 99 L 102 72 "
          "C 85 33 56 12 26 2 Z", fill=light, width=3.5)
    for data in (
        "M 9 13 C 48 22 77 52 87 92",
        "M 17 5 C 59 18 85 47 94 83",
    ):
        curve(data, width=3.0)
    area.add_artist(Circle((50, 50), 46, facecolor="none", edgecolor=ink,
                           linewidth=size * .037, transform=transform))
    return area


class _YarnBall(AnnotationBbox):
    def draw(self, renderer):
        if len(self.point) == 3:
            x, y, _ = proj3d.proj_transform(*self.point, self.axes.get_proj())
            self.xy = (x, y)
        super().draw(renderer)


def yarn_ball(ax, xy, *, color="C0", size=16, zorder=5):
    """Center a removable vector yarn ball on a 2D or 3D data point.

    Size is in points. On 3D axes the illustration is a camera-facing
    billboard, reprojected on redraw and drawn above the plot geometry.
    This decoration does not change the axes limits.
    """
    dimensions = 3 if getattr(ax, "name", "") == "3d" else 2
    point = np.asarray(xy, dtype=float)
    if point.shape != (dimensions,) or not np.isfinite(point).all():
        raise ValueError(f"xy must contain {dimensions} finite coordinates")
    if not np.isfinite(size) or size <= 0:
        raise ValueError("size must be finite and positive")
    ball = _YarnBall(_ball_drawing(color, size), point[:2], xycoords="data",
                    xybox=(0, 0), boxcoords="offset points",
                    frameon=False, pad=0, annotation_clip=True, zorder=zorder)
    ball.point = tuple(point)
    ball.set_gid(f"catplotlib-yarn-ball-{next(_ids)}")
    ball.set_in_layout(False)
    ax.add_artist(ball)
    return ball


@dataclass
class YarnStems:
    """Native stem container plus its endpoint illustrations."""
    stems: object
    balls: list

    def remove(self):
        self.stems.remove()
        for ball in self.balls:
            ball.remove()


def yarn_stem(ax, x, y, z=None, *, bottom=0, color="C0", ball_size=16,
              waviness=.035, linewidth=1.8, label=None):
    """Draw vertical yarn stems in 2D, or in 3D when z is supplied.

    The original measurements and native stem autoscaling are preserved.
    Only the strand between baseline and endpoint curls sideways. Waviness
    is a fraction of the median spacing between distinct stem locations;
    ball_size is in points. All balls stay centered on the exact data.
    Returns YarnStems with a native .stems container and removable .balls.
    Recreate the plot if its measurements change. Numeric finite data only.
    """
    is3d = getattr(ax, "name", "") == "3d"
    if is3d != (z is not None):
        raise ValueError("Provide z exactly when using a 3D Axes")
    arrays = [np.asarray(v, dtype=float) for v in ((x, y, z) if is3d else (x, y))]
    if any(a.ndim != 1 for a in arrays) or len({a.size for a in arrays}) != 1:
        raise ValueError("coordinates must be one-dimensional arrays of equal length")
    if not arrays[0].size or not all(np.isfinite(a).all() for a in arrays):
        raise ValueError("coordinates must be nonempty and finite")
    for name, value, minimum in (("ball_size", ball_size, 0),
                                  ("linewidth", linewidth, 0)):
        if not np.isfinite(value) or value <= minimum:
            raise ValueError(f"{name} must be finite and positive")
    if not np.isfinite(bottom) or not np.isfinite(waviness) or waviness < 0:
        raise ValueError("bottom must be finite; waviness must be finite and nonnegative")
    # Validate colour before adding any artists.
    strand_colour = _mix(color, "#49423f", .12)
    positions = np.column_stack(arrays[:-1])
    distinct = np.unique(np.round(positions, 12), axis=0)
    if len(distinct) > 1:
        nearest = []
        for point in distinct:
            distances = np.linalg.norm(distinct - point, axis=1)
            nearest.append(np.min(distances[distances > 0]))
        spacing = float(np.median(nearest))
    else:
        spacing = 1.
    stems = ax.stem(*arrays, bottom=bottom, linefmt="-", markerfmt="o",
                    basefmt=" ", label=label)
    stems.markerline.set_visible(False)
    stems.stemlines.set_color(strand_colour)
    stems.stemlines.set_linewidth(linewidth)
    stems.stemlines.set_capstyle("round")
    stems.stemlines.set_gid(f"catplotlib-yarn-strings-{next(_ids)}")
    t = np.linspace(0, 1, 101)
    segments = []
    for i, point in enumerate(np.column_stack(arrays)):
        height = point[-1] - bottom
        # One restrained, broad bend, tapering to the exact endpoints.
        # Shorter strings get less lateral movement as well.
        amplitude = waviness * min(spacing, abs(height) * .65)
        wave = amplitude * np.sin(np.pi * t) * np.sin(
            (1.4 + (i % 3) * .12) * np.pi * t + i * 1.9)
        segment = np.tile(point, (len(t), 1))
        angle = i * 2.399963 if is3d else 0
        segment[:, 0] += wave * np.cos(angle)
        if is3d:
            segment[:, 1] += wave * np.sin(angle)
        segment[:, -1] = bottom + t * height
        segment[0] = (*point[:-1], bottom)
        segment[-1] = point
        segments.append(segment)
    stems.stemlines.set_segments(segments)
    balls = [yarn_ball(ax, p, color=color, size=ball_size)
             for p in np.column_stack(arrays)]
    return YarnStems(stems, balls)
