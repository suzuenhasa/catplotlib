"""52 runnable examples, rendered by Matplotlib rather than browser lookalikes."""
from pathlib import Path
import textwrap
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
from matplotlib.tri import Triangulation
import catplotlib as cp

PLOTS = []

def add(id, method, title, category, setup, body, description, projection=None):
    PLOTS.append(dict(id=id, method=method, title=title, category=category,
                      setup=textwrap.dedent(setup).strip(), body=textwrap.dedent(body).strip(),
                      description=description, projection=projection))

add("plot", "plot()", "The daily purr forecast", "Everyday", """
x = np.arange(7)
y = 4 + np.sin(x)*2 + rng.normal(0, .3, len(x))
""", """
line, = ax.plot(x, y)
if companions: cp.catify(line, companion="mochi", size=26)
ax.set(xlabel="Time (naps)", ylabel="Mood (purrs)", ylim=(0, 9))
""", "A connected series, with data-attached vector cat faces.")
add("scatter", "scatter()", "Peer-reviewed paw prints", "Everyday", """
x = rng.uniform(0, 10, 50)
y = .65*x + rng.normal(0, 1.3, len(x))
""", """
ax.scatter(x, y, marker=cp.paw_marker() if companions else 'o', s=160, color=colours[0], alpha=.8)
ax.set(xlabel="Chaos level", ylabel="Zoomies")
""", "Efficient paw-shaped Path markers use ordinary scatter collections.")
add("bar", "bar()", "Treats for the whole squad", "Everyday", """
names = ["Mochi", "Beans", "Nugget", "Tofu"]
y = rng.integers(5, 17, 4)
""", """
bars = ax.bar(names, y, color=colours[:4], width=.6)
ax.set(ylabel="Treats earned", ylim=(0, 22))
bars[1].set_gid("catplotlib-duel-bar")
if companions:
    for i in [0, 2, 3]: cp.cat(ax, (i, y[i]), coords="data", size=25, offset=(0,11))
    lower, upper = cp.cat_duel(ax, (1, 0), lambda: (1, bars[1].get_height()),
                               ground_size=38, top_size=49, ground_offset=(31,0))
    lower.set_gid("catplotlib-cat-duel-lower")
    upper.set_gid("catplotlib-cat-duel-upper")
""", "Mochi stretches up for a swat. Lower Beans' bar and Nugget arches up: personal space, please.")
add("barh", "barh()", "The snack leaderboard", "Everyday", "y = rng.integers(6, 17, 4)", """
bars = ax.barh(["Mochi", "Beans", "Nugget", "Tofu"], y, color=colours[:4], height=.6)
if companions: cp.perch(bars, companion="nugget", size=26)
ax.set(xlabel="Snacks located", xlim=(0, 22))
""", "Horizontal rankings, with a cat at the end of each bar.")
add("stem", "stem()", "Tiny spikes of mischief", "Everyday", "x = np.arange(9)\ny = rng.integers(2, 10, 9)", """
cp.yarn_stem(ax, x, y, color=colours[0], ball_size=17)
ax.set(xlabel="Hour", ylabel="Things knocked over", ylim=(0, 12))
""", "Gently bending yarn strings end in tiny wrapped balls, centered on the exact measurements.")
add("step", "step()", "One stair closer to dinner", "Everyday", "x = np.arange(9)\ny = np.cumsum(rng.integers(0, 3, 9))", """
ax.step(x, y, where="mid", color=colours[0])
if companions: cp.cat(ax, (x[-1], y[-1]), coords="data", companion="nugget", size=30)
ax.set(xlabel="Minutes waiting", ylabel="Meows", ylim=(0, max(y)+5))
""", "Piecewise constant values preserve Matplotlib's step semantics.")
add("fill_between", "fill_between()", "A cozy margin of uncertainty", "Everyday", "x = np.linspace(0, 10, 80)\ny = 4 + np.sin(x/2)\nspread = .4 + rng.random(80)*.25", """
ax.fill_between(x, y-spread, y+spread, alpha=.3, color=colours[0])
ax.plot(x, y, color=colours[0])
ax.set(xlabel="Time", ylabel="Purr intensity")
""", "An uncertainty band keeps the numerical geometry intact.")
add("stackplot", "stackplot()", "A full day of doing nothing", "Everyday", "x = np.arange(8)\ny = rng.uniform(1, 5, (3, 8))", """
ax.stackplot(x, y, labels=["Nap", "Snack", "Zoom"], colors=colours, alpha=.85)
ax.legend(loc="upper left", ncol=3)
ax.set(xlabel="Day", ylabel="Hours of important work")
""", "Cumulative area composition with a matching legend.")
add("stairs", "stairs()", "Measured in tiny steps", "Everyday", "values = rng.integers(1, 9, 8)\nedges = np.arange(9)", """
ax.stairs(values, edges, fill=True, color=colours[0], alpha=.65)
ax.set(xlabel="Nap interval", ylabel="Dreams")
""", "Binned values with explicit bin boundaries.")
add("grouped_bar", "bar() · grouped", "Breakfast versus second breakfast", "Everyday", "x = np.arange(4)\na = rng.integers(4, 12, 4)\nb = rng.integers(5, 14, 4)", """
ax.bar(x-.18, a, width=.35, label="Breakfast", color=colours[0])
ax.bar(x+.18, b, width=.35, label="Second breakfast", color=colours[3])
ax.set_xticks(x, ["Mochi", "Beans", "Nugget", "Tofu"])
ax.set_ylabel("Treats")
ax.legend(loc="upper left")
""", "Compare categories using ordinary grouped bars.")
add("stacked_bar", "bar() · stacked", "The anatomy of a cat day", "Everyday", "x = np.arange(4)\ny = rng.integers(2, 7, (3, 4))", """
bottom = np.zeros(4)
for values, label, colour in zip(y, ["Naps", "Snacks", "Chaos"], colours):
    ax.bar(x, values, bottom=bottom, label=label, color=colour, width=.6)
    bottom += values
ax.set_xticks(x, ["Mochi", "Beans", "Nugget", "Tofu"])
ax.set_ylabel("Hours")
ax.legend(loc="upper left", ncol=3)
""", "Stacked categories share the same theme and colour cycle.")
add("waterfall", "bar() · waterfall", "The treat budget", "Everyday", "changes = np.array([12, -3, -2, 6, -4]) + rng.integers(-1, 2, 5)\nends = np.cumsum(changes)\nstarts = ends-changes", """
for i, (start, end, change) in enumerate(zip(starts, ends, changes)):
    ax.bar(i, abs(change), bottom=min(start, end), color=colours[2] if change>=0 else colours[3], width=.65)
    ax.text(i, max(start, end)+.4, f"{change:+d}", ha="center", fontsize=10)
    if i<4: ax.plot([i+.33, i+.67], [end, end], color="#a89b8e", lw=1, ls="--")
ax.set_xticks(range(5), ["Found", "Ate", "Shared", "Found more", "Ate again"])
ax.set_ylabel("Treat balance")
""", "Positive and negative changes built from native bars.")

