# Install or update the downloaded source: python -m pip install --upgrade .
import matplotlib.pyplot as plt
import catplotlib as cp

with cp.context("milk_tea"):
    fig, (ax, bar_ax) = plt.subplots(1, 2, figsize=(11.5, 4.8))

    line, = ax.plot([0, 1, 2, 3, 4, 5], [2, 3.7, 6.4, 5.2, 8.8, 9.8])
    cp.dreamy_line(line)  # Gradient fill and little stars.
    cp.catify(line, companion="nugget", size=27)
    ax.set(xlabel="Time (naps)", ylabel="Mood (purrs)",
           title="A little data. A lot of cat.", ylim=(0, 12))

    bars = bar_ax.bar(["Mochi", "Beans", "Nugget", "Tofu"],
                      [16, 12, 13, 15], color=cp.palette()[:4], width=.6)
    cp.bubble_bars(bars)  # Rounded corners, outline, and white highlight.
    cp.perch(bars, size=25)
    bar_ax.set(ylabel="Treats earned", title="Treats for the whole squad",
               ylim=(0, 20))

    fig.tight_layout()
    fig.savefig("my-cat-plot.svg")
    fig.savefig("my-cat-plot.png")
    plt.show()
