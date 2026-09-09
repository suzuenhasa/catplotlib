"""Playful vector poses that interact with a chart's geometry.

3D positions are projected on every draw, so a cat stays attached when the
Matplotlib camera moves. The cat itself is an illustrated 2D billboard.
"""
from functools import lru_cache
import math
import xml.etree.ElementTree as ET
import numpy as np
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import PathPatch, Ellipse
from matplotlib.transforms import Affine2D
from mpl_toolkits.mplot3d import proj3d
from .artists import _read_components, _ids, COMPANIONS

POSES = ("belly_up", "swat", "lounging", "sitting", "sprawled", "stretch", "swat_down", "arched")
_COATS = {
    "mochi": ("#a4a19d", "#73716e", "#fff8e8"),
    "beans": ("#55515b", "#34313a", "#eeece4"),
    "nugget": ("#f0bc6d", "#d7924e", "#fff1ca"),
    "tofu": ("#fffaf0", "#e3d5c8", "#fffaf0"),
}
_SIZES = {"belly_up": (230, 170, (122, 124)), "swat": (175, 185, (79, 170)), "lounging": (230, 145, (111, 97)), "sitting": (130, 170, (69, 153)), "sprawled": (230, 125, (110, 84)), "stretch": (130, 250, (67, 235)), "swat_down": (230, 210, (110, 95)), "arched": (235, 185, (110, 152))}

def _profile_head(coat, shade, cream, transform, *, relaxed=False):
    """A purpose-drawn side profile, looking toward the cat's raised paw."""
    eye = ('<path d="M66 45q5 4 11-2" fill="none" stroke-width="2.5"/>' if relaxed else
           '<ellipse cx="72" cy="44" rx="3.4" ry="4.6" fill="#49423f" stroke="none"/><circle cx="73" cy="42" r="1.15" fill="#fffdf6" stroke="none"/>')
    return f'''<g transform="{transform}">
    <path d="M20 59Q10 43 18 29L17 11q0-6 5-2l17 17q12-6 23 0l10-11q5-5 5 3l-1 18q10 4 9 12l10 5q7 5-1 9l-9 2q-2 14-19 15-31 3-46-20Z" fill="{coat}"/>
    <path d="m23 18 10 12-10 1m44-4 6-8v12" fill="#dfaca6" stroke="{shade}" stroke-width="1.3"/>
    <path d="M68 53q9-7 18-3l10 5-9 9q-4 12-20 13l-9-10q4-8 10-14Z" fill="{cream}" stroke="none"/>
    <path d="m43 27 3 9m9-9 1 10m-37 5 11 6m-8 4 10 4" fill="none" stroke="{shade}" stroke-width="3.5" opacity=".75"/>
    {eye}
    <ellipse cx="66" cy="60" rx="4.5" ry="2.8" fill="#e7a5a1" stroke="none" opacity=".65"/>
    <path d="m91 53 7 1-4 5Z" fill="#93686b" stroke="none"/>
    <path d="M87 63q-3 6-9 4m10-6 14-1m-16 7 14 4" fill="none" stroke-width="1.5"/>
    </g>'''

