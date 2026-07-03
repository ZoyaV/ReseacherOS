/**
 * Полноэкранный просмотр картинок из отчётов и базы знаний.
 * Клик по картинке в .markdown-preview открывает её в модальном окне поверх всего;
 * можно приближать/отдалять (кнопки, колесо мыши, двойной клик) и перетаскивать.
 */

const ZOOM_MIN = 1;
const ZOOM_MAX = 8;
const ZOOM_STEP = 1.35;

const state = {
  scale: 1,
  tx: 0,
  ty: 0,
  dragging: false,
  startX: 0,
  startY: 0,
  startTx: 0,
  startTy: 0,
  moved: false,
};

let els = null;

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function applyTransform() {
  if (!els) return;
  els.img.style.transform = `translate(${state.tx}px, ${state.ty}px) scale(${state.scale})`;
  els.stage.classList.toggle("is-zoomed", state.scale > 1);
}

function resetView() {
  state.scale = 1;
  state.tx = 0;
  state.ty = 0;
  applyTransform();
}

/** Масштабирование с центром в точке (cx, cy) внутри области просмотра. */
function zoomTo(nextScale, cx, cy) {
  if (!els) return;
  const clamped = clamp(nextScale, ZOOM_MIN, ZOOM_MAX);
  const rect = els.stage.getBoundingClientRect();
  const originX = cx ?? rect.left + rect.width / 2;
  const originY = cy ?? rect.top + rect.height / 2;
  const px = originX - rect.left - rect.width / 2;
  const py = originY - rect.top - rect.height / 2;
  const ratio = clamped / state.scale;
  state.tx = px - (px - state.tx) * ratio;
  state.ty = py - (py - state.ty) * ratio;
  state.scale = clamped;
  if (state.scale <= ZOOM_MIN + 0.001) {
    state.tx = 0;
    state.ty = 0;
  }
  applyTransform();
}

function open(src, alt) {
  if (!els) return;
  els.img.src = src;
  els.img.alt = alt || "";
  resetView();
  els.root.classList.remove("hidden");
  document.body.classList.add("modal-open");
}

function close() {
  if (!els || els.root.classList.contains("hidden")) return;
  els.root.classList.add("hidden");
  els.img.removeAttribute("src");
  resetView();
  if (!document.querySelector(".modal:not(.hidden)")) {
    document.body.classList.remove("modal-open");
  }
}

function isOpen() {
  return els && !els.root.classList.contains("hidden");
}

function buildDom() {
  const root = document.createElement("div");
  root.id = "image-lightbox";
  root.className = "image-lightbox hidden";
  root.setAttribute("role", "dialog");
  root.setAttribute("aria-label", "Просмотр изображения");
  root.innerHTML = `
    <div class="image-lightbox-backdrop" data-lightbox-close></div>
    <div class="image-lightbox-stage">
      <img class="image-lightbox-img" alt="" draggable="false" />
    </div>
    <div class="image-lightbox-toolbar" role="toolbar" aria-label="Масштаб">
      <button type="button" class="image-lightbox-btn" data-lightbox-action="zoom-out" title="Отдалить" aria-label="Отдалить">−</button>
      <button type="button" class="image-lightbox-btn" data-lightbox-action="reset" title="Сбросить масштаб" aria-label="Сбросить масштаб">⤢</button>
      <button type="button" class="image-lightbox-btn" data-lightbox-action="zoom-in" title="Приблизить" aria-label="Приблизить">+</button>
    </div>
    <button type="button" class="image-lightbox-close" data-lightbox-close title="Закрыть (Esc)" aria-label="Закрыть">×</button>
  `;
  document.body.appendChild(root);
  els = {
    root,
    stage: root.querySelector(".image-lightbox-stage"),
    img: root.querySelector(".image-lightbox-img"),
  };
  bindEvents();
}

function bindEvents() {
  els.root.addEventListener("click", (e) => {
    const target = e.target;
    if (target.closest("[data-lightbox-close]")) {
      close();
      return;
    }
    const actionEl = target.closest("[data-lightbox-action]");
    if (actionEl) {
      const action = actionEl.dataset.lightboxAction;
      if (action === "zoom-in") zoomTo(state.scale * ZOOM_STEP);
      else if (action === "zoom-out") zoomTo(state.scale / ZOOM_STEP);
      else if (action === "reset") resetView();
      return;
    }
    // Клик по пустой области сцены (не по картинке и без перетаскивания) закрывает окно
    if (target === els.stage && !state.moved) {
      close();
    }
  });

  els.stage.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP;
      zoomTo(state.scale * factor, e.clientX, e.clientY);
    },
    { passive: false }
  );

  els.img.addEventListener("dblclick", (e) => {
    e.preventDefault();
    if (state.scale > 1) resetView();
    else zoomTo(ZOOM_STEP * 2, e.clientX, e.clientY);
  });

  els.stage.addEventListener("pointerdown", (e) => {
    state.moved = false;
    if (state.scale <= 1) return;
    state.dragging = true;
    state.startX = e.clientX;
    state.startY = e.clientY;
    state.startTx = state.tx;
    state.startTy = state.ty;
    els.stage.setPointerCapture(e.pointerId);
    els.stage.classList.add("is-dragging");
  });
  els.stage.addEventListener("pointermove", (e) => {
    if (!state.dragging) return;
    state.tx = state.startTx + (e.clientX - state.startX);
    state.ty = state.startTy + (e.clientY - state.startY);
    if (Math.abs(e.clientX - state.startX) + Math.abs(e.clientY - state.startY) > 3) {
      state.moved = true;
    }
    applyTransform();
  });
  const endDrag = (e) => {
    if (!state.dragging) return;
    state.dragging = false;
    els.stage.classList.remove("is-dragging");
    try {
      els.stage.releasePointerCapture(e.pointerId);
    } catch {
      /* ignore */
    }
  };
  els.stage.addEventListener("pointerup", endDrag);
  els.stage.addEventListener("pointercancel", endDrag);
}

/**
 * Найти картинку, по которой кликнули: в отчётах/базе знаний (.markdown-preview)
 * или на мониторе карточки (.card-live-metric — картинка в ссылке).
 * Видео игнорируются.
 */
function resolveClickedImage(target) {
  if (!target?.closest) return null;
  // Плитки метрик на мониторе: <a class="card-live-metric"><img></a>
  const metricLink = target.closest(".card-live-metric");
  if (metricLink) {
    const img = metricLink.querySelector("img");
    if (img) return img;
  }
  const img = target.closest(".markdown-preview img");
  if (img && !img.classList.contains("md-media--video")) return img;
  return null;
}

/**
 * Подключить лайтбокс: делегированный клик по картинкам в отчётах / базе знаний
 * и обработка Escape.
 */
export function initImageLightbox() {
  if (typeof document === "undefined" || els) return;
  buildDom();

  document.addEventListener(
    "click",
    (e) => {
      const img = resolveClickedImage(e.target);
      if (!img) return;
      const src = img.currentSrc || img.getAttribute("src");
      if (!src) return;
      e.preventDefault();
      e.stopPropagation();
      open(src, img.getAttribute("alt"));
    },
    true
  );

  document.addEventListener(
    "keydown",
    (e) => {
      if (!isOpen()) return;
      if (e.key === "Escape") {
        e.stopPropagation();
        close();
      } else if (e.key === "+" || e.key === "=") {
        zoomTo(state.scale * ZOOM_STEP);
      } else if (e.key === "-" || e.key === "_") {
        zoomTo(state.scale / ZOOM_STEP);
      } else if (e.key === "0") {
        resetView();
      }
    },
    true
  );
}
