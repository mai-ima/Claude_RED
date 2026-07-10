/* ==========================================================================
   SUZAKU × アークナイツ:エンドフィールド「前線」LP専用演出
   ・起動カウンタ 0→100%(1セッション1回)
   ・ターミナル起動ログのタイプライタ
   ========================================================================== */
(function () {
  "use strict";
  if (!document.querySelector(".collab--endfield")) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 起動カウンタ ---------- */
  var boot = document.getElementById("efBoot");
  if (boot) {
    var seen = false;
    try { seen = sessionStorage.getItem("sz_ef_boot") === "1"; } catch (e) {}
    if (reduce || seen) {
      boot.classList.add("is-done");
    } else {
      var pctEl = boot.querySelector("[data-boot]");
      var bar = boot.querySelector(".ef-boot__bar");
      var p = 0;
      var step = function () {
        p = Math.min(100, p + 3 + Math.random() * 9);
        var v = Math.floor(p);
        if (pctEl) pctEl.textContent = v + "%";
        if (bar) bar.style.setProperty("--p", v + "%");
        if (p < 100) {
          setTimeout(step, 40 + Math.random() * 70);
        } else {
          setTimeout(function () {
            boot.classList.add("is-done");
            try { sessionStorage.setItem("sz_ef_boot", "1"); } catch (e) {}
          }, 300);
        }
      };
      step();
    }
  }

  /* ---------- ターミナル起動ログ ---------- */
  var term = document.querySelector("[data-terminal]");
  if (term) {
    var out = term.querySelector(".ef-terminal__out");
    var lines = (term.getAttribute("data-lines") || "").split("|").filter(Boolean);
    if (out && lines.length) {
      var run = function () {
        out.textContent = "";
        var li = 0, ci = 0;
        var type = function () {
          if (li >= lines.length) return;
          var line = lines[li];
          if (ci === 0 && li > 0) out.textContent += "\n";
          out.textContent += line.charAt(ci);
          ci++;
          if (ci >= line.length) { li++; ci = 0; setTimeout(type, 240); }
          else { setTimeout(type, 18); }
        };
        type();
      };
      if (reduce) {
        out.textContent = lines.join("\n");
      } else if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) { if (e.isIntersecting) { run(); io.disconnect(); } });
        }, { threshold: 0.3 });
        io.observe(term);
      } else {
        run();
      }
    }
  }
})();
