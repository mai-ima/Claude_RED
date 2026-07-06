/* ==========================================================================
   SUZAKU auth-status.js — /maintenance/ 公開稼働状況ページ
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = window.szFmt.esc;
  var globalCtrl = window.szCtrl.global;
  var effectiveServices = window.szCtrl.effectiveServices;

  /* ---------- メンテナンス状況ページ ---------- */
  var maintPage = $("#maintStatus");
  if (maintPage) {
    var mm = window.szMaint.get();
    var gg = globalCtrl();
    var sv = effectiveServices(); // 管理設定(立入禁止・購入停止・メンテ)と同期した実効状態
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
