(function () {
  function initThemeButton() {
    var btn = document.getElementById("btn-theme");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var root = document.documentElement;
      var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      localStorage.setItem("koi-theme", next);
      btn.title = next === "light" ? "Тёмная тема" : "Светлая тема";
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initThemeButton);
  } else {
    initThemeButton();
  }
})();
