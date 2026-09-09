# Catplotlib

A working Matplotlib theme and vector cat toolkit. This is the **0.5.1**
implementation of the Catplotlib playground, not a replacement plotting engine.

Version **0.5.1** updates every starter example and the website’s copyable
Python to call the finish helpers explicitly. The quick start demonstrates
both effects and exports SVG and PNG files.

Version **0.5.0** brought the playground’s softly rounded, glossy bars to the
2D bar recipes, and fading fills with little four-point stars to the line
recipes. The yarn stems retain their subtle bend and wrapped vector balls.

The stretching cat has one continuous body outline,
with the back sloping into the tail and no separate hip contour. Nugget still
swats down or arches its back depending on the space above Mochi’s paws.
Change the bar height, zoom, or resize, and the reaction updates on redraw.
The gallery animates the swatting paw; Python exports capture the current pose.

```python
ax = fig.add_subplot(projection="3d")
ax.plot_wireframe(X, Y, Z)
cp.mesh_cat(ax, companion="mochi", size=64)  # a small corner companion

# For neighboring bars, anchor each cat to the actual bar-top height:
cp.pose(ax, (3.325, 1.325, lower_height), pose="sitting",
        companion="mochi", size=28, mirror=True)
cp.pose(ax, (3.325, .325, upper_height), pose="sprawled",
        companion="nugget", size=43)
```

`cp.pose(ax, xy, pose="sitting", ...)` places a reusable full-body illustration.
Choose `belly_up`, `swat`, `lounging`, `sitting`, `sprawled`, `stretch`,
`swat_down`, or `arched`. Its ground/perch point is anchored to `xy`.
Choose any of the four companions, set `size` in points, or use `mirror=True`.
The `belly_up` pose has its head toward the lower left and paws raised toward
the mesh. `mesh_cat()` defaults to the high-X, low-Y corner of the axes floor
and does not change axis limits; pass a three-coordinate `xyz` to choose a
different data anchor.
`cp.pose_svg(companion, pose)` returns the standalone SVG. On a 3D Axes the
three-coordinate anchor is reprojected on each draw, so it tracks camera
rotation. The illustration remains a 2D billboard drawn above the geometry,
not a 3D model with occlusion. These artists can be removed without touching
the data. The browser's “Show cats” switch hides the complete scenes.

## Glossy bars and dreamy lines

```python
bars = ax.bar(["Mochi", "Beans"], [16, 12], color=cp.palette()[:2])
cp.bubble_bars(bars)

line, = ax.plot([0, 1, 2, 3], [2, 5, 4, 7])
cp.dreamy_line(line)
```

`bubble_bars()` also accepts horizontal bars, grouped bars, histogram
patches, and rectangular collections returned by `broken_barh()`. Corner
rounding is measured in points; change it with `rounding=2.5`. For vertical
stacks, set `corners="bottom"` on the first layer, `"none"` on middle layers,
and `"top"` on the last layer to keep the stack seams joined. The original
bar containers, dimensions, legends, limits, and height/width setters work
normally. Remove the finish with `patch.set_path_effects([])`.

`dreamy_line()` adds a gradient area fading to the visible bottom of the
axes and two decorative stars. It follows redraws, logarithmic scales,
steps, and gaps in the data, while preserving the original line and markers.
Use `stars=False` for the fill alone; call `.remove()` on the returned artist
to remove the finish. The stars avoid the line and legend and are not data
markers. Both finishes remain vector artwork in SVG/PDF exports.

## Yarn stems

```python
with cp.context("milk_tea"):
    fig, ax = plt.subplots()
    yarn = cp.yarn_stem(ax, [0, 1, 2], [3, 7, 4], ball_size=17)

    fig3d, ax3d = plt.subplots(subplot_kw={"projection": "3d"})
    cp.yarn_stem(ax3d, [0, 1, 2], [0, 1, 0], [1, 3, 2],
                 ball_size=12, waviness=.055)
```

