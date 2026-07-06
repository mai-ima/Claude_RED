/* ==========================================================================
   SUZAKU collab.js — コラボレーション特設の対話UI
   ・.collab-page が無いページでは即 return(自己ゲート。全ページ読み込みでも安全)
   ・カウントダウン(期間限定)/ 数量メーター(数量限定)/ ギャラリーの軽い演出
   ========================================================================== */
(function () {
  "use strict";
  if (!document.querySelector(".collab-page")) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 期間限定カウントダウン ---------- */
  var countEl = document.querySelector(".cl-count[data-until]");
  if (countEl) {
    var until = new Date(countEl.getAttribute("data-until")).getTime();
    var slots = {
      d: countEl.querySelector('[data-c="d"]'),
      h: countEl.querySelector('[data-c="h"]'),
      m: countEl.querySelector('[data-c="m"]'),
      s: countEl.querySelector('[data-c="s"]')
    };
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    var tick = function () {
      var diff = until - Date.now();
      if (diff <= 0) {
        if (slots.d) slots.d.textContent = "0";
        if (slots.h) slots.h.textContent = "00";
        if (slots.m) slots.m.textContent = "00";
        if (slots.s) slots.s.textContent = "00";
        countEl.classList.add("is-ended");
        if (timer) clearInterval(timer);
        return;
      }
      var sec = Math.floor(diff / 1000);
      var d = Math.floor(sec / 86400);
      var h = Math.floor((sec % 86400) / 3600);
      var m = Math.floor((sec % 3600) / 60);
      var s = sec % 60;
      if (slots.d) slots.d.textContent = String(d);
      if (slots.h) slots.h.textContent = pad(h);
      if (slots.m) slots.m.textContent = pad(m);
      if (slots.s) slots.s.textContent = pad(s);
    };
    tick();
    var timer = setInterval(tick, 1000);
  }

  /* ---------- 数量限定メーター ---------- */
  var stockEl = document.querySelector(".cl-stock[data-qty]");
  if (stockEl) {
    var qty = parseInt(stockEl.getAttribute("data-qty"), 10) || 0;
    var sold = parseInt(stockEl.getAttribute("data-sold"), 10) || 0;
    var remain = Math.max(0, qty - sold);
    var pct = qty > 0 ? Math.round((remain / qty) * 100) : 0;
    var fill = stockEl.querySelector(".cl-stock__fill");
    var remainEl = stockEl.querySelector(".cl-stock__remain");
    if (remainEl) remainEl.textContent = remain.toLocaleString("ja-JP");
    var setW = function () { if (fill) fill.style.width = pct + "%"; };
    if (reduce) { setW(); } else {
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { setW(); io.disconnect(); } });
      }, { threshold: 0.3 });
      io.observe(stockEl);
    }
    if (pct <= 25) stockEl.classList.add("is-low");
  }

  /* ---------- ギャラリーの軽いフォーカス演出(クリックで拡大トグル) ---------- */
  document.querySelectorAll(".collab-page .cl-tile").forEach(function (tile) {
    tile.addEventListener("click", function () { tile.classList.toggle("is-active"); });
  });

  /* ---------- fantasy(原神): 七元素ホイール ---------- */
  var elemStage = document.querySelector("[data-elem-stage]");
  if (elemStage) {
    var orb = elemStage.querySelector(".cl-elem-orb");
    var nameEl = elemStage.querySelector(".cl-elem-name");
    elemStage.querySelectorAll(".cl-elem").forEach(function (btn) {
      var apply = function () {
        var col = getComputedStyle(btn).getPropertyValue("--el");
        if (orb) orb.style.setProperty("--el", col);
        if (nameEl) nameEl.textContent = btn.getAttribute("data-elem") + "元素";
        elemStage.querySelectorAll(".cl-elem").forEach(function (b) { b.classList.toggle("is-active", b === btn); });
      };
      btn.addEventListener("mouseenter", apply);
      btn.addEventListener("click", apply);
      btn.addEventListener("focus", apply);
    });
  }

  /* ---------- industrial(エンドフィールド): ターミナル起動ログ ---------- */
  var term = document.querySelector("[data-terminal]");
  if (term) {
    var out = term.querySelector(".cl-terminal__out");
    var lines = (term.getAttribute("data-lines") || "").split("|").filter(Boolean);
    if (out && lines.length) {
      var run = function () {
        out.textContent = "";
        var li = 0, ci = 0;
        var type = function () {
          if (li >= lines.length) { out.innerHTML += '<span class="cl-cursor">▋</span>'; return; }
          var line = lines[li];
          if (ci === 0 && li > 0) out.textContent += "\n";
          out.textContent += line.charAt(ci);
          ci++;
          if (ci >= line.length) { li++; ci = 0; setTimeout(type, 260); }
          else { setTimeout(type, reduce ? 4 : 22); }
        };
        type();
      };
      if (reduce) { out.textContent = lines.join("\n"); }
      else if ("IntersectionObserver" in window) {
        var io2 = new IntersectionObserver(function (es) {
          es.forEach(function (e) { if (e.isIntersecting) { run(); io2.disconnect(); } });
        }, { threshold: 0.3 });
        io2.observe(term);
      } else { run(); }
    }
  }
})();
