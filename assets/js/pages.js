/* ==========================================================================
   SUZAKU pages.js — FAQ / ニュース一覧 / サイト内検索 / 修理受付・照会 / 汎用フォーム
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var SZ = window.SZ || { products: [], news: [], faq: [], pages: [] };

  function escHtml(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ---------------- FAQ ---------------- */
  var faqList = $("#faqList");
  if (faqList) {
    var faqCat = "all";
    var faqQuery = "";
    function renderFaq() {
      var items = SZ.faq.filter(function (f) {
        if (faqCat !== "all" && f.cat !== faqCat) return false;
        if (faqQuery && (f.q + f.a).toLowerCase().indexOf(faqQuery) === -1) return false;
        return true;
      });
      if (!items.length) {
        faqList.innerHTML = '<div class="empty"><p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></p><p>該当するご質問が見つかりませんでした。</p><a class="btn btn--ghost" href="/support/contact/">お問い合わせフォームへ</a></div>';
        return;
      }
      faqList.innerHTML = '<div class="accordion">' + items.map(function (f) {
        return '<div class="accordion__item"><button class="accordion__q" aria-expanded="false"><span><span class="badge" style="margin-right:10px">' + f.cat + "</span>" + escHtml(f.q) + "</span></button>" +
          '<div class="accordion__a"><div class="accordion__a-inner"><div class="accordion__a-body">' + f.a + "</div></div></div></div>";
      }).join("") + "</div>";
      var count = $("#faqCount");
      if (count) count.textContent = items.length + "件";
    }
    var tabsBox = $("#faqTabs");
    if (tabsBox) {
      var cats = ["all"];
      SZ.faq.forEach(function (f) { if (cats.indexOf(f.cat) === -1) cats.push(f.cat); });
      tabsBox.innerHTML = cats.map(function (c, i) {
        return '<button class="tab' + (i === 0 ? " is-active" : "") + '" data-faq-cat="' + c + '">' + (c === "all" ? "すべて" : c) + "</button>";
      }).join("");
      tabsBox.addEventListener("click", function (e) {
        var t = e.target.closest("[data-faq-cat]");
        if (!t) return;
        $$(".tab", tabsBox).forEach(function (x) { x.classList.remove("is-active"); });
        t.classList.add("is-active");
        faqCat = t.getAttribute("data-faq-cat");
        renderFaq();
      });
    }
    var faqSearch = $("#faqSearch");
    if (faqSearch) {
      faqSearch.addEventListener("input", function () {
        faqQuery = faqSearch.value.trim().toLowerCase();
        renderFaq();
      });
    }
    renderFaq();
  }

  /* ---------------- ニュース一覧 ---------------- */
  var newsList = $("#newsList");
  if (newsList) {
    var nYear = "all";
    var nCat = "all";
    function renderNews() {
      var items = SZ.news.filter(function (n) {
        if (nYear !== "all" && n.date.slice(0, 4) !== nYear) return false;
        if (nCat !== "all" && n.cat !== nCat) return false;
        return true;
      });
      if (!items.length) {
        newsList.innerHTML = '<div class="empty"><p>該当するニュースはありません。</p></div>';
        return;
      }
      newsList.innerHTML = items.map(function (n) {
        return '<a class="card card--hover" href="' + n.url + '">' +
          '<p class="t-micro t-faint">' + n.date.replace(/-/g, ".") + ' <span class="badge" style="margin-left:8px">' + n.cat + "</span></p>" +
          '<h2 class="t-h4">' + escHtml(n.title) + "</h2>" +
          '<p class="t-small t-soft">' + escHtml(n.excerpt) + "</p>" +
          '<p class="link-arrow">読む</p></a>';
      }).join("");
    }
    var yearBox = $("#newsYears");
    if (yearBox) {
      var years = ["all"];
      SZ.news.forEach(function (n) {
        var y = n.date.slice(0, 4);
        if (years.indexOf(y) === -1) years.push(y);
      });
      yearBox.innerHTML = years.map(function (y, i) {
        return '<button class="tab' + (i === 0 ? " is-active" : "") + '" data-news-year="' + y + '">' + (y === "all" ? "すべての年" : y + "年") + "</button>";
      }).join("");
    }
    var catBox = $("#newsCats");
    if (catBox) {
      var ncats = ["all"];
      SZ.news.forEach(function (n) { if (ncats.indexOf(n.cat) === -1) ncats.push(n.cat); });
      catBox.innerHTML = ncats.map(function (c, i) {
        return '<button class="tab' + (i === 0 ? " is-active" : "") + '" data-news-cat="' + c + '">' + (c === "all" ? "すべて" : c) + "</button>";
      }).join("");
    }
    document.addEventListener("click", function (e) {
      var y = e.target.closest("[data-news-year]");
      var c = e.target.closest("[data-news-cat]");
      if (y) {
        $$("[data-news-year]").forEach(function (x) { x.classList.remove("is-active"); });
        y.classList.add("is-active");
        nYear = y.getAttribute("data-news-year");
        renderNews();
      } else if (c) {
        $$("[data-news-cat]").forEach(function (x) { x.classList.remove("is-active"); });
        c.classList.add("is-active");
        nCat = c.getAttribute("data-news-cat");
        renderNews();
      }
    });
    renderNews();
  }

  /* ---------------- サイト内検索 ---------------- */
  var searchResults = $("#searchResults");
  if (searchResults) {
    var input = $("#siteSearchInput");
    var params = new URLSearchParams(window.location.search);
    var q0 = params.get("q") || "";
    if (input) input.value = q0;

    function buildIndex() {
      var idx = [];
      SZ.products.forEach(function (p) {
        idx.push({ type: "製品", title: p.name + "(" + p.lineLabel + " / " + p.year + ")", url: p.url, text: p.name + " " + p.kana + " " + p.tagline + " " + p.lineLabel });
      });
      SZ.news.forEach(function (n) {
        idx.push({ type: "ニュース", title: n.title, url: n.url, text: n.title + " " + n.excerpt + " " + n.cat });
      });
      SZ.faq.forEach(function (f) {
        idx.push({ type: "FAQ", title: f.q, url: "/support/faq/", text: f.q + " " + f.a.replace(/<[^>]+>/g, "") });
      });
      SZ.pages.forEach(function (pg) {
        idx.push({ type: pg.group, title: pg.title, url: pg.url, text: pg.title + " " + pg.desc });
      });
      return idx;
    }
    var index = buildIndex();

    function doSearch(q) {
      q = q.trim().toLowerCase();
      var info = $("#searchInfo");
      if (!q) {
        searchResults.innerHTML = "";
        if (info) info.textContent = "キーワードを入力してください(例: SUZAKU 4、冷却、修理、保証)。";
        return;
      }
      var terms = q.split(/\s+/);
      var hits = index.map(function (item) {
        var hay = (item.title + " " + item.text).toLowerCase();
        var score = 0;
        var ok = terms.every(function (t) { return hay.indexOf(t) !== -1; });
        if (!ok) return null;
        terms.forEach(function (t) {
          if (item.title.toLowerCase().indexOf(t) !== -1) score += 3;
          score += 1;
        });
        return { item: item, score: score };
      }).filter(Boolean).sort(function (a, b) { return b.score - a.score; }).slice(0, 40);
      if (info) info.textContent = '「' + q + '」の検索結果: ' + hits.length + "件";
      if (!hits.length) {
        searchResults.innerHTML = '<div class="empty"><p class="empty__icon"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></p><p>一致する結果が見つかりませんでした。別のキーワードをお試しください。</p></div>';
        return;
      }
      searchResults.innerHTML = hits.map(function (h) {
        return '<a class="card card--hover" href="' + h.item.url + '">' +
          '<p class="t-micro" style="color:var(--accent);font-weight:700">' + escHtml(h.item.type) + "</p>" +
          '<h2 class="t-h4">' + escHtml(h.item.title) + "</h2>" +
          '<p class="t-micro t-faint">' + h.item.url + "</p></a>";
      }).join("");
    }
    if (input) {
      input.addEventListener("input", function () { doSearch(input.value); });
    }
    doSearch(q0);
  }

  /* ---------------- 修理受付フォーム ---------------- */
  var repairForm = $("#repairForm");
  if (repairForm) {
    repairForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      $$("input[required], select[required], textarea[required]", repairForm).forEach(function (inp) {
        var field = inp.closest(".field");
        var bad = !inp.value.trim();
        if (inp.type === "email" && inp.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inp.value)) bad = true;
        if (field) field.classList.toggle("has-error", bad);
        if (bad) ok = false;
      });
      if (!ok) { window.szToast("入力内容をご確認ください"); return; }
      var no = "SZR-" + String(Math.floor(10000000 + Math.random() * 90000000));
      var tickets = window.szStore.get("sz_tickets", []);
      tickets.unshift({
        no: no,
        date: new Date().toISOString(),
        model: $("#rpModel").value,
        symptom: $("#rpSymptom").value,
        method: repairForm.querySelector("input[name=rpMethod]:checked").value,
        status: "受付完了"
      });
      window.szStore.set("sz_tickets", tickets);
      repairForm.hidden = true;
      var done = $("#repairDone");
      $("#repairNo").textContent = no;
      done.hidden = false;
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------------- 修理状況照会 ---------------- */
  var ticketLookup = $("#ticketLookupForm");
  if (ticketLookup) {
    ticketLookup.addEventListener("submit", function (e) {
      e.preventDefault();
      var no = $("#ticketNo").value.trim().toUpperCase();
      var tickets = window.szStore.get("sz_tickets", []);
      var hit = tickets.filter(function (t) { return t.no === no; })[0];
      var box = $("#ticketResult");
      if (!hit) {
        box.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> 受付番号「' + escHtml(no) + '」は見つかりませんでした。この端末で行われたお申し込みのみ照会できます(デモ仕様)。</div>';
        return;
      }
      var placed = new Date(hit.date);
      var hours = (Date.now() - placed.getTime()) / 36e5;
      var steps = [
        { t: "受付完了", done: true },
        { t: "端末到着・診断中", done: hours > 24 },
        { t: "修理作業中", done: hours > 48 },
        { t: "修理完了・返送", done: hours > 96 },
        { t: "お届け完了", done: hours > 144 }
      ];
      box.innerHTML = '<div class="card" style="margin-top:24px">' +
        '<p class="eyebrow">受付番号 ' + hit.no + "</p>" +
        '<p class="t-small t-soft">受付日時: ' + placed.toLocaleString("ja-JP") + " / 対象機種: " + escHtml(hit.model) + " / 方法: " + escHtml(hit.method) + "</p>" +
        '<ol class="order-track">' + steps.map(function (s) {
          return '<li class="' + (s.done ? "is-done" : "") + '"><span>' + s.t + "</span></li>";
        }).join("") + "</ol></div>";
    });
  }

  /* ---------------- ドキュメントビューア(PDF閲覧) ---------------- */
  var docPages = $("#docPages");
  if (docPages) {
    var docs = SZ.docs || [];
    var docId = new URLSearchParams(window.location.search).get("doc") || (docs[0] && docs[0].id);
    var doc = docs.filter(function (d) { return d.id === docId; })[0] || docs[0];

    function block(b) {
      if (b.t === "h1") return "<h1>" + escHtml(b.v) + "</h1>";
      if (b.t === "h2") return "<h2>" + escHtml(b.v) + "</h2>";
      if (b.t === "p") return "<p>" + escHtml(b.v) + "</p>";
      if (b.t === "note") return '<p class="doc-note">' + escHtml(b.v) + "</p>";
      if (b.t === "list") return "<ul>" + b.v.map(function (x) { return "<li>" + escHtml(x) + "</li>"; }).join("") + "</ul>";
      if (b.t === "table") {
        return '<table>' + b.v.map(function (row, i) {
          var tag = i === 0 && b.v.length > 2 && b.v[0].length > 2 ? "th" : "td";
          return "<tr>" + row.map(function (c) { return "<" + tag + ">" + escHtml(c) + "</" + tag + ">"; }).join("") + "</tr>";
        }).join("") + "</table>";
      }
      return "";
    }

    if (doc) {
      $("#docTitle").textContent = doc.title;
      $("#docMeta").textContent = doc.category + " / " + doc.version;
      document.title = doc.title + " | SUZAKU(朱雀)";
      docPages.innerHTML = doc.pages.map(function (pg, i) {
        return '<article class="doc-page" data-page="' + (i + 1) + '">' +
          '<header class="doc-page__head"><span>SUZAKU — ' + escHtml(doc.title) + "</span><span>" + escHtml(doc.version) + "</span></header>" +
          pg.map(block).join("") +
          '<footer class="doc-page__foot"><span>© 2022-2026 SUZAKU Inc.(架空のデモ文書)</span><span>' + (i + 1) + " / " + doc.pages.length + "</span></footer></article>";
      }).join("");
      $("#docPageInfo").textContent = "1 / " + doc.pages.length;

      // 表示中ページ番号
      if ("IntersectionObserver" in window) {
        var pio = new IntersectionObserver(function (ens) {
          ens.forEach(function (en) {
            if (en.isIntersecting) $("#docPageInfo").textContent = en.target.getAttribute("data-page") + " / " + doc.pages.length;
          });
        }, { threshold: 0.5 });
        $$(".doc-page", docPages).forEach(function (el) { pio.observe(el); });
      }
    }

    // ズーム
    var zoom = 100;
    function applyZoom() {
      docPages.style.setProperty("--doc-zoom", zoom / 100);
      $("#zoomLevel").textContent = zoom + "%";
    }
    $("#zoomIn").addEventListener("click", function () { zoom = Math.min(150, zoom + 10); applyZoom(); });
    $("#zoomOut").addEventListener("click", function () { zoom = Math.max(70, zoom - 10); applyZoom(); });
    $("#docPrint").addEventListener("click", function () { window.print(); });

    // ライブラリ
    var lib = $("#docLibrary");
    if (lib) {
      lib.innerHTML = docs.map(function (d) {
        var cur = doc && d.id === doc.id;
        return '<a class="card card--hover' + (cur ? " is-current-doc" : "") + '" href="/viewer/?doc=' + d.id + '">' +
          '<div class="spread"><div><p class="eyebrow">' + escHtml(d.category) + "</p><h3 class='t-h4'>" + escHtml(d.title) +
          (cur ? ' <span class="badge">表示中</span>' : "") + "</h3><p class='t-micro t-faint'>" + escHtml(d.version) + " / " + d.pages.length + "ページ</p></div>" +
          '<span class="link-arrow">開く</span></div></a>';
      }).join("");
    }
  }

  /* ---------------- 汎用モックフォーム(お問い合わせ等) ---------------- */
  $$("form[data-mock-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      $$("input[required], select[required], textarea[required]", form).forEach(function (inp) {
        var field = inp.closest(".field");
        var bad = !inp.value.trim();
        if (inp.type === "email" && inp.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inp.value)) bad = true;
        if (inp.type === "checkbox" && inp.required && !inp.checked) bad = true;
        if (field) field.classList.toggle("has-error", bad);
        if (bad) ok = false;
      });
      if (!ok) { window.szToast("入力内容をご確認ください"); return; }
      form.hidden = true;
      var doneSel = form.getAttribute("data-mock-form") || "#formDone";
      var done = $(doneSel);
      if (done) {
        done.hidden = false;
        var ref = done.querySelector("[data-ref-no]");
        if (ref) ref.textContent = "SZC-" + String(Math.floor(10000000 + Math.random() * 90000000));
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
      window.szToast("送信が完了しました");
    });
  });
})();
