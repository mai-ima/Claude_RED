/* ==========================================================================
   SUZAKU × 原神「七耀」LP専用演出
   ・点火イントロ(七元素が順に灯る。1セッション1回)
   ・元素ホイール(選択でページの光と端末グローが7色に切替)
   ・雲パララックス
   ========================================================================== */
(function () {
  "use strict";
  if (!document.querySelector(".collab--genshin")) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 点火イントロ ---------- */
  var intro = document.getElementById("gsIntro");
  if (intro) {
    var seen = false;
    try { seen = sessionStorage.getItem("sz_gs_intro") === "1"; } catch (e) {}
    if (reduce || seen) {
      intro.classList.add("is-done");
    } else {
      requestAnimationFrame(function () { intro.classList.add("is-run"); });
      setTimeout(function () {
        intro.classList.add("is-done");
        try { sessionStorage.setItem("sz_gs_intro", "1"); } catch (e) {}
      }, 1700);
    }
  }

  /* ---------- 元素ホイール ---------- */
  var stage = document.querySelector("[data-elem-stage]");
  if (stage) {
    var nameEl = stage.querySelector(".gs-elem-name");
    stage.querySelectorAll(".gs-elem").forEach(function (btn) {
      var apply = function () {
        var col = getComputedStyle(btn).getPropertyValue("--el").trim();
        stage.style.setProperty("--gs-el", col);
        if (nameEl) nameEl.textContent = btn.getAttribute("data-elem") + "元素 — 元素リング発光プレビュー";
        stage.querySelectorAll(".gs-elem").forEach(function (b) { b.classList.toggle("is-on", b === btn); });
      };
      btn.addEventListener("click", apply);
      btn.addEventListener("mouseenter", apply);
      btn.addEventListener("focus", apply);
    });
  }

  /* ---------- 雲パララックス ---------- */
  var clouds = document.querySelectorAll(".gs-cloud");
  if (clouds.length && !reduce) {
    var onScroll = function () {
      var y = window.scrollY || 0;
      clouds.forEach(function (c, i) {
        var f = (i + 1) * 0.05;
        c.style.transform = "translateX(" + (y * f * (i % 2 ? -1 : 1)) + "px) translateY(" + (y * f * 0.4) + "px)";
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
  }
})();
