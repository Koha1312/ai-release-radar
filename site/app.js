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
  "Perplexity": "#20b8cd",
  "Cursor": "#6366f1",
  "Obsidian": "#9d6bf0",
  "xAI": "#1d9bf0",
  "ElevenLabs": "#a78bfa",
  "GitHub": "#8b949e",
  "OpenClaw": "#f59e0b",
  "n8n": "#ea4b71",
  "Notion": "#b9b3a9",
  "Raycast": "#ff6363",
  "Zed": "#2f6df6",
  "Canva": "#00c4cc",
  "Figma": "#f24e1e",
  "Brave": "#fb542b",
  "Apple": "#9aa0a6",
  "Mistral": "#fa520f",
  "Stability AI": "#9d39e0",
};

// Short monogram per company for the branded thumbnail tile.
const COMPANY_CODES = {
  "Anthropic": "A", "OpenAI": "O", "Google": "G", "Microsoft": "MS",
  "Z.ai": "Z", "DeepSeek": "DS", "Moonshot AI": "Mo", "Meta": "M", "Hugging Face": "HF",
  "Perplexity": "P", "Cursor": "C", "Obsidian": "Ob",
  "xAI": "X", "ElevenLabs": "11", "GitHub": "GH", "OpenClaw": "OC", "n8n": "n8",
  "Notion": "N", "Raycast": "Ra", "Zed": "Ze", "Canva": "Ca", "Figma": "Fi",
  "Brave": "Br", "Apple": "Ap", "Mistral": "Mi", "Stability AI": "St",
};
const monogram = (c) => COMPANY_CODES[c] || (c[0] || "?").toUpperCase();

// Companies with a real logo file in img/ (Simple Icons). Others use a monogram.
const COMPANY_LOGO = {
  "Anthropic": "anthropic", "OpenAI": "openai", "Google": "google", "Google DeepMind": "google",
  "Microsoft": "microsoft", "Meta": "meta", "DeepSeek": "deepseek", "ElevenLabs": "elevenlabs",
  "GitHub": "github", "Apple": "apple", "n8n": "n8n", "Notion": "notion", "Raycast": "raycast",
  "Canva": "canva", "Figma": "figma", "Brave": "brave", "Perplexity": "perplexity",
  "Obsidian": "obsidian", "Cursor": "cursor", "xAI": "x", "Mistral": "mistralai",
};

function isNew(dateStr) {
  if (!dateStr) return false;
  const days = (Date.now() - new Date(dateStr + "T00:00:00").getTime()) / 86400000;
  return days >= 0 && days <= 7; // announced within the last week
}

// Human "2 days ago" / "3 months ago" — the freshness cue the stats sites use.
function relativeDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  if (isNaN(d)) return "";
  const days = Math.floor((Date.now() - d.getTime()) / 86400000);
  if (days < 0) return "scheduled";
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 7) return `${days} days ago`;
  if (days < 14) return "last week";
  if (days < 31) return `${Math.floor(days / 7)} weeks ago`;
  if (days < 61) return "last month";
  if (days < 365) return `${Math.floor(days / 30)} months ago`;
  const y = Math.floor(days / 365);
  return y === 1 ? "last year" : `${y} years ago`;
}

// Infer the modality of a release from its text (we don't store it). First match wins.
const MODALITY = [
  { key: "video", icon: "🎬", label: "video", re: /\b(video|sora|veo|runway|kling|movie|text-to-video)\b/i },
  { key: "image", icon: "🖼️", label: "image", re: /\b(image|diffusion|dall-?e|imagen|midjourney|photo|vision|inpaint|text-to-image)\b/i },
  { key: "audio", icon: "🔊", label: "audio", re: /\b(audio|speech|voice|tts|text-to-speech|music|whisper|sound|transcrib)\b/i },
  { key: "robotics", icon: "🤖", label: "robotics", re: /\b(robot|embodied|humanoid|manipulation)\b/i },
  { key: "code", icon: "💻", label: "code", re: /\b(code|coding|copilot|swe-?bench|developer|programming|autocomplete)\b/i },
];
function inferModality(r) {
  const hay = `${r.product} ${r.title} ${r.summary} ${(r.tags || []).join(" ")}`;
  for (const m of MODALITY) if (m.re.test(hay)) return m;
  return { key: "text", icon: "💬", label: "text" };
}

