# Catplotlib

Cute interactive charts, SVG cats, and a reusable Matplotlib toolkit.

**Live site: <https://suzuenhasa.github.io/catplotlib/>**

## Use the Python package

```sh
python -m pip install --upgrade ./python
python python/examples/quickstart.py
```

The quick start includes rounded highlighted bars and a starry gradient line.
`cp.context()` applies colours and fonts; `cp.bubble_bars(bars)` and
`cp.dreamy_line(line)` explicitly add these finishes. Restart a notebook
kernel after upgrading. See `python/README.md` for the plotting APIs.

## What's in here

- `docs/`: the complete website, gallery, SVG illustrations, and downloads.
- `python/`: installable Matplotlib package, examples, and Python tests.
- `tests/`: the browser scene's JavaScript state tests.

The website runs in the visitor's browser. The gallery uses pre-rendered
Matplotlib SVGs; Python runs locally when someone uses the downloaded package.
The interactive controls and cat animations require no server or API key.
Relative URLs support both a repository subpath and a custom domain.

## Edit or preview locally

Edit `docs/index.html`, `docs/style.css`, and the JavaScript beside them.
To serve the website locally, run:

```sh
python -m http.server 8000 --directory docs
```

Then open <http://localhost:8000>. Use a local server instead of double-clicking
index.html so the gallery can load its JSON and SVG files.

To regenerate the full SVG gallery after editing Python recipes:

```sh
python python/examples/build_gallery.py docs/gallery
```

Regeneration is only needed when changing the Python-rendered charts; all
current gallery assets are already included.

## Publishing

Pages is served from `main` and the `/docs` folder. Pushes that change `docs`
publish the updated website automatically — there is no build step. Keep
`docs/.nojekyll` in the repository.

If you fork this and want your own copy online, open **Settings > Pages**,
choose **Deploy from a branch**, and select **main** and **/docs**.

## License

MIT — see [LICENSE](LICENSE).
