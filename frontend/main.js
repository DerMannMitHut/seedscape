// ---- Config ----
const svg = document.querySelector("#hexmap");
const tooltip = document.querySelector("#tooltip");
const info = document.querySelector("#hexInfo");
const cacheList = document.querySelector("#cacheList");
const labelCoordsEl = document.querySelector("#labelCoords");
const campaignInput = document.querySelector("#campaign");
const resetBtn = document.querySelector("#resetView");
const themeBtn = document.querySelector("#toggleTheme");

const HEX_SIZE = 28; // outer radius px
const GRID_RADIUS = 5; // hexes around origin (roughly 91 hexes)

// Biome classes map — keep in sync with CSS
// Biomes are chosen per-hex. We try to fetch them from the backend once; otherwise use a procedural fallback.
const biomeIndex = new Map(); // key:"id" → biome string

function biomeFor(q, r, id) {
    const b = biomeIndex.get(id);
    return b ?? "unloaded";
}

// ---- Axial helpers (pointy-top) ----
function axialToPixel(q, r, size) {
    const x = size * (Math.sqrt(3) * q + (Math.sqrt(3) / 2) * r);
    const y = size * ((3 / 2) * r);
    return { x, y };
}
function hexCorner(cx, cy, size, i) {
    const angleDeg = 60 * i - 30; // pointy-top
    const angleRad = (Math.PI / 180) * angleDeg;
    return [cx + size * Math.cos(angleRad), cy + size * Math.sin(angleRad)];
}
function hexPoints(cx, cy, size) {
    const pts = Array.from({ length: 6 }, (_, i) => hexCorner(cx, cy, size, i));
    return pts.map((p) => p.join(",")).join(" ");
}

// ---- ID helpers (A1, B3, C5 …) ----
function axialToId(q, r) {
    // Map to offset coordinates for a readable grid id. Simple scheme:
    // col = q + OFFSET, row = r + OFFSET, then A..Z + 1..N
    const OFFSET = GRID_RADIUS + 1; // keep ids positive
    const col = q + OFFSET; // 0..N
    const row = r + OFFSET; // 0..N
    const letter = String.fromCharCode("A".charCodeAt(0) + col);
    return `${letter}${row + 1}`; // 1-based rows
}

// ---- State ----
const state = {
    scale: 1,
    panX: 0,
    panY: 0,
    selectedKey: null,
    labelCoords: false,
};

// ---- Render grid ----
const posIndex = new Map(); // key:"q,r" → { cx, cy, q, r, id }

function keyQR(q, r) {
    return `${q},${r}`;
}

function generateHexes(radius) {
    const list = [];
    for (let q = -radius; q <= radius; q++) {
        for (let r = Math.max(-radius, -q - radius); r <= Math.min(radius, -q + radius); r++) {
            list.push({ q, r });
        }
    }
    return list;
}

function drawGrid() {
    // Clear
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const width = svg.viewBox.baseVal.width || svg.clientWidth;
    const height = svg.viewBox.baseVal.height || svg.clientHeight;

    // Container groups for transform
    const root = group();
    root.setAttribute("id", "root");
    svg.appendChild(root);

    // Compute positions and bounds
    posIndex.clear();
    const hexes = generateHexes(GRID_RADIUS);
    const xs = [],
        ys = [];
    for (const h of hexes) {
        const { x, y } = axialToPixel(h.q, h.r, HEX_SIZE);
        const id = axialToId(h.q, h.r);
        posIndex.set(keyQR(h.q, h.r), { cx: x, cy: y, ...h, id });
        xs.push(x);
        ys.push(y);
    }
    const pad = HEX_SIZE * 1.2;
    const minX = Math.min(...xs) - pad;
    const maxX = Math.max(...xs) + pad;
    const minY = Math.min(...ys) - pad;
    const maxY = Math.max(...ys) + pad;
    const contentW = maxX - minX;
    const contentH = maxY - minY;
    const fitScale = Math.min(width / contentW, height / contentH) * 0.9;

    // apply initial transform (fit to view) + user pan/zoom
    const scale = fitScale * state.scale;
    const tx = state.panX + width / 2 - ((minX + maxX) / 2) * scale;
    const ty = state.panY + height / 2 - ((minY + maxY) / 2) * scale;
    root.setAttribute("transform", `translate(${tx},${ty}) scale(${scale})`);

    // Render cells
    for (const { cx, cy, q, r, id } of posIndex.values()) {
        const g = group("hexcell");
        g.dataset.q = q;
        g.dataset.r = r;
        g.dataset.id = id;

        const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        poly.setAttribute("points", hexPoints(cx, cy, HEX_SIZE));
        const biome = biomeFor(q, r, id);
        poly.setAttribute("class", `hex ${biome} hex-border`);

        g.appendChild(poly);

        // label
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", cx);
        text.setAttribute("y", cy + 4);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-size", "12");
        text.setAttribute("font-weight", "700");
        text.textContent = state.labelCoords ? `${q},${r}` : id;
        text.setAttribute("class", "hex-label");

        g.appendChild(text);

        // interactivity
        g.addEventListener("pointerenter", (e) => showTooltip(e, `${id} — click to load`));
        g.addEventListener("pointermove", (e) => moveTooltip(e));
        g.addEventListener("pointerleave", hideTooltip);
        g.addEventListener("click", () => onHexClick({ q, r, id }));

        root.appendChild(g);
    }
}

