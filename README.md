# AMALIA paper pages

Static project pages for two AMALIA papers. The theme copies the official AMALIA site, [amaliallm.pt](https://amaliallm.pt): Outfit for headings, Inter for body text, orange `#EB6A3F`, yellow `#FED43C` buttons and a warm `#F9F8F6` background.

| Page | Paper |
|---|---|
| `/` (`index.html`) | **AMALIA-VL**: A Native European Portuguese Open-Source Vision and Language Model ([arXiv:2606.19100](https://arxiv.org/abs/2606.19100)) |
| `/portexto/` | **PorTEXTO**: A European Portuguese Benchmark for Visual Text Extraction ([arXiv:2606.19096](https://arxiv.org/abs/2606.19096)) |

There is no build step and no dependencies: plain HTML, CSS and JS.

```
index.html               AMALIA-VL page
portexto/index.html      PorTEXTO page
static/css/style.css     shared theme
static/js/main.js        tabs and BibTeX copy button
static/img/              logos, funder marks and paper figures
scripts/render_figures.py  re-renders the figures from the Overleaf figure PDFs
scripts/build_tables.py  regenerates the main results tables (AMALIA-VL Table 3, PorTEXTO Table 2)
```

## Preview locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Editing results

The numbers come from AMALIA-VL Table 3 and PorTEXTO Table 2. They live in `scripts/build_tables.py`. After editing them, run:

```bash
python3 scripts/build_tables.py
```

The script rewrites the content between the `<!--NAME--> … <!--/NAME-->` markers in the HTML. It also recomputes the bold (best) and underlined (best fully open, or second best) cells.

## Deploy on GitHub Pages

1. Push this folder to a repository, for example `amalia-llm/amalia-vl` or `<org>.github.io`.
2. Go to **Settings → Pages → Deploy from branch** and choose `main` with `/ (root)`.

All paths are relative, so the site works at a domain root or under a sub-path.