add("hist", "hist()", "If I fits, I sits", "Statistics", "data = rng.normal(7, 1.1, 220)", """
ax.hist(data, bins=14, color=colours[0], edgecolor="#fffdf6")
ax.set(xlabel="Box width (inches)", ylabel="Boxes investigated")
""", "Matplotlib computes the bin counts from sample data.")
add("boxplot", "boxplot()", "Whiskers, statistically speaking", "Statistics", "data = [rng.normal(m, s, 90) for m, s in [(5,1), (7,1.7), (4,.7), (6,1.2)]]", """
result = ax.boxplot(data, patch_artist=True, tick_labels=["Mochi", "Beans", "Nugget", "Tofu"], medianprops={"color":"#66507f", "linewidth":2}, flierprops={"marker":cp.paw_marker() if companions else 'o', "markersize":8, "markerfacecolor":colours[3], "markeredgecolor":"none"})
for box, colour in zip(result["boxes"], colours): box.set(facecolor=colour, edgecolor="#80776f", alpha=.7)
ax.set_ylabel("Hours napped")
""", "Real quartiles, medians, 1.5-IQR whiskers, and paw outliers.")
add("errorbar", "errorbar()", "Purrs, plus or minus a little", "Statistics", "x = np.arange(6)\ny = rng.uniform(3, 7, 6)\nerror = rng.uniform(.3, 1, 6)", """
ax.errorbar(x, y, yerr=error, fmt="o-", capsize=6, color=colours[0], ecolor=colours[1])
if companions: cp.catify(ax.lines[0], size=23, companion="tofu")
ax.set(xlabel="Session", ylabel="Purrs", ylim=(0, 10))
""", "Uncertainty stays visible beneath the cat markers.")
add("violinplot", "violinplot()", "The shape of a very good nap", "Statistics", "data = [rng.normal(5,1,120), rng.gamma(4,1,120), rng.normal(6,.6,120), rng.uniform(2,8,120)]", """
v = ax.violinplot(data, showmedians=True)
for body, colour in zip(v["bodies"], colours): body.set(facecolor=colour, edgecolor="#80776f", alpha=.75)
for key in ["cmedians", "cbars", "cmins", "cmaxes"]: v[key].set_color("#735093")
ax.set_xticks([1,2,3,4], ["Mochi", "Beans", "Nugget", "Tofu"])
ax.set_ylabel("Nap duration")
""", "Kernel density estimates rendered by Matplotlib's violin plot.")
add("eventplot", "eventplot()", "The midnight zoomies log", "Statistics", "events = [np.sort(rng.uniform(0,24,28)) for _ in range(4)]", """
ax.eventplot(events, colors=colours[:4], lineoffsets=range(4), linelengths=.65, linewidths=2)
ax.set_yticks(range(4), ["Mochi", "Beans", "Nugget", "Tofu"])
ax.set(xlabel="Hour of day", xlim=(0,24), ylim=(-.7,3.7))
""", "A raster of event timestamps for each companion.")
add("hist2d", "hist2d()", "Where the naps happen", "Statistics", "x, y = rng.multivariate_normal([5,5], [[3,1],[1,2]], 600).T", """
h = ax.hist2d(x, y, bins=18, cmap=cp.cmap(palette_name))
fig.colorbar(h[3], ax=ax, label="Nap count", shrink=.8)
ax.set(xlabel="Sunlight", ylabel="Softness")
""", "Two-dimensional sample counts in rectangular bins.")
add("hexbin", "hexbin()", "A honeycomb of cozy spots", "Statistics", "x, y = rng.multivariate_normal([5,5], [[3,1.5],[1.5,2]], 800).T", """
h = ax.hexbin(x, y, gridsize=19, cmap=cp.cmap(palette_name), mincnt=1, linewidths=.4)
fig.colorbar(h, ax=ax, label="Cats observed", shrink=.8)
ax.set(xlabel="Sunlight", ylabel="Coziness")
""", "Hexagonal binning handles dense clouds without a cat on every point.")
add("pie", "pie()", "A tightly scheduled day", "Statistics", "values = rng.integers(10, 40, 5)", """
ax.pie(values, labels=["Sleep", "Eat", "Zoom", "Cuddle", "Chaos"], colors=colours, autopct="%1.0f%%", startangle=90, textprops={"fontsize":10})
ax.set_aspect("equal")
""", "Proportional slices with consistent category colours.")
add("ecdf", "ecdf()", "Eventually, every cat naps", "Statistics", "data = rng.gamma(3, 1.5, 120)", """
ax.ecdf(data, color=colours[0])
ax.set(xlabel="Minutes until asleep", ylabel="Proportion of cats", ylim=(0,1.08))
""", "An exact empirical cumulative distribution, computed from samples.")
add("donut", "pie() · donut", "The circle of nap", "Statistics", "values = rng.integers(10,35,4)", """
ax.pie(values, labels=["Nap", "Snack", "Zoom", "Repeat"], colors=colours, startangle=90, wedgeprops={"width":.35})
if companions: cp.cat(ax, (0,0), coords="data", companion="nugget", size=65)
ax.set_aspect("equal")
""", "A real donut chart with a vector companion in the centre.")