// ---- Pan / Zoom ----
let dragging = false;
let lastX = 0;
let lastY = 0;
svg.addEventListener(
    "wheel",
    (e) => {
        e.preventDefault();
        const delta = -e.deltaY; // up → zoom in
        const factor = Math.exp(delta * 0.0015);
        state.scale = clamp(state.scale * factor, 0.25, 6);
        drawGrid();
    },
    { passive: false }
);

svg.addEventListener("pointerdown", (e) => {
    dragging = true;
    lastX = e.clientX;
    lastY = e.clientY;
    svg.setPointerCapture(e.pointerId);
});
svg.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - lastX;
    const dy = e.clientY - lastY;
    state.panX += dx;
    state.panY += dy;
    lastX = e.clientX;
    lastY = e.clientY;
    drawGrid();
});
svg.addEventListener("pointerup", () => {
    dragging = false;
});
svg.addEventListener("pointerleave", () => {
    dragging = false;
});

resetBtn.addEventListener("click", () => {
    state.scale = 1;
    state.panX = 0;
    state.panY = 0;
    drawGrid();
});
labelCoordsEl.addEventListener("change", () => {
    state.labelCoords = labelCoordsEl.checked;
    drawGrid();
});

// ---- Click handler: fetch + cache ----
async function onHexClick({ id }) {
    await selectHex(id);
}

function currentCampaignOrFail() {
    const v = campaignInput.value.trim();
    if (!v) throw new Error("No campaign selected");
    return v;
}

function cacheKey(campaign, id, version) {
    return `hex:${campaign}:${id}:${version}`;
}

