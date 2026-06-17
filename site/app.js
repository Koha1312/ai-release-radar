// AI Release Radar — loads the generated releases.json and renders a
// filterable, searchable feed. Pure vanilla JS, no build step, no backend.

const COMPANY_COLORS = {
  "Anthropic": "#d97757",
  "OpenAI": "#10a37f",
  "Google": "#4285f4",
  "Google DeepMind": "#4285f4",
  "Microsoft": "#0078d4",
  "Hugging Face": "#ff9d00",
  "Z.ai": "#e0457b",
  "DeepSeek": "#4d6bfe",
  "Moonshot AI": "#16b1a6",
  "Meta": "#0668e1",
};

// Short monogram per company for the branded thumbnail tile.
const COMPANY_CODES = {
  "Anthropic": "A", "OpenAI": "O", "Google": "G", "Microsoft": "MS",
  "Z.ai": "Z", "DeepSeek": "DS", "Moonshot AI": "Mo", "Meta": "M", "Hugging Face": "HF",
};
const monogram = (c) => COMPANY_CODES[c] || (c[0] || "?").toUpperCase();

const state = { all: [], company: "All", type: "All", access: "All", q: "" };

async function load() {
  try {
    const res = await fetch("releases.json", { cache: "no-store" });
    const data = await res.json();
    state.all = data.releases || [];
    const openCount = state.all.filter((r) => r.open_source).length;
    document.getElementById("meta").textContent =
      `${data.count} releases · ${openCount} open-source · ${data.companies.length} companies · updated ${data.generated_at}`;
    buildFilters(data.companies, data.types);
    render();
  } catch (err) {
    document.getElementById("meta").textContent = "Could not load releases.json — run `radar build` first.";
    console.error(err);
  }
}

function buildFilters(companies, types) {
  renderChips("company-filters", ["All", ...companies], "company");
  renderChips("type-filters", ["All", ...types], "type");
  renderAccessChips();
}

// Access (open-source) filter — labels differ from values, so render it directly.
function renderAccessChips() {
  const el = document.getElementById("access-filters");
  el.innerHTML = "";
  const opts = [["All", "All"], ["open", "🔓 Open source"], ["proprietary", "🔒 Proprietary"]];
  for (const [val, label] of opts) {
    const chip = document.createElement("button");
    chip.className = "chip" + (state.access === val ? " active" : "");
    chip.textContent = label;
    chip.onclick = () => {
      state.access = val;
      [...el.children].forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      render();
    };
    el.appendChild(chip);
  }
}

function renderChips(containerId, values, key) {
  const el = document.getElementById(containerId);
  el.innerHTML = "";
  for (const v of values) {
    const chip = document.createElement("button");
    chip.className = "chip" + (state[key] === v ? " active" : "");
    chip.textContent = key === "type" && v !== "All" ? v.toUpperCase() : v;
    chip.onclick = () => {
      state[key] = v;
      [...el.children].forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      render();
    };
    el.appendChild(chip);
  }
}

function matches(r) {
  if (state.company !== "All" && r.company !== state.company) return false;
  if (state.type !== "All" && r.type !== state.type) return false;
  if (state.access === "open" && !r.open_source) return false;
  if (state.access === "proprietary" && r.open_source) return false;
  if (state.q) {
    const hay = `${r.company} ${r.product} ${r.title} ${r.summary} ${(r.tags || []).join(" ")}`.toLowerCase();
    if (!hay.includes(state.q)) return false;
  }
  return true;
}

function render() {
  const feed = document.getElementById("feed");
  const empty = document.getElementById("empty");
  const items = state.all.filter(matches);
  feed.innerHTML = "";
  empty.hidden = items.length > 0;

  for (const r of items) {
    const color = COMPANY_COLORS[r.company] || "#7c5cff";
    // Thumbnail: branded monogram tile, with an optional real image layered on top.
    const img = r.image
      ? `<img src="${esc(r.image)}" alt="${esc(r.company)}" loading="lazy" onerror="this.remove()">`
      : "";
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <div class="thumb" style="--c:${color}"><span class="mono">${esc(monogram(r.company))}</span>${img}</div>
      <div class="card-body">
        <div class="card-top">
          <span class="badge" style="background:${color}">${esc(r.company)}</span>
          <span class="type-pill type-${esc(r.type)}">${esc(r.type)}</span>
          ${r.open_source ? `<span class="type-pill os-pill">🔓 open</span>` : ""}
          <span class="date">${esc(r.date)}</span>
        </div>
        <h3>${esc(r.product)} — ${esc(r.title)}</h3>
        <p>${esc(r.summary)}</p>
        <div class="tags">
          ${(r.tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join("")}
          ${r.url ? `<a class="source" href="${esc(r.url)}" target="_blank" rel="noopener">source ↗</a>` : ""}
        </div>
      </div>`;
    feed.appendChild(card);
  }
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

document.getElementById("search").addEventListener("input", (e) => {
  state.q = e.target.value.trim().toLowerCase();
  render();
});

load();
