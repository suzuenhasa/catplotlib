"""Native data, dynamic geometry, and export checks for decorative finishes."""
import io
import unittest
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import catplotlib as cp


class FinishTests(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def test_bubble_bars_keep_native_data_legends_and_live_geometry(self):
        for horizontal in (False,True):
            fig,ax=plt.subplots()
            bars=(ax.barh if horizontal else ax.bar)([0,1],[-3,5],label="Treats")
            limits=ax.dataLim.bounds
            bounds=[b.get_bbox().bounds for b in bars]
            self.assertIs(cp.bubble_bars(bars),bars)
            self.assertEqual(bounds,[b.get_bbox().bounds for b in bars])
            self.assertEqual(ax.dataLim.bounds,limits)
            self.assertEqual(ax.get_legend_handles_labels()[1],["Treats"])
            ax.legend()
            before=io.BytesIO(); fig.savefig(before,format="svg")
            (bars[1].set_width if horizontal else bars[1].set_height)(2)
            after=io.BytesIO(); fig.savefig(after,format="svg")
            self.assertNotEqual(before.getvalue(),after.getvalue())
            self.assertEqual((bars[1].get_width if horizontal else bars[1].get_height)(),2)
            root=ET.fromstring(after.getvalue())
            self.assertTrue(any(e.get("id","").startswith("catplotlib-bubble-shine-") for e in root.iter()))
            self.assertFalse(list(root.iter("{http://www.w3.org/2000/svg}image")))

    def test_histogram_and_intervals_preserve_computed_geometry(self):
        fig,(a,b)=plt.subplots(1,2)
        counts,edges,bars=a.hist([0,0,1,2,3,3],bins=[0,1,2,3,4])
        cp.bubble_bars(bars)
        np.testing.assert_array_equal([p.get_height() for p in bars],counts)
        np.testing.assert_array_equal([p.get_x() for p in bars],edges[:-1])
        intervals=b.broken_barh([(1,3),(7,4)],(0,.6))
        paths=[p.vertices.copy() for p in intervals.get_paths()]
        cp.bubble_bars(intervals)
        fig.canvas.draw()
        for original,styled in zip(paths,intervals.get_paths()):
            np.testing.assert_array_equal(original,styled.vertices)

    def test_gradient_preserves_nan_gaps_and_step_boundaries(self):
        for step in (False,True):
            fig,ax=plt.subplots(figsize=(4,3),dpi=100,facecolor="white")
            ax.set_facecolor("white"); ax.set_axis_off()
            if step:
                line,=ax.step([0,1,2],[1,3,2],where="post",color="#800080")
                empty,filled=(.75,2),(1.25,2)
            else:
                line,=ax.plot([0,1,2,3,4],[3,3,np.nan,3,3],color="#800080")
                empty,filled=(2,2),(.5,2)
            ax.set(xlim=(0,4),ylim=(0,4))
            data=line.get_xydata().copy(); limits=ax.dataLim.bounds
            finish=cp.dreamy_line(line,stars=False)
            fig.canvas.draw()
            pixels=np.asarray(fig.canvas.buffer_rgba())
            def sample(point):
                x,y=ax.transData.transform(point)
                return pixels[pixels.shape[0]-1-int(y),int(x),:3]
            np.testing.assert_array_equal(sample(empty),[255,255,255])
            self.assertLess(sample(filled)[1],250)
            np.testing.assert_array_equal(line.get_xydata(),data)
            self.assertEqual(ax.dataLim.bounds,limits)
            finish.remove()
            self.assertEqual(len(ax.artists),0)

    def test_log_gradient_and_stars_export_without_rasterization(self):
        fig,ax=plt.subplots()
        line,=ax.loglog([1,10,100],[2,8,40])
        data=line.get_xydata().copy()
        cp.dreamy_line(line)
        ax.set_xlim(2,200)
        for format in ("svg","pdf"):
            out=io.BytesIO(); fig.savefig(out,format=format)
            if format=="svg":
                root=ET.fromstring(out.getvalue())
                self.assertFalse(list(root.iter("{http://www.w3.org/2000/svg}image")))
                self.assertTrue(any(e.get("id","").startswith("catplotlib-dreamy-line-") for e in root.iter()))
            else:
                self.assertTrue(out.getvalue().startswith(b"%PDF"))
        np.testing.assert_array_equal(line.get_xydata(),data)

    def test_unsupported_inputs_do_not_change_artists(self):
        fig,ax=plt.subplots()
        bars=ax.bar([0],[1])
        with self.assertRaises(ValueError): cp.bubble_bars(bars,rounding=-1)
        with self.assertRaises(ValueError): cp.bubble_bars(bars,corners="invalid")
        self.assertFalse(bars[0].get_path_effects())
        ax3=fig.add_subplot(projection="3d")
        line,=ax3.plot([0,1],[0,1],[0,1])
        with self.assertRaises(ValueError): cp.dreamy_line(line)


if __name__ == "__main__": unittest.main()
