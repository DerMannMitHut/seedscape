// ---- Config ----
const svg = document.querySelector('#hexmap');
const tooltip = document.querySelector('#tooltip');
const info = document.querySelector('#hexInfo');
const cacheList = document.querySelector('#cacheList');
const labelCoordsEl = document.querySelector('#labelCoords');
const campaignInput = document.querySelector('#campaign');
const resetBtn = document.querySelector('#resetView');
const themeBtn = document.querySelector('#toggleTheme');

const HEX_SIZE = 28; // outer radius px
const GRID_RADIUS = 5; // hexes around origin (roughly 91 hexes)

// Biome classes map — keep in sync with CSS
// Biomes are chosen per-hex. We try to fetch them from the backend once; otherwise use a procedural fallback.
const biomeIndex = new Map(); // key:"id" → biome string

function biomeFor(q, r, id) {
  const b = biomeIndex.get(id);
  if (b) return b;
  // Fallback procedural pattern (varied but deterministic)
  const dist = Math.max(Math.abs(q), Math.abs(r), Math.abs(-q - r));
  const hash = (id || '').split('').reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 0);
  if (dist <= 1) return 'plains';
  if (dist === 2) return (hash % 3 === 0) ? 'forest' : 'hills';
  if (dist === 3) return (hash % 4 === 0) ? 'mountains' : 'desert';
  if ((q === 0 || q === 1) && r >= -2) return 'water'; // a little river
  return ['forest','hills','swamp','desert','tundra'][hash % 5];
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
  return pts.map((p) => p.join(',')).join(' ');
}

// ---- ID helpers (A1, B3, C5 …) ----
function axialToId(q, r) {
  // Map to offset coordinates for a readable grid id. Simple scheme:
  // col = q + OFFSET, row = r + OFFSET, then A..Z + 1..N
  const OFFSET = GRID_RADIUS + 1; // keep ids positive
  const col = q + OFFSET; // 0..N
  const row = r + OFFSET; // 0..N
  const letter = String.fromCharCode('A'.charCodeAt(0) + col);
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

function keyQR(q, r) { return `${q},${r}`; }

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
  root.setAttribute('id', 'root');
  svg.appendChild(root);

  // Compute positions and bounds
  posIndex.clear();
  const hexes = generateHexes(GRID_RADIUS);
  const xs = [], ys = [];
  for (const h of hexes) {
    const { x, y } = axialToPixel(h.q, h.r, HEX_SIZE);
    const id = axialToId(h.q, h.r);
    posIndex.set(keyQR(h.q, h.r), { cx: x, cy: y, ...h, id });
    xs.push(x); ys.push(y);
  }
  const pad = HEX_SIZE * 1.2;
  const minX = Math.min(...xs) - pad; const maxX = Math.max(...xs) + pad;
  const minY = Math.min(...ys) - pad; const maxY = Math.max(...ys) + pad;
  const contentW = maxX - minX; const contentH = maxY - minY;
  const fitScale = Math.min(width / contentW, height / contentH) * 0.9;

  // apply initial transform (fit to view) + user pan/zoom
  const scale = fitScale * state.scale;
  const tx = state.panX + width / 2 - ((minX + maxX) / 2) * scale;
  const ty = state.panY + height / 2 - ((minY + maxY) / 2) * scale;
  root.setAttribute('transform', `translate(${tx},${ty}) scale(${scale})`);

  // Render cells
  for (const { cx, cy, q, r, id } of posIndex.values()) {
    const g = group('hexcell');
    g.dataset.q = q; g.dataset.r = r; g.dataset.id = id;

    const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    poly.setAttribute('points', hexPoints(cx, cy, HEX_SIZE));
    const biome = biomeFor(q, r, id);
    poly.setAttribute('class', `hex ${biome} hex-border`);

    g.appendChild(poly);

    // label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', cx);
    text.setAttribute('y', cy + 4);
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('font-size', '12');
    text.setAttribute('font-weight', '700');
        text.textContent = state.labelCoords ? `${q},${r}` : id;
    text.setAttribute('class', 'hex-label');

    g.appendChild(text);

    // interactivity
    g.addEventListener('pointerenter', (e) => showTooltip(e, `${id} — click to load`));
    g.addEventListener('pointermove', (e) => moveTooltip(e));
    g.addEventListener('pointerleave', hideTooltip);
    g.addEventListener('click', () => onHexClick({ q, r, id }));

    root.appendChild(g);
  }
}

// ---- Pan / Zoom ----
let dragging = false; let lastX = 0; let lastY = 0;
svg.addEventListener('wheel', (e) => {
  e.preventDefault();
  const delta = -e.deltaY; // up → zoom in
  const factor = Math.exp(delta * 0.0015);
  state.scale = clamp(state.scale * factor, 0.25, 6);
  drawGrid();
}, { passive: false });

svg.addEventListener('pointerdown', (e) => {
  dragging = true; lastX = e.clientX; lastY = e.clientY; svg.setPointerCapture(e.pointerId);
});
svg.addEventListener('pointermove', (e) => {
  if (!dragging) return;
  const dx = e.clientX - lastX; const dy = e.clientY - lastY;
  state.panX += dx; state.panY += dy; lastX = e.clientX; lastY = e.clientY;
  drawGrid();
});
svg.addEventListener('pointerup', () => { dragging = false; });
svg.addEventListener('pointerleave', () => { dragging = false; });

resetBtn.addEventListener('click', () => { state.scale = 1; state.panX = 0; state.panY = 0; drawGrid(); });
labelCoordsEl.addEventListener('change', () => { state.labelCoords = labelCoordsEl.checked; drawGrid(); });

