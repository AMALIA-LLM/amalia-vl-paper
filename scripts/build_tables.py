"""Build the results tables and the icon sprite into the two pages.

Values are transcribed from the arXiv PDFs (AMALIA-VL Table 3, PorTEXTO Table 2).
Re-run after editing the numbers:  python3 scripts/build_tables.py
Content is written between <!--NAME--> ... <!--/NAME--> markers in the HTML.
"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------- AMALIA-VL Table 3 ----------------
# column names and groups follow the paper; † = held-in benchmark
COLS = ["MME", "MMMU", "MMStar", "MMPro", "SEED", "POPE", "RWQA", "OCR", "TxtVQA", "DocVQA", "InfoVQA",
        "AI2D", "ChartQA", "EmbSp", "RefRec", "COCO", "RefCap", "MVision", "Average"]
GROUPS = [("General VQA", 7), ("OCR &amp; Document", 4), ("Chart &amp; Diagram", 2), ("Spatial", 2),
          ("Caption", 2), ("Math", 1), ("", 1)]
HELD_IN = {"MME", "MMMU", "MMStar", "SEED", "POPE", "TxtVQA", "DocVQA", "InfoVQA", "COCO", "MVision"}
# openness: W = open weights, D = fully open vision data, L = fully open LLM
VL_RAW = """Ministral-3-8B|W|1756 45.4 45.3 26.8 70.3 77.1 56.2 61.7 52.8 70.0 52.7 71.9 49.5 49.2 26.9 22.4 4.0 29.5 48.6
Gemma-3-12B|W|2120 47.8 51.4 32.1 70.5 85.1 49.4 62.7 61.2 67.8 42.8 75.9 54.2 55.7 6.1 26.7 5.8 32.4 50.2
GLM-4.6V-Flash|W|2294 48.6 60.7 36.9 77.1 86.8 66.8 76.2 69.9 66.0 5.7 80.6 42.8 70.6 86.9 25.8 9.8 7.8 55.6
MiniCPM-V4|W|2274 44.9 60.4 27.9 76.8 85.7 66.6 72.4 65.1 70.0 59.8 79.0 74.5 66.2 45.1 32.0 6.0 19.1 57.4
Qwen3-VL-8B|W|2355 51.3 60.8 37.2 78.1 85.5 68.2 75.7 67.7 70.9 66.0 80.7 75.5 73.9 0.2 30.4 12.2 24.4 57.9
InternVL3.5-8B|W|2217 53.7 62.4 38.0 76.2 86.3 62.9 72.6 62.3 66.4 58.4 79.0 74.8 69.9 39.2 29.9 5.6 38.1 58.6
Nemotron-Nano-12B|W|2004 50.7 59.9 36.3 77.9 85.2 69.9 80.2 69.0 69.7 64.9 83.9 78.6 64.7 62.3 18.8 2.9 33.1 60.0
Qwen3.5-9B|W|2226 52.2 57.6 36.7 78.5 84.7 74.6 71.7 70.8 76.3 71.6 83.5 80.3 69.3 83.6 33.7 13.5 54.4 65.2
EuroVLM-9B|WL|1581 34.0 40.3 19.8 66.8 84.2 55.2 46.4 54.1 56.4 34.0 61.5 47.6 38.8 5.1 23.9 5.3 12.9 41.3
TowerVision-9B|WD|1414 39.1 41.9 21.7 70.8 85.1 49.9 47.5 58.3 56.1 38.3 65.0 39.2 49.1 8.3 24.4 4.9 14.6 42.5
Molmo2-8B|WD|1936 52.7 61.2 36.4 73.0 87.2 66.8 59.0 61.2 62.8 50.2 80.9 43.5 62.1 3.6 19.5 3.8 22.4 50.8
LLaVA-OV1.5-8B|WD|2244 52.9 64.7 36.9 75.8 86.4 62.9 76.1 63.3 72.0 62.6 81.6 74.2 60.2 78.1 36.5 8.2 23.1 60.9
Salamandra-VL-7B|WDL|784 27.7 32.0 11.8 33.3 64.9 19.7 21.0 1.6 6.0 8.7 30.1 14.0 26.3 0.0 19.7 8.2 3.1 19.8
Molmo2-O-7B|WDL|1618 37.8 52.6 26.5 70.0 81.5 58.3 57.4 55.1 52.7 41.6 66.4 40.4 54.7 3.4 18.4 4.7 11.8 43.9
Perception-LM-8B|WDL|1368 37.7 52.8 22.9 73.0 82.8 53.4 76.5 60.8 65.4 60.3 67.6 69.2 62.2 0.0 15.2 3.1 4.7 47.6
AMALIA-VL|WDL|1815 40.0 44.7 27.9 72.0 89.3 60.9 59.0 66.2 68.7 45.0 68.4 67.8 53.7 77.4 50.8 11.2 12.2 54.5
AMALIA-VL-DPO|WDL|1824 40.3 44.0 27.1 73.8 89.1 59.9 62.4 68.0 69.5 45.6 69.3 66.5 57.0 79.2 49.7 10.7 14.0 55.1"""
GLYPH = {"W": "◇", "WL": "◇♣", "WD": "◇♡", "WDL": "◇♡♣"}
BLOCK = {"W": 0, "WL": 1, "WD": 1, "WDL": 2}  # row groups separated by a rule, as in the paper


def vl_table():
    rows = []
    for line in VL_RAW.splitlines():
        name, openness, values = line.split("|")
        vals = [float(x) for x in values.split()]
        assert len(vals) == len(COLS), name
        rows.append((name, openness, vals))
    best = [max(r[2][i] for r in rows) for i in range(len(COLS))]
    best_open = [max(r[2][i] for r in rows if r[1] == "WDL") for i in range(len(COLS))]
    starts, k = set(), 0
    for _, w in GROUPS:
        starts.add(k)
        k += w

    out = ['<table class="paper compact">', '<thead><tr class="group"><th></th>']
    out += [f'<th colspan="{w}">{f"<span>{g}</span>" if g else ""}</th>' for g, w in GROUPS]
    out.append("</tr><tr><th>Model</th>")
    for i, c in enumerate(COLS):
        out.append(f'<th class="{"sep" if i in starts else ""}">{c}{"<sup>†</sup>" if c in HELD_IN else ""}</th>')
    out.append("</tr></thead><tbody>")
    prev = None
    for name, o, vals in rows:
        cls = []
        if prev is not None and BLOCK[o] != prev:
            cls.append("rule")
        if name.startswith("AMALIA"):
            cls.append("ours")
        prev = BLOCK[o]
        out.append(f'<tr class="{" ".join(cls)}"><td>{name}<span class="glyph">{GLYPH[o]}</span></td>')
        for i, (c, x) in enumerate(zip(COLS, vals)):
            cl = ["sep"] if i in starts else []
            if x == best[i]:
                cl.append("best")
            if o == "WDL" and x == best_open[i]:
                cl.append("second")
            txt = f"{int(x)}" if c == "MME" else f"{x:.1f}"
            out.append(f'<td class="{" ".join(cl)}">{txt}</td>')
        out.append("</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


def vl_chart():
    """Average pt-PT score per model, coloured by openness tier (palette validated for CVD)."""
    series = {"W": "open_weights", "WL": "open_weights", "WD": "open_data", "WDL": "fully_open"}
    rows = []
    for line in VL_RAW.splitlines():
        name, o, values = line.split("|")
        row = {"name": name, "value": float(values.split()[-1]), "series": series[o]}
        if name.startswith("AMALIA"):
            row["ours"] = True
        if o == "WL":
            row["note"] = "open LLM, closed vision data"
        rows.append(row)
    spec = {
        "metric": "pt-PT average", "max": 70, "ticks": [0, 10, 20, 30, 40, 50, 60, 70],
        "series": {
            "open_weights": {"label": "Open weights", "color": "#5b6cb8"},
            "open_data": {"label": "Open weights + open vision data", "color": "#2a9d8f"},
            "fully_open": {"label": "Fully open (weights, vision data & LLM)", "color": "#eb6a3f"},
        },
        "rows": rows,
    }
    return '<script type="application/json">' + json.dumps(spec, ensure_ascii=False) + "</script>"


# ---------------- PorTEXTO Table 2 ----------------
PT_RAW = """OCR-Specific
Nemotron-OCR-V2|15.6 9.6 11.2 9.5 91.4 81.0 75.9 68.8 48.5 42.2
DeepSeek-OCR-2-3B|36.1 30.2 18.7 23.3 91.4 84.3 84.1 75.0 57.6 53.2
First-tier LVLMs (≤ 12B parameters)
Molmo2-O-7B|26.1 22.1 6.6 10.7 70.7 61.5 56.7 34.8 40.0 32.3
GLM-4.6V-Flash-10B|46.5 34.3 21.8 19.3 56.8 54.1 48.3 45.5 43.4 38.3
PerceptionLM-8B|36.7 29.9 10.1 9.1 78.2 71.7 59.2 46.0 46.1 39.2
Molmo2-8B|35.0 26.8 12.4 14.3 81.5 66.6 70.9 44.0 50.0 37.9
AMALIA-VL|41.6 32.7 28.4 28.0 81.3 79.6 72.6 60.8 56.0 50.3
InternVL3.5-8B|51.6 43.6 31.8 34.0 75.5 71.6 81.0 71.7 60.0 55.2
AMALIA-VL-DPO|48.2 38.2 39.3 37.7 83.2 81.5 74.8 64.6 61.4 55.5
Bee-RL-8B|45.2 37.5 27.1 30.7 94.6 87.7 83.1 79.1 62.5 58.8
Nemotron-Nano-12B-VL-V2|53.3 42.3 37.5 32.7 92.2 90.0 76.8 72.9 65.0 59.5
LLaVA-OneVision-1.5-8B|61.1 51.4 32.6 37.2 98.2 93.0 77.4 70.9 67.3 63.1
Gemma-4-E4B-it|78.2 63.7 42.7 38.7 95.6 89.1 82.7 78.5 74.8 67.5
Ministral3-Instruct-8B|74.0 59.9 63.9 56.8 98.6 96.1 71.4 58.9 77.0 67.9
Qwen3.5-9B|80.1 70.3 70.0 64.9 99.8 99.0 85.4 80.9 83.8 78.8
Second-tier LVLMs (&gt; 12B parameters)
InternVL3.5-38B|56.5 47.7 42.6 43.2 81.2 76.8 75.2 68.2 63.9 59.0
Gemma-4-31B-it|88.0 79.0 65.2 58.8 98.3 93.0 89.8 87.0 85.3 79.5
Qwen3.6-27B|81.5 71.8 75.4 71.1 99.9 96.5 90.5 86.5 86.8 81.5"""


def pt_table():
    items = []
    for line in PT_RAW.splitlines():
        if "|" in line:
            name, values = line.split("|")
            vals = [float(x) for x in values.split()]
            assert len(vals) == 10, name
            items.append(("row", name, vals))
        else:
            items.append(("tier", line, None))
    rows = [i for i in items if i[0] == "row"]
    top = [sorted({r[2][j] for r in rows}, reverse=True)[:2] for j in range(10)]
    out = ['<table class="paper">', '<thead><tr class="group"><th></th>']
    for g in ["Handwritten (R)", "Handwritten (FP)", "Synthetic", "In-The-Wild", "Mean"]:
        out.append(f'<th colspan="2"><span>{g}</span></th>')
    out.append("</tr><tr><th>Model</th>")
    out += [f'<th class="{"sep" if j % 2 == 0 else ""}">{"ANLS" if j % 2 == 0 else "BLEU-1"}</th>' for j in range(10)]
    out.append("</tr></thead><tbody>")
    for kind, name, vals in items:
        if kind == "tier":
            out.append(f'<tr class="tier"><td colspan="11">{name}</td></tr>')
            continue
        cls = ' class="ours"' if name.startswith("AMALIA") else ""
        cells = []
        for j, x in enumerate(vals):
            cl = ["sep"] if j % 2 == 0 else []
            if x == top[j][0]:
                cl.append("best")
            elif len(top[j]) > 1 and x == top[j][1]:
                cl.append("second")
            cells.append(f'<td class="{" ".join(cl)}">{x:.1f}</td>')
        out.append(f"<tr{cls}><td>{name}</td>{''.join(cells)}</tr>")
    out.append("</tbody></table>")
    return "\n".join(out)


# ---------------- icons ----------------
GH = "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
STROKE = 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
ICONS = f"""<svg width="0" height="0" style="position:absolute" aria-hidden="true">
<symbol id="i-gh" viewBox="0 0 16 16"><path fill="currentColor" d="{GH}"/></symbol>
<symbol id="i-paper" viewBox="0 0 24 24"><g {STROKE}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></g></symbol>
<symbol id="i-data" viewBox="0 0 24 24"><g {STROKE}><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></g></symbol>
<symbol id="i-bench" viewBox="0 0 24 24"><g {STROKE}><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></g></symbol>
</svg>"""


def inject(path, blocks):
    f = ROOT / path
    html = f.read_text()
    for name, content in blocks.items():
        pat = re.compile(rf"<!--{name}-->.*?<!--/{name}-->|<!--{name}-->", re.S)
        assert pat.search(html), f"marker {name} missing in {path}"
        html = pat.sub(lambda _: f"<!--{name}-->{content}<!--/{name}-->", html, count=1)
    f.write_text(html)
    print("updated", path)


if __name__ == "__main__":
    inject("index.html", {"ICONS": ICONS, "VL_CHART": vl_chart(), "VL_TABLE": vl_table()})
    inject("portexto/index.html", {"ICONS": ICONS, "PT_TABLE": pt_table()})
