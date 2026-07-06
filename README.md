# 朱雀 / SUZAKU — 架空ゲーミングデバイス企業 公式サイト

REDMAGICと同じ思想(自社シリコン・冷却技術・ゲーミング特化)を持つ架空の日本企業
「株式会社朱雀(SUZAKU Inc.)」のコーポレートサイトです。
2022年5月1日創業、2023年5月1日初製品発表という設定で、製品・技術・法人・開発者・
サポート・法務まで154ページをフル構成で実装しています。

**すべてのコンテンツ・企業・製品・数値はフィクションです。**

## 技術構成

- **静的HTML + CSS + JavaScript**(ビルド不要・外部ライブラリ0・外部画像0)
- Vercelにゼロ設定でデプロイ可能(`vercel.json` 同梱)
- ローカル確認: `python3 -m http.server 3000` → http://localhost:3000/

```
/
├── index.html ほか各ページ     # 生成物(ディレクトリ = ルート)
├── assets/
│   ├── css/   tokens / base / components / animations
│   ├── js/    keys(sz_*キー一元管理) / fmt(esc・yen共通ヘルパー) /
│   │          main(nav・Cookie同意・演出) / charts(SVGグラフ) / store(カート・購入) /
│   │          pages(FAQ・検索ほか) / auth-core・auth-guard・auth-account・
│   │          auth-admin・auth-status(認証・アクセス制御・管理ボード、責務ごとに分割)
│   └── img/   全SVG自動生成(製品画像・ダイアグラム)
├── data/products.js            # クライアント用データ(自動生成)
├── src/pages/                  # フラグメント(本文のみのHTML+METAコメント)
└── scripts/
    ├── gen.py                  # 静的サイトジェネレータ(このリポジトリの心臓)
    ├── data_products.py        # 製品データ(単一ソース)
    ├── data_tech.py            # 技術・OSデータ
    ├── data_misc.py            # ニュース・FAQ・沿革
    ├── svg_art.py              # SVGアート生成
    └── check_links.py          # リンク切れ検査
```

## ページの編集・再生成

```bash
# データやフラグメントを編集したら再生成
python3 scripts/gen.py

# リンク切れ0を検証
python3 scripts/check_links.py
```

- 製品・価格・スペック・ニュースは `scripts/data_*.py` の単一ソースから、
  製品ページ / specsページ / ストア / 比較 / 検索 / チャートすべてに供給されます。
- 固有ページ(ホーム・ストア・サポート等)は `src/pages/` のフラグメントを編集します。
  先頭の `<!--META {...} -->` でタイトル・説明・テーマ(dark/light)・パンくずを指定します。

## 実動作するモック機能(すべてlocalStorage完結)

Cookie同意バナー(カテゴリ別設定) / カート / 多段チェックアウト(Luhn検証・
支払方法・配送日時指定・注文番号発行) / 注文照会 / 修理受付と照会 / 比較ツール
(スペック表+レーダーチャート) / FAQ検索 / ニュースフィルタ / サイト内検索 /
各種お問い合わせフォーム / SVGチャート(棒・折れ線・レーダー・ドーナツ、表フォールバック付き) /
アカウント・ログイン / メンテナンスシステム / サイトお知らせバナー / 表示設定(`/settings/`)

### 管理ボード(`/admin/`)

WAI-ARIA Tabsパターン(自動アクティベーション・roving tabindex・矢印キー/Home/End
操作対応)によるタブ構成で、以下の機能を提供する:

- **概要**: クイック操作・曜日別売上チャート・操作履歴(監査ログ)
- **稼働制御**: メンテナンスモード / 全体制御(立入禁止・購入停止・問い合わせ停止) /
  サービス別状況
- **ページ制御**: 個別ページを会員限定・管理者限定・メンテナンス中・非公開(404)に設定
- **ニュース**: 作成・削除(公開すると `/news/` 一覧と専用記事ページに反映)
- **サイト**: お知らせバナー設定・ストア設定(送料無料しきい値・配送料)
- **会員**: 追加・検索・権限変更・パスワード表示・削除
- **分析**: 会員登録推移・権限内訳のチャート
- **記録・ツール**: 注文/修理のステータス変更、データのバックアップ(書き出し/
  読み込み)・デモデータのリセット

バックアップ・リセット対象の `sz_*` キー一覧は `assets/js/keys.js` の
`window.szKeys` に一元管理されており、機能追加時にここへ1箇所追記するだけで
バックアップ・リセットの両方に反映される。

### 表示設定システム(`window.szPrefs`)

`assets/js/main.js` の `PREF_SCHEMA` が単一ソース。項目を追加するには
`{ default, apply }` を1行足すだけでよく、`applyPrefs()` が全項目を
`<html>` の `data-*` 属性へ自動反映する(個別配線は不要)。現在の項目:
`footerMode`(フッターの折りたたみ/常時展開)・`density`(文字とUIの大きさ)・
`motion`(アニメーション低減)。設定は `sz_prefs`(localStorage)に保存される。
設定ページ(`src/pages/settings.html`)側は `data-pref` / `data-pref-value`
属性だけで動く汎用配線のため、HTMLにグループを追加するだけで新項目に対応できる。

### カラーテーマの単一ソース

テーマ選択肢は `scripts/gen.py` の `THEME_OPTS` にのみ定義し、
ヘッダーのドロップダウン(`theme_menu_buttons()`)とドロワーの
セグメント切替(`theme_seg_buttons()`)を同じ配列から生成する。
テーマを追加・変更する場合は `THEME_OPTS` だけを編集すればよい。

### キャッシュバスティング

`scripts/gen.py` はビルド時に `assets/css`・`assets/js`・`scripts/data_*.py`
(`/data/products.js` の生成元)の内容ハッシュ(`ASSET_V`)を計算し、全
`<link>` / `<script>` に `?v=<hash>` を付与する。資産やデータが変わるたびに
URLが変わるため、CDN・ブラウザの古いキャッシュを確実に回避できる
(`vercel.json` の `/assets/` は `immutable` で長期キャッシュ)。
利用者は Cookie設定ページ(`/legal/cookie/`)からキャッシュを手動削除もできる。

## Next.js(App Router)への移行ガイド

本サイトは後日のNext.js移行を想定した構造になっています。

1. **ルーティング**: ディレクトリ構造がそのまま App Router に対応します。
   `/products/phone/suzaku-4/index.html` → `app/products/phone/suzaku-4/page.tsx`
2. **データ**: `scripts/data_*.py` の内容を `lib/data.ts` へ移植(構造はJSONそのまま)。
   製品ページ群は `generateStaticParams` による動的ルート1本に集約できます。
3. **スタイル**: `assets/css/tokens.css` のCSS変数を `globals.css` にそのままコピー。
   コンポーネントCSSはBEM風クラスのため、CSS Modulesへの分割が機械的に可能です。
4. **共通UI**: ヘッダー / フッター / Cookie同意 / 製品カードは全ページ同一マークアップ
   (`scripts/gen.py` の `header_html()` / `footer_html()` / `product_card()`)なので、
   そのままReactコンポーネント化できます。
5. **JS**: `charts.js` / `store.js` / `pages.js` は依存0のバニラJSのため、
   `"use client"` コンポーネントのフックへ段階的に移行できます。

## デプロイ(Vercel)

リポジトリをVercelにインポートするだけで公開できます(Framework Preset: Other)。
`vercel.json` でクリーンURL・キャッシュ・セキュリティヘッダを設定済みです。
`src/`・`scripts/`・`docs/`(内部監査メモ)は `.vercelignore` により配信対象
から除外されます。