// ---- Click handler: fetch + cache ----
async function onHexClick({ id }) {
  await selectHex(id);
}

async function selectHex(id) {
  setSelected(id);
  const campaign = campaignInput.value.trim() || 'default';
  const cacheKey = `hex:${campaign}:${id}`;

  // Try cache first
  const cached = localStorage.getItem(cacheKey);
  if (cached) {
    renderInfo(JSON.parse(cached), { cached: true });
  }

  try {
    const res = await fetch(`/api/${encodeURIComponent(campaign)}/hex/${encodeURIComponent(id)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    // Save cache + render
    localStorage.setItem(cacheKey, JSON.stringify(data));
    renderInfo(data, { cached: false });
  } catch (err) {
    // Fallback demo content so you see immediate results
    const demo = demoHexPayload(id);
    renderInfo(demo, { cached: false, demo: true, error: String(err) });
  }

  refreshCacheList();
}

function setSelected(id) {
  // remove old selection
  svg.querySelectorAll('.hex.selected').forEach((el) => el.classList.remove('selected'));
  // find matching cell
  const cell = [...svg.querySelectorAll('.hexcell')].find((g) => g.dataset.id === id);
  if (cell) {
    const poly = cell.querySelector('polygon');
    poly?.classList.add('selected');
  }
}

function renderInfo(payload, { cached = false, demo = false, error = null } = {}) {
  info.innerHTML = '';
  const block = document.createElement('div');
  block.className = 'card';
  block.innerHTML = `
    <div class="row"><span class="k">Hex</span><span class="v">${escapeHtml(payload.id ?? payload.label ?? '—')}</span></div>
    <div class="row"><span class="k">Biome</span><span class="v">${escapeHtml(payload.biome ?? 'unknown')}</span></div>
    <div class="row"><span class="k">Summary</span><span class="v">${escapeHtml(payload.summary ?? '—')}</span></div>
    <div class="row"><span class="k">Threat</span><span class="v">${escapeHtml(payload.threat ?? '—')}</span></div>
    <div class="row"><span class="k">Loot</span><span class="v">${escapeHtml(payload.loot ?? '—')}</span></div>
    <div class="meta">${cached ? 'from cache' : demo ? 'demo data' : 'live' }${error ? ` — <span class="err">${escapeHtml(error)}</span>` : ''}</div>
  `;
  info.appendChild(block);
}

function refreshCacheList() {
  cacheList.innerHTML = '';
  const items = Object.keys(localStorage)
    .filter((k) => k.startsWith('hex:'))
    .sort();
  if (items.length === 0) {
    cacheList.innerHTML = '<li class="muted">No cached entries</li>';
    return;
  }
  for (const key of items) {
    const li = document.createElement('li');
    const { campaign, id } = parseCacheKey(key);
    li.innerHTML = `<button data-k="${key}">${id}</button> <span class="muted">(${campaign})</span>`;
    li.querySelector('button').addEventListener('click', () => {
      const payload = JSON.parse(localStorage.getItem(key));
      renderInfo(payload, { cached: true });
      setSelected(id);
    });
    cacheList.appendChild(li);
  }
}

function parseCacheKey(k) {
  // hex:campaign:id
  const [, campaign, id] = k.split(':');
  return { campaign, id };
}

// ---- Utilities ----
function group(cls) {
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  if (cls) g.setAttribute('class', cls);
  return g;
}
function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }
function showTooltip(e, text) {
  tooltip.textContent = text; tooltip.hidden = false; moveTooltip(e);
}
function moveTooltip(e) {
  const pad = 12;
  tooltip.style.left = e.clientX + pad + 'px';
  tooltip.style.top = e.clientY + pad + 'px';
}
function hideTooltip() { tooltip.hidden = true; }
function escapeHtml(s) { return String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c])); }

function demoHexPayload(id) {
  // Minimal fake to visualize the UI if backend is not yet wired
  const biomes = ['plains','forest','hills','mountains','swamp','desert','water','tundra'];
  const seed = id.split('').reduce((a,c) => a + c.charCodeAt(0), 0);
  const biome = biomes[seed % biomes.length];
  return {
    id,
    biome,
    summary: `A ${biome} hex with gentle features. (demo)`,
    threat: ['none','low','moderate','high'][seed % 4],
    loot: ['berries','ore vein','ruins','herbs'][seed % 4],
  };
}

// Try to fetch a biome map for the grid (optional API)
async function loadBiomeIndex() {
  try {
    const campaign = campaignInput.value.trim() || 'default';
    const res = await fetch(`/api/${encodeURIComponent(campaign)}/hexmap`);
    if (!res.ok) return;
    const list = await res.json(); // expect [{id, biome}] or [{q,r,biome}]
    for (const item of list) {
      const id = item.id ?? axialToId(item.q, item.r);
      if (item.biome) biomeIndex.set(id, item.biome);
    }
  } catch (_) { /* ignore, fallback will be used */ }
}

// ---- Init ----
labelCoordsEl.checked = state.labelCoords;
drawGrid();
refreshCacheList();

// Theme toggle
function applyTheme() {
  const isDark = document.body.classList.contains('theme-dark');
  themeBtn.textContent = isDark ? 'Light mode' : 'Dark mode';
}

themeBtn?.addEventListener('click', () => {
  document.body.classList.toggle('theme-dark');
  document.body.classList.toggle('theme-light');
  applyTheme();
});
applyTheme();

// Preselect a central hex for quick demo
selectHex(axialToId(0,0));