async function getData(id) {
    const campaign = currentCampaignOrFail();
    const latestVersion = localStorage.getItem("hex:latest-version");

    if (latestVersion) {
        const key = cacheKey(campaign, id, latestVersion);
        const cached = localStorage.getItem(key);
        if (cached) {
            const data = JSON.parse(cached);
            return { data, isCached: true };
        }
    }

    const res = await fetch(`/api/${encodeURIComponent(campaign)}/hex/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const ver = String(data.version ?? "0");

    // Purge older cached versions for this (campaign,id)
    for (const k of Object.keys(localStorage)) {
        if (k.startsWith(`hex:${campaign}:${id}:`) && k !== cacheKey(campaign, id, ver)) {
            localStorage.removeItem(k);
        }
    }

    localStorage.setItem(cacheKey(campaign, id, ver), JSON.stringify(data));
    localStorage.setItem("hex:latest-version", ver);
    return { data, isCached: false };
}

async function selectHex(id) {
    setSelected(id);

    try {
        const { data, isCached } = await getData(id);

        if (data.biome) {
            const biomeName = data.biome.name;
            biomeIndex.set(id, biomeName);
            const cell = svg.querySelector(`g.hexcell[data-id="${id}"] polygon`);
            if (cell) {
                cell.setAttribute("class", `hex ${biomeName} hex-border`);
            }
        }
        renderInfo(data, { cached: isCached });
    } catch (err) {
        const demo = {
            id,
            biome: { name: "demo", altitude: 0, temperature: 0, humidity: 0 },
            features: [{ name: "demo" }],
            encounter: { name: "demo" },
            discovered: false,
        };
        renderInfo(demo, { cached: false, demo: true, error: String(err) });
    }

    refreshCacheList();
}

function setSelected(id) {
    // remove old selection
    svg.querySelectorAll(".hex.selected").forEach((el) => el.classList.remove("selected"));
    // find matching cell
    const cell = [...svg.querySelectorAll(".hexcell")].find((g) => g.dataset.id === id);
    if (cell) {
        const poly = cell.querySelector("polygon");
        poly?.classList.add("selected");
    }
}

function renderInfo(payload, { cached = false, demo = false, error = null } = {}) {
    info.innerHTML = "";
    const block = document.createElement("div");
    block.className = "card";
    const biome = payload.biome;
    const features = payload.features ?? [];
    const encounter = payload.encounter;
    const createdAt = payload.created_at ? String(payload.created_at) : "";
    const biomeName = biome?.name ?? "unknown";
    const encounterName = encounter?.name ?? "—";

    block.innerHTML = `
    <div class="row"><span class="k">Hex</span><span class="v">${escapeHtml(payload.id ?? payload.label ?? "—")}</span></div>
    <div class="row"><span class="k">Biome</span><span class="v">${escapeHtml(biomeName)}</span></div>
    <div class="row"><span class="k">Altitude</span><span class="v">${escapeHtml(biome.altitude)}</span></div>
    <div class="row"><span class="k">Temperature</span><span class="v">${escapeHtml(biome.temperature)}</span></div>
    <div class="row"><span class="k">Humidity</span><span class="v">${escapeHtml(biome.humidity)}</span></div>
    <div class="row"><span class="k">Features</span><span class="v">${features.length ? features.map((f) => escapeHtml(f.name)).join(", ") : "—"}</span></div>
    <div class="row"><span class="k">Encounter</span><span class="v">${escapeHtml(encounterName)}</span></div>
    <div class="row"><span class="k">Discovered</span><span class="v">${payload.discovered ? "yes" : "no"}</span></div>
    <div class="row"><span class="k">Created</span><span class="v">${escapeHtml(createdAt || "—")}</span></div>
    <div class="meta">${cached ? "from cache" : demo ? "demo data" : "live"}${error ? ` — <span class="err">${escapeHtml(error)}</span>` : ""}</div>
  `;
    info.appendChild(block);
}

function refreshCacheList() {
    cacheList.innerHTML = "";
    const items = Object.keys(localStorage)
        .filter((k) => k.startsWith("hex:"))
        .sort();
    if (items.length === 0) {
        cacheList.innerHTML = '<li class="muted">No cached entries</li>';
        return;
    }
    for (const key of items) {
        const li = document.createElement("li");
        const { campaign, id, version } = parseCacheKey(key);
        li.innerHTML = `<button data-k="${key}">${id}</button> <span class="muted">(${campaign} • v${version})</span>`;
        li.querySelector("button").addEventListener("click", () => {
            const payload = JSON.parse(localStorage.getItem(key));
            renderInfo(payload, { cached: true });
            setSelected(id);
        });
        cacheList.appendChild(li);
    }
}

function parseCacheKey(k) {
    // hex:campaign:id:version
    const [, campaign, id, version] = k.split(":");
    return { campaign, id, version };
}

// ---- Utilities ----
function group(cls) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    if (cls) g.setAttribute("class", cls);
    return g;
}
function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
}
function showTooltip(e, text) {
    tooltip.textContent = text;
    tooltip.hidden = false;
    moveTooltip(e);
}
function moveTooltip(e) {
    const pad = 12;
    tooltip.style.left = e.clientX + pad + "px";
    tooltip.style.top = e.clientY + pad + "px";
}
function hideTooltip() {
    tooltip.hidden = true;
}
function escapeHtml(s) {
    return String(s).replace(
        /[&<>"']/g,
        (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]
    );
}

// ---- Init ----
labelCoordsEl.checked = state.labelCoords;
try {
    ensureCampaignStyles(currentCampaignOrFail());
} catch (e) {
    console.error("Campaign styles not loaded:", e);
}
drawGrid();
refreshCacheList();

const clearCacheBtn = document.getElementById("clearCache");
clearCacheBtn?.addEventListener("click", () => {
    if (confirm("Delete all cached hex data?")) {
        for (const key of Object.keys(localStorage)) {
            if (key.startsWith("hex:")) {
                localStorage.removeItem(key);
            }
        }
        biomeIndex.clear();
        refreshCacheList();
        location.reload();
    }
});

// -------------------------------------------------------------------------------- Theme toggle
function applyTheme() {
    const isDark = document.body.classList.contains("theme-dark");
    themeBtn.textContent = isDark ? "Light mode" : "Dark mode";
}

themeBtn?.addEventListener("click", () => {
    document.body.classList.toggle("theme-dark");
    document.body.classList.toggle("theme-light");
    applyTheme();
});
applyTheme();

// -------------------------------------------------------------------------------- preselect hex
selectHex(axialToId(0, 0));

// -------------------------------------------------------------------------------- campaign assets (biomes.css)
function ensureCampaignStyles(campaign) {
    const id = "campaign-biomes-css";
    const href = `/api/campaigns/${encodeURIComponent(campaign)}/assets/biomes.css`;
    let link = document.getElementById(id);
    if (!link) {
        link = document.createElement("link");
        link.id = id;
        link.rel = "stylesheet";
        document.head.appendChild(link);
    }
    // Add a cache-busting param when campaign changes
    const url = new URL(href, location.origin);
    url.searchParams.set("_", String(Date.now()));
    link.href = url.pathname + url.search;
}

campaignInput.addEventListener("change", () => {
    const v = campaignInput.value.trim();
    if (!v) {
        console.error("No campaign selected; not loading styles");
        return;
    }
    ensureCampaignStyles(v);
});
