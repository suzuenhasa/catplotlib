"""Matplotlib-native styling. Importing Catplotlib changes no global settings."""
from contextlib import contextmanager
from importlib.resources import files
import matplotlib as mpl
from cycler import cycler
from matplotlib.colors import LinearSegmentedColormap

PALETTES = {
    "milk_tea": ("#b49ad2", "#81b4cf", "#a8bb86", "#ef9dac", "#f0ba72"),
    "strawberry": ("#e88cac", "#f5b4bd", "#c8a2d6", "#efa27d", "#adc7aa"),
    "blueberry": ("#8d9bd2", "#9cc6d6", "#b2a2d5", "#8bbdb4", "#e0c0d6"),
    "matcha": ("#9eaf7e", "#c3cba1", "#ddb781", "#89b9a7", "#c5a7bb"),
}

def palette(name="milk_tea"):
    """Return the five categorical colours in a named palette."""
    try:
        return PALETTES[name]
    except KeyError:
        raise ValueError(f"Unknown palette {name!r}; choose from {tuple(PALETTES)}") from None

def cmap(name="milk_tea", *, kind="sequential"):
    """Return a colormap without modifying Matplotlib's global registry."""
    c = palette(name)
    if kind == "sequential":
        stops = ["#fff8e9", c[0], "#66507f"]
    elif kind == "diverging":
        stops = [c[1], "#fff8e9", c[3]]
    elif kind == "warm":
        stops = ["#fff2b6", "#ffd16b", "#f6ab44", "#df7430", "#ae4d30"]
    else:
        raise ValueError("kind must be 'sequential', 'diverging', or 'warm'")
    return LinearSegmentedColormap.from_list(f"catplotlib_{name}_{kind}", stops)

def rc(palette_name="milk_tea", *, grid=True):
    """Build validated rcParams for new figures. Explicit artist colours win."""
    values = dict(mpl.rc_params_from_file(str(files("catplotlib") / "catplotlib.mplstyle"), use_default_template=False))
    values["axes.prop_cycle"] = cycler(color=palette(palette_name))
    values["axes.grid"] = bool(grid)
    return values

def use(palette="milk_tea", *, grid=True):
    """Apply colours/fonts globally; add bubble_bars/dreamy_line separately."""
    mpl.rcParams.update(rc(palette, grid=grid))

@contextmanager
def context(palette="milk_tea", *, grid=True):
    """Temporarily apply colours/fonts; add bubble_bars/dreamy_line separately.

    Restores rcParams even when plotting fails. Illustrated finishes are
    explicit artist helpers and are not activated by the theme alone.
    """
    with mpl.rc_context(rc(palette, grid=grid)):
        yield