def _soft_profile_head(coat, shade, cream, transform, *, relaxed=False, angry=False):
    """Rounded three-quarter cheeks and a short muzzle, legible at chart size."""
    eyes = ('<path d="M61 47q5 5 10 0m7 0q3 3 6 0" fill="none" stroke-width="2.3"/>' if relaxed else
            '<ellipse cx="66" cy="45" rx="4.3" ry="5.1" fill="#49423f" stroke="none"/>'
            '<ellipse cx="79" cy="44" rx="2.4" ry="3.7" fill="#49423f" stroke="none"/>'
            '<circle cx="67.3" cy="43.5" r="1.35" fill="#fffdf6" stroke="none"/>'
            '<circle cx="79.5" cy="42.8" r=".9" fill="#fffdf6" stroke="none"/>')
    brows = '<path d="m59 38 12 5m6 0 8-5" stroke-width="2.8"/>' if angry else ''
    mouth = 'M75 66q4-5 9-2' if angry else 'M81 60v2q-2 4-6 1m6-1q2 3 4 1'
    return f'''<g transform="{transform}">
    <path d="M22 32 19 12q-1-5 4-3l17 14q12-4 24 1l14-11q4-3 3 3l-3 19q11 7 12 20 2 17-15 25-16 9-37 1-20-8-23-24-3-14 7-25Z" fill="{coat}"/>
    <path d="m25 16 9 10-9 3Zm45 12 7-8-1 12Z" fill="#e8b0ad" stroke="none"/>
    <path d="M65 55q12-7 23 1 4 13-13 22-10 5-18-1-5-9 0-16 3-4 8-6Z" fill="{cream}" stroke="none"/>
    <path d="m45 25 1 8m9-8 0 8m-36 13 9 3m-7 7 8 2" fill="none" stroke="{shade}" stroke-width="3.6" opacity=".7"/>
    {eyes}
    <ellipse cx="60" cy="60" rx="5" ry="3.5" fill="#e7a5a1" stroke="none" opacity=".7"/>
    <path d="M77 56q4-2 7 0 1 1-1 3l-2 1q-4-1-4-4Z" fill="#b77e83" stroke="none"/>
    {brows}
    <path d="{mouth}" fill="none" stroke-width="1.65"/>
    <path d="m61 66-9 1m11 4-8 3m31-10 8-1m-8 6 7 2" fill="none" stroke-width="1.1" opacity=".8"/>
    </g>'''