field_setup = """
x = np.linspace(-3,3,32)
X, Y = np.meshgrid(x,x)
Z = np.exp(-((X-.5)**2+(Y+.3)**2)) - .55*np.exp(-((X+1.4)**2+(Y-1)**2))
Z += .08*np.sin(X*3 + seed)
"""
for id, method, title, body, desc in [
    ("imshow", "imshow()", "A map of maximum coziness", 'm = ax.imshow(Z, extent=(-3,3,-3,3), origin="lower", cmap=cp.cmap(palette_name))', "Image data use the selected sequential colormap."),
    ("pcolormesh", "pcolormesh()", "A patchwork of purrs", 'm = ax.pcolormesh(X, Y, Z, cmap=cp.cmap(palette_name), shading="auto")', "Coloured grid cells remain separate vector polygons in SVG."),
    ("contour", "contour()", "Contours of a cozy afternoon", 'm = ax.contour(X, Y, Z, levels=8, cmap=cp.cmap(palette_name))\nax.clabel(m, fontsize=8)', "Contour levels and labels are calculated by Matplotlib."),
    ("contourf", "contourf()", "Little islands of warmth", 'm = ax.contourf(X, Y, Z, levels=9, cmap=cp.cmap(palette_name))', "Filled contours represent actual field thresholds."),
]:
    add(id, method, title, "Fields", field_setup, body+'\nfig.colorbar(m, ax=ax, shrink=.8, label="Cozy index")\nax.set(xlabel="Window distance", ylabel="Blanket distance")', desc)

