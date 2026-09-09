"""Catplotlib: a theme and artist toolkit for ordinary Matplotlib."""
from .theme import PALETTES, palette, cmap, rc, use, context
from .artists import COMPANIONS, MOODS, cat, catify, perch, paw_marker
from .scenes import POSES, pose, pose_svg, mesh_cat, cat_duel
from .yarn import yarn_ball, yarn_stem, YarnStems
from .finishes import bubble_bars, dreamy_line

__version__ = "0.5.1"
__all__ = ["PALETTES", "COMPANIONS", "MOODS", "POSES", "palette", "cmap", "rc", "use", "context", "cat", "catify", "perch", "paw_marker", "pose", "pose_svg", "mesh_cat", "cat_duel", "yarn_ball", "yarn_stem", "YarnStems", "bubble_bars", "dreamy_line"]
