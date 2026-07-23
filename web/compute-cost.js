/** Optional compute_cost: line in card reports / descriptions (see koi.projects.compute_cost). */

const COMPUTE_COST_RE = /^compute_cost:\s*(.+)$/im;
const PAIR_RE = /^([a-z_]+)\s*=\s*(.+)$/i;
const HOURS_RE = /^([+-]?\d+(?:[.,]\d+)?)\s*(h|hr|hrs|hours|m|min|mins|minutes|s|sec|secs)?$/i;
const VALID_SOURCES = new Set(["measured", "estimated", "recovered"]);

/**
 * @param {string|null|undefined} raw
 * @returns {number|null}
 */
export function parseHoursValue(raw) {
  if (raw == null) return null;
  const s = String(raw).trim();
  if (!s) return null;
  const m = HOURS_RE.exec(s);
  if (!m) return null;
  const n = Number(m[1].replace(",", "."));
  if (!Number.isFinite(n)) return null;
  const unit = (m[2] || "h").toLowerCase();
  if (unit.startsWith("m")) return n / 60;
  if (unit.startsWith("s")) return n / 3600;
  return n;
}

/**
 * @param {string} raw
 * @returns {string[]}
 */
function splitPairs(raw) {
  const text = String(raw || "").trim();
  if (!text) return [];
  if (text.includes(";")) {
    return text
      .split(";")
      .map((c) => c.trim())
      .filter(Boolean);
  }
  return (text.match(/[a-z_]+\s*=\s*\S+/gi) || []).map((c) => c.trim());
}

/**
 * @param {string|null|undefined} text
 * @returns {null|{raw:string, wall_h?:number, gpu_h?:number, n_gpus?:number, until?:string, source:string}}
 */
export function parseComputeCost(text) {
  const body = String(text || "").replace(/\\n/g, "\n");
  const m = COMPUTE_COST_RE.exec(body);
  if (!m) return null;
  const raw = m[1].trim();
  if (!raw) return null;

  /** @type {Record<string, string>} */
  const fields = {};
  for (const chunk of splitPairs(raw)) {
    const pm = PAIR_RE.exec(chunk);
    if (!pm) continue;
    fields[pm[1].trim().toLowerCase()] = pm[2].trim();
  }
  if (!Object.keys(fields).length) return null;

  /** @type {{raw:string, wall_h?:number, gpu_h?:number, n_gpus?:number, until?:string, source:string}} */
  const out = { raw, source: "measured" };
  const wall = parseHoursValue(fields.wall_h || fields.wall);
  const gpu = parseHoursValue(fields.gpu_h || fields.gpu || fields.gpu_hours);
  if (wall != null) out.wall_h = wall;
  if (gpu != null) out.gpu_h = gpu;

  const nRaw = fields.n_gpus || fields.gpus || fields.n_gpu;
  if (nRaw != null && /^\d+$/.test(String(nRaw).trim())) {
    out.n_gpus = Number(String(nRaw).trim());
  }

  const until = fields.until || fields.to;
  if (until) out.until = until;

  const source = String(fields.source || "measured").trim().toLowerCase();
  out.source = VALID_SOURCES.has(source) ? source : "measured";

  if (out.wall_h == null && out.gpu_h == null) return null;
  return out;
}

/**
 * @param {string|null|undefined} description
 * @param {string|null|undefined} reportContent
 */
export function mergeComputeCost(description, reportContent) {
  return parseComputeCost(description) || parseComputeCost(reportContent);
}

/**
 * @param {number|null|undefined} hours
 * @returns {string|null}
 */
export function formatHoursShort(hours) {
  if (hours == null || !Number.isFinite(Number(hours))) return null;
  const h = Number(hours);
  if (h < 0) return null;
  if (h < 1 / 60) return `${Math.max(1, Math.round(h * 3600))}s`;
  if (h < 1) {
    const mins = h * 60;
    const label = mins < 10 ? String(Number(mins.toFixed(1))) : String(Math.round(mins));
    return `${label}m`;
  }
  const label = h < 10 ? String(Number(h.toFixed(2))) : String(Number(h.toFixed(1)));
  return `${label}h`;
}

/**
 * @param {ReturnType<typeof parseComputeCost>} cost
 * @returns {string}
 */
export function computeCostTitle(cost) {
  if (!cost) return "";
  const bits = [];
  if (cost.wall_h != null) bits.push(`wall ${formatHoursShort(cost.wall_h)}`);
  if (cost.gpu_h != null) bits.push(`GPU ${formatHoursShort(cost.gpu_h)}`);
  if (cost.n_gpus != null) bits.push(`${cost.n_gpus}×GPU`);
  if (cost.until) bits.push(`until ${cost.until}`);
  if (cost.source && cost.source !== "measured") bits.push(`(${cost.source})`);
  return bits.join(" · ");
}

/**
 * @param {ReturnType<typeof parseComputeCost>} cost
 * @returns {string}
 */
export function computeCostChipLabel(cost) {
  if (!cost) return "";
  const wall = formatHoursShort(cost.wall_h);
  const gpu = formatHoursShort(cost.gpu_h);
  if (gpu && wall && gpu !== wall) return `${wall} · ${gpu} GPU·h`;
  if (gpu) return `${gpu} GPU·h`;
  if (wall) return `${wall} wall`;
  return "";
}

const CLOCK_SVG = `<svg class="compute-cost-icon" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.75"/><path d="M12 7v5.2l3.2 1.8" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

/**
 * Compact chip for kanban cards.
 * @param {ReturnType<typeof parseComputeCost>} cost
 * @param {{ escapeHtml?: (s: string) => string }} [opts]
 */
export function computeCostChipHtml(cost, opts = {}) {
  if (!cost) return "";
  const esc = opts.escapeHtml || ((s) => String(s));
  const label = computeCostChipLabel(cost);
  if (!label) return "";
  const title = esc(computeCostTitle(cost));
  const source = cost.source || "measured";
  const approx = source !== "measured" ? `<span class="compute-cost-approx" aria-hidden="true">≈</span>` : "";
  return `<span class="compute-cost-chip compute-cost-chip--${esc(source)}" title="${title}" aria-label="${title}">${CLOCK_SVG}${approx}<span class="compute-cost-chip-label">${esc(label)}</span></span>`;
}

/**
 * Corner badge for the report modal.
 * @param {ReturnType<typeof parseComputeCost>} cost
 * @param {{ escapeHtml?: (s: string) => string }} [opts]
 */
export function computeCostBadgeHtml(cost, opts = {}) {
  if (!cost) return "";
  const esc = opts.escapeHtml || ((s) => String(s));
  const label = computeCostChipLabel(cost);
  if (!label) return "";
  const title = esc(computeCostTitle(cost));
  const source = cost.source || "measured";
  const sourceLabel =
    source === "estimated" ? "estimate" : source === "recovered" ? "recovered" : "measured";
  const until = cost.until
    ? `<span class="compute-cost-badge-until">${esc(cost.until)}</span>`
    : "";
  return `<div class="compute-cost-badge compute-cost-badge--${esc(source)}" title="${title}" role="status" aria-label="${title}">
    <div class="compute-cost-badge-head">${CLOCK_SVG}<span class="compute-cost-badge-kicker">Compute</span><span class="compute-cost-badge-source">${esc(sourceLabel)}</span></div>
    <div class="compute-cost-badge-value">${esc(label)}</div>
    ${until}
  </div>`;
}
