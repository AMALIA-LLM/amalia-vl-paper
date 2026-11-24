// Shared behaviour for the AMALIA paper pages: tabs, BibTeX copy button, results bar chart, figure viewer.

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-tabs]").forEach((group) => {
    const tabs = group.querySelectorAll('[role="tab"]');
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => {
          const on = t === tab;
          t.setAttribute("aria-selected", on);
          document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
        });
      });
    });
  });

  document.querySelectorAll(".copy").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const text = btn.parentElement.querySelector("pre").innerText;
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "Copied";
      } catch {
        btn.textContent = "Select & copy";
      }
      setTimeout(() => (btn.textContent = "Copy"), 1600);
    });
  });
  document.querySelectorAll("[data-bar-chart]").forEach(renderBarChart);
  setupLightbox();
});

// Every figure gets an expand button (top-right corner) that opens the image at full resolution
// on a dark overlay. Inside the viewer, "Fit to screen" toggles between full size and fitted.
const EXPAND_ICON =
  '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
  '<path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M16 21h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>';

function setupLightbox() {
  const box = document.createElement("div");
  box.className = "lightbox full";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-modal", "true");
  box.innerHTML =
    '<div class="bar"><span class="cap"></span><span class="actions">' +
    '<button type="button" class="fit">Fit to screen</button>' +
    '<a class="orig" target="_blank" rel="noopener">Open in new tab</a>' +
    '<button type="button" class="close" aria-label="Close">Close</button></span></div>' +
    '<div class="stage"><img alt=""></div>';
  document.body.append(box);
  const img = box.querySelector("img");
  const fitBtn = box.querySelector(".fit");
  let opener = null;

  const setFull = (full) => {
    box.classList.toggle("full", full);
    fitBtn.textContent = full ? "Fit to screen" : "Full resolution";
  };
  const open = (fig) => {
    opener = document.activeElement;
    img.src = fig.currentSrc || fig.src;
    img.alt = fig.alt;
    box.querySelector(".orig").href = img.src;
    const cap = fig.closest("figure").querySelector("figcaption");
    box.querySelector(".cap").textContent = cap ? cap.textContent : "";
    setFull(true);
    box.querySelector(".stage").scrollTo(0, 0);
    box.classList.add("open");
    document.body.style.overflow = "hidden";
    box.querySelector(".close").focus();
  };
  const close = () => {
    box.classList.remove("open");
    document.body.style.overflow = "";
    if (opener) opener.focus();
  };

  document.querySelectorAll("figure img").forEach((fig) => {
    const wrap = document.createElement("div");
    wrap.className = "fig-media";
    fig.replaceWith(wrap);
    wrap.append(fig);
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "expand";
    btn.title = "View full resolution";
    btn.setAttribute("aria-label", "View full resolution");
    btn.innerHTML = EXPAND_ICON;
    btn.addEventListener("click", () => open(fig));
    wrap.append(btn);
    fig.addEventListener("click", () => open(fig));
  });

  fitBtn.addEventListener("click", () => setFull(!box.classList.contains("full")));
  img.addEventListener("click", (e) => {
    e.stopPropagation();
    setFull(!box.classList.contains("full"));
  });
  box.querySelector(".close").addEventListener("click", close);
  box.addEventListener("click", (e) => {
    if (e.target === box || e.target.classList.contains("stage")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && box.classList.contains("open")) close();
  });
}


// Horizontal bar chart from a <script type="application/json"> child:
// { metric, max, ticks, series: {key: {label, color}}, rows: [{name, value, series, ours?, note?}] }
function renderBarChart(root) {
  const spec = JSON.parse(root.querySelector('script[type="application/json"]').textContent);
  const rows = [...spec.rows].sort((a, b) => b.value - a.value);
  const max = spec.max;

  const legend = document.createElement("div");
  legend.className = "legend";
  for (const s of Object.values(spec.series)) {
    legend.insertAdjacentHTML("beforeend", `<span><i style="background:${s.color}"></i>${s.label}</span>`);
  }
  const bars = document.createElement("div");
  bars.className = "bars";
  bars.setAttribute("role", "list");
  const tip = document.createElement("div");
  tip.className = "tooltip";
  tip.setAttribute("aria-hidden", "true");

  for (const r of rows) {
    const s = spec.series[r.series];
    const name = document.createElement("div");
    name.className = "name" + (r.ours ? " ours" : "");
    name.textContent = r.name;
    const track = document.createElement("div");
    track.className = "track";
    track.setAttribute("role", "listitem");
    track.tabIndex = 0;
    track.setAttribute("aria-label", `${r.name}: ${r.value.toFixed(1)} (${s.label})`);
    track.innerHTML =
      `<div class="bar" style="width:${(r.value / max) * 100}%;background:${s.color}"></div>` +
      `<span class="val">${r.value.toFixed(1)}</span>`;
    const show = () => {
      bars.classList.add("dim");
      tip.innerHTML = `<b>${r.name}</b><br>${spec.metric}: ${r.value.toFixed(1)}<br>${s.label}${r.note ? `<br>${r.note}` : ""}`;
      const box = root.getBoundingClientRect();
      const bar = track.querySelector(".bar").getBoundingClientRect();
      tip.style.left = `${Math.min(bar.right - box.left + 12, box.width - 220)}px`;
      tip.style.top = `${bar.top - box.top - 8}px`;
      tip.classList.add("show");
    };
    const hide = () => {
      bars.classList.remove("dim");
      tip.classList.remove("show");
    };
    track.addEventListener("mouseenter", show);
    track.addEventListener("mouseleave", hide);
    track.addEventListener("focus", show);
    track.addEventListener("blur", hide);
    bars.append(name, track);
  }
  const ticks = spec.ticks.map((t) => `<span style="left:${(t / max) * 100}%">${t}</span>`).join("");
  bars.insertAdjacentHTML("beforeend", `<div></div><div class="ticks" aria-hidden="true">${ticks}</div>`);
  root.querySelector(".chart-body").append(legend, bars, tip);
}
