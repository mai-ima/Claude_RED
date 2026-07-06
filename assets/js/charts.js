/* ==========================================================================
   SUZAKU charts.js — 外部ライブラリ0のSVG/HTMLチャートエンジン
   使い方: <figure class="chart" data-chart='{"type":"bar",...}'></figure>
   種類: bar(横棒) / line(折れ線) / radar(レーダー) / donut(ドーナツ)
   - 系列色は検証済みパレット(朱/青/金)を固定順で使用
   - IntersectionObserverで画面内に入ってからアニメーション
   - すべてのチャートに「データを表で見る」フォールバックを自動生成
   ========================================================================== */
(function () {
  "use strict";

  var PALETTE = ["#e8442e", "#3d8bff", "#b8862b"]; // 検証済み固定順(朱→青→金)
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function fmt(v) {
    return Number(v).toLocaleString("ja-JP");
  }

  /* ---------- データ表フォールバック ---------- */
  function dataTable(cfg) {
    var head = "", rows = "";
    if (cfg.type === "radar") {
      head = "<tr><th>軸</th>" + cfg.series.map(function (s) { return "<th>" + esc(s.name) + "</th>"; }).join("") + "</tr>";
      rows = cfg.axes.map(function (ax, i) {
        return "<tr><th>" + esc(ax) + "</th>" + cfg.series.map(function (s) { return "<td>" + fmt(s.values[i]) + "</td>"; }).join("") + "</tr>";
      }).join("");
    } else if (cfg.type === "donut") {
      head = "<tr><th>" + esc(cfg.label || "値") + "</th><td>" + fmt(cfg.value) + (cfg.unit || "") + " / " + fmt(cfg.max) + (cfg.unit || "") + "</td></tr>";
    } else if (cfg.series) {
      head = "<tr><th></th>" + cfg.labels.map(function (l) { return "<th>" + esc(l) + "</th>"; }).join("") + "</tr>";
      rows = cfg.series.map(function (s) {
        return "<tr><th>" + esc(s.name) + "</th>" + s.values.map(function (v) { return "<td>" + fmt(v) + (cfg.unit || "") + "</td>"; }).join("") + "</tr>";
      }).join("");
    } else {
      rows = cfg.labels.map(function (l, i) {
        return "<tr><th>" + esc(l) + "</th><td>" + fmt(cfg.values[i]) + (cfg.unit || "") + "</td></tr>";
      }).join("");
    }
    return '<details class="chart__data"><summary>データを表で見る</summary><div class="scroll-x"><table>' + head + rows + "</table></div></details>";
  }

  function legend(series) {
    if (!series || series.length < 2) return "";
    return '<div class="chart__legend">' + series.map(function (s, i) {
      return '<span class="chart__legend-item"><i style="background:' + (s.color || PALETTE[i % 3]) + '"></i>' + esc(s.name) + "</span>";
    }).join("") + "</div>";
  }

  function header(cfg) {
    var t = cfg.title ? '<figcaption class="chart__title">' + esc(cfg.title) + (cfg.unit ? ' <span class="chart__unit">単位: ' + esc(cfg.unit) + "</span>" : "") + "</figcaption>" : "";
    return t;
  }

  /* ---------- 横棒グラフ(HTML) ---------- */
  function renderBar(el, cfg) {
    /* 横棒は単系列(cfg.values)を正とするが、単一系列を series 形式で渡された
       場合も許容して values に正規化する(記述ゆれによる描画エラーの防止)。 */
    if (!cfg.values && cfg.series && cfg.series.length) cfg.values = cfg.series[0].values;
    if (!cfg.values || !cfg.labels) return;
    var max = cfg.max || Math.max.apply(null, cfg.values) * 1.06;
    var rows = cfg.labels.map(function (label, i) {
      var v = cfg.values[i];
      var pct = Math.max(1.5, (v / max) * 100);
      var hi = cfg.highlight === i;
      var color = hi ? PALETTE[0] : (cfg.color || "rgba(232,68,46,0.45)");
      if (cfg.categorical) color = PALETTE[i % 3];
      return '<div class="chart-bar__row' + (hi ? " is-hi" : "") + '" title="' + esc(label) + ": " + fmt(v) + (cfg.unit || "") + '">' +
        '<span class="chart-bar__label">' + esc(label) + "</span>" +
        '<span class="chart-bar__track"><i class="chart-bar__fill" style="background:' + color + '" data-w="' + pct.toFixed(1) + '"></i></span>' +
        '<span class="chart-bar__value">' + fmt(v) + '<small>' + esc(cfg.unit || "") + "</small></span>" +
        "</div>";
    }).join("");
    el.innerHTML = header(cfg) + '<div class="chart-bar" role="img" aria-label="' + esc(cfg.title || "棒グラフ") + '">' + rows + "</div>" + dataTable(cfg);
  }

  /* ---------- 折れ線グラフ(SVG) ---------- */
  function renderLine(el, cfg) {
    if (!cfg.series || !cfg.series.length || !cfg.labels) return;
    var W = 560, H = 240, PL = 46, PR = 16, PT = 14, PB = 30;
    var series = cfg.series;
    var all = [];
    series.forEach(function (s) { all = all.concat(s.values); });
    var maxV = cfg.max || Math.max.apply(null, all) * 1.1;
    var minV = cfg.min !== undefined ? cfg.min : 0;
    var n = cfg.labels.length;
    function X(i) { return PL + (i / Math.max(1, n - 1)) * (W - PL - PR); }
    function Y(v) { return PT + (1 - (v - minV) / (maxV - minV)) * (H - PT - PB); }

    var grid = "", ticks = 3;
    for (var g = 0; g <= ticks; g++) {
      var val = minV + ((maxV - minV) * g) / ticks;
      var y = Y(val);
      grid += '<line x1="' + PL + '" y1="' + y + '" x2="' + (W - PR) + '" y2="' + y + '" class="chart-line__grid"/>' +
        '<text x="' + (PL - 8) + '" y="' + (y + 4) + '" class="chart-line__tick" text-anchor="end">' + fmt(Math.round(val)) + "</text>";
    }
    var xlabels = cfg.labels.map(function (l, i) {
      return '<text x="' + X(i) + '" y="' + (H - 8) + '" class="chart-line__tick" text-anchor="middle">' + esc(l) + "</text>";
    }).join("");

    var paths = series.map(function (s, si) {
      var color = s.color || PALETTE[si % 3];
      var pts = s.values.map(function (v, i) { return X(i).toFixed(1) + "," + Y(v).toFixed(1); });
      var dots = s.values.map(function (v, i) {
        return '<circle cx="' + X(i).toFixed(1) + '" cy="' + Y(v).toFixed(1) + '" r="4" fill="' + color + '" stroke="var(--surface)" stroke-width="2"><title>' + esc(cfg.labels[i]) + ": " + fmt(v) + (cfg.unit || "") + "</title></circle>";
      }).join("");
      var last = s.values.length - 1;
      var endLabel = '<text x="' + (X(last) - 2) + '" y="' + (Y(s.values[last]) - 10) + '" class="chart-line__end" text-anchor="end" fill="' + color + '">' + fmt(s.values[last]) + (cfg.unit || "") + "</text>";
      var area = cfg.area && si === 0
        ? '<polygon points="' + PL + "," + Y(minV) + " " + pts.join(" ") + " " + X(last).toFixed(1) + "," + Y(minV) + '" fill="' + color + '" opacity="0.09"/>' : "";
      return area + '<polyline points="' + pts.join(" ") + '" fill="none" stroke="' + color + '" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="chart-line__path"/>' + dots + endLabel;
    }).join("");

    el.innerHTML = header(cfg) +
      '<svg viewBox="0 0 ' + W + " " + H + '" class="chart-line" role="img" aria-label="' + esc(cfg.title || "折れ線グラフ") + '">' + grid + xlabels + paths + "</svg>" +
      legend(series) + dataTable(cfg);
  }

  /* ---------- レーダーチャート(SVG) ---------- */
  function renderRadar(el, cfg) {
    if (!cfg.axes || !cfg.axes.length || !cfg.series || !cfg.series.length) return;
    var W = 360, H = 320, cx = W / 2, cy = H / 2 + 6, R = 108;
    var n = cfg.axes.length;
    function pt(i, r) {
      var a = (Math.PI * 2 * i) / n - Math.PI / 2;
      return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
    }
    var rings = [0.25, 0.5, 0.75, 1].map(function (f) {
      var p = [];
      for (var i = 0; i < n; i++) p.push(pt(i, R * f).map(function (x) { return x.toFixed(1); }).join(","));
      return '<polygon points="' + p.join(" ") + '" class="chart-radar__ring"/>';
    }).join("");
    var spokes = "", axLabels = "";
    for (var i = 0; i < n; i++) {
      var e = pt(i, R), lp = pt(i, R + 22);
      spokes += '<line x1="' + cx + '" y1="' + cy + '" x2="' + e[0].toFixed(1) + '" y2="' + e[1].toFixed(1) + '" class="chart-radar__ring"/>';
      axLabels += '<text x="' + lp[0].toFixed(1) + '" y="' + (lp[1] + 4).toFixed(1) + '" class="chart-radar__ax" text-anchor="middle">' + esc(cfg.axes[i]) + "</text>";
    }
    var polys = cfg.series.map(function (s, si) {
      var color = s.color || PALETTE[si % 3];
      var p = s.values.map(function (v, i) {
        return pt(i, (Math.max(0, Math.min(100, v)) / 100) * R).map(function (x) { return x.toFixed(1); }).join(",");
      });
      return '<polygon points="' + p.join(" ") + '" fill="' + color + '" fill-opacity="0.13" stroke="' + color + '" stroke-width="2" stroke-linejoin="round"><title>' + esc(s.name) + "</title></polygon>";
    }).join("");
    el.innerHTML = header(cfg) +
      '<svg viewBox="0 0 ' + W + " " + H + '" class="chart-radar" role="img" aria-label="' + esc(cfg.title || "レーダーチャート") + '">' + rings + spokes + axLabels + polys + "</svg>" +
      legend(cfg.series) + dataTable(cfg);
  }

  /* ---------- ドーナツ/ゲージ(SVG) ---------- */
  function renderDonut(el, cfg) {
    if (typeof cfg.value !== "number" || typeof cfg.max !== "number" || !cfg.max) return;
    var R = 62, C = 2 * Math.PI * R;
    var ratio = Math.max(0, Math.min(1, cfg.value / cfg.max));
    el.innerHTML = header(cfg) +
      '<div class="chart-donut" role="img" aria-label="' + esc(cfg.label || "") + " " + fmt(cfg.value) + (cfg.unit || "") + '">' +
      '<svg viewBox="0 0 160 160">' +
      '<circle cx="80" cy="80" r="' + R + '" class="chart-donut__track"/>' +
      '<circle cx="80" cy="80" r="' + R + '" class="chart-donut__fill" stroke="' + (cfg.color || PALETTE[0]) + '" stroke-dasharray="' + C.toFixed(1) + '" stroke-dashoffset="' + C.toFixed(1) + '" data-off="' + (C * (1 - ratio)).toFixed(1) + '" transform="rotate(-90 80 80)"/>' +
      "</svg>" +
      '<div class="chart-donut__center"><strong>' + fmt(cfg.value) + '<small>' + esc(cfg.unit || "") + "</small></strong><span>" + esc(cfg.label || "") + "</span></div>" +
      "</div>" + dataTable(cfg);
  }

  /* ---------- 起動 ----------
     チャート種別はマップで管理する。新しい種別を追加するときは
     render関数を書いて RENDERERS に1行足すだけでよい。 */
  var RENDERERS = { bar: renderBar, line: renderLine, radar: renderRadar, donut: renderDonut };
  function render(el) {
    var cfg;
    try { cfg = JSON.parse(el.getAttribute("data-chart")); } catch (e) { return; }
    var fn = cfg && RENDERERS[cfg.type];
    if (!fn) return;
    /* 1つのチャートの不備でページ全体のスクリプトが止まらないよう隔離する */
    try {
      fn(el, cfg);
      el.classList.add("is-rendered");
    } catch (e) {
      if (window.console && console.warn) console.warn("SUZAKU charts: 描画をスキップしました", e);
    }
  }

  function animate(el) {
    el.classList.add("chart--animate");
    // 棒グラフ: 幅を0→データ値へ
    Array.prototype.forEach.call(el.querySelectorAll(".chart-bar__fill"), function (bar, i) {
      var w = bar.getAttribute("data-w") + "%";
      if (reduced) { bar.style.width = w; return; }
      setTimeout(function () { bar.style.width = w; }, 80 * i);
    });
    // 折れ線: ダッシュで描画
    Array.prototype.forEach.call(el.querySelectorAll(".chart-line__path"), function (path) {
      if (reduced) return;
      var len = path.getTotalLength();
      path.style.strokeDasharray = len;
      path.style.strokeDashoffset = len;
      path.getBoundingClientRect();
      path.style.transition = "stroke-dashoffset 1.4s cubic-bezier(0.22,1,0.36,1)";
      path.style.strokeDashoffset = "0";
    });
    // ドーナツ
    Array.prototype.forEach.call(el.querySelectorAll(".chart-donut__fill"), function (c) {
      var off = c.getAttribute("data-off");
      if (reduced) { c.style.strokeDashoffset = off; return; }
      setTimeout(function () { c.style.strokeDashoffset = off; }, 150);
    });
  }

  window.szCharts = {
    renderInto: function (el, cfg) {
      el.setAttribute("data-chart", JSON.stringify(cfg));
      render(el);
      animate(el);
    }
  };

  var charts = Array.prototype.slice.call(document.querySelectorAll(".chart[data-chart]"));
  charts.forEach(render);
  if ("IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          animate(en.target);
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.3 });
    charts.forEach(function (el) { io.observe(el); });
  } else {
    charts.forEach(animate);
  }
})();
