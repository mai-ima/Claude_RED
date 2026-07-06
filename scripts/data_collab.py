# -*- coding: utf-8 -*-
"""SUZAKU サイト単一ソースデータ — ゲームコラボ特設。

ここがコラボ特設の「唯一の真実の源」。色を変える=tokens を1行編集、
UIを変える=gen.py の build_collab_page() テンプレートを1箇所編集、で全コラボに反映される。
本コラボ企画・製品はすべて架空のデモであり、実在の販売を行うものではありません。

各エントリのフィールド:
  slug        … URL とCSSクラス(/collab/{slug}/ ・ .collab--{slug})
  game/studio … 実在ゲーム名・開発元(コラボ相手)
  active      … True で特設LP・製品を生成。False はハブに「近日公開」表示のみ
  motif       … 装飾バリアント(fantasy / techwear / neon / industrial)
  tokens      … 配色トークン。CSS変数 --cl-* としてページに注入され collab.css を駆動
  edition     … コラボ限定エディション名
  hero        … 没入ヒーローの文言
  phone_id / accessory_ids … data_products.py 側の製品ID(特設から自動で引く)
  limited     … 期間限定(until)・数量限定(qty/sold)
  world       … 作品世界観の短い導入文(没入用)
  highlights  … 訴求ポイント(title/body)
  bundle      … 同梱バンドル(title/desc)
  gallery     … ギャラリーの各タイル見出し(SVGはトークンから自動生成)
  note        … 架空デモである旨の注記
"""

