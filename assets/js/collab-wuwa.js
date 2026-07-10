/* ==========================================================================
   SUZAKU × 鳴潮「残響」LP専用演出
   ・ヒーロー下の周波数波形(スクロール量で振幅が育つcanvas)
   ・まれに走る一瞬のシアン反転(グリッチ)
   ========================================================================== */
(function () {
  "use strict";
  var root = document.querySelector(".collab--wuwa");
  if (!root) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- スクロール連動の波形 ---------- */
  var cv = document.getElementById("wwWave");
  if (cv && !reduce) {
    var ctx = cv.getContext("2d");
    var W = 0, H = 0, t = 0, amp = 0;
    var resize = function () {
      W = cv.clientWidth; H = cv.clientHeight;
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      cv.width = W * dpr; cv.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);
    var target = 0;
    window.addEventListener("scroll", function () {
      target = Math.min(1, (window.scrollY || 0) / 600);
    }, { passive: true });
    var draw = function () {
      t += 0.016;
      amp += (target + 0.15 - amp) * 0.04;
      ctx.clearRect(0, 0, W, H);
      var mid = H * 0.55;
      for (var l = 0; l < 2; l++) {
        ctx.beginPath();
        for (var x = 0; x <= W; x += 3) {
          var k = x / W;
          var env = Math.sin(k * Math.PI);
          var y = mid +
            Math.sin(x * 0.02 + t * (l ? 1.6 : 2.3)) * 16 * env * amp +
            Math.sin(x * 0.045 - t * 1.1) * 9 * env * amp;
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.strokeStyle = l ? "rgba(0,224,255,0.35)" : "rgba(242,242,244,0.75)";
        ctx.lineWidth = l ? 1 : 1.4;
        ctx.stroke();
      }
      requestAnimationFrame(draw);
    };
    requestAnimationFrame(draw);
  }

  /* ---------- 一瞬のシアン反転 ---------- */
  if (!reduce) {
    var flash = function () {
      root.classList.add("ww-flash");
      setTimeout(function () { root.classList.remove("ww-flash"); }, 90);
      setTimeout(flash, 6000 + Math.random() * 9000);
    };
    setTimeout(flash, 5000);
  }
})();