`yarn_stem()` wraps native `ax.stem()`, preserving its measurements and
autoscaling. `bottom` sets the baseline, `color` tints both ball and string,
and `waviness` sets the sideways curl as a fraction of the spacing between
distinct stems. Only the strand between baseline and endpoint wiggles;
the yarn balls stay centered on the exact data values. The return value
has `.stems` (the native container), `.balls`, and `.remove()` for cleanup.
Recreate it when changing the measurements. Use finite numeric arrays.

`cp.yarn_ball(ax, xy, color="C0", size=16)` also works as a standalone
component, accepting two or three data coordinates without changing limits.
Balls are fixed-size vector illustrations, measured in points, and export
to SVG/PDF without raster images. In 3D they face the camera and draw above
geometry; they do not simulate volumetric occlusion. The “Show cats” switch
only controls cats, so yarn remains visible in both gallery recipes.

## Reactive bar scene

```python
bars = ax.bar(["Mochi", "Beans"], [16, 12])
cp.bubble_bars(bars)
ax.set_ylim(0, 22)
lower, upper = cp.cat_duel(
    ax, (1, 0), lambda: (1, bars[1].get_height()),
    ground_size=38, top_size=49, ground_offset=(31, 0),
    close_gap=18, hysteresis=3,
)
bars[1].set_height(8)
fig.canvas.draw_idle()  # the upper cat reacts without being recreated
```

`close_gap` is the vertical clearance above the raised paws, in points.
The upper cat arches at or below that gap and resumes swatting after an
extra `hysteresis` points of space. Data and axis limits are never changed
by the artists. `upper.pose_name` reports the pose after a draw. A callable
anchor follows changing data; ordinary coordinate tuples stay fixed.
Both cats are removable artists and exports remain vector SVG/PDF.

Run `python examples/reactive_duel.py` for a live Matplotlib height slider.
The gallery's downloaded bar recipe includes the same slider. The browser
also provides a swatting-motion switch and respects reduced-motion settings.
Saved SVGs contain the chosen height and current pose, with motion removed.

## Install

Unzip this project, open a terminal in its folder, then run:

```sh
python -m pip install --upgrade .
python examples/quickstart.py
```

The quick start renders both the rounded, highlighted bars and the line with
its gradient and stars, and saves SVG and PNG copies. After updating in a
notebook, restart its kernel before importing Catplotlib again.

Requires Python 3.10+ and Matplotlib 3.10+. Tested here on Matplotlib 3.10.8 and
NumPy 2.3.5. The package has **not been published to PyPI**; do not assume that a
package with this name on a registry is this project.

## Keep your existing plotting code

```python
import matplotlib.pyplot as plt
import catplotlib as cp

with cp.context("milk_tea"):
    fig, ax = plt.subplots()
    line, = ax.plot([0, 1, 2, 3], [2, 5, 4, 8])
    cp.dreamy_line(line)
    cp.catify(line, companion="nugget", size=30)
    ax.set(xlabel="Time (naps)", ylabel="Mood (purrs)")
    ax.margins(y=.2)
    fig.savefig("purrs.svg")
    plt.show()
```

`cp.use()` applies the theme globally to new plots. `cp.context()` restores
settings when its block exits. Importing Catplotlib does not change rcParams.
For a style sheet alone: `plt.style.use("catplotlib.catplotlib")`.

**The theme alone does not add the illustrated finishes.** After creating
bars with `ax.bar()` or `ax.barh()`, call `cp.bubble_bars(bars)` for rounding
and highlights. Call `cp.dreamy_line(line)` for the gradient and stars. These
helpers are used explicitly in the quick start and gallery recipes.

If local output looks flat, check the calls above and confirm which package
your interpreter loaded:

```python
import catplotlib as cp
print(cp.__version__)  # 0.5.1 or later
print(cp.__file__)
```

## What the skin does

The style controls the paper and axes backgrounds, categorical colour cycle,
grid, lines, ticks, typography, legends and export settings. It works with
ordinary Matplotlib plot types, including plots created through pandas or
Seaborn when they respect rcParams. Explicit colours and later Seaborn themes
can override it. It styles new artists; it does not retroactively recolour an
existing figure, alter data, replace axes, or monkey-patch Matplotlib.

Four palettes: `milk_tea`, `strawberry`, `blueberry`, `matcha`.

