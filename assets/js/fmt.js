/* ==========================================================================
   SUZAKU fmt.js — HTMLエスケープ・通貨表示の共通ヘルパー
   auth.js/store.js/charts.js/pages.js から重複定義を排除し、ここに一本化する。
   読み込み順の先頭(products.jsより前)に置くことで、以降の全JSから利用できる。
   ========================================================================== */
(function () {
  "use strict";

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function yen(n) { return "¥" + Math.round(n).toLocaleString("ja-JP"); }

  window.szFmt = { esc: esc, yen: yen };
})();
