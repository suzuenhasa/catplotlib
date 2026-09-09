"""Playground-inspired finishes that preserve native Matplotlib geometry."""
from itertools import count
import numpy as np
from matplotlib.artist import Artist
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
from matplotlib.path import Path
from matplotlib.patheffects import AbstractPathEffect
from matplotlib.transforms import Affine2D, IdentityTransform, TransformedPath
from matplotlib.colors import to_rgba

_ids = count()


def _round_rect(x0, y0, x1, y1, radius, corners="all"):
    r = min(radius, (x1-x0)/2, (y1-y0)/2)
    b = r if corners in ("all", "bottom") else 0
    t = r if corners in ("all", "top") else 0
    vertices = [(x0+b,y0),(x1-b,y0),(x1,y0),(x1,y0+b),
                (x1,y1-t),(x1,y1),(x1-t,y1),(x0+t,y1),
                (x0,y1),(x0,y1-t),(x0,y0+b),(x0,y0),(x0+b,y0),(x0+b,y0)]
    return Path(vertices, [1,2,3,3,2,3,3,2,3,3,2,3,3,79])


class _BubbleEffect(AbstractPathEffect):
    def __init__(self, rounding, orientation, corners):
        super().__init__()
        self.rounding, self.orientation, self.corners = rounding, orientation, corners

    def draw_path(self, renderer, gc, tpath, affine, rgbFace=None):
        if rgbFace is None:
            renderer.draw_path(gc, tpath, affine, rgbFace)
            return
        bounds = affine.transform_path(tpath).get_extents()
        x0,y0,x1,y1 = bounds.extents
        if not np.isfinite(bounds.extents).all() or bounds.width <= 0 or bounds.height <= 0:
            return
        unit = renderer.points_to_pixels(1)
        rounded = _round_rect(x0,y0,x1,y1,self.rounding*unit,self.corners)
        colour = to_rgba(rgbFace)
        stroke = renderer.new_gc()
        stroke.copy_properties(gc)
        stroke.set_foreground(colour)
        stroke.set_linewidth(.85)
        stroke.set_joinstyle("round")
        renderer.open_group("bubble-body", gid=f"catplotlib-bubble-body-{next(_ids)}")
        renderer.draw_path(stroke, rounded, IdentityTransform(), (*colour[:3],colour[3]*.82))
        renderer.close_group("bubble-body")
        stroke.restore()
        inset = min(3.2*unit, bounds.width*.22, bounds.height*.22)
        if self.orientation == "horizontal":
            vertices = [(x0+inset,y1-inset),(x1-inset,y1-inset)]
        else:
            vertices = [(x0+inset,y0+inset),(x0+inset,y1-inset)]
        shine = renderer.new_gc()
        shine.copy_properties(gc)
        shine.set_foreground((1,1,1,colour[3]*.34))
        shine.set_linewidth(min(1.4, inset/unit*.6))
        shine.set_capstyle("round")
        renderer.open_group("bubble-shine", gid=f"catplotlib-bubble-shine-{next(_ids)}")
        renderer.draw_path(shine, Path(vertices), IdentityTransform())
        renderer.close_group("bubble-shine")
        shine.restore()


def bubble_bars(bars, *, rounding=2.5, corners="all", orientation=None):
    """Give native bars rounded corners, a tinted outline, and a white shine.

    Accepts a BarContainer, rectangle iterable (including histogram patches),
    or a rectangular PolyCollection from broken_barh. All measurements,
    limits, containers, legends, and set_height/set_width methods are retained.
    Rounding is in points. For vertical stacks, use corners='bottom', 'none',
    and 'top' on the first, middle, and last layers so the seams remain joined.
    Returns the same input; set_path_effects([]) restores a plain artist.
    """
    if not np.isfinite(rounding) or rounding < 0:
        raise ValueError("rounding must be finite and nonnegative")
    if corners not in ("all", "top", "bottom", "none"):
        raise ValueError("corners must be all, top, bottom, or none")
    if orientation is None:
        orientation = getattr(bars, "orientation", None) or ("horizontal" if isinstance(bars, PolyCollection) else "vertical")
    if orientation not in ("vertical", "horizontal"):
        raise ValueError("orientation must be vertical or horizontal")
    artists = [bars] if isinstance(bars, PolyCollection) else list(bars)
    for artist in artists:
        if artist.axes is None or artist.axes.name != "rectilinear":
            raise ValueError("bubble_bars requires ordinary 2D axes")
        if isinstance(artist, Rectangle):
            if artist.angle != 0:
                raise ValueError("rotated rectangles are not supported")
        elif isinstance(artist, PolyCollection):
            for path in artist.get_paths():
                v = np.unique(path.vertices, axis=0)
                if v.shape != (4,2) or len(np.unique(v[:,0])) != 2 or len(np.unique(v[:,1])) != 2:
                    raise ValueError("collection must contain rectangles")
        else:
            raise ValueError("expected bars, rectangles, or a rectangular collection")
    for artist in artists:
        artist.set_path_effects([_BubbleEffect(rounding,orientation,corners)])
    return bars


