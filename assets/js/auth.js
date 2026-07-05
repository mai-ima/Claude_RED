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

  function users() { return get("sz_users", []); }

  function seedAdmin() {
    var us = users();
    if (!us.some(function (u) { return u.email === ADMIN_EMAIL; })) {
      us.push({ name: "SUZAKU 管理者", email: ADMIN_EMAIL, pw: hash("suzaku-admin"), role: "admin", created: "2022-05-01T00:00:00.000Z" });
      set("sz_users", us);
    }
  }
  seedAdmin();

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

  /* ---------- メンテナンスシステム ---------- */
  var maint = get("sz_maintenance", { on: false, msg: "" });
  var path = window.location.pathname;
  if (maint.on && path.indexOf("/admin") !== 0) {
    var bar = document.createElement("div");
    bar.className = "maint-bar";
    bar.setAttribute("role", "status");
    bar.innerHTML = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6L15 12l-3-3z"/></svg> ' +
      "ただいまメンテナンス中です。" + (maint.msg ? esc(maint.msg) + " " : "") +
      '<a href="/maintenance/">詳細</a>';
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add("has-maint-bar");
  }
  window.szMaint = {
    get: function () { return get("sz_maintenance", { on: false, msg: "" }); },
    set: function (v) { set("sz_maintenance", v); }
  };

  /* ---------- ログインページ ---------- */
  var loginForm = $("#loginForm");
  if (loginForm) {
    if (currentUser()) window.location.replace(currentUser().role === "admin" ? "/admin/" : "/account/");
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
      us.push({ name: name, email: email, pw: hash(pw), role: "member", created: new Date().toISOString() });
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

    $("#admReset").addEventListener("click", function () {
      if (!window.confirm("この端末のデモデータ(注文・修理・会員・メンテ状態)をすべて削除します。よろしいですか?")) return;
      ["sz_orders", "sz_tickets", "sz_users", "sz_maintenance", "sz_cart"].forEach(function (k) {
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
    maintPage.innerHTML = mm.on
      ? '<div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> <strong>現在メンテナンス中です。</strong> ' +
        (mm.msg ? esc(mm.msg) : "ご利用いただけない機能があります。完了までしばらくお待ちください。") + "</div>"
      : '<div class="notice" style="border-color:rgba(0,200,120,.4);background:rgba(0,200,120,.08)"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg> 現在、すべてのシステムは正常に稼働しています。</div>';
  }
})();