Use `cp.cmap("milk_tea")` for sequential data, `kind="diverging"` for data
centred around a meaningful midpoint, or `kind="warm"` for the orange heat map.
Colormaps are opt-in because a decorative categorical palette is not an
appropriate default for every scalar field.

## The cat layer

| Helper | Purpose |
| --- | --- |
| `cp.cat(ax, (.9, .9), ...)` | A fixed-size cat annotation, defaulting to axes-fraction coordinates. |
| `cp.cat(ax, (x, y), coords="data", ...)` | A cat attached to a 2D data position through zoom, pan and log transforms. |
| `cp.catify(line, every=1, ...)` | Add cats to an existing 2D `Line2D`. Returns removable artists. |
| `cp.perch(bars, ...)` | Cats at vertical or horizontal bar endpoints, including negative bars. |
| `cp.paw_marker()` | A true `Path` marker usable with `plot`, `scatter`, `stem`, and similar methods. |

Choose `companion="mochi"`, `"beans"`, `"nugget"`, or `"tofu"`, and
`mood="happy"`, `"sleepy"`, or `"surprised"`. Sizes are in points, independent
of data coordinates. The original 12 SVG faces are bundled. The renderer uses
Matplotlib paths and ellipses, so cats remain vectors in SVG/PDF; PNG is also
supported. There is no browser, SVG conversion dependency, or network request.

Multicolour cats require individual artists. `catify` refuses more than 80 cats
by default; use `every=10` or efficient single-colour paw markers for dense data.
Annotations added with `catify` follow axis transforms but are snapshots of the
line's data: remove/recreate them after `line.set_data()` or in an animation.
3D plots support decorative cats in axes coordinates; projected 3D cat markers
and animated faces are not implemented. Give edge markers room with margins.
Custom cats in legends are not automatic.

## 52 plot recipes

```python
from catplotlib.gallery import PLOTS, draw, code
import matplotlib.pyplot as plt

fig, ax = draw("violinplot", seed=7, palette_name="strawberry")
plt.show()
print(code("surface"))  # complete Python source for a 3D surface
print([p["id"] for p in PLOTS])
```

The gallery covers all **37 entries in Matplotlib's main plot-types overview**,
plus 15 common variants and specialist plots:

- Everyday: line, scatter, vertical/horizontal bars, stem, step, filled bands,
  stacked areas, stairs, grouped/stacked bars, waterfall.
- Statistics: histogram, box, error bars, violin, event raster, 2D histogram,
  hexbin, pie, ECDF, donut.
- Fields: image, pseudocolour mesh, contour/filled contour, quiver, barbs,
  streamlines, sparse-matrix spy and matrix heat map.
- Unstructured: triangular contour/filled contour, tripcolor and triangulation.
- 3D: line, scatter, bars, ribbon, quiver, stem, surface, triangular surface,
  wireframe and voxels.
- Special: polar, radar, Sankey, interval/Gantt, spectrogram, PSD and log-log.

This is coverage of that catalogue and common examples, not a claim to
implement every possible composition in Matplotlib's much larger example
gallery. Statistical computations and axes remain Matplotlib's responsibility.

The website uses two pre-rendered sample datasets and four palettes for this
extended gallery. Its six original plots remain live browser demonstrations.
The Python package accepts your real data. 3D website previews are SVG snapshots;
interactive 3D rotation is available through Matplotlib's normal GUI backends.

## Validation

```sh
python -m unittest discover -s tests -v
```

Checks cover restoration of style settings, true vector SVG/PDF export for all
12 cat faces, unchanged line data and limits, log-axis positioning, horizontal
and negative bars, the dense-data guard, and rendering all 52 examples.

## Design references

- [Matplotlib style sheets](https://matplotlib.org/stable/api/style_api.html)
- [Artists as annotations](https://matplotlib.org/stable/gallery/text_labels_and_annotations/demo_annotation_box.html)
- [Matplotlib plot types](https://matplotlib.org/stable/plot_types/index.html)

No Matplotlib source files are replaced. The included artwork and examples were
created for this Catplotlib project. Released under the MIT License; see LICENSE.
