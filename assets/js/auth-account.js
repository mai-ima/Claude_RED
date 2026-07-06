/* ==========================================================================
   SUZAKU auth-account.js — ログイン / 新規登録 / マイページ
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var get = function (k, f) { return window.szStore.get(k, f); };
  var set = function (k, v) { window.szStore.set(k, v); };
  var yen = window.szFmt.yen;
  var esc = window.szFmt.esc;

  var currentUser = window.szAuth.currentUser;
  var logout = window.szAuth.logout;
  var login = window.szAuth.login;
  var users = window.szAuth.users;
  var hash = window.szAuth.hash;

  var ADMIN_EMAIL = "admin@suzaku.example.jp";
  var DEMO_EMAIL = "user@suzaku.example.jp";
  var ADMIN_PW = "suzaku-admin";
  var DEMO_PW = "suzaku-user";

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
})();
