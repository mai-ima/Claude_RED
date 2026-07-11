/* ==========================================================================
   SUZAKU × アークナイツ:エンドフィールド「前線」LP専用演出
   ・ターミナル起動ログのタイプライタ(実機の稼働ログ再現)
   ・タイトル画面のグリッチ断片を時々ちらつかせる
   ========================================================================== */
(function () {
  "use strict";
  if (!document.querySelector(".collab--endfield")) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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

  /* ---------- タイトル画面のグリッチちらつき ---------- */
  var noise = document.querySelectorAll(".ef-title__noise i");
  if (noise.length && !reduce) {
    setInterval(function () {
      var el = noise[Math.floor(Math.random() * noise.length)];
      el.style.visibility = "hidden";
      setTimeout(function () { el.style.visibility = ""; }, 120 + Math.random() * 200);
    }, 1400);
  }
})();
