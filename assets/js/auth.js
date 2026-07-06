/* ==========================================================================
   SUZAKU auth.js — アカウント / 管理ボード / メンテナンスシステム
   localStorageで完結するデモ実装(実際の認証・通信は行いません)。
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var get = function (k, f) { return window.szStore.get(k, f); };
  var set = function (k, v) { window.szStore.set(k, v); };

  function yen(n) { return "¥" + Math.round(n).toLocaleString("ja-JP"); }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* ---------- パスワードハッシュ(デモ用の簡易実装) ---------- */
  function hash(str) {
    var h = 5381;
    for (var i = 0; i < str.length; i++) h = ((h << 5) + h + str.charCodeAt(i)) >>> 0;
    return "h" + h.toString(36) + str.length.toString(36);
  }

  /* ---------- ユーザーストア ---------- */
  var ADMIN_EMAIL = "admin@suzaku.example.jp";
  var DEMO_EMAIL = "user@suzaku.example.jp";
  var ADMIN_PW = "suzaku-admin";
  var DEMO_PW = "suzaku-user";

  function users() { return get("sz_users", []); }

  function seedUsers() {
    var us = users();
    var deleted = get("sz_seed_del", []); /* 管理ボードで削除されたシードは復活させない */
    var dirty = false;
    if (!us.some(function (u) { return u.email === ADMIN_EMAIL; })) {
      us.push({ name: "SUZAKU 管理者", email: ADMIN_EMAIL, pw: hash(ADMIN_PW), pwPlain: ADMIN_PW, role: "admin", created: "2022-05-01T00:00:00.000Z" });
      dirty = true;
    }
    if (deleted.indexOf(DEMO_EMAIL) === -1 && !us.some(function (u) { return u.email === DEMO_EMAIL; })) {
      us.push({ name: "燕 みなみ(デモ会員)", email: DEMO_EMAIL, pw: hash(DEMO_PW), pwPlain: DEMO_PW, role: "member", created: "2024-05-17T09:00:00.000Z" });
      dirty = true;
    }
    /* 既存シードにもデモ用の平文パスワードを補完(管理ボードの閲覧用) */
    us.forEach(function (u) {
      if (!u.pwPlain && u.email === ADMIN_EMAIL) { u.pwPlain = ADMIN_PW; dirty = true; }
      if (!u.pwPlain && u.email === DEMO_EMAIL) { u.pwPlain = DEMO_PW; dirty = true; }
    });
    if (dirty) set("sz_users", us);
  }
  seedUsers();

  /* ---------- 全体制御・ページ制御・サービス状況(管理ボードから設定) ---------- */
  var SVC_DEFAULT = { store: "ok", repair: "ok", os: "ok", jin: "ok", api: "ok" };
  function globalCtrl() { return get("sz_global", { lockdown: false, lockMsg: "", shopStop: false, contactStop: false }); }
  function pageCtrl() { return get("sz_page_ctrl", {}); }
  function services() {
    var s = get("sz_services", {});
    var out = {};
    for (var k in SVC_DEFAULT) out[k] = s[k] || SVC_DEFAULT[k];
    return out;
  }
  window.szCtrl = {
    global: globalCtrl,
    setGlobal: function (v) { set("sz_global", v); },
    pages: pageCtrl,
    setPages: function (v) { set("sz_page_ctrl", v); },
    services: services,
    setServices: function (v) { set("sz_services", v); }
  };

  function session() { return get("sz_session", null); }
  function currentUser() {
    var s = session();
    if (!s) return null;
    return users().filter(function (u) { return u.email === s.email; })[0] || null;
  }
  function login(email, pw) {
    var u = users().filter(function (x) { return x.email === email.toLowerCase().trim(); })[0];
    if (!u || u.pw !== hash(pw)) return null;
    set("sz_session", { email: u.email, role: u.role, at: new Date().toISOString() });
    return u;
  }
  function logout() {
    try { localStorage.removeItem("sz_session"); } catch (e) { /* noop */ }
  }

  window.szAuth = { currentUser: currentUser, logout: logout };

  /* ---------- ヘッダーのアカウント表示 ---------- */
  var acctLink = $("#accountLink");
  var u0 = currentUser();
  if (acctLink && u0) {
    acctLink.setAttribute("href", u0.role === "admin" ? "/admin/" : "/account/");
    acctLink.setAttribute("aria-label", u0.name + " のアカウント");
    acctLink.classList.add("is-logged-in");
  }

  /* ---------- アクセス制御(全体立入禁止・ページ別ステータス) ---------- */
  var path = window.location.pathname;
  var normPath = path;
  if (normPath.slice(-1) !== "/" && normPath.indexOf(".html") === -1) normPath += "/";
  if (/\/index\.html$/.test(normPath)) normPath = normPath.replace(/index\.html$/, "");
  var me0 = currentUser();
  var isAdmin0 = !!(me0 && me0.role === "admin");
  var CTRL_LABEL = { members: "会員限定", admin: "管理者限定", maint: "メンテナンス中", gone: "非公開(404)" };

  function adminPreviewChip(text) {
    var chip = document.createElement("div");
    chip.className = "admin-preview";
    chip.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/></svg> ' + text;
    document.body.appendChild(chip);
  }

  /* 管理者が「一般ユーザーとしての見え方」を確認するためのプレビュー。
     URLに ?preview=user が付いている場合、管理者でも一般ユーザー扱いにして
     立入禁止・メンテ・ページ制御の実際の挙動(リダイレクト等)を再現する。 */
  var previewAsUser = /[?&]preview=user(&|$)/.test(window.location.search);
  var effectiveAdmin = isAdmin0 && !previewAsUser;

  (function accessControl() {
    var glob = globalCtrl();
    var ctrl = pageCtrl()[normPath];
    /* 常時アクセス可能(締め出し防止): アカウント系(ログイン・ログアウト導線)・メンテ案内・404・管理ボード */
    var alwaysOpen = normPath.indexOf("/account/") === 0 || normPath === "/maintenance/" ||
      normPath === "/404.html" || normPath.indexOf("/admin") === 0;
    if (effectiveAdmin) {
      /* 管理者はすべて閲覧可能。制御中のページではプレビュー表示 */
      if (glob.lockdown && normPath.indexOf("/admin") !== 0) {
        adminPreviewChip("全サイト立入禁止 設定中(管理者として閲覧しています)");
      } else if (ctrl) {
        adminPreviewChip("このページは「" + CTRL_LABEL[ctrl] + "」設定中(管理者として閲覧しています)");
      }
      return;
    }
    if (previewAsUser) adminPreviewChip("プレビュー: 一般ユーザーとしての表示です");
    if (glob.lockdown && !alwaysOpen) {
      window.location.replace("/maintenance/" + (previewAsUser ? "?preview=user" : ""));
      return;
    }
    if (!ctrl || alwaysOpen) return;
    var q = previewAsUser ? "?preview=user" : "";
    if (ctrl === "gone" || ctrl === "admin") window.location.replace("/404.html" + q);
    else if (ctrl === "maint") window.location.replace("/maintenance/" + q);
    else if (ctrl === "members" && !me0) window.location.replace("/account/login/" + q);
  })();

  /* ---------- メンテナンスシステム ---------- */
  var maint = get("sz_maintenance", { on: false, msg: "" });
  if (maint.on && path.indexOf("/admin") !== 0) {
    var bar = document.createElement("div");
    bar.className = "maint-bar";
    bar.setAttribute("role", "status");
    bar.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6L15 12l-3-3z"/></svg> ' +
      "ただいまメンテナンス中です。" + (maint.msg ? esc(maint.msg) + " " : "") +
      '<a href="/maintenance/">詳細</a>';
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add("has-maint-bar");
    // バナーは折返しで高さが変わるため、実高を測ってCSS変数に反映する
    var syncMaintH = function () {
      document.documentElement.style.setProperty("--maint-h", bar.offsetHeight + "px");
    };
    syncMaintH();
    window.addEventListener("resize", syncMaintH);
    window.addEventListener("load", syncMaintH);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(syncMaintH);
  }
  window.szMaint = {
    get: function () { return get("sz_maintenance", { on: false, msg: "" }); },
    set: function (v) { set("sz_maintenance", v); }
  };

  /* ---------- ログインページ ---------- */
  var loginForm = $("#loginForm");
  if (loginForm) {
    if (currentUser()) window.location.replace(currentUser().role === "admin" ? "/admin/" : "/account/");
    /* デモ用: 資格情報のワンタップ入力 */
    function fillLogin(email, pw, label) {
      $("#loginEmail").value = email;
      $("#loginPw").value = pw;
      $("#loginError").hidden = true;
      window.szToast(label + "の情報を入力しました。「ログイン」を押してください");
    }
    var fillAdmin = $("#fillAdmin");
    if (fillAdmin) fillAdmin.addEventListener("click", function () { fillLogin(ADMIN_EMAIL, ADMIN_PW, "管理者アカウント"); });
    var fillUser = $("#fillUser");
    if (fillUser) fillUser.addEventListener("click", function () { fillLogin(DEMO_EMAIL, DEMO_PW, "デモ会員アカウント"); });
    loginForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var u = login($("#loginEmail").value, $("#loginPw").value);
      var err = $("#loginError");
      if (!u) {
        err.hidden = false;
        return;
      }
      window.szToast("おかえりなさい、" + u.name + " さん");
      setTimeout(function () {
        window.location.href = u.role === "admin" ? "/admin/" : "/account/";
      }, 500);
    });
  }

  /* ---------- アカウント作成ページ ---------- */
  var regForm = $("#registerForm");
  if (regForm) {
    regForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = $("#regName").value.trim();
      var email = $("#regEmail").value.trim().toLowerCase();
      var pw = $("#regPw").value;
      var pw2 = $("#regPw2").value;
      var agree = $("#regAgree").checked;
      var err = $("#regError");
      var bad = "";
      if (!name) bad = "お名前を入力してください。";
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) bad = "メールアドレスの形式が正しくありません。";
      else if (pw.length < 8) bad = "パスワードは8文字以上で設定してください。";
      else if (pw !== pw2) bad = "確認用パスワードが一致しません。";
      else if (!agree) bad = "利用規約とプライバシーポリシーへの同意が必要です。";
      else if (users().some(function (x) { return x.email === email; })) bad = "このメールアドレスは既に登録されています。";
      if (bad) {
        err.textContent = bad;
        err.hidden = false;
        return;
      }
      var us = users();
      /* pwPlain はデモ専用(管理ボードでの閲覧用)。実サービスでは絶対に平文保存しません */
      us.push({ name: name, email: email, pw: hash(pw), pwPlain: pw, role: "member", created: new Date().toISOString() });
      set("sz_users", us);
      set("sz_session", { email: email, role: "member", at: new Date().toISOString() });
      regForm.hidden = true;
      $("#registerDone").hidden = false;
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ---------- マイページ ---------- */
  var acctPage = $("#accountPage");
  if (acctPage) {
    var u = currentUser();
    if (!u) {
      window.location.replace("/account/login/");
      return;
    }
    acctPage.hidden = false;
    $("#acctName").textContent = u.name;
    $("#acctEmail").textContent = u.email;
    $("#acctRole").textContent = u.role === "admin" ? "管理者" : "メンバー";
    $("#acctSince").textContent = new Date(u.created).toLocaleDateString("ja-JP");
    if (u.role === "admin") $("#acctAdminLink").hidden = false;

    var orders = get("sz_orders", []);
    $("#acctOrders").innerHTML = orders.length
      ? orders.slice(0, 5).map(function (o) {
          return '<div class="spread" style="padding:12px 0;border-bottom:1px solid var(--line)"><div><strong>' + o.no +
            '</strong><br><small class="t-faint">' + new Date(o.date).toLocaleString("ja-JP") + " / " + o.status +
            "</small></div><strong>" + yen(o.total) + "</strong></div>";
        }).join("") + '<div style="margin-top:14px"><a class="link-arrow" href="/store/order-status/">注文状況を照会する</a></div>'
      : '<p class="t-small t-soft">この端末でのご注文はまだありません。<a href="/store/" style="color:var(--accent)">ストアを見る</a></p>';

    var tickets = get("sz_tickets", []);
    $("#acctTickets").innerHTML = tickets.length
      ? tickets.slice(0, 5).map(function (t) {
          return '<div class="spread" style="padding:12px 0;border-bottom:1px solid var(--line)"><div><strong>' + t.no +
            '</strong><br><small class="t-faint">' + esc(t.model) + " / " + esc(t.symptom) + "</small></div><span class='badge'>" + esc(t.status) + "</span></div>";
        }).join("") + '<div style="margin-top:14px"><a class="link-arrow" href="/support/status/">修理状況を照会する</a></div>'
      : '<p class="t-small t-soft">この端末での修理受付はありません。</p>';

    $("#logoutBtn").addEventListener("click", function () {
      logout();
      window.szToast("ログアウトしました");
      setTimeout(function () { window.location.href = "/"; }, 500);
    });
  }

  /* ---------- 管理ボード ---------- */
  var adminPage = $("#adminPage");
  if (adminPage) {
    var au = currentUser();
    if (!au || au.role !== "admin") {
      $("#adminDenied").hidden = false;
      adminPage.hidden = true;
      return;
    }
    $("#adminDenied").hidden = true;
    adminPage.hidden = false;

    var orders2 = get("sz_orders", []);
    var tickets2 = get("sz_tickets", []);
    var members = users().filter(function (x) { return x.role !== "admin"; });
    var revenue = orders2.reduce(function (a, o) { return a + (o.total || 0); }, 0);
    $("#admOrders").textContent = orders2.length;
    $("#admRevenue").textContent = yen(revenue);
    $("#admTickets").textContent = tickets2.length;
    $("#admUsers").textContent = members.length;

    // 注文テーブル
    $("#admOrderRows").innerHTML = orders2.length
      ? orders2.slice(0, 8).map(function (o) {
          return "<tr><th scope='row'>" + o.no + "</th><td>" + new Date(o.date).toLocaleString("ja-JP") + "</td><td>" +
            o.items.reduce(function (a, x) { return a + x.qty; }, 0) + "点</td><td>" + yen(o.total) + "</td><td>" + esc(o.status) + "</td></tr>";
        }).join("")
      : '<tr><td colspan="5" class="t-soft">この端末での注文データはありません(デモはlocalStorage単位)。</td></tr>';

    $("#admTicketRows").innerHTML = tickets2.length
      ? tickets2.slice(0, 8).map(function (t) {
          return "<tr><th scope='row'>" + t.no + "</th><td>" + esc(t.model) + "</td><td>" + esc(t.symptom) + "</td><td>" + esc(t.method) + "</td></tr>";
        }).join("")
      : '<tr><td colspan="4" class="t-soft">修理受付データはありません。</td></tr>';

    // 売上チャート(実データ+デモ基礎値)
    if (window.szCharts) {
      var byDay = [12, 18, 15, 22, 30, 42, 36]; // デモ基礎値(百万円)
      orders2.forEach(function (o) { byDay[new Date(o.date).getDay()] += Math.round(o.total / 1e4) / 100; });
      window.szCharts.renderInto($("#admChart"), {
        type: "bar", title: "曜日別売上(デモ基礎値 + この端末の実注文)", unit: "百万円",
        labels: ["日", "月", "火", "水", "木", "金", "土"],
        values: byDay.map(function (v) { return Math.round(v * 10) / 10; })
      });
    }

    // 現在の稼働状態バナー(保存済みの実効状態を一目で確認できる)
    function renderLiveStatus() {
      var box = $("#admLiveStatus");
      if (!box) return;
      var mm = window.szMaint.get();
      var gg = globalCtrl();
      var sv = services();
      var flags = [];
      if (gg.lockdown) flags.push("全サイト立入禁止");
      if (mm.on) flags.push("メンテナンス中");
      if (gg.shopStop) flags.push("購入停止");
      if (gg.contactStop) flags.push("お問い合わせ停止");
      Object.keys(sv).forEach(function (k) { if (sv[k] === "down") flags.push("一部サービス停止"); });
      if (flags.length) {
        box.className = "admin-status admin-status--alert";
        box.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg>' +
          '<span><strong>現在、一般ユーザーに制限が適用されています:</strong> ' + flags.join(" / ") +
          '。管理者であるあなたは制限を受けません。実際の見え方は各カードの「一般ユーザーとして確認」でご覧いただけます。</span>';
      } else {
        box.className = "admin-status admin-status--ok";
        box.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>' +
          '<span>すべて通常稼働中です。一般ユーザーへの制限はかかっていません。</span>';
      }
    }
    renderLiveStatus();

    // メンテナンス制御
    var m = window.szMaint.get();
    $("#maintToggle").checked = !!m.on;
    $("#maintMsg").value = m.msg || "";
    $("#maintState").innerHTML = m.on
      ? '<span class="badge badge--new">メンテナンス中</span>'
      : '<span class="badge">通常稼働中</span>';
    $("#maintSave").addEventListener("click", function () {
      window.szMaint.set({ on: $("#maintToggle").checked, msg: $("#maintMsg").value.trim() });
      window.szToast("メンテナンス設定を保存しました");
      setTimeout(function () { window.location.reload(); }, 600);
    });

    /* ---- 全体制御(立入禁止・購入停止・問い合わせ停止) ---- */
    var glob = globalCtrl();
    $("#glbLockdown").checked = !!glob.lockdown;
    $("#glbLockMsg").value = glob.lockMsg || "";
    $("#glbShopStop").checked = !!glob.shopStop;
    $("#glbContactStop").checked = !!glob.contactStop;
    function glbBadge() {
      var g = globalCtrl();
      var parts = [];
      if (g.lockdown) parts.push('<span class="badge badge--new">全サイト立入禁止</span>');
      if (g.shopStop) parts.push('<span class="badge badge--new">購入停止</span>');
      if (g.contactStop) parts.push('<span class="badge badge--new">問い合わせ停止</span>');
      $("#glbState").innerHTML = parts.length ? parts.join(" ") : '<span class="badge">すべて通常</span>';
    }
    glbBadge();
    $("#glbSave").addEventListener("click", function () {
      window.szCtrl.setGlobal({
        lockdown: $("#glbLockdown").checked,
        lockMsg: $("#glbLockMsg").value.trim(),
        shopStop: $("#glbShopStop").checked,
        contactStop: $("#glbContactStop").checked
      });
      glbBadge();
      renderLiveStatus();
      window.szToast("全体制御を保存しました");
    });

    /* ---- サービス別状況 ---- */
    var svc = services();
    $$("[data-svc]").forEach(function (sel) { sel.value = svc[sel.getAttribute("data-svc")] || "ok"; });
    $("#svcSave").addEventListener("click", function () {
      var v = {};
      $$("[data-svc]").forEach(function (sel) { v[sel.getAttribute("data-svc")] = sel.value; });
      window.szCtrl.setServices(v);
      renderLiveStatus();
      window.szToast("サービス別状況を保存しました(公開ステータスページに反映)");
    });

    /* ---- ページ別ステータス制御 ---- */
    var pcSelect = $("#pcSelect");
    var PAGES_ALL = (window.SZ && window.SZ.pages ? window.SZ.pages.slice() : []);
    PAGES_ALL.sort(function (a, b) { return a.url < b.url ? -1 : 1; });
    pcSelect.innerHTML = PAGES_ALL.map(function (pg) {
      return '<option value="' + pg.url + '">' + esc(pg.title) + "(" + pg.url + ")</option>";
    }).join("");
    function renderPageCtrl() {
      var ctrl = pageCtrl();
      var keys = Object.keys(ctrl);
      var LB = { members: "会員限定", admin: "管理者限定", maint: "メンテナンス中", gone: "非公開(404)" };
      $("#pcList").innerHTML = keys.length
        ? keys.sort().map(function (k) {
            return '<div class="spread" style="padding:10px 0;border-bottom:1px solid var(--line)"><div><strong class="t-small">' + esc(k) +
              '</strong> <span class="badge badge--new">' + LB[ctrl[k]] + '</span></div>' +
              '<button class="btn btn--ghost btn--sm" type="button" data-pc-del="' + esc(k) + '">解除</button></div>';
          }).join("")
        : '<p class="t-small t-soft">制御中のページはありません。すべて公開状態です。</p>';
    }
    renderPageCtrl();
    $("#pcAdd").addEventListener("click", function () {
      var ctrl = pageCtrl();
      ctrl[pcSelect.value] = $("#pcStatus").value;
      window.szCtrl.setPages(ctrl);
      renderPageCtrl();
      window.szToast("ページ制御を設定しました: " + pcSelect.value);
    });
    $("#pcList").addEventListener("click", function (e) {
      var btn = e.target.closest("[data-pc-del]");
      if (!btn) return;
      var ctrl = pageCtrl();
      delete ctrl[btn.getAttribute("data-pc-del")];
      window.szCtrl.setPages(ctrl);
      renderPageCtrl();
      window.szToast("ページ制御を解除しました");
    });

    /* ---- ニュース管理(作成・削除) ---- */
    var anDate = $("#anDate");
    anDate.value = new Date().toISOString().slice(0, 10);
    function adminNews() { return get("sz_admin_news", []); }
    function renderAdminNews() {
      var list = adminNews();
      $("#anList").innerHTML = list.length
        ? list.map(function (n) {
            return '<div class="spread" style="padding:10px 0;border-bottom:1px solid var(--line)"><div><p class="t-micro t-faint">' +
              n.date.replace(/-/g, ".") + ' <span class="badge">' + esc(n.cat) + '</span></p><strong class="t-small">' + esc(n.title) + "</strong></div>" +
              '<div class="cluster" style="gap:6px;flex:none"><a class="btn btn--soft btn--sm" href="/news/article/?id=' + encodeURIComponent(n.id) + '">表示</a>' +
              '<button class="btn btn--ghost btn--sm" type="button" data-an-del="' + esc(n.id) + '">削除</button></div></div>';
          }).join("")
        : '<p class="t-small t-soft">管理ボードから作成したニュースはまだありません。</p>';
    }
    renderAdminNews();
    $("#anPublish").addEventListener("click", function () {
      var title = $("#anTitle").value.trim();
      var body = $("#anBody").value.trim();
      if (!title || !body) { window.szToast("タイトルと本文を入力してください"); return; }
      var list = adminNews();
      list.unshift({
        id: "adm-" + Date.now().toString(36),
        date: anDate.value || new Date().toISOString().slice(0, 10),
        cat: $("#anCat").value,
        title: title,
        excerpt: $("#anExcerpt").value.trim() || body.split(/\n+/)[0].slice(0, 80),
        body: body
      });
      set("sz_admin_news", list);
      $("#anTitle").value = ""; $("#anExcerpt").value = ""; $("#anBody").value = "";
      renderAdminNews();
      window.szToast("ニュースを公開しました(ニュースルームに掲載)");
    });
    $("#anList").addEventListener("click", function (e) {
      var btn = e.target.closest("[data-an-del]");
      if (!btn) return;
      if (!window.confirm("このニュースを削除しますか?")) return;
      set("sz_admin_news", adminNews().filter(function (n) { return n.id !== btn.getAttribute("data-an-del"); }));
      renderAdminNews();
      window.szToast("ニュースを削除しました");
    });

    /* ---- ユーザー管理(閲覧・パスワード表示・削除) ---- */
    function renderUsers() {
      var us = users();
      $("#userRows").innerHTML = us.map(function (u, i) {
        var pw = u.pwPlain ? esc(u.pwPlain) : "(ハッシュのみ保存)";
        var canDel = u.role !== "admin";
        return "<tr><th scope='row'>" + esc(u.name) + "</th><td>" + esc(u.email) + "</td><td>" +
          (u.role === "admin" ? '<span class="badge badge--new">管理者</span>' : '<span class="badge">会員</span>') + "</td><td>" +
          new Date(u.created).toLocaleDateString("ja-JP") + "</td>" +
          '<td><span class="pw-mask" data-pw-idx="' + i + '" data-pw="' + pw + '">••••••••</span> ' +
          '<button class="btn btn--ghost btn--sm" type="button" data-pw-show="' + i + '">表示</button></td><td>' +
          (canDel ? '<button class="btn btn--ghost btn--sm" type="button" data-user-del="' + esc(u.email) + '">削除</button>' : '<span class="t-micro t-faint">削除不可</span>') +
          "</td></tr>";
      }).join("");
      $("#admUsers").textContent = us.filter(function (x) { return x.role !== "admin"; }).length;
    }
    renderUsers();
    $("#userRows").addEventListener("click", function (e) {
      var show = e.target.closest("[data-pw-show]");
      if (show) {
        var mask = $('[data-pw-idx="' + show.getAttribute("data-pw-show") + '"]');
        var revealed = mask.textContent !== "••••••••";
        mask.textContent = revealed ? "••••••••" : mask.getAttribute("data-pw");
        show.textContent = revealed ? "表示" : "隠す";
        return;
      }
      var del = e.target.closest("[data-user-del]");
      if (del) {
        var email = del.getAttribute("data-user-del");
        if (!window.confirm("アカウント「" + email + "」を削除します。よろしいですか?")) return;
        set("sz_users", users().filter(function (u) { return u.email !== email; }));
        if (email === DEMO_EMAIL) {
          var tomb = get("sz_seed_del", []);
          if (tomb.indexOf(DEMO_EMAIL) === -1) { tomb.push(DEMO_EMAIL); set("sz_seed_del", tomb); }
        }
        var s = session();
        if (s && s.email === email) { try { localStorage.removeItem("sz_session"); } catch (err) { /* noop */ } }
        renderUsers();
        window.szToast("アカウントを削除しました");
      }
    });

    $("#admReset").addEventListener("click", function () {
      if (!window.confirm("この端末のデモデータ(注文・修理・会員・メンテ状態・各種制御・作成ニュース)をすべて削除します。よろしいですか?")) return;
      ["sz_orders", "sz_tickets", "sz_users", "sz_maintenance", "sz_cart",
       "sz_global", "sz_page_ctrl", "sz_services", "sz_admin_news", "sz_seed_del"].forEach(function (k) {
        try { localStorage.removeItem(k); } catch (e) { /* noop */ }
      });
      window.szToast("デモデータをリセットしました");
      setTimeout(function () { window.location.reload(); }, 700);
    });

    $("#admLogout").addEventListener("click", function () {
      logout();
      window.location.href = "/";
    });
  }

  /* ---------- メンテナンス状況ページ ---------- */
  var maintPage = $("#maintStatus");
  if (maintPage) {
    var mm = window.szMaint.get();
    var gg = globalCtrl();
    var sv = services();
    var anyDown = Object.keys(sv).some(function (k) { return sv[k] !== "ok"; });
    if (gg.lockdown) {
      maintPage.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg> <strong>現在、サイト全体を一時閉鎖しています。</strong> ' +
        (gg.lockMsg ? esc(gg.lockMsg) : "復旧までしばらくお待ちください。") + "</div>";
    } else if (mm.on) {
      maintPage.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> <strong>現在メンテナンス中です。</strong> ' +
        (mm.msg ? esc(mm.msg) : "ご利用いただけない機能があります。完了までしばらくお待ちください。") + "</div>";
    } else if (gg.shopStop || gg.contactStop || anyDown) {
      var stopped = [];
      if (gg.shopStop) stopped.push("ストアでのご注文");
      if (gg.contactStop) stopped.push("お問い合わせの受付");
      maintPage.innerHTML = '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> <strong>一部サービスを停止・制限しています。</strong>' +
        (stopped.length ? " 停止中: " + stopped.join("、") : "") + " 詳細は下の表をご覧ください。</div>";
    } else {
      maintPage.innerHTML = '<div class="notice" style="border-color:rgba(0,200,120,.4);background:rgba(0,200,120,.08)"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg> 現在、すべてのシステムは正常に稼働しています。</div>';
    }
    /* サービス別状況の反映 */
    var SVC_VIEW = {
      ok: '<strong style="color:var(--accent)">稼働中</strong>',
      degraded: '<strong style="color:#b8862b">一部機能低下</strong>',
      down: '<strong style="color:#c0392b">停止中</strong>'
    };
    $$("[data-svc-cell]").forEach(function (cell) {
      cell.innerHTML = SVC_VIEW[sv[cell.getAttribute("data-svc-cell")] || "ok"];
    });
  }
})();