vector_setup = "x = np.linspace(-2,2,13)\nX,Y = np.meshgrid(x,x)\nU = -Y\nV = X + .2*np.sin(seed)"
add("quiver", "quiver()", "The direction of the zoomies", "Fields", vector_setup, """
ax.quiver(X,Y,U,V, color=colours[0], width=.006, pivot="middle")
ax.set(xlabel="Living room X", ylabel="Living room Y", aspect="equal")
""", "Arrow direction and length encode a real vector field.")
add("barbs", "barbs()", "A light breeze of mischief", "Fields", vector_setup, """
ax.barbs(X,Y,U*14,V*14, length=5, barbcolor=colours[0], flagcolor=colours[3])
ax.set(xlabel="Window X", ylabel="Window Y", aspect="equal")
""", "Meteorological barbs preserve their standard magnitude encoding.")
add("streamplot", "streamplot()", "Follow the invisible laser", "Fields", vector_setup, """
ax.streamplot(X,Y,U,V, color=np.hypot(U,V), cmap=cp.cmap(palette_name), density=.9, linewidth=1.6)
ax.set(xlabel="Floor X", ylabel="Floor Y", aspect="equal")
""", "Integrated streamlines show the flow through a vector field.")
add("spy", "spy()", "Evidence of tiny footprints", "Fields", "matrix = rng.random((25,35)) < .08", """
ax.spy(matrix, marker=cp.paw_marker() if companions else 'o', markersize=7, color=colours[0])
ax.set(xlabel="Column", ylabel="Row")
""", "A sparse matrix pattern, with paw-shaped nonzero entries.")
add("matshow", "matshow()", "The cuddle correlation matrix", "Fields", "data = rng.normal(size=(50,6))\nmatrix = np.corrcoef(data.T)", """
m = ax.matshow(matrix, cmap=cp.cmap(palette_name, kind="diverging"), vmin=-1, vmax=1)
for i in range(6):
    for j in range(6): ax.text(j,i,f"{matrix[i,j]:.1f}",ha="center",va="center",fontsize=9)
fig.colorbar(m,ax=ax,shrink=.8,label="Correlation")
ax.set(xlabel="Companion", ylabel="Companion")
""", "Diverging colours centre on zero; values remain legible.")

