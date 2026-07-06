/* ==========================================================================
   SUZAKU auth-guard.js — ヘッダー表示 / アクセス制御 / メンテ・お知らせバナー
   全ページで即時実行される(要素の有無に応じて各処理が自己判定する)。
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var get = function (k, f) { return window.szStore.get(k, f); };
  var set = function (k, v) { window.szStore.set(k, v); };
  var esc = window.szFmt.esc;

  var currentUser = window.szAuth.currentUser;
  var logout = window.szAuth.logout;
  var globalCtrl = window.szCtrl.global;
  var pageCtrl = window.szCtrl.pages;

  /* ---------- ヘッダーのアカウント表示 ---------- */
  var acctLink = $("#accountLink");
  var u0 = currentUser();
  if (acctLink && u0) {
    acctLink.setAttribute("href", u0.role === "admin" ? "/admin/" : "/account/");
    acctLink.setAttribute("aria-label", u0.name + " のアカウント");
    acctLink.classList.add("is-logged-in");
  }

  /* ログイン中は、どのページからでもログアウトできるよう
     ドロワー(モバイルメニュー)の項目を「マイページ」+「ログアウト」に切り替える。 */
  (function drawerAccount() {
    var drawerLogin = document.querySelector('.drawer a[href="/account/login/"]');
    if (!drawerLogin) return;
    if (u0) {
      drawerLogin.textContent = u0.role === "admin" ? "管理ボード / マイページ" : "マイページ";
      drawerLogin.setAttribute("href", u0.role === "admin" ? "/admin/" : "/account/");
      var lo = document.createElement("a");
      lo.className = "drawer__direct";
      lo.href = "#logout";
      lo.textContent = "ログアウト";
      lo.addEventListener("click", function (e) {
        e.preventDefault();
        logout();
        window.szToast("ログアウトしました");
        setTimeout(function () { window.location.href = "/"; }, 400);
      });
      drawerLogin.parentNode.insertBefore(lo, drawerLogin.nextSibling);
    }
  })();

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

  var BLOCK_ICON = {
    lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
    warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg>',
    wrench: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6L15 12l-3-3z"/></svg>',
    user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 20c1.5-3.5 4.5-5.5 8-5.5s6.5 2 8 5.5"/></svg>'
  };

  /* サイト制限をその場で表示するオーバーレイ(ページ遷移をせず、いま見ている
     ページ上に「閉鎖中」等を表示する)。締め出し感のある強制リダイレクトを避ける。 */
  function showBlockOverlay(opts) {
    if (document.querySelector(".site-block")) return;
    var ov = document.createElement("div");
    ov.className = "site-block";
    ov.setAttribute("role", "alertdialog");
    ov.setAttribute("aria-label", opts.title);
    ov.innerHTML =
      '<div class="site-block__card">' +
      '<div class="site-block__icon">' + (opts.icon || BLOCK_ICON.warn) + "</div>" +
      '<h1 class="t-h2">' + esc(opts.title) + "</h1>" +
      (opts.msg ? '<p class="t-soft">' + esc(opts.msg) + "</p>" : "") +
      (opts.actions ? '<div class="cluster cluster--center" style="margin-top:8px">' + opts.actions + "</div>" : "") +
      "</div>";
    document.body.appendChild(ov);
    document.body.classList.add("is-blocked");
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
      showBlockOverlay({
        icon: BLOCK_ICON.lock,
        title: "現在、サイトを一時閉鎖しています",
        msg: glob.lockMsg || "システムメンテナンスのため、一時的にすべてのページをご利用いただけません。再開までしばらくお待ちください。",
        actions: '<a class="btn btn--ghost" href="/maintenance/">稼働状況を見る</a>'
      });
      return;
    }
    if (!ctrl || alwaysOpen) return;
    if (ctrl === "gone" || ctrl === "admin") {
      showBlockOverlay({
        icon: BLOCK_ICON.warn,
        title: "このページはご覧いただけません",
        msg: "お探しのページは現在非公開に設定されています。時間をおいて再度お試しください。",
        actions: '<a class="btn btn--primary" href="/">ホームへ戻る</a><a class="btn btn--ghost" href="/search/">検索する</a>'
      });
    } else if (ctrl === "maint") {
      showBlockOverlay({
        icon: BLOCK_ICON.wrench,
        title: "このページはメンテナンス中です",
        msg: "ただいまこのページの更新作業を行っています。ご不便をおかけしますが、しばらくお待ちください。",
        actions: '<a class="btn btn--primary" href="/">ホームへ戻る</a><a class="btn btn--ghost" href="/maintenance/">稼働状況を見る</a>'
      });
    } else if (ctrl === "members" && !me0) {
      showBlockOverlay({
        icon: BLOCK_ICON.user,
        title: "会員限定ページです",
        msg: "このページをご覧いただくには、ログインが必要です。",
        actions: '<a class="btn btn--primary" href="/account/login/">ログイン</a><a class="btn btn--ghost" href="/account/register/">新規登録(無料)</a>'
      });
    }
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

  /* ---------- サイトお知らせバナー(メンテナンスとは別の告知) ---------- */
  (function announceBar() {
    var ann = get("sz_announce", { on: false, msg: "", kind: "info", link: "" });
    if (!ann.on || !ann.msg) return;
    if (path.indexOf("/admin") === 0) return;
    if (document.querySelector(".site-block")) return; // 閉鎖オーバーレイ時は出さない
    if (document.body.classList.contains("has-maint-bar")) return; // メンテバー優先
    var seen = get("sz_announce_seen", "");
    if (seen === ann.msg) return; // 同じ内容を閉じたら再表示しない
    var bar = document.createElement("div");
    bar.className = "announce-bar announce-bar--" + (ann.kind || "info");
    bar.setAttribute("role", "status");
    var inner = esc(ann.msg);
    if (ann.link) inner = '<a href="' + esc(ann.link) + '">' + inner + "</a>";
    bar.innerHTML = '<span>' + inner + "</span>" +
      '<button type="button" class="announce-bar__close" aria-label="閉じる"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>';
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add("has-announce-bar");
    var syncAnnH = function () {
      document.documentElement.style.setProperty("--announce-h", bar.offsetHeight + "px");
    };
    syncAnnH();
    window.addEventListener("resize", syncAnnH);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(syncAnnH);
    bar.querySelector(".announce-bar__close").addEventListener("click", function () {
      set("sz_announce_seen", ann.msg);
      bar.remove();
      document.body.classList.remove("has-announce-bar");
      document.documentElement.style.setProperty("--announce-h", "0px");
    });
  })();
})();