@lru_cache(maxsize=32)
def pose_svg(companion="mochi", pose="belly_up"):
    """Return a standalone SVG of a small, naturally posed cat."""
    if companion not in COMPANIONS: raise ValueError(f"companion must be one of {COMPANIONS}")
    if pose not in POSES: raise ValueError(f"pose must be one of {POSES}")
    coat, shade, cream = _COATS[companion]
    width, height, _ = _SIZES[pose]
    ink = "#49423f"
    if pose == "belly_up":
        # Head toward the foreground, rump toward the mesh. Four separate,
        # softly folded legs make the silhouette read as a cat on its back.
        art = f'''<g transform="rotate(-24 115 100)">
        <ellipse cx="113" cy="132" rx="77" ry="4" fill="#d9ccb9" opacity=".28" stroke="none"/>
        <path d="M168 112q21 7 32-5 10-12 0-24-4-6 1-9 5-3 10 4 16 23-4 39-17 13-39 5" fill="{coat}"/>
        <path d="m201 106 7 4m-3-15 8 1" fill="none" stroke="{shade}" stroke-width="4"/>
        <path d="M151 93q-15-9-15-23l-5-13q-3-10 5-12 10-1 13 11l9 14 12 13" fill="{coat}"/>
        <path d="m135 49 6 2m-7 3 7 2" fill="none" stroke-width="1.4"/>
        <path d="M87 92q-11-6-12-19l2-18q0-11 8-12 10-1 11 8-1 6-8 7l1 15 10 11" fill="{coat}"/>
        <path d="m82 46 1 7m5-7 1 7" fill="none" stroke-width="1.4"/>
        <path d="M68 104q5-22 33-23 14-1 34 1 19-10 35 4 15 16 2 33-12 13-45 13l-33-1q-24 1-31-13Z" fill="{coat}"/>
        <path d="M84 98q13-14 39-8 24-6 36 10 7 11-7 19-22 10-52 2-21-5-16-23Z" fill="{cream}" stroke="none"/>
        <path d="m116 119 4 1" fill="none" stroke="{shade}" stroke-width="1.6" opacity=".65"/>
        <path d="M151 118q-17-3-15-17 1-10 18-18l-6-15q-5-10 2-14 8-4 13 6l12 22q4 8-4 14l-12 11" fill="{coat}"/>
        <ellipse cx="153" cy="63" rx="3.5" ry="4.5" fill="#e5aaa6" stroke="none" transform="rotate(-27 153 63)"/>
        <path d="m149 57 4-2m1 4 4-2" fill="none" stroke-width="1.2"/>
        <path d="m165 108 6-4m-4 11 6-5m-56 17 1-5m10 6 1-6" fill="none" stroke="{shade}" stroke-width="3.5" opacity=".65"/>
        {_profile_head(coat, shade, cream, 'translate(20 82) rotate(-56 32 30) scale(.7)')}
        <path d="M85 115q15-1 24-14 5-9-1-19l-7-12q-5-8-12-4-7 4-2 12l5 10q3 5-3 9l-11 5" fill="{coat}"/>
        <ellipse cx="92" cy="72" rx="3.3" ry="4.3" fill="#e5aaa6" stroke="none" transform="rotate(-27 92 72)"/>
        <path d="m88 66 4-2m1 4 4-2" fill="none" stroke-width="1.2"/>
        <path d="m109 49 2-5m5 13 5-2" fill="none" stroke="#b49ad2" stroke-width="1.7"/>
        </g>'''
    elif pose == "swat":
        art = f'''
        <ellipse cx="78" cy="175" rx="57" ry="4" fill="#d9ccb9" opacity=".3" stroke="none"/>
        <path d="M43 157q-29 12-36-4-4-10 4-16 6-4 9 1 3 4-3 7-4 7 8 8l16-6" fill="{coat}"/>
        <path d="M67 87q-24 6-30 35-9 28 3 40 16 16 49 6l17-6q9-4 0-9l-16-1q13-23 12-47-4-21-20-21" fill="{coat}"/>
        <path d="M83 102q17 5 15 24l-12 30-14 6q-7-25 11-60" fill="{cream}" stroke="none"/>
        <path d="M51 127q23-5 27 14l-2 12q19-3 23 6 2 8-11 9H61" fill="{coat}"/>
        <path d="m84 160 1 6m6-7 1 6" fill="none" stroke-width="1.3"/>
        <path d="M96 107q13 25 10 47l10 3q10 6-2 11h-16q-7-2-5-10l2-25" fill="{coat}"/>
        <path d="m105 160 1 6m5-5 1 5" fill="none" stroke-width="1.3"/>
        {_profile_head(coat, shade, cream, 'translate(66 48) rotate(-28 31 38) scale(.66)')}
        <path d="M88 112q17 7 30-7l14-21q4-8 10-10 7-2 10 4 2 6-5 11l-11 23q-12 17-32 15" fill="{coat}"/>
        <path d="m142 79 4 3m-8 0 4 3" fill="none" stroke-width="1.3"/>
        <path d="m43 116 8 4m-10 5 8 3m8-28 7 5m-8 3 6 4" fill="none" stroke="{shade}" stroke-width="3.5" opacity=".7"/>
        <path d="m150 61 3-5m7 19 6-1" fill="none" stroke="#ef9dac" stroke-width="1.7"/>
        '''
    elif pose == "stretch":
        # A single torso-to-leg silhouette keeps the back sloping into the
        # tail root, with no separate round hip or internal haunch contour.
        art = f'''
        <ellipse cx="66" cy="239" rx="41" ry="3" fill="#d9ccb9" opacity=".3" stroke="none"/>
        <path d="M24 191Q5 194 5 212 3 226 15 230q10 3 17-5 4-5-1-8-4-2-7 5-7 5-10-1-6-8 3-16l12-2" fill="{coat}"/>
        <path d="m8 204 8 4m-11 8 8 0m3 12 3-6" stroke="{shade}" stroke-width="3.5" opacity=".65"/>
        <path d="M62 173q18 10 16 24l-6 21 7 12h11q6 5-1 7H74q-6-1-9-8l-7-17-4-22" fill="{coat}"/>
        <path d="m80 231 0 5m5-5 0 5" stroke-width="1.2"/>
        <path d="M72 102q9-11 13-28l6-15q-4-5 0-9 5-5 11-1 5 4 1 9l-5 21q-3 23-15 34" fill="{coat}"/>
        <path d="m92 51 2 3m3-5 1 3" stroke-width="1.1"/>
        <path d="M61 74q-19 17-26 44C31 132 29 148 28 164 27 176 24 188 22 196q1 9 18 23-3 3 0 8l5 8q1 4 8 4h21q7-2 2-7-4-3-15-3l-6-9 19-16q7-9 2-19-4-11 2-24 10-22 10-57l-4-16q-8-13-23-14Z" fill="{coat}"/>
        <path d="M73 99q11 9 5 33-8 25-12 47-11 3-13-14 4-35 12-55 3-7 8-11Z" fill="{cream}" stroke="none"/>
        <path d="m66 233 1 5m5-5 1 4" stroke-width="1.2"/>
        {_soft_profile_head(coat, shade, cream, 'translate(40 43) rotate(-43 31 38) scale(.64)')}
        <path d="M79 99q14-13 20-35l11-28 2-7q-4-5-1-9 4-6 10-3 6 4 2 11l-2 9-9 34q-6 26-23 39" fill="{coat}"/>
        <path d="m112 21 2 3m3-5 1 4" stroke-width="1.1"/>
        <path d="M88 94q6-5 9-12" stroke="{shade}" stroke-width="1.6" opacity=".6"/>
        <path d="m35 128 9 3m-11 9 9 2m-11 13 9 1m-9 9 8 1" stroke="{shade}" stroke-width="3.3" opacity=".7"/>
        '''
    elif pose == "swat_down":
        art = f'''
        <path d="M55 82q-29 2-30-14 0-10 10-13 7-2 9 3 1 5-6 6-7 4 0 8l17-1" fill="{coat}"/>
        <path d="M47 72q10-20 38-21 29 0 56 16 22 10 19 22-1 9-24 8H61q-25 0-22-13 1-6 8-12Z" fill="{coat}"/>
        <path d="M82 89q26-11 64 1l-10 6H78" fill="{cream}" stroke="none"/>
        <path d="M62 72q21-4 26 11 0 9-18 10" stroke-width="2"/>
        <path d="m91 54 2 9m10-6 1 9m10-5 0 8" stroke="{shade}" stroke-width="3.5" opacity=".7"/>
        <path d="M144 86q15 4 14 20l-2 13q0 8 7 8 7-1 8-10l2-19" fill="{coat}"/>
        {_soft_profile_head(coat, shade, cream, 'translate(135 42) rotate(34 34 37) scale(.68)')}
        <g data-part="swatting-paw">
        <path d="M157 91q18 2 20 22l-6 36-1 11q-1 10-10 9-9-2-6-12l1-12 3-31q0-8-7-11" fill="{coat}"/>
        <path d="m158 160 0 6m5-6 0 6" stroke-width="1.3"/>
        <ellipse cx="161" cy="154" rx="3.5" ry="4.3" fill="#e7a5a1" stroke="none"/>
        </g>
        '''
    elif pose == "arched":
        art = f'''
        <path d="M49 103q-23-7-24-25l-1-26q-1-8-7-9l-4-7 9 1 5-5 3 8q12 7 10 24l1 13q1 10 12 12" fill="{coat}"/>
        <path d="m28 54 10 1m-9 10 10 1m-5 11 9-2" stroke="{shade}" stroke-width="4.5" opacity=".75"/>
        <path d="M66 100 62 141l8 4q9 6-2 9H54q-9-1-8-10l-1-31" fill="{coat}"/>
        <path d="M154 105 166 142l10 3q10 6-2 9h-16q-6-1-8-9l-16-27" fill="{coat}"/>
        <path d="M39 111q-1-33 20-52l5-12 5 5 9-12 4 5q31-14 51 7l9 3 0 8q20 17 29 41l-23 20q-10-31-37-31-26 0-37 29l-9 15H41Z" fill="{coat}"/>
        <path d="M69 104q9-18 25-22 22-7 39 8l13 21-9 2q-19-22-42-11l-22 20Z" fill="{cream}" stroke="none"/>
        <path d="M51 108 42 143l6 3q8 6-2 9H33q-8-1-5-10l10-36" fill="{coat}"/>
        <path d="M154 115 175 143l8 1q11 5 2 10h-16q-6-1-11-8l-17-23" fill="{coat}"/>
        <path d="m36 148-1 5m5-4-1 5m134-5 1 5m5-5 1 5" stroke-width="1.2"/>
        <path d="m87 47 1 12m12-14-1 13m13-8-3 12m16-4-6 10" stroke="{shade}" stroke-width="4" opacity=".7"/>
        {_soft_profile_head(coat, shade, cream, 'translate(142 76) rotate(29 34 37) scale(.75)', angry=True)}
        <path d="m207 86 5-6m-1 16 7-1" stroke="#d88791" stroke-width="2"/>
        '''
    elif pose == "sitting":
        art = f'''
        <ellipse cx="69" cy="155" rx="40" ry="3" fill="#d9ccb9" opacity=".3" stroke="none"/>
        <path d="M49 138q-27 9-30-7-1-9 7-12 6-2 8 3 1 4-4 6-4 4 1 6l18-4" fill="{coat}"/>
        <path d="M81 86q14 11 14 32l-1 23 9 3q8 5 0 9H88q-6-1-5-9l1-28" fill="{coat}"/>
        <path d="M64 76q-22 11-27 40-7 23 4 31 12 9 29 6l19-4q10-6-1-9l-8-1q10-18 9-38-2-20-15-24Z" fill="{coat}"/>
        <path d="M77 91q12 4 12 22l-9 29-13 1q-4-25 10-52Z" fill="{cream}" stroke="none"/>
        <path d="M48 120q21-5 23 14l-2 8q12-2 17 4 4 7-7 8H57" fill="{coat}"/>
        <path d="M78 109q-2 13-2 31l9 4q9 5 1 10H73q-8-1-7-9l1-27" fill="{coat}"/>
        <path d="m76 148 0 5m5-5 0 4m15-5 0 5" fill="none" stroke-width="1.3"/>
        {_soft_profile_head(coat, shade, cream, 'translate(41 33) rotate(-38 31 38) scale(.7)')}
        <path d="m44 105 8 4m-10 5 8 3m4-25 6 4m-4 3 5 3" fill="none" stroke="{shade}" stroke-width="3.5" opacity=".7"/>
        <path d="m21 130 7-1m-3 8 4-5" fill="none" stroke="{shade}" stroke-width="3" opacity=".65"/>
        '''
    elif pose == "sprawled":
        art = f'''
        <path d="M58 73q-28 4-28-10 0-10 11-13 7-1 8 4 0 4-6 5-6 3-1 7l15-2" fill="{coat}"/>
        <path d="M50 64q8-18 34-19 31-2 57 12 23 6 25 19 1 10-20 10H62q-25-1-21-12 2-6 9-10Z" fill="{coat}"/>
        <path d="M84 79q27-12 63 2l-9 4H78" fill="{cream}" stroke="none"/>
        <path d="M65 62q20-5 27 8 3 10-14 12H62" fill="none" stroke-width="2"/>
        <path d="m94 48 2 9m11-7 1 9m10-6 0 8m-79 4 7-3" fill="none" stroke="{shade}" stroke-width="3.7" opacity=".75"/>
        <path d="M145 72q17 0 23 10l-1 15q-1 8 6 8 7-1 7-9l1-17" fill="{coat}"/>
        <path d="M153 75q18-3 30 4l7 12q4 8-3 11-6 3-10-5l-5-9-15-1" fill="{coat}"/>
        <path d="m168 98 7 1m8-4 6-2" fill="none" stroke-width="1.3"/>
        {_soft_profile_head(coat, shade, cream, 'translate(143 29) rotate(17 34 37) scale(.65)', relaxed=True)}
        '''
    else:
        art = f'''
        <path d="M60 82q-28 9-31-10-1-11 10-14 6-1 7 4 0 4-6 5-8 6 2 10 5 2 13-4" fill="{coat}"/>
        <path d="M57 68q38-22 76-5 25 10 27 23 0 11-31 13H62q-21-1-18-16 3-10 13-15Z" fill="{coat}"/>
        <path d="M92 88q25-8 46 7H81" fill="{cream}" stroke="none"/>
        <path d="M65 76q19-5 24 9-1 9-17 9" fill="none" stroke-width="2"/>
        <path d="m93 63 2 9m11-7 1 9m11-5-1 8" fill="none" stroke="{shade}" stroke-width="3.8" opacity=".7"/>
        <path d="M145 80q24 8 21 28l-3 13q-2 8 6 8 7-1 9-12l1-29" fill="{coat}"/>
        <path d="M158 83q26 1 27 22l-2 13q-1 8 7 8 8-2 8-13l-2-24" fill="{coat}"/>
        <path d="m165 120 7 1m13-4 8 1" fill="none" stroke-width="1.3"/>
        {_profile_head(coat, shade, cream, 'translate(139 35) rotate(14 34 37) scale(.67)', relaxed=True)}
        '''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{companion} {pose.replace("_", " ")} in profile"><g stroke="{ink}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" fill="none">{art}</g></svg>'