tri_setup = "x,y = rng.uniform(-2,2,(2,90))\nz = np.exp(-x*x-y*y)\ntri = Triangulation(x,y)"
for id, title, body, desc in [
    ("tricontour", "Contour lines, off the grid", 'm = ax.tricontour(tri,z,levels=8,cmap=cp.cmap(palette_name))\nax.clabel(m,fontsize=8)', "Contours interpolated on an unstructured triangulation."),
    ("tricontourf", "An unstructured cuddle puddle", 'm = ax.tricontourf(tri,z,levels=9,cmap=cp.cmap(palette_name))', "Filled contour regions on irregular coordinates."),
    ("tripcolor", "A quilt of cozy triangles", 'm = ax.tripcolor(tri,z,cmap=cp.cmap(palette_name),shading="flat",edgecolors="#fffdf6",linewidth=.4)', "Triangles intentionally encode a scalar field; their fills are explicit."),
    ("triplot", "The secret feline network", 'ax.triplot(tri,color=colours[0],linewidth=.8)\nax.scatter(x,y,s=8,color=colours[3])', "A triangulation mesh shows connections between irregular samples."),
]:
    add(id, id+'()', title, "Unstructured", tri_setup, body+'\nax.set(xlabel="X",ylabel="Y",aspect="equal")', desc)

helix = "t = np.linspace(0,4*np.pi,100)\nx,y,z = np.cos(t),np.sin(t),t/4\nz += .1*np.sin(seed)"
add("plot3d", "plot() · 3D", "An upward spiral of zoomies", "3D", helix, 'ax.plot(x,y,z,color=colours[0],lw=2.5)', "A native 3D line with Matplotlib's perspective projection.", "3d")
add("scatter3d", "scatter() · 3D", "Cats in three dimensions", "3D", "x,y,z = rng.normal(size=(3,90))", 'ax.scatter(x,y,z,c=z,cmap=cp.cmap(palette_name),s=35,depthshade=True)', "A depth-shaded 3D point cloud.", "3d")
add("bar3d", "bar3d()", "The treat towers", "3D", "x,y = np.meshgrid(np.arange(4),np.arange(4))\nx,y = x.ravel(),y.ravel()\nz = rng.integers(1,8,len(x))", '''ax.bar3d(x,y,np.zeros_like(z),.65,.65,z,color=[colours[i%5] for i in range(len(x))],shade=True,edgecolor="#fffdf6",linewidth=.4)
ax.set(xlim=(-.5,4.8), ylim=(-1,3.8), zlim=(0,max(z)+2))
if companions:
    cp.pose(ax, (3.325,1.325,float(z[7])), pose="sitting", companion="mochi", size=28, mirror=True)
    cp.pose(ax, (3.325,.325,float(z[3])), pose="sprawled", companion="nugget", size=43)''', "Nugget stretches out on a tall tower while Mochi sits on the neighboring shorter bar, looking up. Both cats are anchored to the bar tops.", "3d")
add("fill_between3d", "fill_between() · 3D", "A ribbon of purrs", "3D", "t = np.linspace(0,2*np.pi,45)\nz = np.sin(t + seed*.1)", 'ax.fill_between(t,np.zeros_like(t),z,t,np.ones_like(t)*2,z+.6,facecolors=colours[0],alpha=.75)', "A native 3D fill_between ribbon; requires Matplotlib 3.10 or later.", "3d")
add("quiver3d", "quiver() · 3D", "Mischief in every direction", "3D", "x,y,z = np.meshgrid(np.linspace(-1,1,4),np.linspace(-1,1,4),np.linspace(-1,1,3))", 'ax.quiver(x,y,z,-y,x,.5+z*.2,length=.3,color=colours[0],normalize=True)', "A three-dimensional direction field.", "3d")
add("stem3d", "stem() · 3D", "A forest of tiny purrs", "3D", "t = np.linspace(0,2*np.pi,14)\nx,y = np.cos(t),np.sin(t)\nz = rng.uniform(.5,2.5,14)", 'cp.yarn_stem(ax, x, y, z, color=colours[0], ball_size=12, waviness=.055, linewidth=1.4)', "Little yarn balls sit on subtly bending 3D strings. Their data anchors follow camera rotation in Matplotlib.", "3d")
add("surface", "plot_surface()", "Mount Napmore", "3D", field_setup, 'ax.plot_surface(X,Y,Z,cmap=cp.cmap(palette_name),edgecolor="none",antialiased=True)', "A gridded surface coloured by its height.", "3d")
add("trisurf", "plot_trisurf()", "An irregular mountain of naps", "3D", tri_setup, 'ax.plot_trisurf(tri,z,cmap=cp.cmap(palette_name),edgecolor="#fffdf6",linewidth=.25)', "A 3D surface made from an irregular triangulation.", "3d")
add("wireframe", "plot_wireframe()", "The blueprint of a nap", "3D", field_setup, '''ax.plot_wireframe(X,Y,Z,rstride=3,cstride=3,color=colours[0],linewidth=.8)
if companions: cp.mesh_cat(ax, companion="mochi", size=64)''', "Mochi lies belly-up along the front floor corner, curling little paws toward the wireframe strings.", "3d")
add("voxels", "voxels()", "A very chunky little world", "3D", "x,y,z = np.indices((6,6,6))\nfilled = ((x-2.5)**2+(y-2.5)**2+(z-2.5)**2)<7\nfacecolors = np.where(z<3,colours[0],colours[3])", 'ax.voxels(filled,facecolors=facecolors,edgecolor="#fffdf6",linewidth=.5)', "A true volumetric voxel rendering.", "3d")

