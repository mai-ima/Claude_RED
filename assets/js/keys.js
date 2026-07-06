/* ==========================================================================
   SUZAKU keys.js — localStorage(sz_*)キーの一元管理レジストリ
   バックアップ対象・リセット対象のキー一覧がファイルごとに個別ハードコードされ
   ズレていく問題を防ぐため、真実の情報源をここに集約する。
   読み込み順の先頭(products.jsより前)に置く。
   ========================================================================== */
(function () {
  "use strict";

  var PREF = ["sz_theme", "sz_prefs", "sz_consent"];
  var DATA = ["sz_users", "sz_orders", "sz_tickets", "sz_maintenance", "sz_global",
    "sz_page_ctrl", "sz_services", "sz_admin_news", "sz_seed_del",
    "sz_announce", "sz_store_cfg", "sz_admin_log"];
  var VOLATILE = ["sz_cart", "sz_announce_seen"];

  /* sz_session は意図的に含めない(ログアウトは logout() で個別削除する) */
  window.szKeys = {
    PREF: PREF,
    DATA: DATA,
    VOLATILE: VOLATILE,
    BACKUP: DATA.slice(),
    RESET: DATA.concat(VOLATILE)
  };
})();