def _drawing(companion, pose_name, size, mirror):
    svg = pose_svg(companion, pose_name)
    w, h, anchor = _SIZES[pose_name]
    scale = size / w
    area = DrawingArea(size, h * scale, 0, 0)
    flip = Affine2D().scale(-scale if mirror else scale, -scale).translate(size if mirror else 0, h*scale)
    for kind, geometry, a, matrix in _read_components(ET.fromstring(svg)):
        kw = dict(facecolor=a.get("fill", "none"), edgecolor=a.get("stroke", "none"), linewidth=float(a["stroke-width"])*scale, alpha=float(a.get("opacity", 1)), capstyle="round", joinstyle="round")
        patch = PathPatch(geometry, **kw) if kind == "path" else Ellipse(geometry[:2], geometry[2]*2, geometry[3]*2, **kw)
        patch.set_transform(Affine2D(matrix) + flip + area.get_transform())
        area.add_artist(patch)
    alignment = ((1-anchor[0]/w) if mirror else anchor[0]/w, 1-anchor[1]/h)
    return area, alignment

class _PoseCat(AnnotationBbox):
    """One removable vector artist, optionally following a live data anchor."""
    def __init__(self, point, *, dimensions, coords, pose_name, companion, size, mirror, offset, zorder):
        self.point, self.dimensions = point, dimensions
        self.pose_name, self.companion, self.size, self.mirror = pose_name, companion, size, mirror
        self.reaction = None
        self._variants = {pose_name: _drawing(companion, pose_name, size, mirror)}
        area, alignment = self._variants[pose_name]
        initial = point() if callable(point) else point
        if dimensions == 3: self.xyz = tuple(initial)
        super().__init__(area, (0,0) if dimensions == 3 else initial, xycoords=coords,
                         xybox=offset, boxcoords="offset points", box_alignment=alignment,
                         frameon=False, pad=0, annotation_clip=False, zorder=zorder)

    def _resolve_point(self):
        point = self.point() if callable(self.point) else self.point
        if np.shape(point) != (self.dimensions,) or not np.isfinite(point).all():
            raise ValueError(f"xy must contain {self.dimensions} finite coordinates")
        if self.dimensions == 3:
            self.xyz = tuple(point)
            x, y, _ = proj3d.proj_transform(*self.xyz, self.axes.get_proj())
            self.xy = (x,y)
        else: self.xy = tuple(point)

    def anchor_display(self, renderer):
        self._resolve_point()
        transform = self.axes.transAxes if self.xycoords == "axes fraction" else self.axes.transData
        return transform.transform(self.xy) + np.asarray(self.xybox)*renderer.points_to_pixels(1)

    def set_pose(self, name):
        if name == self.pose_name: return
        if name not in self._variants:
            self._variants[name] = _drawing(self.companion, name, self.size, self.mirror)
        self.offsetbox, self._box_alignment = self._variants[name]
        self.offsetbox.set_figure(self.get_figure())
        self.pose_name = name
        self.stale = True

    def draw(self, renderer):
        self._resolve_point()
        if self.reaction is not None: self.reaction(renderer)
        super().draw(renderer)