add("polar", "plot() · polar", "Orbiting the treat jar", "Special", "theta = np.linspace(0,2*np.pi,160)\nr = 1.4+.4*np.cos(5*theta + seed*.1)", 'ax.plot(theta,r,color=colours[0])\nax.fill(theta,r,color=colours[0],alpha=.2)\nax.set_ylim(0,2.2)\nax.set_rticks([.5,1,1.5,2])', "Radial coordinates with normal Matplotlib polar axes.", "polar")
add("radar", "plot() · radar", "The companion skill tree", "Special", "theta = np.linspace(0,2*np.pi,5,endpoint=False)\nvalues = rng.uniform(3,9,5)\nangles = np.r_[theta,theta[0]]\nclosed = np.r_[values,values[0]]", 'ax.plot(angles,closed,color=colours[0])\nax.fill(angles,closed,color=colours[0],alpha=.25)\nax.set_xticks(theta,["Naps","Snacks","Zoomies","Cuddles","Chaos"])\nax.set_ylim(0,10)', "A radar chart assembled from polar plotting primitives.", "polar")
add("sankey", "Sankey()", "Where all the energy went", "Special", "sleep = .5 + rng.uniform(-.1,.1)\nsnacks = .2\nchaos = 1-sleep-snacks", 'ax.set_axis_off()\nSankey(ax=ax,scale=1.2,offset=.2,format="%.2f").add(flows=[1,-sleep,-snacks,-chaos],labels=["Energy","Naps","Snacks","Chaos"],orientations=[0,1,0,-1],facecolor=colours[0],edgecolor="#80776f",alpha=.8).finish()', "Conserved flows rendered with Matplotlib's native Sankey class.")
add("broken_barh", "broken_barh()", "A busy schedule of absolutely nothing", "Special", "shifts = rng.integers(0,2,4)", 'for i, shift in enumerate(shifts):\n    ax.broken_barh([(1+shift,3),(7+shift,4),(15+shift,5)],(i-.3,.6),facecolors=colours[i])\nax.set_yticks(range(4),["Mochi","Beans","Nugget","Tofu"])\nax.set(xlabel="Hour",xlim=(0,24))', "Time intervals make a simple Gantt-style nap schedule.")
signal_setup = "fs = 1000\nt = np.arange(2000)/fs\nsignal = np.sin(2*np.pi*80*t) + .5*np.sin(2*np.pi*(160+30*t)*t) + rng.normal(0,.15,len(t))"
add("specgram", "specgram()", "A spectrogram of synthetic purrs", "Special", signal_setup, 'ax.specgram(signal,NFFT=128,Fs=fs,noverlap=100,cmap=cp.cmap(palette_name))\nax.set(xlabel="Time (s)",ylabel="Frequency (Hz)",ylim=(0,400))', "A real short-time Fourier spectrogram of a synthetic signal.")
add("psd", "psd()", "The frequencies of feline happiness", "Special", signal_setup, 'ax.psd(signal,NFFT=256,Fs=fs,color=colours[0])\nax.set(xlabel="Frequency (Hz)",ylabel="Power / frequency (dB/Hz)")', "A power spectral density estimate of the same synthetic purr.")
add("loglog", "loglog()", "Small cat, exponential attitude", "Special", "x = np.logspace(0,3,40)\ny = x**.65 * rng.uniform(.8,1.2,len(x))", 'ax.loglog(x,y,color=colours[0])\nif companions: cp.catify(ax.lines[0],every=7,size=24,companion="beans")\nax.set(xlabel="Cat confidence",ylabel="Required attention")', "Logarithmic transforms work normally; data-attached cats follow the axes.")

