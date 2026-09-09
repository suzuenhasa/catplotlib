"""Run with: python -m unittest discover -s tests -v"""
import io
import unittest
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import catplotlib as cp
from catplotlib.gallery import PLOTS, draw

class CatplotlibTests(unittest.TestCase):
    def tearDown(self): plt.close("all")

    def test_context_restores_on_exception(self):
        before = matplotlib.rcParams["axes.facecolor"]
        with self.assertRaises(RuntimeError):
            with cp.context("strawberry"):
                self.assertEqual(matplotlib.rcParams["axes.facecolor"], "#fffdf6")
                raise RuntimeError("intentional")
        self.assertEqual(matplotlib.rcParams["axes.facecolor"], before)

    def test_all_palettes_and_stylesheet(self):
        for p in cp.PALETTES:
            with cp.context(p): self.assertEqual(len(matplotlib.rcParams["axes.prop_cycle"]), 5)
        with plt.style.context("catplotlib.catplotlib"):
            self.assertEqual(matplotlib.rcParams["axes.facecolor"], "#fffdf6")
        with self.assertRaises(ValueError): cp.palette("missing")

    def test_vector_exports_have_no_raster_cats(self):
        for companion in cp.COMPANIONS:
            for mood in cp.MOODS:
                fig, ax = plt.subplots()
                cp.cat(ax, companion=companion, mood=mood)
                buf = io.BytesIO(); fig.savefig(buf, format="svg")
                root = ET.fromstring(buf.getvalue())
                self.assertFalse(list(root.iter("{http://www.w3.org/2000/svg}image")))
                self.assertTrue(any("catplotlib-cat" in e.get("id", "") for e in root.iter()))
                pdf = io.BytesIO(); fig.savefig(pdf, format="pdf")
                self.assertTrue(pdf.getvalue().startswith(b"%PDF"))
                plt.close(fig)

    def test_catify_keeps_data_and_limits(self):
        fig, ax = plt.subplots()
        line, = ax.plot([1,2,3], [2,6,4])
        before = line.get_xydata().copy(); limits = ax.dataLim.bounds
        artists = cp.catify(line)
        np.testing.assert_array_equal(line.get_xydata(), before)
        self.assertEqual(ax.dataLim.bounds, limits)
        self.assertEqual(len(artists), 3)
        for a in artists: a.remove()
        self.assertEqual(len(ax.artists), 0)

    def test_catify_follows_log_transform(self):
        fig, ax = plt.subplots()
        line, = ax.loglog([1,10,100], [2,20,200])
        cats = cp.catify(line)
        fig.canvas.draw()
        before = cats[1].get_window_extent().x0
        ax.set_xlim(1,1000); fig.canvas.draw()
        self.assertNotEqual(before, cats[1].get_window_extent().x0)

    def test_marker_and_perch(self):
        fig, ax = plt.subplots()
        collection = ax.scatter([0,1], [1,2], marker=cp.paw_marker())
        self.assertEqual(len(collection.get_offsets()), 2)
        bars = ax.barh([0,1], [3,-2])
        cats = cp.perch(bars)
        self.assertEqual(cats[0].xy, (3., 0.))
        self.assertEqual(cats[1].xy, (-2., 1.))
        fig.canvas.draw()

    def test_large_line_guard_and_invalid_input(self):
        fig, ax = plt.subplots()
        line, = ax.plot(np.arange(100))
        with self.assertRaises(ValueError): cp.catify(line)
        with self.assertRaises(ValueError): cp.catify(line, every=0)
        with self.assertRaises(ValueError): cp.cat(ax, size=-1)
        self.assertEqual(len(cp.catify(line, every=10)), 10)

    def test_all_recipes_render(self):
        for p in PLOTS:
            with self.subTest(plot=p["id"]):
                fig, ax = draw(p["id"])
                fig.canvas.draw()
                self.assertGreater(len(fig.axes), 0)
                plt.close(fig)

    def test_all_poses_remain_vectors(self):
        for companion in cp.COMPANIONS:
            for name in cp.POSES:
                with self.subTest(companion=companion, pose=name):
                    ET.fromstring(cp.pose_svg(companion, name))
                    fig, ax = plt.subplots()
                    cp.pose(ax, (.5,.3), coords="axes fraction", pose=name, companion=companion, mirror=True)
                    buf = io.BytesIO(); fig.savefig(buf, format="svg")
                    root = ET.fromstring(buf.getvalue())
                    self.assertFalse(list(root.iter("{http://www.w3.org/2000/svg}image")))
                    self.assertTrue(any("catplotlib-cat-scene" in e.get("id", "") for e in root.iter()))
                    plt.close(fig)

    def test_3d_pose_tracks_camera_without_changing_limits(self):
        fig = plt.figure(); ax = fig.add_subplot(projection="3d")
        ax.scatter([0,2], [1,3], [2,5])
        limits = ax.get_w_lims()
        kitty = cp.pose(ax, (1,2,3), pose="swat")
        fig.canvas.draw(); first = kitty.xy
        ax.view_init(elev=35, azim=75); fig.canvas.draw()
        self.assertNotEqual(first, kitty.xy)
        self.assertEqual(kitty.xyz, (1,2,3))
        self.assertEqual(limits, ax.get_w_lims())
        kitty.remove()
        self.assertEqual(len(ax.artists), 0)

    def test_duel_reacts_to_live_bar_height_without_changing_limits(self):
        for dpi in (72, 150):
            with self.subTest(dpi=dpi):
                fig, ax = draw("bar")
                fig.set_dpi(dpi)
                bar = ax.patches[1]
                lower, upper = ax.artists[-2:]
                limits, count = ax.get_ylim(), len(ax.artists)
                bar.set_height(12); fig.canvas.draw()
                self.assertEqual(lower.pose_name, "stretch")
                self.assertEqual(upper.pose_name, "swat_down")
                bar.set_height(8); fig.canvas.draw()
                self.assertEqual(upper.pose_name, "arched")
                self.assertEqual(upper.xy, (1, 8))
                # Stay arched in the hysteresis band, then relax beyond it.
                points_per_unit = ax.bbox.height / (fig.dpi / 72) / 22
                bar.set_height((upper.reach_points + 19) / points_per_unit)
                fig.canvas.draw(); self.assertEqual(upper.pose_name, "arched")
                bar.set_height(12); fig.canvas.draw()
                self.assertEqual(upper.pose_name, "swat_down")
                self.assertEqual(ax.get_ylim(), limits)
                self.assertEqual(len(ax.artists), count)
                buf = io.BytesIO(); fig.savefig(buf, format="svg")
                self.assertNotIn(b"<image", buf.getvalue())
                plt.close(fig)

    def test_duel_reacts_to_zoom_and_removes_cleanly(self):
        fig, ax = draw("bar")
        lower, upper = ax.artists[-2:]
        fig.canvas.draw(); self.assertEqual(upper.pose_name, "swat_down")
        ax.set_ylim(0, 40); fig.canvas.draw()
        self.assertEqual(upper.pose_name, "arched")
        lower.remove(); upper.remove()
        self.assertEqual(len(ax.artists), 3)

    def test_bar_recipe_contains_working_slider(self):
        from catplotlib.gallery import code
        namespace = {}
        exec(code("bar").replace("plt.show()", ""), namespace)
        namespace["height_slider"].set_val(8)
        namespace["fig"].canvas.draw()
        self.assertEqual(namespace["bars"][1].get_height(), 8)
        self.assertEqual(namespace["upper"].pose_name, "arched")

    def test_scene_arguments(self):
        fig, ax = plt.subplots()
        with self.assertRaises(ValueError): cp.mesh_cat(ax)
        with self.assertRaises(ValueError): cp.pose(ax, (0,1,2))
        with self.assertRaises(ValueError): cp.pose(ax, (0,1), pose="unknown")
        with self.assertRaises(ValueError): cp.pose(ax, (0,1), size=float("nan"))

    def test_corner_cat_preserves_wireframe_geometry(self):
        plain, plain_ax = draw("wireframe", companions=False)
        decorated, decorated_ax = draw("wireframe", companions=True)
        self.assertEqual(plain_ax.get_w_lims(), decorated_ax.get_w_lims())
        kitty = list(decorated_ax.artists)[0]
        x0, x1, y0, y1, z0, z1 = decorated_ax.get_w_lims()
        self.assertTrue(x0 < kitty.xyz[0] < x1)
        self.assertTrue(y0 < kitty.xyz[1] < y1)
        self.assertEqual(kitty.xyz[2], z0)
        decorated.canvas.draw()
        first = kitty.xy
        decorated_ax.view_init(elev=32, azim=-30)
        decorated.canvas.draw()
        self.assertNotEqual(first, kitty.xy)
        self.assertEqual(plain_ax.get_w_lims(), decorated_ax.get_w_lims())

if __name__ == "__main__": unittest.main()
