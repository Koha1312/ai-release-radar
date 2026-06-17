// AI Release Radar — loads the generated releases.json and renders a
// filterable, searchable feed. Pure vanilla JS, no build step, no backend.

const COMPANY_COLORS = {
  "Anthropic": "#d97757",
  "OpenAI": "#10a37f",
  "Google": "#4285f4",
  "Google DeepMind": "#4285f4",
  "Microsoft": "#0078d4",
  "Hugging Face": "#ff9d00",
};

const state = { all: [], company: "All", type: "All", q: "" };

async function load() {
  try {
    const res = await fetch("releases.json", { cache: "no-store" });
    const data = await res.json();
    state.all = data.releases || [];
    document.getElementById("meta").textContent =
      `${data.count} releases · ${data.companies.length} companies · updated ${data.generated_at}`;
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
    const card = document.createElement("article");
    card.className = "card";
    card.innerHTML = `
      <div class="card-top">
        <span class="badge" style="background:${color}">${esc(r.company)}</span>
        <span class="type-pill type-${esc(r.type)}">${esc(r.type)}</span>
        <span class="date">${esc(r.date)}</span>
      </div>
      <h3>${esc(r.product)} — ${esc(r.title)}</h3>
      <p>${esc(r.summary)}</p>
      <div class="tags">
        ${(r.tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join("")}
        ${r.url ? `<a class="source" href="${esc(r.url)}" target="_blank" rel="noopener">source ↗</a>` : ""}
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