def _record(name):
    try: return next(p for p in PLOTS if p["id"] == name)
    except StopIteration: raise ValueError(f"Unknown plot {name!r}") from None

def code(name, *, seed=7, palette_name="milk_tea", companions=True, interactive=True):
    """Return a complete, runnable script for one gallery example."""
    r = _record(name)
    finish = ""
    if name in ("bar", "barh", "grouped_bar", "waterfall", "hist"):
        finish = "for bars_to_style in ax.containers: cp.bubble_bars(bars_to_style)"
    elif name == "stacked_bar":
        finish = '''for layer, bars_to_style in enumerate(ax.containers):
    cp.bubble_bars(bars_to_style, corners="bottom" if layer == 0 else "top" if layer == len(ax.containers)-1 else "none")'''
    elif name == "broken_barh":
        finish = "for intervals in ax.collections: cp.bubble_bars(intervals)"
    elif name in ("plot", "step", "errorbar", "ecdf", "loglog", "psd"):
        finish = "cp.dreamy_line(ax.lines[0])"
    projection = f', subplot_kw={{"projection": {r["projection"]!r}}}' if r["projection"] else ""
    body = f'''rng = np.random.default_rng({seed})
seed = {seed}
palette_name = {palette_name!r}
companions = {companions!r}
colours = cp.palette(palette_name)
fig, ax = plt.subplots(figsize=(7.2, 4.8){projection})
fig.subplots_adjust(left=.14, right=.85, bottom=.18, top=.76)
{r['setup']}
{r['body']}
{finish}
fig.suptitle({r['title']!r}, x=.12, y=.94, ha="left", fontsize=16, color="#735093", weight="bold")
if companions and {name!r} not in ("bar", "bar3d", "wireframe"): cp.cat(ax, (1.09, 1.15), coords="axes fraction", companion="mochi", size=43)
'''
    if r["projection"] == "3d": body += 'ax.set(xlabel="X", ylabel="Y", zlabel="Z")\nax.view_init(elev=25, azim=-55+seed%7*4)\n'
    if name == "bar" and interactive:
        body += '''
# This slider changes the bar; the cat reacts automatically on redraw.
from matplotlib.widgets import Slider
height_slider = Slider(fig.add_axes([.28, .045, .42, .025]), "Beans' treats",
                       8, 18, valinit=float(bars[1].get_height()), valstep=.1,
                       color=colours[1])
def change_height(value):
    bars[1].set_height(value)
    fig.canvas.draw_idle()
height_slider.on_changed(change_height)
'''
    imports = 'import numpy as np\nimport matplotlib.pyplot as plt\nfrom matplotlib.sankey import Sankey\nfrom matplotlib.tri import Triangulation\nimport catplotlib as cp\n\n'
    return imports + f'with cp.context({palette_name!r}):\n' + textwrap.indent(body, "    ") + '\nplt.show()\n'

def draw(name, *, seed=7, palette_name="milk_tea", companions=True):
    """Create a real figure. Caller owns and closes the returned Figure."""
    namespace = {}
    source = code(name, seed=seed, palette_name=palette_name, companions=companions, interactive=False).replace('\nplt.show()\n', '\n')
    exec(compile(source, f'<catplotlib example {name}>', 'exec'), namespace)
    return namespace["fig"], namespace["ax"]