COLLABS = [
    {
        "slug": "genshin", "game": "原神", "studio": "HoYoverse",
        "active": True, "motif": "fantasy",
        "tokens": {
            "bg": "#0f1a17", "bg2": "#152521", "ink": "#f5efe0", "soft": "#c7d3c9",
            "accent": "#2fb9a3", "accent2": "#e5c07b", "line": "rgba(229,192,123,.28)",
            "glow": "#2fb9a3",
        },
        "edition": "SUZAKU 4 × 原神 元素の頂 Edition",
        "hero": {
            "eyebrow": "SUZAKU × 原神 — LIMITED COLLABORATION",
            "title": "七つの元素が、<br>手のひらの頂に宿る。",
            "lead": "テイワットの旅を、史上最高性能のSUZAKUで。元素の輝きをまとった数量限定エディション。",
            "tagline": "元素の頂 Edition",
        },
        "phone_id": "suzaku-4-genshin", "accessory_ids": ["pb-genshin"],
        "limited": {"until": "2026-08-31T23:59:59", "qty": 8000, "sold": 5240},
        "world": "空高くそびえる大地テイワット。七つの元素と、旅の途上で出会う無数の物語。その世界の輝きを、一台のフラッグシップに封じ込めました。",
        "highlights": [
            {"title": "元素グラデーションの背面", "body": "七元素の色をまとった専用ガラス背面。光の角度で色相が移ろう蒸着コーティングを、コラボ限定色として用意しました。"},
            {"title": "特別選別チップ「RAI-G4 元素選別版」", "body": "歩留まり上位の個体のみを選別した特別ビン。最大3.9GHz、AnTuTu 405万点。史上最高性能をこのエディションだけに。"},
            {"title": "テイワット・テーマパック", "body": "SUZAKU OS「陣」に、専用ロック画面・アイコン・起動音・ダイナミック壁紙を収録した限定テーマを同梱。"},
        ],
        "bundle": [
            {"title": "限定ギフトコード", "desc": "ゲーム内アイテムの引き換えコード(デモ表記)を同梱。"},
            {"title": "元素の頂 専用ケース", "desc": "コラボ意匠の保護ケースを標準同梱。"},
            {"title": "コレクターズボックス", "desc": "収納・展示できる限定パッケージ。"},
            {"title": "テイワット・テーマパック", "desc": "ロック画面・アイコン・起動音・壁紙。"},
        ],
        "gallery": ["元素の背面デザイン", "限定テーマUI", "コレクターズボックス", "専用ケース"],
        "note": "本コラボレーションはデモンストレーション用の架空企画です。原神は HoYoverse の作品であり、実在の商品・提携・販売を示すものではありません。",
    },
    {
        "slug": "wuwa", "game": "鳴潮", "studio": "Kuro Games",
        "active": False, "motif": "techwear",
        "tokens": {
            "bg": "#0e1216", "bg2": "#131a20", "ink": "#eaf6ff", "soft": "#9fb3c2",
            "accent": "#00e0ff", "accent2": "#8b5cf6", "line": "rgba(0,224,255,.28)",
            "glow": "#00e0ff",
        },
        "edition": "SUZAKU 4 × 鳴潮 共鳴 Edition",
        "hero": {
            "eyebrow": "SUZAKU × 鳴潮 — LIMITED COLLABORATION",
            "title": "音濤の共鳴を、<br>この掌に響かせろ。",
            "lead": "ソラリス-3を駆けるあなたへ。テックウェアの意匠をまとう共鳴のフラッグシップ。",
            "tagline": "共鳴 Edition",
        },
        "phone_id": "suzaku-4-wuwa", "accessory_ids": ["pb-wuwa"],
        "limited": {"until": "2026-09-30T23:59:59", "qty": 7000, "sold": 3110},
        "world": "災厄後の世界ソラリス-3。廃墟と新緑が交差する大地を、共鳴者たちが駆ける。その疾走感を、テックウェアの一台に。",
        "highlights": [
            {"title": "テックウェア・フィニッシュ", "body": "エレクトリックシアンの発光ラインを走らせた、機能美のマット背面。"},
            {"title": "特別選別チップ「RAI-G4 共鳴選別版」", "body": "最大3.9GHz・AnTuTu 405万点の特別ビン。史上最高性能。"},
            {"title": "共鳴テーマパック", "body": "HUD調の専用UI・起動音・壁紙を同梱。"},
        ],
        "bundle": [
            {"title": "限定ギフトコード", "desc": "ゲーム内アイテムの引き換えコード(デモ表記)。"},
            {"title": "共鳴 専用ケース", "desc": "テックウェア意匠の保護ケース。"},
            {"title": "コレクターズボックス", "desc": "限定パッケージ。"},
            {"title": "共鳴テーマパック", "desc": "HUD UI・起動音・壁紙。"},
        ],
        "gallery": ["テックウェア背面", "HUDテーマUI", "コレクターズボックス", "専用ケース"],
        "note": "本コラボレーションはデモンストレーション用の架空企画です。鳴潮は Kuro Games の作品であり、実在の商品・提携・販売を示すものではありません。",
    },
    {
        "slug": "nte", "game": "NTE(Neverness to Everness)", "studio": "Hotta Studio",
        "active": False, "motif": "neon",
        "tokens": {
            "bg": "#0a0812", "bg2": "#120a1c", "ink": "#f4ecff", "soft": "#c3b3d6",
            "accent": "#ff2d78", "accent2": "#22d3ee", "line": "rgba(255,45,120,.30)",
            "glow": "#ff2d78",
        },
        "edition": "SUZAKU 4 × NTE ネオンシティ Edition",
        "hero": {
            "eyebrow": "SUZAKU × NTE — LIMITED COLLABORATION",
            "title": "眠らない街の光を、<br>ポケットの中へ。",
            "lead": "超常が息づく都市ヘザロウ。ネオンの夜をまとう、限定のフラッグシップ。",
            "tagline": "ネオンシティ Edition",
        },
        "phone_id": "suzaku-4-nte", "accessory_ids": ["pb-nte"],
        "limited": {"until": "2026-10-31T23:59:59", "qty": 6000, "sold": 1980},
        "world": "超常現象と日常が隣り合う開かれた都市ヘザロウ。ネオンに濡れた夜の街の高揚を、一台に閉じ込めました。",
        "highlights": [
            {"title": "ネオングロー背面", "body": "マゼンタ×シアンのネオンが走る、高コントラストの夜景デザイン。"},
            {"title": "特別選別チップ「RAI-G4 夜想選別版」", "body": "最大3.9GHz・AnTuTu 405万点の特別ビン。史上最高性能。"},
            {"title": "ネオンシティ・テーマパック", "body": "都市夜景の専用UI・起動音・壁紙を同梱。"},
        ],
        "bundle": [
            {"title": "限定ギフトコード", "desc": "ゲーム内アイテムの引き換えコード(デモ表記)。"},
            {"title": "ネオンシティ 専用ケース", "desc": "夜景意匠の保護ケース。"},
            {"title": "コレクターズボックス", "desc": "限定パッケージ。"},
            {"title": "ネオンシティ・テーマパック", "desc": "都市夜景UI・起動音・壁紙。"},
        ],
        "gallery": ["ネオン背面", "夜景テーマUI", "コレクターズボックス", "専用ケース"],
        "note": "本コラボレーションはデモンストレーション用の架空企画です。NTE(Neverness to Everness)は Hotta Studio の作品であり、実在の商品・提携・販売を示すものではありません。",
    },
    {
        "slug": "endfield", "game": "アークナイツ: エンドフィールド", "studio": "Hypergryph",
        "active": False, "motif": "industrial",
        "tokens": {
            "bg": "#0d0f0e", "bg2": "#15130f", "ink": "#f2ede4", "soft": "#b9b3a6",
            "accent": "#ff7a1a", "accent2": "#ffb020", "line": "rgba(255,122,26,.30)",
            "glow": "#ff7a1a",
        },
        "edition": "SUZAKU 4 × エンドフィールド 開拓 Edition",
        "hero": {
            "eyebrow": "SUZAKU × ENDFIELD — LIMITED COLLABORATION",
            "title": "極地の産業を、<br>掌のターミナルで動かせ。",
            "lead": "インダストリアルSFの世界を、ハザードイエローの一台で。開拓の相棒となる限定フラッグシップ。",
            "tagline": "開拓 Edition",
        },
        "phone_id": "suzaku-4-endfield", "accessory_ids": ["pb-endfield"],
        "limited": {"until": "2026-11-30T23:59:59", "qty": 6500, "sold": 2470},
        "world": "未知の惑星タラス。産業と荒野が交差する開拓の最前線。その質実剛健な世界観を、ターミナル調の一台に。",
        "highlights": [
            {"title": "インダストリアル・フィニッシュ", "body": "ハザードストライプとアンバーのアクセントをまとった、無骨で機能的な背面。"},
            {"title": "特別選別チップ「RAI-G4 開拓選別版」", "body": "最大3.9GHz・AnTuTu 405万点の特別ビン。史上最高性能。"},
            {"title": "ターミナル・テーマパック", "body": "HUD/ターミナル調の専用UI・起動音・壁紙を同梱。"},
        ],
        "bundle": [
            {"title": "限定ギフトコード", "desc": "ゲーム内アイテムの引き換えコード(デモ表記)。"},
            {"title": "開拓 専用ケース", "desc": "インダストリアル意匠の保護ケース。"},
            {"title": "コレクターズボックス", "desc": "限定パッケージ。"},
            {"title": "ターミナル・テーマパック", "desc": "HUD UI・起動音・壁紙。"},
        ],
        "gallery": ["インダストリアル背面", "ターミナルUI", "コレクターズボックス", "専用ケース"],
        "note": "本コラボレーションはデモンストレーション用の架空企画です。アークナイツ: エンドフィールドは Hypergryph の作品であり、実在の商品・提携・販売を示すものではありません。",
    },
]


def collab_by_slug(slug):
    for c in COLLABS:
        if c["slug"] == slug:
            return c
    return None
