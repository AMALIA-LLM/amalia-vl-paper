"""Render the papers' figure PDFs (from the Overleaf sources) into web images under static/img.

Usage: python3 scripts/render_figures.py <overleaf_dir>
where <overleaf_dir> contains the extracted projects as amalia/ and portexto/.
Requires poppler (pdftoppm, pdfinfo) and Pillow.
"""
import pathlib, subprocess, sys
from PIL import Image
src = sys.argv[1]
IMG = pathlib.Path(__file__).resolve().parent.parent / "static" / "img"
out = "/tmp/amalia_fig_render"; pathlib.Path(out).mkdir(exist_ok=True)
DEST = {"vl_teaser": "amalia-vl/teaser.jpg", "vl_synth": "amalia-vl/synthetic-data.jpg",
        "pt_teaser": "portexto/teaser.jpg", "pt_hw": "portexto/handwritten.jpg", "pt_itw": "portexto/in-the-wild.jpg",
        "pt_syn": "portexto/synthetic.jpg", "pt_platform": "portexto/annotation-platform.jpg",
        "pt_stats": "portexto/statistics.png", "pt_ocrbench": "portexto/ocrbench-vs-portexto.png",
        "pt_reason": "portexto/reasoning-delta.png"}
# (source pdf, output name, target width px, trim in pts (l,b,r,t) from \includegraphics, format)
jobs = [
 ("amalia/figures/amalia_vl_teaser_3col.pdf", "vl_teaser", 2400, (10,15,10,0), "jpg"),
 ("amalia/figures/all_examples.pdf",          "vl_synth",  2400, (20,16,20,12), "jpg"),
 ("portexto/figures/modern_apps.pdf",         "pt_teaser", 2400, None, "jpg"),
 ("portexto/figures/handwritten_samples_w_redacted.pdf", "pt_hw", 2400, None, "jpg"),
 ("portexto/figures/in_the_wild_samples.pdf", "pt_itw", 2400, None, "jpg"),
 ("portexto/figures/synthetic_samples.pdf",   "pt_syn", 2400, None, "jpg"),
 ("portexto/figures/annotation_review.pdf",   "pt_platform", 2000, None, "jpg"),
 ("portexto/figures/stats.pdf",               "pt_stats", 2000, None, "png"),
 ("portexto/figures/ocrbench_vs_portexto.pdf","pt_ocrbench", 1100, None, "png"),
 ("portexto/figures/thinking_heatmap.pdf",    "pt_reason", 1100, None, "png"),
]
for pdf, name, w, trim, fmt in jobs:
    p = f"{src}/{pdf}"
    info = subprocess.run(["pdfinfo", p], capture_output=True, text=True).stdout
    pw, ph = [float(x) for x in info.split("Page size:")[1].split("pts")[0].split("x")]
    usable_w = pw - (trim[0] + trim[2] if trim else 0)
    dpi = w / usable_w * 72
    base = f"{out}/{name}"
    subprocess.run(["pdftoppm", "-r", f"{dpi:.2f}", "-png", "-singlefile", "-f", "1", "-l", "1", p, base], check=True, stderr=subprocess.DEVNULL)
    im = Image.open(base + ".png").convert("RGB")
    if trim:
        s = dpi / 72
        l, b, r, t = trim
        im = im.crop((round(l*s), round(t*s), im.width - round(r*s), im.height - round(b*s)))
    dest = IMG / DEST[name]
    if fmt == "jpg":
        im.save(dest, quality=90 if name == "pt_platform" else 86, optimize=True, progressive=True)
    else:
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT).save(dest, optimize=True)
    print(DEST[name], im.size)
