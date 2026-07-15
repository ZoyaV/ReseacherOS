const HubApi = {
  async get(path) {
    const r = await fetch(path, { credentials: "same-origin" });
    if (!r.ok) {
      const text = await parseError(r);
      throw new Error(text || r.statusText);
    }
    return r.json();
  },
  async post(path, body) {
    const r = await fetch(path, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    if (!r.ok) {
      const text = await parseError(r);
      throw new Error(text || r.statusText);
    }
    return r.json();
  },
  async patch(path, body) {
    const r = await fetch(path, {
      method: "PATCH",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
    if (!r.ok) {
      const text = await parseError(r);
      throw new Error(text || r.statusText);
    }
    return r.json();
  },
  async delete(path) {
    const r = await fetch(path, {
      method: "DELETE",
      credentials: "same-origin",
    });
    if (!r.ok) {
      const text = await parseError(r);
      throw new Error(text || r.statusText);
    }
    return r.json();
  },
};

const HUB_TABS = {
  all: {
    title: "Все проекты",
    desc: "Публичный каталог — деревья гипотез и канбан без кода. + подписаться на автора, → открыть проект.",
    api: "/api/catalog/public",
    requiresAuth: false,
  },
  subscriptions: {
    title: "Подписки",
    desc: "Проекты авторов, на которых вы подписаны, и сохранённые по ссылке (в т.ч. unlisted с token).",
    api: "/api/catalog/network",
    requiresAuth: true,
  },
  mine: {
    title: "Мои проекты",
    desc: "Ваши репозитории в Hub: sync с GitHub, видимость, вкл/выкл в каталоге.",
    api: "/api/projects/mine",
    requiresAuth: true,
    manage: true,
  },
};

const VISIBILITY_LABELS = {
  public: "Публичный",
  network: "Сеть",
  unlisted: "По ссылке",
};

async function parseError(r) {
  const text = await r.text();
  try {
    const data = JSON.parse(text);
    if (data && data.detail) {
      return typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    }
  } catch (_err) {
    /* keep raw text */
  }
  return text;
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showBootError(message) {
  const banner = document.createElement("div");
  banner.style.cssText =
    "background:#5c1f1f;color:#fff;padding:0.75rem 1rem;margin:0;border-bottom:1px solid #8b3030";
  banner.textContent = message;
  document.body.insertBefore(banner, document.body.firstChild);
}

function parseTabFromUrl() {
  const tab = new URLSearchParams(location.search).get("tab");
  if (tab && HUB_TABS[tab]) return tab;
  if (tab === "public") return "all";
  if (tab === "network") return "subscriptions";
  return "all";
}

function setTabInUrl(tab) {
  const url = new URL(location.href);
  if (tab === "all") url.searchParams.delete("tab");
  else url.searchParams.set("tab", tab);
  history.replaceState({ tab }, "", url.pathname + url.search);
}

function visibilityBadge(visibility) {
  const label = VISIBILITY_LABELS[visibility] || visibility;
  return (
    '<span class="hub-badge hub-badge--' +
    escapeHtml(visibility || "public") +
    '">' +
    escapeHtml(label) +
    "</span>"
  );
}

function projectMetaLine(p, { showOwner = true } = {}) {
  const parts = [];
  if (showOwner && p.owner_login) parts.push("@" + escapeHtml(p.owner_login));
  if (p.repo_full_name) parts.push(escapeHtml(p.repo_full_name));
  if (p.branch) parts.push(escapeHtml(p.branch));
  return parts.join(" · ");
}

function projectHref(p) {
  return p.view_href || p.view_url || "/p/" + encodeURIComponent(p.slug);
}

function renderBrowseCard(p, { tab = "all" } = {}) {
  const href = projectHref(p);
  const showVis = p.visibility && p.visibility !== "public";
  const showFollow =
    tab === "all" && !p.is_self && p.is_following !== true;
  const savedBadge = p.saved_by_link
    ? '<span class="hub-badge hub-badge--link">По ссылке</span>'
    : "";
  const mainHtml =
    '<div class="hub-project-card__head">' +
    "<h3>" +
    escapeHtml(p.title || p.slug) +
    "</h3>" +
    savedBadge +
    (showVis ? visibilityBadge(p.visibility) : "") +
    "</div>" +
    '<p class="hub-project-card__meta">' +
    projectMetaLine(p) +
    "</p>" +
    '<p class="hub-project-card__meta hub-project-card__meta--muted">Обновлено: ' +
    escapeHtml(p.last_sync_at || "—") +
    "</p>";

  if (showFollow) {
    const ownerId = p.owner_github_id != null ? String(p.owner_github_id) : "";
    const ownerLogin = p.owner_login || "автора";
    return (
      '<article class="hub-project-card hub-project-card--browse">' +
      '<a class="hub-project-card__main" href="' +
      href +
      '">' +
      mainHtml +
      "</a>" +
      '<button type="button" class="hub-project-card__follow" data-action="follow" data-owner-id="' +
      escapeHtml(ownerId) +
      '" title="Подписаться на @' +
      escapeHtml(ownerLogin) +
      '" aria-label="Подписаться на @' +
      escapeHtml(ownerLogin) +
      '">+</button>' +
      "</article>"
    );
  }

  return (
    '<a class="hub-project-card hub-project-card--link" href="' +
    href +
    '">' +
    '<div class="hub-project-card__main">' +
    mainHtml +
    "</div>" +
    '<span class="hub-project-card__arrow" aria-hidden="true">→</span>' +
    "</a>"
  );
}

function renderMineCard(p) {
  const on = p.enabled !== false;
  const dup = p.is_canonical === false;
  const href = projectHref(p);
  const shareUrl = p.share_url || "";
  return (
    '<article class="hub-project-card hub-project-card--mine' +
    (on ? "" : " hub-project-card--off") +
    (dup ? " hub-project-card--dup" : "") +
    '" data-slug="' +
    escapeHtml(p.slug) +
    '">' +
    '<a class="hub-project-card__main" href="' +
    escapeHtml(href) +
    '">' +
    '<div class="hub-project-card__head">' +
    "<h3>" +
    escapeHtml(p.title || p.slug) +
    "</h3>" +
    visibilityBadge(p.visibility) +
    (on ? "" : '<span class="hub-badge hub-badge--off">Скрыт</span>') +
    "</div>" +
    '<p class="hub-project-card__meta">' +
    projectMetaLine(p, { showOwner: false }) +
    "</p>" +
    '<p class="hub-project-card__meta hub-project-card__meta--muted">Обновлено: ' +
    escapeHtml(p.last_sync_at || "—") +
    "</p>" +
    "</a>" +
    (dup
      ? '<p class="hub-project-card__meta hub-dup-badge hub-project-card__dup">Дубликат · основной: <a href="/p/' +
        escapeHtml(p.canonical_slug || "") +
        '">' +
        escapeHtml(p.canonical_slug || "") +
        "</a></p>"
      : "") +
    '<div class="hub-project-card__actions">' +
    (shareUrl
      ? '<button type="button" class="btn btn-small hub-copy-link" data-action="copy-link" data-share-url="' +
        escapeHtml(shareUrl) +
        '">Ссылка</button>'
      : "") +
    '<label class="hub-toggle" title="Показать или скрыть в каталоге">' +
    '<input type="checkbox" class="hub-toggle__input" data-action="enabled"' +
    (on ? " checked" : "") +
    " />" +
    '<span class="hub-toggle__label">' +
    (on ? "Включён" : "Отключён") +
    "</span>" +
    "</label>" +
    '<button type="button" class="btn btn-small hub-sync-btn" data-action="sync">Sync</button>' +
    (dup
      ? '<button type="button" class="btn btn-small hub-delete-btn" data-action="delete">Удалить</button>'
      : "") +
    "</div>" +
    "</article>"
  );
}

function renderAddProjectCard() {
  return (
    '<a class="hub-project-card hub-project-card--add" href="/connect">' +
    '<span class="hub-project-card__add-icon" aria-hidden="true">+</span>' +
    '<span class="hub-project-card__add-label">Подключить проект</span>' +
    "</a>"
  );
}

function renderProjectGrid(projects, { manage = false, tab = "all" } = {}) {
  const cards = projects.map(function (p) {
    return manage ? renderMineCard(p) : renderBrowseCard(p, { tab });
  });
  if (manage) {
    return (
      '<div class="hub-grid">' + renderAddProjectCard() + cards.join("") + "</div>"
    );
  }
  if (!cards.length) return "";
  return '<div class="hub-grid">' + cards.join("") + "</div>";
}

function renderEmptyState(tab) {
  if (tab === "all") {
    return (
      '<div class="hub-empty-state">' +
      "<p>Пока нет публичных проектов.</p>" +
      '<p class="hub-empty-state__hint">Подключите свой репозиторий и выберите visibility «Публичный».</p>' +
      '<a class="btn btn-primary" href="/connect">Подключить проект</a>' +
      "</div>"
    );
  }
  if (tab === "subscriptions") {
    return (
      '<div class="hub-empty-state">' +
      "<p>Лента подписок пуста.</p>" +
      '<p class="hub-empty-state__hint">Подпишитесь на авторов или добавьте проект по секретной ссылке.</p>' +
      '<button type="button" class="btn btn-primary" data-action="open-link-modal">Добавить по ссылке</button>' +
      "</div>"
    );
  }
  return (
    '<div class="hub-empty-state">' +
    "<p>Вы ещё не подключили проекты.</p>" +
    '<p class="hub-empty-state__hint">Нажмите <strong>+</strong> слева, чтобы подключить репозиторий.</p>' +
    "</div>"
  );
}

function renderAuthRequired(tab) {
  const cfg = HUB_TABS[tab];
  return (
    '<div class="hub-empty-state">' +
    "<p>Нужен вход через GitHub</p>" +
    '<p class="hub-empty-state__hint">' +
    escapeHtml(cfg.desc) +
    "</p>" +
    '<a class="btn btn-primary" href="/auth/github">Войти через GitHub</a>' +
    "</div>"
  );
}

async function renderAuthToolbar() {
  const el = document.getElementById("auth-toolbar");
  if (!el) return null;
  try {
    const me = await HubApi.get("/api/me");
    if (!me.authenticated) {
      el.innerHTML = "";
      return me;
    }
    const u = me.user;
    el.innerHTML =
      '<div class="hub-account">' +
      '<button type="button" class="user-chip hub-account__trigger" id="hub-account-trigger" aria-expanded="false" aria-haspopup="menu" aria-controls="hub-account-menu">' +
      '<img src="' + escapeHtml(u.avatar_url) + '" alt="" width="24" height="24" />' +
      "<span>@" + escapeHtml(u.login) + "</span>" +
      '<span class="hub-account__chevron" aria-hidden="true">▾</span>' +
      "</button>" +
      '<div class="hub-account__menu hidden" id="hub-account-menu" role="menu">' +
      '<a class="hub-account__item" href="/connect" role="menuitem">+ Подключить репозиторий</a>' +
      '<button type="button" class="hub-account__item hub-account__item--danger" data-action="logout" role="menuitem">Выйти</button>' +
      "</div>" +
      "</div>";
    bindAccountMenu(el);
    return me;
  } catch (err) {
    el.innerHTML = '<span class="meta">Auth: ' + escapeHtml(err.message) + "</span>";
    return null;
  }
}

function bindAccountMenu(root) {
  const trigger = root.querySelector("#hub-account-trigger");
  const menu = root.querySelector("#hub-account-menu");
  if (!trigger || !menu) return;

  function closeMenu() {
    menu.classList.add("hidden");
    trigger.setAttribute("aria-expanded", "false");
  }

  function openMenu() {
    menu.classList.remove("hidden");
    trigger.setAttribute("aria-expanded", "true");
  }

  trigger.addEventListener("click", function (e) {
    e.stopPropagation();
    if (menu.classList.contains("hidden")) openMenu();
    else closeMenu();
  });

  menu.querySelector('[data-action="logout"]')?.addEventListener("click", async function () {
    closeMenu();
    await HubApi.post("/auth/logout");
    location.reload();
  });

  document.addEventListener("click", function (e) {
    if (!root.contains(e.target)) closeMenu();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenu();
  });
}

function syncHubPanelCta(authState, href) {
  if (document.body.getAttribute("data-page") !== "index") return;
  const cta = document.getElementById("hub-panel-cta");
  if (!cta) return;
  if (!href) {
    const isGuest = !authState || !authState.authenticated;
    href = isGuest ? "/auth/github" : "/connect";
  }

  cta.classList.remove("hidden");
  cta.innerHTML =
    '<a href="' +
    escapeHtml(href) +
    '" class="btn btn-primary hub-enter-btn">Войти в мир исследований</a>';
}

async function resolveEnterWorldHref(projects, authState) {
  if (projects && projects.length > 0) {
    return projectHref(projects[0]);
  }
  try {
    const data = await HubApi.get("/api/catalog/public");
    const pub = (data.projects || [])[0];
    if (pub) return projectHref(pub);
  } catch (_err) {
    /* fallback below */
  }
  const isGuest = !authState || !authState.authenticated;
  return isGuest ? "/auth/github" : "/connect";
}

function updatePanel(tab) {
  const cfg = HUB_TABS[tab];
  const title = document.getElementById("hub-panel-title");
  const desc = document.getElementById("hub-panel-desc");
  if (title) title.textContent = cfg.title;
  if (desc) desc.textContent = cfg.desc;
  document.title = cfg.title + " · ResearchOS Hub";
}

function setActiveTabUi(tab) {
  document.querySelectorAll(".hub-panel__tab").forEach(function (btn) {
    const on = btn.getAttribute("data-tab") === tab;
    btn.classList.toggle("is-active", on);
    btn.setAttribute("aria-selected", on ? "true" : "false");
  });
}

function renderSubscriptionsBar() {
  return (
    '<div class="hub-subscriptions-bar">' +
    '<button type="button" class="btn btn-primary" data-action="open-link-modal">+ Добавить по ссылке</button>' +
    "</div>"
  );
}

function initLinkModal(onSuccess) {
  const modal = document.getElementById("hub-link-modal");
  const form = document.getElementById("hub-link-form");
  const input = document.getElementById("hub-link-input");
  const status = document.getElementById("hub-link-status");
  if (!modal || !form || !input) return;

  function openModal() {
    modal.classList.remove("hidden");
    input.value = "";
    if (status) status.textContent = "";
    input.focus();
  }

  function closeModal() {
    modal.classList.add("hidden");
  }

  document.addEventListener("click", function (e) {
    if (e.target.closest('[data-action="open-link-modal"]')) {
      e.preventDefault();
      openModal();
    }
    if (
      e.target.closest('[data-action="close-link-modal"]') ||
      e.target.dataset.close === "hub-link-modal"
    ) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) {
      closeModal();
    }
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const url = input.value.trim();
    if (!url) return;
    if (status) status.textContent = "Проверка ссылки…";
    try {
      const result = await HubApi.post("/api/subscriptions/by-link", { url });
      closeModal();
      if (typeof onSuccess === "function") await onSuccess(result);
    } catch (err) {
      if (status) status.textContent = err.message;
    }
  });
}

function initIndexPage() {
  let activeTab = parseTabFromUrl();
  let authState = null;
  let manageBound = false;
  let followBound = false;

  function setStatus(msg) {
    const el = document.getElementById("hub-status");
    if (el) el.textContent = msg || "";
  }

  async function refreshEnterWorldCta(projects) {
    const href = await resolveEnterWorldHref(projects, authState);
    syncHubPanelCta(authState, href);
  }

  async function loadCatalog() {
    const root = document.getElementById("catalog");
    if (!root) return;
    const cfg = HUB_TABS[activeTab];
    updatePanel(activeTab);
    setActiveTabUi(activeTab);
    setTabInUrl(activeTab);
    setStatus("");
    root.innerHTML = '<p class="hub-empty">Загрузка…</p>';

    if (cfg.requiresAuth && (!authState || !authState.authenticated)) {
      root.innerHTML = renderAuthRequired(activeTab);
      await refreshEnterWorldCta([]);
      return;
    }

    try {
      const data = await HubApi.get(cfg.api);
      const projects = data.projects || [];
      if (!projects.length && !cfg.manage) {
        root.innerHTML =
          (activeTab === "subscriptions" ? renderSubscriptionsBar() : "") +
          renderEmptyState(activeTab);
        await refreshEnterWorldCta([]);
        return;
      }
      root.innerHTML =
        (activeTab === "subscriptions" ? renderSubscriptionsBar() : "") +
        renderProjectGrid(projects, {
          manage: !!cfg.manage,
          tab: activeTab,
        });
      if (cfg.manage && !manageBound) bindManageActions(root);
      if (!cfg.manage && !followBound) bindFollowActions(root);
      await refreshEnterWorldCta(projects);
    } catch (err) {
      const msg = /sign in|auth|401|403|session/i.test(String(err.message))
        ? "Войдите через GitHub, чтобы открыть этот раздел."
        : err.message;
      root.innerHTML = '<p class="hub-empty">' + escapeHtml(msg) + "</p>";
      await refreshEnterWorldCta([]);
    }
  }

  function bindFollowActions(root) {
    if (followBound) return;
    followBound = true;

    root.addEventListener("click", async function (e) {
      const btn = e.target.closest('[data-action="follow"]');
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      if (!authState || !authState.authenticated) {
        location.href = "/auth/github";
        return;
      }
      const ownerId = Number(btn.dataset.ownerId);
      if (!ownerId) return;
      btn.disabled = true;
      setStatus("");
      try {
        await HubApi.post("/api/follow", { github_id: ownerId });
        setStatus("Подписка оформлена — network-проекты автора появятся во вкладке «Подписки».");
        await loadCatalog();
      } catch (err) {
        setStatus(err.message);
        btn.disabled = false;
      }
    });
  }

  function bindManageActions(root) {
    if (manageBound) return;
    manageBound = true;

    root.addEventListener("change", async function (e) {
      const input = e.target.closest('[data-action="enabled"]');
      if (!input) return;
      const card = input.closest(".hub-project-card--mine");
      const slug = card && card.getAttribute("data-slug");
      if (!slug) return;
      input.disabled = true;
      setStatus("");
      try {
        await HubApi.patch("/api/projects/" + encodeURIComponent(slug), {
          enabled: input.checked,
        });
        await loadCatalog();
        setStatus(
          input.checked
            ? "Проект снова виден в каталоге (если visibility public или network)."
            : "Проект скрыт из каталога."
        );
      } catch (err) {
        input.checked = !input.checked;
        setStatus(err.message);
      } finally {
        input.disabled = false;
      }
    });

    root.addEventListener("click", async function (e) {
      const copyBtn = e.target.closest('[data-action="copy-link"]');
      if (copyBtn) {
        const url = copyBtn.dataset.shareUrl;
        if (!url) return;
        try {
          await navigator.clipboard.writeText(url);
          setStatus("Ссылка скопирована.");
        } catch (_err) {
          window.prompt("Скопируйте ссылку:", url);
        }
        return;
      }
      const delBtn = e.target.closest('[data-action="delete"]');
      if (delBtn) {
        const card = delBtn.closest(".hub-project-card--mine");
        const slug = card && card.getAttribute("data-slug");
        if (!slug || !window.confirm("Удалить дубликат «" + slug + "»?")) return;
        delBtn.disabled = true;
        setStatus("Удаление…");
        try {
          await HubApi.delete("/api/projects/" + encodeURIComponent(slug));
          setStatus("Дубликат удалён.");
          await loadCatalog();
        } catch (err) {
          setStatus(err.message);
          delBtn.disabled = false;
        }
        return;
      }
      const btn = e.target.closest('[data-action="sync"]');
      if (!btn) return;
      const card = btn.closest(".hub-project-card--mine");
      const slug = card && card.getAttribute("data-slug");
      if (!slug) return;
      btn.disabled = true;
      setStatus("Синхронизация с GitHub…");
      try {
        await HubApi.post("/api/projects/" + encodeURIComponent(slug) + "/sync");
        setStatus("Синхронизация завершена.");
        await loadCatalog();
      } catch (err) {
        setStatus(err.message);
      } finally {
        btn.disabled = false;
      }
    });
  }

  document.querySelectorAll(".hub-panel__tab").forEach(function (btn) {
    btn.addEventListener("click", function () {
      activeTab = btn.getAttribute("data-tab") || "all";
      loadCatalog();
    });
  });

  window.addEventListener("popstate", function () {
    activeTab = parseTabFromUrl();
    loadCatalog();
  });

  renderAuthToolbar().then(function (me) {
    authState = me;
    initLinkModal(async function (result) {
      if (activeTab !== "subscriptions") {
        activeTab = "subscriptions";
      }
      setStatus(
        result.already_saved
          ? "Проект уже был в подписках: " + (result.title || result.slug)
          : "Добавлено в подписки: " + (result.title || result.slug)
      );
      await loadCatalog();
    });
    loadCatalog();
  });
}

async function initConnectPage() {
  await renderAuthToolbar();
  try {
    const me = await HubApi.get("/api/me");
    if (!me.authenticated) {
      location.href = "/auth/github";
      return;
    }
  } catch (err) {
    showBootError("Не удалось проверить сессию: " + err.message);
    return;
  }

  const select = document.getElementById("repo");
  if (!select) return;
  select.innerHTML = '<option value="">Загрузка…</option>';
  try {
    const data = await HubApi.get("/api/repos");
    const repos = data.repos || [];
    if (!repos.length) {
      select.innerHTML = '<option value="">Репозитории не найдены</option>';
      return;
    }
    select.innerHTML = repos
      .map(function (r) {
        return (
          '<option value="' +
          escapeHtml(r.full_name) +
          '">' +
          escapeHtml(r.full_name) +
          (r.private ? " (private)" : "") +
          "</option>"
        );
      })
      .join("");
  } catch (err) {
    document.getElementById("status").textContent = err.message;
  }

  const form = document.getElementById("connect-form");
  if (!form) return;
  let syncing = false;
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    if (syncing) return;
    syncing = true;
    const status = document.getElementById("status");
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;
    status.textContent = "Синхронизация с GitHub… (до минуты)";
    try {
      const result = await HubApi.post("/api/projects", {
        repo_full_name: document.getElementById("repo").value,
        branch: document.getElementById("branch").value,
        title: document.getElementById("title").value,
        visibility: document.getElementById("visibility").value,
      });
      const viewUrl = result.view_url || "/p/" + encodeURIComponent(result.slug);
      let html =
        'Готово: <a href="' +
        escapeHtml(viewUrl) +
        '">' +
        escapeHtml(result.title || result.slug) +
        "</a> · " +
        '<a href="/?tab=mine">Мои проекты</a>';
      if (result.secret_token) {
        html +=
          '<br><span class="meta">Unlisted: /p/' +
          escapeHtml(result.slug) +
          "?token=" +
          escapeHtml(result.secret_token) +
          "</span>";
      }
      if (result.reused_existing) {
        html = "Уже подключено — обновлено: " + html;
      }
      status.innerHTML = html;
    } catch (err) {
      status.textContent = err.message;
      if (submitBtn) submitBtn.disabled = false;
      syncing = false;
    }
  });
}

async function initOnboardingPage() {
  await renderAuthToolbar();
  try {
    const me = await HubApi.get("/api/me");
    const signin = document.getElementById("onboarding-signin");
    if (me.authenticated && signin) {
      signin.textContent = "Подключить проект";
      signin.href = "/connect";
    }
  } catch (_err) {
    /* ignore */
  }

  const list = document.getElementById("discover-users");
  const status = document.getElementById("discover-status");
  if (!list) return;
  list.innerHTML = "";
  try {
    const data = await HubApi.get("/api/users/discoverable");
    const users = data.users || [];
    if (!users.length) {
      if (status) status.textContent = "Пока никто не отметился как discoverable.";
      return;
    }
    list.innerHTML = users
      .map(function (u) {
        return (
          "<li>" +
          '<span class="user-chip"><img src="' +
          escapeHtml(u.avatar_url) +
          '" alt="" width="24" height="24" /><span>@' +
          escapeHtml(u.login) +
          "</span></span>" +
          '<button type="button" class="btn btn-primary hub-follow-btn" data-id="' +
          u.github_id +
          '">Подписаться</button>' +
          "</li>"
        );
      })
      .join("");
    list.querySelectorAll(".hub-follow-btn").forEach(function (btn) {
      btn.addEventListener("click", async function () {
        btn.disabled = true;
        try {
          await HubApi.post("/api/follow", { github_id: Number(btn.dataset.id) });
          btn.textContent = "Подписаны";
          if (status) {
            status.innerHTML =
              'Подписка оформлена. Смотрите ленту во вкладке <a href="/?tab=subscriptions">Подписки</a>.';
          }
        } catch (err) {
          btn.disabled = false;
          if (status) status.textContent = err.message;
        }
      });
    });
  } catch (err) {
    if (status) status.textContent = err.message;
  }
}

function boot() {
  const page = document.body.getAttribute("data-page");
  if (page === "index") initIndexPage();
  else if (page === "connect") initConnectPage();
  else if (page === "onboarding") initOnboardingPage();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