def pose(ax, xy, *, pose="belly_up", companion="mochi", size=76,
         coords="data", offset=(0, 0), mirror=False, zorder=100):
    """Place a full-body vector cat, sized in points.

    xy takes two data coordinates on 2D axes or three on 3D axes. It may also
    be a zero-argument callable, evaluated on every draw, to follow changing
    data. With coords='axes fraction', use two fractions on either Axes.
    The illustration's ground/perch point is anchored to xy. Returns one
    removable artist. This does not change data or axis limits.
    """
    if not math.isfinite(size) or size <= 0: raise ValueError("size must be finite and positive")
    if coords not in ("data", "axes fraction"): raise ValueError("coords must be data or axes fraction")
    if np.shape(offset) != (2,) or not np.isfinite(offset).all(): raise ValueError("offset must contain two finite values")
    dimensions = 3 if getattr(ax, "name", "") == "3d" and coords == "data" else 2
    initial = xy() if callable(xy) else xy
    if np.shape(initial) != (dimensions,) or not np.isfinite(initial).all():
        raise ValueError(f"xy must contain {dimensions} finite coordinates")
    artist = _PoseCat(xy, dimensions=dimensions, coords=coords, pose_name=pose,
                      companion=companion, size=size, mirror=mirror, offset=offset, zorder=zorder)
    artist.set_gid(f"catplotlib-cat-scene-{next(_ids)}")
    artist.set_in_layout(False)
    ax.add_artist(artist)
    return artist