class _DreamyLine(Artist):
    def __init__(self, line, stars):
        super().__init__()
        self.line, self.stars = line, stars
        self.set_zorder(line.get_zorder()-.2)
        self.set_in_layout(False)
        self.set_gid(f"catplotlib-dreamy-line-{next(_ids)}")

    def draw(self, renderer):
        if not self.get_visible() or not self.line.get_visible():
            return
        ax = self.axes
        path = self.line.get_path().transformed(self.line.get_transform())
        points = path.vertices
        finite = np.isfinite(points).all(axis=1)
        if not np.any(finite):
            return
        # Separate missing-data runs; never paint a bridge across a NaN gap.
        runs = np.split(np.arange(len(points)), np.flatnonzero(np.diff(finite))+1)
        polygons = []
        floor = ax.bbox.y0
        for run in runs:
            if len(run) < 2 or not finite[run[0]]:
                continue
            p = points[run]
            polygons.append(Path(np.vstack(([p[0,0],floor],p,[p[-1,0],floor],[p[0,0],floor])),
                                 [Path.MOVETO]+[Path.LINETO]*(len(p)+1)+[Path.CLOSEPOLY]))
        colour = to_rgba(self.line.get_color(), self.line.get_alpha())
        unit = renderer.points_to_pixels(1)
        renderer.open_group("dreamy-line", gid=self.get_gid())
        if polygons:
            clip = TransformedPath(Path.make_compound_path(*polygons), IdentityTransform())
            ceiling = min(ax.bbox.y1, np.max(points[finite,1]))
            gc = renderer.new_gc()
            gc.set_clip_rectangle(ax.bbox)
            gc.set_clip_path(clip)
            gc.set_linewidth(0)
            # Small adjacent vector bands keep both SVG and PDF fully vector.
            for i in range(80):
                lo = floor+(ceiling-floor)*i/80
                hi = floor+(ceiling-floor)*(i+1)/80
                if hi <= lo:
                    continue
                band = Path([(ax.bbox.x0,lo),(ax.bbox.x1,lo),
                             (ax.bbox.x1,hi),(ax.bbox.x0,hi),(ax.bbox.x0,lo)], [1,2,2,2,79])
                renderer.draw_path(gc,band,IdentityTransform(),(*colour[:3],colour[3]*(.012+.18*((i+.5)/80)**1.3)))
            gc.restore()
        if self.stars:
            candidates = [( .13,.76),(.79,.44),(.88,.79),(.33,.84),(.60,.84),(.91,.23),(.18,.32)]
            segments = np.stack((points[:-1],points[1:]),axis=1)
            segments = segments[np.isfinite(segments).all(axis=(1,2))]
            chosen = []
            for position in candidates:
                center = ax.transAxes.transform(position)
                if len(segments):
                    a,b = segments[:,0],segments[:,1]
                    v = b-a
                    f = np.clip(np.sum((center-a)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1e-12),0,1)
                    if np.min(np.linalg.norm(center-(a+f[:,None]*v),axis=1)) < 20*unit:
                        continue
                legend = ax.get_legend()
                if legend is not None and legend.get_window_extent(renderer).padded(8*unit).contains(*center):
                    continue
                if any(np.linalg.norm(center-p) < 55*unit for p in chosen):
                    continue
                chosen.append(center)
                star = Path([(0,1),(.22,.25),(1,0),(.22,-.25),(0,-1),(-.22,-.25),(-1,0),(-.22,.25),(0,1)], [1,2,2,2,2,2,2,2,79])
                gc = renderer.new_gc()
                gc.set_linewidth(0)
                gc.set_clip_rectangle(ax.bbox)
                transform = Affine2D().scale((5 if len(chosen)==1 else 6.5)*unit).translate(*center)
                renderer.draw_path(gc,star,transform,(*colour[:3],.48))
                gc.restore()
                if len(chosen) == 2:
                    break
        renderer.close_group("dreamy-line")
        self.stale = False


def dreamy_line(line, *, stars=True):
    """Add a fading area and two decorative sparkles to a native 2D line.

    The line and data markers remain unchanged. The fill ends at the visible
    bottom of the axes and follows pan, zoom, log scales, steps, and NaN gaps.
    Returns one removable artist. Stars avoid the line and legend.
    """
    if line.axes is None or line.axes.name != "rectilinear":
        raise ValueError("dreamy_line requires a line on ordinary 2D axes")
    artist = _DreamyLine(line,stars)
    line.axes.add_artist(artist)
    return artist
