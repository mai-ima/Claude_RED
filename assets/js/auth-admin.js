/* ==========================================================================
   SUZAKU auth-admin.js — 管理ボード(稼働制御・ページ制御・ニュース・サイト設定・
   会員管理・分析・バックアップ)
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var get = function (k, f) { return window.szStore.get(k, f); };
  var set = function (k, v) { window.szStore.set(k, v); };
  var yen = window.szFmt.yen;
  var esc = window.szFmt.esc;

  var currentUser = window.szAuth.currentUser;
  var logout = window.szAuth.logout;
  var users = window.szAuth.users;
  var hash = window.szAuth.hash;
  var globalCtrl = window.szCtrl.global;
  var pageCtrl = window.szCtrl.pages;
  var services = window.szCtrl.services;
  function session() { return get("sz_session", null); }

  var DEMO_EMAIL = "user@suzaku.example.jp";

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

    /* タブ切替(スマートフォンで縦に長くなりすぎないよう機能を分割) */
    var adminTabs = $("#adminTabs");
    if (adminTabs) {
      adminTabs.addEventListener("click", function (e) {
        var t = e.target.closest("[data-admin-tab]");
        if (!t) return;
        var name = t.getAttribute("data-admin-tab");
        $$(".admin-tab", adminPage).forEach(function (b) {
          b.classList.toggle("is-active", b === t);
          b.setAttribute("aria-selected", String(b === t));
        });
        $$(".admin-panel", adminPage).forEach(function (p) {
          p.hidden = p.getAttribute("data-admin-panel") !== name;
        });
      });
    }

    var orders2 = get("sz_orders", []);
    var tickets2 = get("sz_tickets", []);
    var members = users().filter(function (x) { return x.role !== "admin"; });
    var revenue = orders2.reduce(function (a, o) { return a + (o.total || 0); }, 0);
    $("#admOrders").textContent = orders2.length;
    $("#admRevenue").textContent = yen(revenue);
    $("#admTickets").textContent = tickets2.length;
    $("#admUsers").textContent = members.length;

    /* ---- 操作履歴(監査ログ) ---- */
    function adminLog() { return get("sz_admin_log", []); }
    function logAction(text) {
      var log = adminLog();
      log.unshift({ t: text, at: new Date().toISOString() });
      set("sz_admin_log", log.slice(0, 60));
      renderActivity();
    }
    function renderActivity() {
      var box = $("#admActivity");
      if (!box) return;
      var log = adminLog();
      box.innerHTML = log.length
        ? log.slice(0, 12).map(function (e) {
            return '<div class="activity-log__row"><span>' + esc(e.t) + '</span><span class="t-micro t-faint">' + new Date(e.at).toLocaleString("ja-JP") + "</span></div>";
          }).join("")
        : '<p class="t-small t-soft">まだ操作履歴はありません。</p>';
    }
    renderActivity();

    /* ---- クイック操作(ログアウトもここから) ---- */
    (function renderQuick() {
      var box = $("#admQuick");
      if (!box) return;
      var mOn = window.szMaint.get().on;
      box.innerHTML =
        '<button class="btn btn--' + (mOn ? "primary" : "soft") + ' btn--sm" id="qkMaint" type="button">' + (mOn ? "メンテナンスを解除" : "メンテナンスを開始") + "</button>" +
        '<a class="btn btn--soft btn--sm" href="/?preview=user" target="_blank" rel="noopener">一般ユーザーとして確認</a>' +
        '<button class="btn btn--soft btn--sm" id="qkNews" type="button">ニュースを作成</button>' +
        '<button class="btn btn--ghost btn--sm" id="qkLogout" type="button">ログアウト</button>';
      $("#qkMaint").addEventListener("click", function () {
        var m = window.szMaint.get();
        window.szMaint.set({ on: !m.on, msg: m.msg || "" });
        logAction(!m.on ? "メンテナンスを開始しました" : "メンテナンスを解除しました");
        window.szToast("メンテナンスを" + (!m.on ? "開始" : "解除") + "しました");
        setTimeout(function () { window.location.reload(); }, 600);
      });
      $("#qkNews").addEventListener("click", function () {
        var t = $('[data-admin-tab="news"]');
        if (t) t.click();
        var f = $("#anTitle");
        if (f) f.focus();
      });
      $("#qkLogout").addEventListener("click", function () {
        logout();
        window.szToast("ログアウトしました");
        setTimeout(function () { window.location.href = "/"; }, 400);
      });
    })();

    /* ---- 注文テーブル(ステータス変更可) ---- */
    var ORDER_STAGES = (window.szStages && window.szStages.order) || [];
    function renderOrderRows() {
      var orders = get("sz_orders", []);
      $("#admOrderRows").innerHTML = orders.length
        ? orders.slice(0, 12).map(function (o, i) {
            var reached = typeof o.statusIdx === "number" ? o.statusIdx : 0;
            var opts = ORDER_STAGES.map(function (s, k) {
              return '<option value="' + k + '"' + (k === reached ? " selected" : "") + ">" + esc(s) + "</option>";
            }).join("");
            var sel = o.cancelled
              ? '<span class="badge badge--new">キャンセル</span>'
              : '<select class="select select--mini" data-order-idx="' + i + '">' + opts + "</select>";
            var cancelBtn = o.cancelled ? "" : ' <button class="btn btn--ghost btn--sm" type="button" data-order-cancel="' + i + '">取消</button>';
            return "<tr><th scope='row'>" + o.no + "</th><td>" + new Date(o.date).toLocaleString("ja-JP") + "</td><td>" +
              o.items.reduce(function (a, x) { return a + x.qty; }, 0) + "点</td><td>" + yen(o.total) + "</td><td>" + sel + cancelBtn + "</td></tr>";
          }).join("")
        : '<tr><td colspan="5" class="t-soft">この端末での注文データはありません(デモはlocalStorage単位)。</td></tr>';
    }
    renderOrderRows();
    $("#admOrderRows").addEventListener("change", function (e) {
      var sel = e.target.closest("[data-order-idx]");
      if (!sel) return;
      var orders = get("sz_orders", []);
      var i = +sel.getAttribute("data-order-idx");
      if (!orders[i]) return;
      orders[i].statusIdx = +sel.value;
      orders[i].status = ORDER_STAGES[+sel.value];
      set("sz_orders", orders);
      logAction("注文 " + orders[i].no + " を「" + ORDER_STAGES[+sel.value] + "」に更新");
      window.szToast("注文ステータスを更新しました(照会画面に反映)");
    });
    $("#admOrderRows").addEventListener("click", function (e) {
      var btn = e.target.closest("[data-order-cancel]");
      if (!btn) return;
      if (!window.confirm("この注文をキャンセル扱いにしますか?")) return;
      var orders = get("sz_orders", []);
      var i = +btn.getAttribute("data-order-cancel");
      if (!orders[i]) return;
      orders[i].cancelled = true;
      orders[i].status = "キャンセル";
      set("sz_orders", orders);
      logAction("注文 " + orders[i].no + " をキャンセル");
      renderOrderRows();
      window.szToast("注文をキャンセルしました");
    });

    /* ---- 修理テーブル(ステータス変更可) ---- */
    var REPAIR_STAGES = (window.szStages && window.szStages.repair) || [];
    function renderTicketRows() {
      var tickets = get("sz_tickets", []);
      $("#admTicketRows").innerHTML = tickets.length
        ? tickets.slice(0, 12).map(function (t, i) {
            var reached = typeof t.statusIdx === "number" ? t.statusIdx : 0;
            var opts = REPAIR_STAGES.map(function (s, k) {
              return '<option value="' + k + '"' + (k === reached ? " selected" : "") + ">" + esc(s) + "</option>";
            }).join("");
            return "<tr><th scope='row'>" + t.no + "</th><td>" + esc(t.model) + "</td><td>" + esc(t.symptom) +
              '</td><td><select class="select select--mini" data-ticket-idx="' + i + '">' + opts + "</select></td></tr>";
          }).join("")
        : '<tr><td colspan="4" class="t-soft">修理受付データはありません。</td></tr>';
    }
    renderTicketRows();
    $("#admTicketRows").addEventListener("change", function (e) {
      var sel = e.target.closest("[data-ticket-idx]");
      if (!sel) return;
      var tickets = get("sz_tickets", []);
      var i = +sel.getAttribute("data-ticket-idx");
      if (!tickets[i]) return;
      tickets[i].statusIdx = +sel.value;
      tickets[i].status = REPAIR_STAGES[+sel.value];
      set("sz_tickets", tickets);
      logAction("修理 " + tickets[i].no + " を「" + REPAIR_STAGES[+sel.value] + "」に更新");
      window.szToast("修理ステータスを更新しました(照会画面に反映)");
    });

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
      var on = $("#maintToggle").checked;
      window.szMaint.set({ on: on, msg: $("#maintMsg").value.trim() });
      logAction("メンテナンスを" + (on ? "開始" : "解除"));
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
      logAction("全体制御を更新(立入禁止:" + ($("#glbLockdown").checked ? "ON" : "OFF") +
        " / 購入停止:" + ($("#glbShopStop").checked ? "ON" : "OFF") +
        " / 問い合わせ停止:" + ($("#glbContactStop").checked ? "ON" : "OFF") + ")");
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
      logAction("サービス別状況を更新");
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
      logAction("ページ制御を設定: " + pcSelect.value + " → " + $("#pcStatus").value);
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
      logAction("ニュースを公開: " + title);
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
    var userQuery = "";
    function adminCount() { return users().filter(function (x) { return x.role === "admin"; }).length; }
    function renderUsers() {
      var us = users().filter(function (u) {
        if (!userQuery) return true;
        return (u.name + " " + u.email).toLowerCase().indexOf(userQuery) !== -1;
      });
      $("#userRows").innerHTML = us.length ? us.map(function (u) {
        var pw = u.pwPlain ? esc(u.pwPlain) : "(ハッシュのみ保存)";
        var isAdmin = u.role === "admin";
        var lastAdmin = isAdmin && adminCount() <= 1;
        var roleBtn = isAdmin
          ? '<button class="btn btn--ghost btn--sm" type="button" data-user-role="' + esc(u.email) + '" data-to="member"' + (lastAdmin ? " disabled title=\"最後の管理者は変更できません\"" : "") + ">メンバーに</button>"
          : '<button class="btn btn--ghost btn--sm" type="button" data-user-role="' + esc(u.email) + '" data-to="admin">管理者に</button>';
        var delBtn = (isAdmin && lastAdmin)
          ? '<span class="t-micro t-faint">削除不可</span>'
          : '<button class="btn btn--ghost btn--sm" type="button" data-user-del="' + esc(u.email) + '">削除</button>';
        return "<tr><th scope='row'>" + esc(u.name) + "</th><td>" + esc(u.email) + "</td><td>" +
          (isAdmin ? '<span class="badge badge--new">管理者</span>' : '<span class="badge">会員</span>') + "</td><td>" +
          new Date(u.created).toLocaleDateString("ja-JP") + "</td>" +
          '<td><span class="pw-mask" data-pw="' + pw + '">••••••••</span> ' +
          '<button class="btn btn--ghost btn--sm" type="button" data-pw-show>表示</button></td>' +
          '<td><span class="cluster" style="gap:6px">' + roleBtn + delBtn + "</span></td></tr>";
      }).join("") : '<tr><td colspan="6" class="t-soft">該当する会員がいません。</td></tr>';
      $("#admUsers").textContent = users().filter(function (x) { return x.role !== "admin"; }).length;
    }
    renderUsers();
    var userSearch = $("#userSearch");
    if (userSearch) userSearch.addEventListener("input", function () { userQuery = userSearch.value.trim().toLowerCase(); renderUsers(); });

    /* 会員を追加 */
    var auAdd = $("#auAdd");
    if (auAdd) {
      auAdd.addEventListener("click", function () {
        var name = $("#auName").value.trim();
        var email = $("#auEmail").value.trim().toLowerCase();
        var pw = $("#auPw").value;
        var role = $("#auRole").value;
        var err = $("#auError");
        var bad = "";
        if (!name) bad = "お名前を入力してください。";
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) bad = "メールアドレスの形式が正しくありません。";
        else if (pw.length < 8) bad = "パスワードは8文字以上で設定してください。";
        else if (users().some(function (x) { return x.email === email; })) bad = "このメールアドレスは既に登録されています。";
        if (bad) { err.textContent = bad; err.style.display = "block"; return; }
        err.style.display = "none";
        var us = users();
        us.push({ name: name, email: email, pw: hash(pw), pwPlain: pw, role: role, created: new Date().toISOString() });
        set("sz_users", us);
        $("#auName").value = ""; $("#auEmail").value = ""; $("#auPw").value = "";
        renderUsers();
        logAction("会員 " + email + " を追加(" + (role === "admin" ? "管理者" : "メンバー") + ")");
        window.szToast("会員を追加しました");
      });
    }

    $("#userRows").addEventListener("click", function (e) {
      var show = e.target.closest("[data-pw-show]");
      if (show) {
        var mask = show.closest("td").querySelector(".pw-mask");
        var revealed = mask.textContent !== "••••••••";
        mask.textContent = revealed ? "••••••••" : mask.getAttribute("data-pw");
        show.textContent = revealed ? "表示" : "隠す";
        return;
      }
      var role = e.target.closest("[data-user-role]");
      if (role) {
        var em = role.getAttribute("data-user-role");
        var to = role.getAttribute("data-to");
        var us = users();
        var target = us.filter(function (u) { return u.email === em; })[0];
        if (!target) return;
        if (target.role === "admin" && to === "member" && adminCount() <= 1) { window.szToast("最後の管理者は変更できません"); return; }
        target.role = to;
        set("sz_users", us);
        var s0 = session();
        if (s0 && s0.email === em) { s0.role = to; set("sz_session", s0); }
        renderUsers();
        logAction("会員 " + em + " の権限を" + (to === "admin" ? "管理者" : "メンバー") + "に変更");
        window.szToast("権限を変更しました");
        return;
      }
      var del = e.target.closest("[data-user-del]");
      if (del) {
        var email = del.getAttribute("data-user-del");
        var t2 = users().filter(function (u) { return u.email === email; })[0];
        if (t2 && t2.role === "admin" && adminCount() <= 1) { window.szToast("最後の管理者は削除できません"); return; }
        if (!window.confirm("アカウント「" + email + "」を削除します。よろしいですか?")) return;
        set("sz_users", users().filter(function (u) { return u.email !== email; }));
        if (email === DEMO_EMAIL) {
          var tomb = get("sz_seed_del", []);
          if (tomb.indexOf(DEMO_EMAIL) === -1) { tomb.push(DEMO_EMAIL); set("sz_seed_del", tomb); }
        }
        var s = session();
        if (s && s.email === email) { try { localStorage.removeItem("sz_session"); } catch (err) { /* noop */ } }
        renderUsers();
        logAction("会員 " + email + " を削除");
        window.szToast("アカウントを削除しました");
      }
    });

    /* ---- 分析 ---- */
    (function renderAnalytics() {
      var us = users();
      var orders = get("sz_orders", []);
      var news = adminNews();
      $("#anaMembers").textContent = us.filter(function (x) { return x.role !== "admin"; }).length;
      $("#anaOrders").textContent = orders.length;
      var rev = orders.reduce(function (a, o) { return a + (o.total || 0); }, 0);
      $("#anaAov").textContent = yen(orders.length ? rev / orders.length : 0);
      $("#anaNews").textContent = news.length;
      if (!window.szCharts) return;
      // 会員登録の月別推移(直近6か月)
      var labels = [], counts = [];
      var now = new Date();
      for (var m = 5; m >= 0; m--) {
        var d = new Date(now.getFullYear(), now.getMonth() - m, 1);
        labels.push((d.getMonth() + 1) + "月");
        var key = d.getFullYear() + "-" + d.getMonth();
        counts.push(us.filter(function (u) {
          var c = new Date(u.created);
          return c.getFullYear() + "-" + c.getMonth() === key;
        }).length);
      }
      window.szCharts.renderInto($("#anaMemberChart"), {
        type: "line", title: "会員登録数(月別)", unit: "人", area: true, labels: labels,
        series: [{ name: "新規登録", values: counts }]
      });
      var adminN = us.filter(function (x) { return x.role === "admin"; }).length;
      var memberN = us.length - adminN;
      window.szCharts.renderInto($("#anaRoleChart"), {
        type: "donut", title: "権限の内訳", value: memberN, max: us.length || 1, unit: "人", label: "会員"
      });
    })();

    /* ---- サイトお知らせバナー設定 ---- */
    var ann0 = get("sz_announce", { on: false, msg: "", kind: "info", link: "" });
    if ($("#annOn")) {
      $("#annOn").checked = !!ann0.on;
      $("#annMsg").value = ann0.msg || "";
      $("#annKind").value = ann0.kind || "info";
      $("#annLink").value = ann0.link || "";
      var annBadge = function () {
        var a = get("sz_announce", { on: false });
        $("#annState").innerHTML = a.on ? '<span class="badge badge--new">表示中</span>' : '<span class="badge">非表示</span>';
      };
      annBadge();
      $("#annSave").addEventListener("click", function () {
        var v = { on: $("#annOn").checked, msg: $("#annMsg").value.trim(), kind: $("#annKind").value, link: $("#annLink").value.trim() };
        set("sz_announce", v);
        try { localStorage.removeItem("sz_announce_seen"); } catch (e) { /* noop */ } // 新しい内容は再表示
        annBadge();
        logAction("お知らせバナーを" + (v.on ? "表示ON" : "非表示"));
        window.szToast("お知らせバナーを保存しました");
      });
    }

    /* ---- ストア設定(送料) ---- */
    var cfg0 = get("sz_store_cfg", {});
    if ($("#cfgFree")) {
      var defFree = (window.SZ && window.SZ.freeShipping) || 5000;
      var defShip = (window.SZ && window.SZ.shippingFee) || 550;
      $("#cfgFree").value = typeof cfg0.freeShipping === "number" ? cfg0.freeShipping : defFree;
      $("#cfgShip").value = typeof cfg0.shippingFee === "number" ? cfg0.shippingFee : defShip;
      $("#cfgSave").addEventListener("click", function () {
        var free = parseInt($("#cfgFree").value, 10);
        var ship = parseInt($("#cfgShip").value, 10);
        if (isNaN(free) || free < 0 || isNaN(ship) || ship < 0) { window.szToast("正しい金額を入力してください"); return; }
        set("sz_store_cfg", { freeShipping: free, shippingFee: ship });
        logAction("ストア設定を更新(送料無料 " + free + "円 / 送料 " + ship + "円)");
        window.szToast("ストア設定を保存しました(カートに反映)");
      });
    }

    /* ---- バックアップ(エクスポート/インポート) ---- */
    var BACKUP_KEYS = window.szKeys.BACKUP;
    var admExport = $("#admExport");
    if (admExport) {
      admExport.addEventListener("click", function () {
        var dump = { _app: "SUZAKU-admin-backup", _at: new Date().toISOString() };
        BACKUP_KEYS.forEach(function (k) {
          try { var v = localStorage.getItem(k); if (v !== null) dump[k] = JSON.parse(v); } catch (e) { /* noop */ }
        });
        var blob = new Blob([JSON.stringify(dump, null, 2)], { type: "application/json" });
        var a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "suzaku-backup-" + new Date().toISOString().slice(0, 10) + ".json";
        a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
        $("#admBackupMsg").textContent = "バックアップを書き出しました。";
        logAction("データをエクスポート");
      });
    }
    var admImportFile = $("#admImportFile");
    if (admImportFile) {
      admImportFile.addEventListener("change", function () {
        var file = admImportFile.files && admImportFile.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function () {
          var data;
          try { data = JSON.parse(reader.result); } catch (e) { $("#admBackupMsg").textContent = "読み込みに失敗しました(JSON形式ではありません)。"; return; }
          if (!data || data._app !== "SUZAKU-admin-backup") { $("#admBackupMsg").textContent = "SUZAKUのバックアップファイルではありません。"; return; }
          if (!window.confirm("現在のデータをこのバックアップで置き換えます。よろしいですか?")) { admImportFile.value = ""; return; }
          BACKUP_KEYS.forEach(function (k) {
            if (Object.prototype.hasOwnProperty.call(data, k)) set(k, data[k]);
          });
          logAction("データをインポート(復元)");
          window.szToast("バックアップを復元しました");
          setTimeout(function () { window.location.reload(); }, 700);
        };
        reader.readAsText(file);
      });
    }

    $("#admReset").addEventListener("click", function () {
      if (!window.confirm("この端末のデモデータ(注文・修理・会員・メンテ状態・各種制御・作成ニュース)をすべて削除します。よろしいですか?")) return;
      window.szKeys.RESET.forEach(function (k) {
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
})();