def mesh_cat(ax, xyz=None, *, companion="mochi", size=64):
    """A belly-up cat playing diagonally along the front floor corner.

    By default its back rests near the high-X, low-Y corner of the axes floor.
    Pass a three-coordinate xyz to choose another anchor. Neither placement
    changes the axis limits; the anchor follows the camera on every draw.
    """
    if getattr(ax, "name", "") != "3d": raise ValueError("mesh_cat requires a 3D Axes")
    if xyz is None:
        x0, x1 = ax.get_xlim3d()
        y0, y1 = ax.get_ylim3d()
        z0, _ = ax.get_zlim3d()
        xyz = (x0 + .84*(x1-x0), y0 + .20*(y1-y0), z0)
    return pose(ax, xyz, pose="belly_up", companion=companion, size=size)

def cat_duel(ax, floor, roof, *, ground="mochi", top="nugget", ground_size=38,
             top_size=49, ground_offset=(0,0), top_offset=(0,0), mirror=True,
             close_gap=18, hysteresis=3):
    """A stretching cat and a reactive cat above it; returns (lower, upper).

    The upper cat swats down when there is room, and arches its back when
    the vertical gap above the lower cat's raised paws is <= close_gap points.
    It relaxes again at close_gap + hysteresis, avoiding flicker at the edge.
    The decision is recalculated on each draw, including resize and zoom.
    Anchors may be 2D or 3D tuples, or callables following live bar heights.
    Use upper.pose_name to inspect the current pose after drawing.
    """
    if not math.isfinite(close_gap) or close_gap < 0: raise ValueError("close_gap must be finite and nonnegative")
    if not math.isfinite(hysteresis) or hysteresis < 0: raise ValueError("hysteresis must be finite and nonnegative")
    lower = pose(ax, floor, pose="stretch", companion=ground, size=ground_size, mirror=mirror, offset=ground_offset)
    upper = pose(ax, roof, pose="swat_down", companion=top, size=top_size, offset=top_offset)
    reach = ground_size / _SIZES["stretch"][0] * (_SIZES["stretch"][2][1] - 16)
    upper.close_gap, upper.hysteresis, upper.reach_points = close_gap, hysteresis, reach
    def react(renderer):
        gap = (upper.anchor_display(renderer)[1] - lower.anchor_display(renderer)[1]) / renderer.points_to_pixels(1) - reach
        threshold = upper.close_gap + (upper.hysteresis if upper.pose_name == "arched" else 0)
        upper.set_pose("arched" if gap <= threshold else "swat_down")
        upper.gap_points = float(gap)
    upper.reaction = react
    return lower, upper
