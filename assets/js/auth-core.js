/* ==========================================================================
   SUZAKU auth-core.js — ハッシュ / ユーザーストア / セッション / 全体制御
   szAuth・szCtrl の実体をここで定義する。auth-guard/account/admin/status は
   このファイルより後に読み込まれる前提(scripts/gen.pyの読み込み順で保証)。
   ========================================================================== */
(function () {
  "use strict";

  var get = function (k, f) { return window.szStore.get(k, f); };
  var set = function (k, v) { window.szStore.set(k, v); };

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
  /* サービス別状況を、管理者の設定(全体制御・メンテナンス)と同期させた
     「実効状態」に変換する。公開の稼働状況ページはこの実効状態を表示するため、
     立入禁止・購入停止・メンテナンスの設定が自動的にサービス状況へ反映される。 */
  function effectiveServices() {
    var sv = services();
    var g = globalCtrl();
    var m = get("sz_maintenance", { on: false });
    var out = {};
    for (var k in sv) out[k] = sv[k];
    if (m.on && out.store === "ok") out.store = "degraded";
    if (g.shopStop) out.store = "down";
    if (g.contactStop && out.repair === "ok") out.repair = "degraded";
    if (g.lockdown) { for (var k2 in out) out[k2] = "down"; }
    return out;
  }

  window.szCtrl = {
    global: globalCtrl,
    setGlobal: function (v) { set("sz_global", v); },
    pages: pageCtrl,
    setPages: function (v) { set("sz_page_ctrl", v); },
    services: services,
    effectiveServices: effectiveServices,
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

  window.szAuth = { currentUser: currentUser, logout: logout, login: login, users: users, hash: hash };
})();
