/* ==========================================================================
   SUZAKU × NTE「夜行」LP専用演出
   ・夜景シティ: スクロールで街の窓が点灯
   ・EL発光背面のパターン切替デモ
   ========================================================================== */
(function () {
  "use strict";
  if (!document.querySelector(".collab--nte")) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 街の窓が点く ---------- */
  var city = document.querySelector("[data-city]");
  if (city) {
    if (reduce || !("IntersectionObserver" in window)) {
      city.classList.add("is-lit");
    } else {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (e.isIntersecting) { city.classList.add("is-lit"); io.disconnect(); }
        });
      }, { threshold: 0.35 });
      io.observe(city);
    }
  }

  /* ---------- EL発光パターン切替 ---------- */
  var panel = document.querySelector("[data-elpanel]");
  var btns = document.querySelectorAll(".nt-elbtn");
  if (panel && btns.length) {
    panel.setAttribute("data-mode", "pulse");
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        btns.forEach(function (x) { x.classList.toggle("is-on", x === b); });
        panel.setAttribute("data-mode", b.getAttribute("data-el"));
      });
    });
  }
})();
