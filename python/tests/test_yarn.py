"""Verify measurement anchors, 3D redraws, and vector-only yarn exports."""
import io
import unittest
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import proj3d
import catplotlib as cp


class YarnTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_native_limits_and_exact_endpoints_including_zero_and_negative(self):
        x, y = np.array([0, 1, 2, 3]), np.array([5, 0, -3, 7])
        fig, (plain, decorated) = plt.subplots(1, 2)
        plain.stem(x, y, bottom=0)
        yarn = cp.yarn_stem(decorated, x, y)
        fig.canvas.draw()
        np.testing.assert_array_equal(plain.dataLim.bounds, decorated.dataLim.bounds)
        np.testing.assert_array_equal(plain.get_xlim(), decorated.get_xlim())
        np.testing.assert_array_equal(plain.get_ylim(), decorated.get_ylim())
        np.testing.assert_array_equal(yarn.stems.markerline.get_xydata(), np.c_[x, y])
        for i, (segment, ball) in enumerate(zip(yarn.stems.stemlines.get_segments(), yarn.balls)):
            np.testing.assert_array_equal(segment[0], [x[i], 0])
            np.testing.assert_array_equal(segment[-1], [x[i], y[i]])
            self.assertEqual(ball.point, (x[i], y[i]))
            if y[i]:
                self.assertGreater(np.ptp(segment[:, 0]), .01)
            else:
                np.testing.assert_array_equal(segment, np.tile([x[i], 0], (101, 1)))
        yarn.remove()
        self.assertEqual(len(decorated.artists), 0)
        self.assertEqual(len(decorated.containers), 0)
        self.assertEqual(len(decorated.collections), 0)

    def test_3d_ball_centers_follow_camera_and_export_as_vectors(self):
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        x, y, z = [0, 1, 2], [0, 1, -1], [1, 3, 2]
        yarn = cp.yarn_stem(ax, x, y, z, bottom=.25)
        for i, segment in enumerate(yarn.stems.stemlines._segments3d):
            np.testing.assert_array_equal(segment[0], [x[i], y[i], .25])
            np.testing.assert_array_equal(segment[-1], [x[i], y[i], z[i]])
        centers = []
        for elev, azim, dpi in [(25, -55, 72), (40, 100, 144)]:
            ax.view_init(elev=elev, azim=azim)
            fig.set_dpi(dpi)
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            for ball in yarn.balls:
                px, py, _ = proj3d.proj_transform(*ball.point, ax.get_proj())
                expected = ax.transData.transform((px, py))
                bounds = ball.offsetbox.get_window_extent(renderer)
                actual = (bounds.x0 + bounds.width / 2, bounds.y0 + bounds.height / 2)
                np.testing.assert_allclose(actual, expected, atol=.01)
            centers.append(yarn.balls[0].xy)
        self.assertFalse(np.allclose(*centers))
        out = io.BytesIO()
        fig.savefig(out, format="svg")
        root = ET.fromstring(out.getvalue())
        self.assertFalse(list(root.iter("{http://www.w3.org/2000/svg}image")))
        self.assertEqual(sum(e.get("id", "").startswith("catplotlib-yarn-ball-")
                             for e in root.iter()), 3)
        # All open yarn thread paths explicitly opt out of polygon filling.
        balls = [e for e in root.iter() if e.get("id", "").startswith("catplotlib-yarn-ball-")]
        for ball in balls:
            for path in ball.iter("{http://www.w3.org/2000/svg}path"):
                if not path.get("d", "").rstrip().endswith("z"):
                    self.assertIn("fill: none", path.get("style", ""))

    def test_invalid_data_adds_no_partial_plot(self):
        fig, ax = plt.subplots()
        for kwargs in ({"waviness": -1}, {"ball_size": 0}, {"color": "invalid"}):
            with self.assertRaises(ValueError):
                cp.yarn_stem(ax, [0, 1], [2, 3], **kwargs)
        with self.assertRaises(ValueError):
            cp.yarn_stem(ax, [0], [np.nan])
        with self.assertRaises(ValueError):
            cp.yarn_stem(ax, [0], [1], [2])
        self.assertEqual(len(ax.containers), 0)
        self.assertEqual(len(ax.artists), 0)


if __name__ == "__main__":
    unittest.main()
