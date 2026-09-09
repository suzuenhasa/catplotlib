"""Build the website's examples from real Matplotlib figures."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import catplotlib as cp
from catplotlib.gallery import PLOTS, draw, code
from build_duel_scene import build_duel_scene

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for n, p in enumerate(PLOTS):
        for palette in cp.PALETTES:
            for sample, seed in enumerate([7, 19]):
                with cp.context(palette):
                    fig, ax = draw(p["id"], seed=seed, palette_name=palette)
                    fig.savefig(args.output / f"{p['id']}-{palette}-{sample}.svg", format="svg", metadata={"Date": None, "Creator": f"Catplotlib {cp.__version__}; Matplotlib {matplotlib.__version__}"})
                    if palette == "milk_tea" and sample == 0:
                        fig.savefig(args.output / f"{p['id']}.png", dpi=65)
                    plt.close(fig)
        entry = {key: p[key] for key in ["id", "method", "title", "category", "description", "projection"]}
        entry["code"] = code(p["id"])
        manifest.append(entry)
        print(f"{n+1}/{len(PLOTS)} rendered {p['id']}", flush=True)
    (args.output / "manifest.json").write_text(json.dumps({"count": len(PLOTS), "matplotlib": matplotlib.__version__, "package": cp.__version__, "plots": manifest}, ensure_ascii=False))
    build_duel_scene(args.output)
    print("Gallery complete.", flush=True)

if __name__ == "__main__": main()