const MONTHS = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];
function monthLabel(mk) {
  const [y, m] = (mk || "").split("-");
  return m ? `${MONTHS[+m - 1]} ${y}` : "Undated";
}

const state = { all: [], company: "All", type: "All", access: "All", q: "" };

async function load() {
  try {
    const res = await fetch("releases.json", { cache: "no-store" });
    const data = await res.json();
    state.all = data.releases || [];
    readUrl();
    document.getElementById("search").value = state.q;
    const openCount = state.all.filter((r) => r.open_source).length;
    document.getElementById("meta").textContent =
      `${data.count} releases · ${openCount} open-source · ${data.companies.length} companies · updated ${data.generated_at}`;
    buildFilters(data.companies, data.types);
    render();
    renderHeroStats();
    initAnalytics();
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
  const counts = {
    All: state.all.length,
    open: state.all.filter((r) => r.open_source).length,
    proprietary: state.all.filter((r) => !r.open_source).length,
  };
  const opts = [["All", "All"], ["open", "🔓 Open source"], ["proprietary", "🔒 Proprietary"]];
  for (const [val, label] of opts) {
    const chip = document.createElement("button");
    chip.className = "chip" + (state.access === val ? " active" : "");
    chip.innerHTML = `${label} <span class="cc">${counts[val]}</span>`;
    chip.onclick = () => {
      state.access = val;
      [...el.children].forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      render();
    };
    el.appendChild(chip);
  }
}

function countFor(key, value) {
  if (value === "All") return state.all.length;
  return state.all.filter((r) => r[key] === value).length;
}

function renderChips(containerId, values, key) {
  const el = document.getElementById(containerId);
  el.innerHTML = "";
  for (const v of values) {
    const chip = document.createElement("button");
    chip.className = "chip" + (state[key] === v ? " active" : "");
    const label = key === "type" && v !== "All" ? v.toUpperCase() : v;
    chip.innerHTML = `${esc(label)} <span class="cc">${countFor(key, v)}</span>`;
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

// Shareable filter links: keep ?company=&type=&access=&q= in sync with state.
function readUrl() {
  const p = new URLSearchParams(location.search);
  for (const k of ["company", "type", "access"]) if (p.get(k)) state[k] = p.get(k);
  if (p.get("q")) state.q = p.get("q");
}
function syncUrl() {
  const p = new URLSearchParams();
  if (state.company !== "All") p.set("company", state.company);
  if (state.type !== "All") p.set("type", state.type);
  if (state.access !== "All") p.set("access", state.access);
  if (state.q) p.set("q", state.q);
  const qs = p.toString();
  history.replaceState(null, "", qs ? "?" + qs : location.pathname);
}

function render() {
  syncUrl();
  renderSpotlight();
  const feed = document.getElementById("feed");
  const empty = document.getElementById("empty");
  const items = state.all.filter(matches);
  feed.innerHTML = "";
  empty.hidden = items.length > 0;

  let curMonth = null;
  for (const r of items) {
    const mk = (r.date || "").slice(0, 7); // YYYY-MM
    if (mk !== curMonth) {
      curMonth = mk;
      const h = document.createElement("div");
      h.className = "month-header";
      h.textContent = monthLabel(mk);
      feed.appendChild(h);
    }
    const color = COMPANY_COLORS[r.company] || "#7c5cff";
    const mod = inferModality(r);
    // Thumbnail: real logo (Simple Icons, tinted white) or a branded monogram tile.
    const logo = COMPANY_LOGO[r.company];
    const tileInner = logo
      ? `<span class="logo" style="-webkit-mask-image:url('img/${logo}.svg');mask-image:url('img/${logo}.svg')"></span>`
      : `<span class="mono">${esc(monogram(r.company))}</span>`;
    const img = r.image
      ? `<img src="${esc(r.image)}" alt="${esc(r.company)}" loading="lazy" onerror="this.remove()">`
      : "";
    const card = document.createElement("article");
    card.className = "card";
    card.style.setProperty("--c", color); // brand-color accent bar + hover glow
    card.innerHTML = `
      <div class="thumb" style="--c:${color}">${tileInner}${img}</div>
      <div class="card-body">
        <div class="card-top">
          <span class="badge" style="background:${color}">${esc(r.company)}</span>
          <span class="type-pill type-${esc(r.type)}">${esc(r.type)}</span>
          <span class="type-pill modality-pill" title="modality: ${mod.label}">${mod.icon} ${mod.label}</span>
          ${r.open_source ? `<span class="type-pill os-pill">🔓 open</span>` : ""}
          ${isNew(r.date) ? `<span class="new-badge">🆕 NEW</span>` : ""}
          <span class="date" title="${esc(r.date)}">${esc(relativeDate(r.date) || r.date)}</span>
        </div>
        <h3>${esc(r.product)} — ${esc(r.title)}</h3>
        <p>${esc(r.summary)}</p>
        <div class="tags">
          ${(r.tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join("")}
          ${r.url ? `<span class="trust ${r.official ? "official" : "reported"}" title="${r.official ? "Primary source — the company's own announcement" : "Secondary source — reported by a news site"}">${r.official ? "✓ official" : "↗ reported"}</span>` : ""}
          ${r.url ? `<a class="source" href="${esc(r.url)}" target="_blank" rel="noopener">source ↗</a>` : ""}
        </div>
      </div>`;
    // Make the whole card open the source — but don't hijack real links or text selection.
    if (r.url) {
      card.classList.add("clickable");
      card.addEventListener("click", (e) => {
        if (e.target.closest("a") || String(window.getSelection())) return;
        window.open(r.url, "_blank", "noopener");
      });
    }
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

// Company spotlight: when one company is selected, show a header card with its stats.
function renderSpotlight() {
  const el = document.getElementById("spotlight");
  if (!el) return;
  if (state.company === "All") { el.hidden = true; el.innerHTML = ""; return; }
  const items = state.all.filter((r) => r.company === state.company);
  if (!items.length) { el.hidden = true; el.innerHTML = ""; return; }
  const color = COMPANY_COLORS[state.company] || "#7c5cff";
  const logo = COMPANY_LOGO[state.company];
  const tile = logo
    ? `<span class="logo" style="-webkit-mask-image:url('img/${logo}.svg');mask-image:url('img/${logo}.svg')"></span>`
    : `<span class="mono">${esc(monogram(state.company))}</span>`;
  const latest = [...items].sort((a, b) => (b.date || "").localeCompare(a.date || ""))[0];
  const openN = items.filter((r) => r.open_source).length;
  const officialN = items.filter((r) => r.official).length;
  el.hidden = false;
  el.innerHTML = `
    <div class="spotlight-card" style="--c:${color}">
      <div class="thumb spotlight-thumb" style="--c:${color}">${tile}</div>
      <div class="spotlight-body">
        <h2>${esc(state.company)}</h2>
        <div class="spotlight-stats">
          <span><b>${items.length}</b> releases</span>
          <span><b>${openN}</b> open-source</span>
          <span><b>${officialN}</b> official-sourced</span>
        </div>
        <div class="spotlight-latest">Latest: <b>${esc(latest.product)}</b> · ${esc(relativeDate(latest.date) || latest.date)}</div>
      </div>
    </div>`;
}

// Analytics panel: releases-by-company bars + a 12-month cadence chart + type breakdown.
function renderAnalytics() {
  const el = document.getElementById("analytics");
  if (!el) return;
  const byCo = {};
  for (const r of state.all) byCo[r.company] = (byCo[r.company] || 0) + 1;
  const cos = Object.entries(byCo).sort((a, b) => b[1] - a[1]);
  const maxCo = Math.max(1, ...cos.map((c) => c[1]));
  const coBars = cos.map(([c, n]) => `
    <div class="abar-row">
      <span class="abar-label">${esc(c)}</span>
      <span class="abar-track"><span class="abar-fill" style="width:${Math.round((n / maxCo) * 100)}%;background:${COMPANY_COLORS[c] || "#7c5cff"}"></span></span>
      <span class="abar-num">${n}</span>
    </div>`).join("");

  const byMonth = {};
  for (const r of state.all) { const mk = (r.date || "").slice(0, 7); if (mk) byMonth[mk] = (byMonth[mk] || 0) + 1; }
  const now = new Date();
  const months = [];
  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const mk = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    months.push({ mk, count: byMonth[mk] || 0 });
  }
  const maxM = Math.max(1, ...months.map((m) => m.count));
  const monthCols = months.map((m) => `
    <span class="acol" title="${monthLabel(m.mk)}: ${m.count}">
      <span class="acol-fill" style="height:${Math.round((m.count / maxM) * 90) + 4}px"></span>
      <span class="acol-x">${m.mk.slice(5)}</span>
    </span>`).join("");

  const byType = {};
  for (const r of state.all) byType[r.type] = (byType[r.type] || 0) + 1;
  const typeChips = Object.entries(byType).sort((a, b) => b[1] - a[1])
    .map(([t, n]) => `<span class="atype">${esc(t)} <b>${n}</b></span>`).join("");

  el.innerHTML = `
    <div class="apanel">
      <div class="ablock">
        <h4>Releases by company</h4>
        <div class="abars">${coBars}</div>
      </div>
      <div class="ablock">
        <h4>Release cadence — last 12 months</h4>
        <div class="acols">${monthCols}</div>
        <h4 style="margin-top:16px">By type</h4>
        <div class="atypes">${typeChips}</div>
      </div>
    </div>`;
}

function initAnalytics() {
  const btn = document.getElementById("analytics-toggle");
  const panel = document.getElementById("analytics");
  if (!btn || !panel) return;
  renderAnalytics();
  btn.onclick = () => {
    const open = panel.hidden; // currently hidden -> we're opening
    panel.hidden = !open;
    btn.classList.toggle("active", open);
    btn.textContent = open ? "📊 Hide analytics" : "📊 Analytics";
  };
}

// Hero: "N releases this month" + a 6-month sparkline.
function renderHeroStats() {
  const el = document.getElementById("hero-stats");
  if (!el) return;
  const byMonth = {};
  for (const r of state.all) {
    const mk = (r.date || "").slice(0, 7);
    if (mk) byMonth[mk] = (byMonth[mk] || 0) + 1;
  }
  const now = new Date();
  const months = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const mk = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    months.push({ mk, count: byMonth[mk] || 0 });
  }
  const thisMonth = months[months.length - 1].count;
  const max = Math.max(1, ...months.map((m) => m.count));
  const bars = months
    .map((m) => `<span class="bar" style="height:${Math.round((m.count / max) * 26) + 3}px" title="${monthLabel(m.mk)}: ${m.count}"></span>`)
    .join("");
  el.innerHTML = `<span class="stat-num">${thisMonth}</span> releases this month <span class="spark">${bars}</span>`;
}

// Light / dark theme toggle (persisted).
function initTheme() {
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;
  if (localStorage.getItem("radar-theme") === "light") document.body.classList.add("light");
  const sync = () => { btn.textContent = document.body.classList.contains("light") ? "🌙" : "☀️"; };
  sync();
  btn.onclick = () => {
    document.body.classList.toggle("light");
    localStorage.setItem("radar-theme", document.body.classList.contains("light") ? "light" : "dark");
    sync();
  };
}

initTheme();
load();
