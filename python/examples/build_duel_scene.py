"""Export the shared SVG poses and point geometry for the browser scene."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import catplotlib as cp
from catplotlib.scenes import _SIZES
from catplotlib.gallery import draw

def build_duel_scene(output):
    output=Path(output)
    fig,ax=draw('bar')
    fig.canvas.draw()
    lower,upper=ax.artists[-2:]
    points_per_pixel=72/fig.dpi
    figure_height=fig.get_figheight()*72
    def point(x,y):
        px,py=ax.transData.transform((x,y))*points_per_pixel
        return float(px),float(figure_height-py)
    cx,floor=point(1,0)
    model=dict(centerX=cx,floorY=floor,barLeft=point(.7,0)[0],barRight=point(1.3,0)[0],
               pointsPerTreat=floor-point(1,1)[1],groundOffset=float(lower.xybox[0]),
               reach=upper.reach_points,closeGap=upper.close_gap,hysteresis=upper.hysteresis,
               minHeight=8,maxHeight=18,
               sampleHeights=[int(np.random.default_rng(seed).integers(5,17,4)[1]) for seed in [7,19]],poses={})
    for name,companion,size in [('stretch','mochi',lower.size),('swat_down','nugget',upper.size),('arched','nugget',upper.size)]:
        w,h,anchor=_SIZES[name]
        model['poses'][name]=dict(width=w,height=h,anchor=anchor,size=size,svg=cp.pose_svg(companion,name))
    (output/'duel-scene.json').write_text(json.dumps(model,ensure_ascii=False))
    plt.close(fig)
    return model

if __name__=='__main__':
    build_duel_scene(sys.argv[1])
