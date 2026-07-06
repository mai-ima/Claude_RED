# -*- coding: utf-8 -*-
"""SUZAKU 静的サイトジェネレータ。

使い方:
    python3 scripts/gen.py

- scripts/data_*.py の単一ソースデータから、製品/技術/OS/ニュースの各ページを生成
- src/pages/ 配下のフラグメント(本文のみのHTML)を共通レイアウトで包んで出力
- 製品画像・技術ビジュアルをSVGとして assets/img/ に生成
- クライアント用データ data/products.js、sitemap.xml、robots.txt を生成

Next.js移行時は、この出力ディレクトリ構造が app/ ルータのルートに1:1対応する。
"""
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_products import ALL_PRODUCTS, PHONES, TABLETS, ACCESSORIES, LINES  # noqa: E402
from data_tech import TECHS, OS_VERSIONS  # noqa: E402
from data_misc import NEWS, FAQ, HISTORY  # noqa: E402
from data_docs import DOCS  # noqa: E402
import svg_art  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"
SITE_NAME = "SUZAKU(朱雀)"
BASE_URL = "https://suzaku.example.jp"


def _asset_version():
    """assets/css・assets/js・data_*.py(/data/products.js の生成元)の内容から
    短いハッシュを作り、キャッシュバスティング用のクエリ文字列(?v=...)に使う。
    CSS/JSはもちろん、商品データだけを更新した場合でも /data/products.js が
    古いキャッシュのまま配信され続けないよう、生成元データもハッシュ対象に含める。"""
    h = hashlib.sha256()
    for sub in ("css", "js"):
        d = ROOT / "assets" / sub
        if not d.exists():
            continue
        for f in sorted(d.glob("*")):
            if f.is_file():
                h.update(f.read_bytes())
    for f in sorted((ROOT / "scripts").glob("data_*.py")):
        h.update(f.read_bytes())
    return h.hexdigest()[:10]


ASSET_V = _asset_version()

PAGES = []  # 検索インデックス + sitemap 用 {url,title,desc,group}


def yen(n):
    return f"¥{n:,}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def num(s):
    m = re.search(r"([\d,]+)", s or "")
    return int(m.group(1).replace(",", "")) if m else 0


# ==========================================================================
# チャート(charts.js が data-chart JSON を描画する)
# ==========================================================================

def chart(cfg, cls=""):
    js = json.dumps(cfg, ensure_ascii=False).replace("'", "&#39;")
    return f'<figure class="chart reveal{(" " + cls) if cls else ""}" data-chart=\'{js}\'></figure>'


# ベンチマーク・技術トレンドの単一ソース(架空値)
ANTUTU = {"rai-g1": 158, "rai-g2": 218, "rai-g3": 312, "rai-g4": 385}   # 万点(旗艦G系)
ANTUTU_E = {"rai-e1": 62, "rai-e2": 85}                                   # 万点(エントリーE系)
TFLOPS_L = {"homura-l1": 0.35, "homura-l2": 0.5}                          # Lite GPU
CLOCK = {"rai-g1": 3.2, "rai-g2": 3.3, "rai-g3": 3.5, "rai-g4": 3.8}    # GHz
NPU_TOPS = {"rai-g1": 20, "rai-g2": 45, "rai-g3": 75, "rai-g4": 120}
TFLOPS = {"homura-x1": 1.0, "homura-x2": 1.6, "homura-x3": 2.3, "homura-x4": 3.4}
MEM_MBPS = {"hayate-m1": 8533, "hayate-m2": 10667}
SSD_MBS = {"shun-s1": 4300, "shun-s2": 5800}
VC_AREA = [("氷刃 V1(2023)", 9000), ("氷刃 V2(2024)", 10200), ("氷刃 V3(2025)", 11000), ("氷刃 V4(2026)", 12800)]
FAN_RPM = [("第1世代(2023)", 18000), ("第2世代(2024-25)", 22000), ("第3世代(2026)", 24000)]
COOL_DELTA = [("氷刃 V1", 9.5), ("氷刃 V2", 12.0), ("氷刃 V3", 14.2), ("氷刃 V4", 16.8)]  # 表面温度低下℃


def product_antutu(p):
    """製品の搭載SoCからAnTuTuスコア(万点)を算出。省電力版(A)は0.74倍。"""
    chip = p.get("chip")
    if not chip:
        return None
    if chip in ANTUTU_E:
        return ANTUTU_E[chip]
    if chip not in ANTUTU:
        return None
    soc = get_spec(p, ["性能"], "SoC")
    base = ANTUTU[chip]
    if re.search(r"RAI-G\dA", soc):
        return round(base * 0.74)
    return base


def radar_values(p):
    """5軸(性能/カメラ/バッテリー/冷却/コスパ)を仕様から算出、0-100。"""
    perf = round((product_antutu(p) or 100) / 385 * 100)
    cam_s = get_spec(p, ["カメラ"], "リアカメラ")
    cam = 95 if "RS-2+" in cam_s else 86 if "RS-2" in cam_s else 72 if "RS-1" in cam_s else 50
    bat = num(get_spec(p, ["バッテリー"], "バッテリー容量"))
    batv = round(min(100, bat / (10500 if p["cat"] == "tablet" else 7600) * 100)) if bat else 40
    cool_s = get_spec(p, ["冷却"], "冷却システム")
    cool = 98 if "V4" in cool_s else 88 if "V3" in cool_s else 76 if "V2" in cool_s else 64 if "V1" in cool_s else 42
    cost = round(max(35, min(100, 100 - (p["price"] - 30000) / 1400)))
    return [perf, cam, batv, cool, cost]


RADAR_AXES = ["性能", "カメラ", "バッテリー", "冷却", "コスパ"]


# ==========================================================================
# 製品ページの追加コンテンツ(同梱物・対応アクセサリ・製品別FAQ)
# ==========================================================================

def box_items(p):
    """同梱物リスト。カテゴリ・ラインごとに現実的な内容を生成。"""
    if p["cat"] == "phone":
        items = ["本体", "USB Type-C to C ケーブル(1m)", "SIMピン", "クイックスタートガイド / 保証のご案内", "SUZAKUステッカー"]
        if p["line"] in ("suzaku", "neo"):
            watt = num(get_spec(p, ["バッテリー"], "有線充電")) or 65
            items.insert(1, f"雷速チャージャー {watt}W(同梱)")
            items += ["クリアソフトケース", "画面保護フィルム(貼付済み)"]
        return items
    if p["cat"] == "tablet":
        items = ["本体", "USB Type-C to C ケーブル(1.5m)", "クイックスタートガイド / 保証のご案内"]
        if p["line"] in ("pad", "pad-neo"):
            watt = num(get_spec(p, ["バッテリー"], "有線充電")) or 67
            items.insert(1, f"雷速チャージャー {watt}W(同梱)")
        return items
    extra = {
        "hyoran-cooler": ["USB Type-C ケーブル(1.2m)"],
        "grip-pro": ["キャリングポーチ", "USB Type-C ケーブル(0.8m)"],
        "buds": ["充電ケース", "2.4GHz USB-C ドングル", "イヤーピース(XS/S/M/L)"],
        "raisoku-charger": ["120W対応 USB-C ケーブル(1.5m)"],
        "shield-case": ["クリーニングクロス"],
        "dock": ["電源アダプタ(140W)", "HDMI 2.1 ケーブル(1.5m)"],
    }
    return ["本体"] + extra.get(p["id"], []) + ["クイックスタートガイド / 保証のご案内"]


def acc_compat_table(p):
    """スマホ/タブレット向け: 純正アクセサリ対応表。"""
    def compat(acc_id):
        if acc_id == "shield-case":
            return ("対応", "専用設計") if p["id"] == "suzaku-4" else ("非対応", "SUZAKU 4 専用")
        if acc_id in ("hyoran-cooler", "grip-pro"):
            return ("対応", "幅67〜82mm") if p["cat"] == "phone" else ("非対応", "スマートフォン専用")
        if acc_id == "dock":
            wl = "ワイヤレス充電も利用可" if p["id"] in ("suzaku-4",) else "有線接続で利用可"
            return ("対応", wl)
        return ("対応", "全機種対応")

    rows = ""
    for a in ACCESSORIES:
        if a["status"] != "current":
            continue
        ok, note = compat(a["id"])
        mark = ('<strong style="color:var(--accent)">対応</strong>' if ok == "対応"
                else '<span class="t-faint">—</span>')
        rows += (f'<tr><td><a href="{product_url(a)}" style="color:var(--accent);font-weight:700">{esc(a["name"])}</a></td>'
                 f'<td>{yen(a["price"])}</td><td>{mark}</td><td class="t-soft">{esc(note)}</td></tr>')
    return f"""
<div class="scroll-x reveal"><table class="spec-table quick-table">
  <thead><tr><th scope="col">アクセサリ</th><th scope="col">価格(税込)</th><th scope="col">{esc(p['name'])}</th><th scope="col">備考</th></tr></thead>
  <tbody>{rows}</tbody>
</table></div>"""


LINE_FAQ = {
    "suzaku": [
        ("ファンの音はゲーム中どのくらい聞こえますか?",
         "自動モードでは28〜38dB(ささやき声〜静かな図書館程度)で制御されます。動画視聴などの低負荷時はファンは停止します。「陣」から手動で4段階+停止を選択できます。"),
        ("冷却用の通気口があっても防水は大丈夫ですか?",
         "IP54(防塵・防滴)に対応しています。エアダクトを迷路状に設計し、雨滴や手汗が内部へ到達しない構造です。ただし水没には対応しないため、入浴・水泳でのご使用はお避けください。"),
        ("発熱で性能が落ちる「サーマルスロットリング」は起きませんか?",
         "60分の高負荷連続プレイを想定した当社試験では、フレームレート低下5%未満を維持しています。氷刃ベイパーチャンバー・旋風ファン・液焔の多層冷却と、神楽サーマルの予測制御によるものです。"),
    ],
    "neo": [
        ("フラッグシップとの違いは何ですか?",
         "SoC・冷却は前年フラッグシップと同一で、ディスプレイのピーク輝度・カメラ構成・充電速度などを合理化しています。ゲーム性能そのものは前年旗艦とほぼ同等です。<a href='/products/compare/'>比較ツール</a>で並べてご確認ください。"),
        ("ショルダートリガーは搭載されていますか?",
         "はい。Neoシリーズ全機種に静電容量式ショルダートリガーを搭載しています。「陣」のエアトリガー設定から感度・割当を調整できます。"),
        ("何年使えますか?",
         "OSアップデート2世代+セキュリティ更新4年を保証しています。バッテリーは充電上限設定・バイパス充電で劣化を抑えられます。"),
    ],
    "tsubame": [
        ("ゲーミングスマホのような派手なデザインではありませんか?",
         "はい。TSUBAMEは日本の伝統色とマット仕上げの落ち着いたデザインです。SUZAKU OSも「ピュアモード」が初期設定で、ゲーム機能は必要な時だけ呼び出せます。"),
        ("カメラの画質はフラッグシップと同じですか?",
         "TSUBAME 3はフラッグシップと同じ「天眼 RS-2+」センサーを搭載しています。望遠レンズの有無などの構成差はありますが、広角カメラの画質は同水準です。"),
        ("おサイフケータイ・防水は使えますか?",
         "FeliCa(おサイフケータイ)とIP68防塵防水に対応しています。日常利用の安心を最優先した設計です。"),
    ],
    "lite": [
        ("価格が安い理由は何ですか?",
         "エントリー専用に新設計した自社SoC「雷 RAI-E」シリーズの採用、液晶ディスプレイの選択、パッケージの簡素化によるものです。FeliCa・防水・セキュリティ更新など「毎日の安心」に関わる部分は削っていません。<a href='/tech/cpu/rai-e2/'>RAI-E2の技術詳細</a>もご覧ください。"),
        ("ゲームはどの程度動きますか?",
         "人気タイトルの標準〜中設定で快適に動作します。高フレームレート・最高画質でのプレイをご希望の場合はNeoシリーズをご検討ください。"),
        ("初めてのスマホでも使えますか?",
         "かんたんホーム、文字サイズの一括拡大、迷惑電話ブロックなど、初めての方向けの機能を標準搭載しています。"),
    ],
    "acc": [
        ("他社製スマートフォンでも使えますか?",
         "Bluetooth・USB-C等の標準規格に準拠しているため、多くの他社製端末でも基本機能はご利用いただけます。ただし「陣」との連携機能(自動起動・プロファイル同期など)はSUZAKU端末専用です。"),
        ("保証期間はどのくらいですか?",
         "ご購入日から1年間のメーカー保証が付属します。詳細は<a href='/support/warranty/'>保証について</a>をご覧ください。"),
        ("本体と同時購入するメリットはありますか?",
         "税込5,000円以上で送料無料になるほか、ストアのカートで本体とまとめて一度に受け取れます。"),
    ],
}
LINE_FAQ["pad"] = LINE_FAQ["suzaku"]
LINE_FAQ["pad-neo"] = LINE_FAQ["neo"]
LINE_FAQ["t-pad"] = LINE_FAQ["tsubame"]
LINE_FAQ["t-pad-lite"] = LINE_FAQ["lite"]

GAMING_LINES = {"suzaku", "neo", "pad", "pad-neo"}
LIFE_LINES = {"tsubame", "lite", "t-pad", "t-pad-lite"}

# チップ世代別 タイトル実測fps: (平均fps, 30分後fps) ×4ジャンル(架空タイトル)
GAME_TITLES = [
    ("幻晶のエルド", "オープンワールドRPG", "最高画質 / 60fps上限"),
    ("NOVA STRIKE", "FPSシューター", "最高画質 / 上限解放"),
    ("頂上決戦アリーナ", "MOBA", "最高画質 / 上限解放"),
    ("雷鳴レーシング8", "レーシング", "最高画質 / 上限解放"),
]
GAME_FPS = {
    "rai-g1": [(55, 48), (88, 79), (118, 112), (86, 77)],
    "rai-g2": [(59, 55), (116, 108), (142, 137), (108, 101)],
    "rai-g3": [(60, 59), (143, 138), (164, 160), (132, 127)],
    "rai-g4": [(60, 60), (172, 170), (175, 175), (158, 155)],
}


def game_fps_section(p):
    """ゲーミング系ライン専用: タイトル別実測パフォーマンス表。"""
    fps = GAME_FPS.get(p["chip"])
    if not fps:
        return ""
    rows = ""
    for (title, genre, setting), (avg, sustained) in zip(GAME_TITLES, fps):
        keep = round(sustained / avg * 100)
        rows += (f'<tr><th scope="row">{title}<br><small class="t-faint">{genre}</small></th>'
                 f'<td>{setting}</td><td><strong>{avg}fps</strong></td>'
                 f'<td>{sustained}fps <small class="t-faint">(維持率{keep}%)</small></td></tr>')
    return f"""
<section class="section--sm" id="game-ready">
  <div class="container">
    <div class="section-head"><p class="eyebrow">GAME READY</p><h2 class="t-h2">タイトル別 実測パフォーマンス</h2>
    <p class="t-soft t-small">室温25℃・輝度50%・Wi-Fi接続の当社試験値(タイトルは検証用の架空タイトル)。「30分後」は連続プレイでの持続性能 — 冷却の実力はここに出ます。</p></div>
    <div class="scroll-x reveal"><table class="spec-table quick-table">
      <thead><tr><th scope="col">タイトル</th><th scope="col">画質設定</th><th scope="col">平均fps</th><th scope="col">30分後fps</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p class="t-micro t-faint" style="margin-top:14px">ゲーム側からの性能制御は<a href="/developers/docs/performance-api/" style="color:var(--accent);text-decoration:underline">Performance API</a>で開発者に開放しています。</p>
  </div>
</section>"""


def battery_life_section(p):
    """スタンダード/エントリー系ライン専用: 電池持ちと充電の目安表。"""
    bat = num(get_spec(p, ["バッテリー"], "バッテリー容量"))
    watt = num(get_spec(p, ["バッテリー"], "有線充電"))
    if not bat:
        return ""
    tablet = p["cat"] == "tablet"
    video = round(bat / (640 if tablet else 195))
    browse = round(video * 0.7)
    call = round(video * 0.35)
    recover = min(85, round((watt or 18) * 0.7))
    rows = (
        f'<tr><th scope="row">動画の連続再生</th><td><strong>約{video}時間</strong></td><td>フル充電から・機内モード</td></tr>'
        f'<tr><th scope="row">SNS・ブラウジング</th><td><strong>約{browse}時間</strong></td><td>5G接続・画面点灯連続</td></tr>'
        f'<tr><th scope="row">ビデオ通話</th><td><strong>約{call}時間</strong></td><td>Wi-Fi接続・インカメラ使用</td></tr>'
        f'<tr><th scope="row">30分の充電で</th><td><strong>約{recover}%まで回復</strong></td><td>{watt}W急速充電・電源オフ時</td></tr>')
    return f"""
<section class="section--sm" id="battery-life">
  <div class="container">
    <div class="section-head"><p class="eyebrow">BATTERY LIFE</p><h2 class="t-h2">電池持ちと充電の目安</h2>
    <p class="t-soft t-small">輝度50%・当社試験条件での参考値です。使用状況により変動します。</p></div>
    <div class="scroll-x reveal"><table class="spec-table quick-table">
      <thead><tr><th scope="col">使い方</th><th scope="col">{esc(p['name'])}</th><th scope="col">条件</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
    <p class="t-micro t-faint" style="margin-top:14px">いたわり充電(充電上限80%設定)を使うと、2年後の電池劣化を大幅に抑えられます。</p>
  </div>
</section>"""


# アクセサリ製品別の比較チャート(製品の性格をデータで示す)
ACC_CHARTS = {
    "hyoran-cooler": {"type": "bar", "title": "背面温度の低下量(SUZAKU 4・30分高負荷時)", "unit": "℃",
                      "labels": ["冷却なし", "初代 氷嵐クーラー", "氷嵐クーラー 2"], "values": [0, 19, 28], "highlight": 2},
    "grip-pro": {"type": "bar", "title": "入力遅延の比較(ボタン押下→画面反映)", "unit": "ms",
                 "labels": ["一般的なBluetoothパッド", "Grip Pro(Bluetooth)", "Grip Pro(USB-C直結)"], "values": [45, 12, 0.8], "highlight": 2},
    "buds": {"type": "bar", "title": "音声遅延の比較", "unit": "ms",
             "labels": ["一般的なTWS(AAC)", "低遅延モード搭載TWS", "SUZAKU Buds(2.4GHzドングル)"], "values": [180, 80, 38], "highlight": 2},
    "raisoku-charger": {"type": "bar", "title": "SUZAKU 4 のフル充電時間比較", "unit": "分",
                        "labels": ["一般的な30W充電器", "65W級充電器", "雷速チャージャー 120W"], "values": [78, 52, 34], "highlight": 2},
    "shield-case": {"type": "bar", "title": "ケース装着による背面温度上昇(30分高負荷)", "unit": "℃",
                    "labels": ["手帳型ケース", "一般的なTPUケース", "SUZAKU Shield"], "values": [9.2, 6.8, 1.9], "highlight": 2},
    "dock": {"type": "bar", "title": "ワイヤレス給電出力の比較", "unit": "W",
             "labels": ["Qi(EPP)", "Qi2", "SUZAKU Dock(対応機種)"], "values": [15, 25, 80], "highlight": 2},
}


# ==========================================================================
# 共通レイアウト
# ==========================================================================

def mega_products():
    def li(url, label, small=None, strong=False):
        lbl = f"<strong>{label}</strong>" if strong else label
        sm = f"<small>{small}</small>" if small else ""
        return f'<li><a href="{url}">{lbl}{sm}</a></li>'

    return f"""
<div class="mega" style="--mega-cols:4">
  <div class="mega__inner">
    <div>
      <p class="mega__group-title">スマートフォン</p>
      <ul class="mega__list">
        {li('/products/phone/suzaku-4/', 'SUZAKU 4', 'ゲーミングフラッグシップ', True)}
        {li('/products/phone/suzaku-3/', 'SUZAKU 3', 'ゲーミングフラッグシップ')}
        {li('/products/phone/neo-3/', 'SUZAKU Neo 3', 'ゲーミングスタンダード')}
        {li('/products/phone/tsubame-3/', 'TSUBAME 3', 'スタンダード')}
        {li('/products/phone/tsubame-lite-2/', 'TSUBAME Lite 2', 'エントリー')}
        {li('/products/phone/', 'すべてのスマートフォン')}
      </ul>
    </div>
    <div>
      <p class="mega__group-title">タブレット</p>
      <ul class="mega__list">
        {li('/products/tablet/pad-2/', 'SUZAKU Pad 2', 'ゲーミング', True)}
        {li('/products/tablet/pad-neo/', 'SUZAKU Pad Neo', 'ゲーミング')}
        {li('/products/tablet/t-pad-2/', 'TSUBAME Pad 2', 'スタンダード')}
        {li('/products/tablet/t-pad-lite/', 'TSUBAME Pad Lite', 'エントリー')}
        {li('/products/tablet/', 'すべてのタブレット')}
      </ul>
    </div>
    <div>
      <p class="mega__group-title">アクセサリ</p>
      <ul class="mega__list">
        {li('/products/accessories/hyoran-cooler/', '氷嵐クーラー 2')}
        {li('/products/accessories/grip-pro/', 'SUZAKU Grip Pro')}
        {li('/products/accessories/buds/', 'SUZAKU Buds')}
        {li('/products/accessories/raisoku-charger/', '雷速チャージャー 120W')}
        {li('/products/accessories/', 'すべてのアクセサリ')}
      </ul>
    </div>
    <div>
      <p class="mega__group-title">ショッピング</p>
      <ul class="mega__list">
        {li('/store/', 'SUZAKU ストア')}
        {li('/products/compare/', '製品を比較する')}
        {li('/store/guide/', '購入ガイド')}
        {li('/store/order-status/', '注文状況の確認')}
        {li('/store/cart/', 'カートを見る')}
      </ul>
    </div>
  </div>
</div>"""


def mega_tech():
    def li(url, label, small=None):
        sm = f"<small>{small}</small>" if small else ""
        return f'<li><a href="{url}">{label}{sm}</a></li>'

    return f"""
<div class="mega" style="--mega-cols:4">
  <div class="mega__inner">
    <div>
      <p class="mega__group-title">自社シリコン</p>
      <ul class="mega__list">
        {li('/tech/cpu/', '雷 RAI', 'CPU / SoC')}
        {li('/tech/gpu/', '焔 HOMURA', 'GPU')}
        {li('/tech/memory/', '疾風 HAYATE', 'メモリ')}
        {li('/tech/storage/', '瞬 SHUN', 'ストレージ')}
      </ul>
    </div>
    <div>
      <p class="mega__group-title">冷却技術</p>
      <ul class="mega__list">
        {li('/tech/cooling/hyojin/', '氷刃', 'ベイパーチャンバー')}
        {li('/tech/cooling/senpu/', '旋風', '内蔵アクティブファン')}
        {li('/tech/cooling/ekien/', '液焔', 'リキッドメタル')}
        {li('/tech/cooling/suiryu/', '水龍', '能動液冷(次世代)')}
        {li('/tech/cooling/', '冷却技術のすべて')}
      </ul>
    </div>
    <div>
      <p class="mega__group-title">イメージング & AI</p>
      <ul class="mega__list">
        {li('/tech/camera/', '天眼 TENGAN', 'カメラシステム')}
        {li('/tech/ai/', '神楽 KAGURA', 'AIエンジン')}
        {li('/tech/display/', '燐光 RINKO', 'ディスプレイ')}
      </ul>
    </div>
    <div>
      <p class="mega__group-title">ソフトウェア</p>
      <ul class="mega__list">
        {li('/os/v4/', 'SUZAKU OS 4.0', '最新バージョン「不知火」')}
        {li('/os/game-space/', 'ゲームスペース「陣」')}
        {li('/os/', 'SUZAKU OS トップ')}
        {li('/tech/', 'テクノロジー トップ')}
      </ul>
    </div>
  </div>
</div>"""


def mega_company():
    return """
<div class="mega" style="--mega-cols:3">
  <div class="mega__inner">
    <div>
      <p class="mega__group-title">企業情報</p>
      <ul class="mega__list">
        <li><a href="/company/">会社概要</a></li>
        <li><a href="/company/history/">沿革 — SUZAKUの歴史</a></li>
        <li><a href="/news/">ニュースルーム</a></li>
        <li><a href="/company/careers/">採用情報</a></li>
      </ul>
    </div>
    <div>
      <p class="mega__group-title">取り組み</p>
      <ul class="mega__list">
        <li><a href="/sustainability/">環境への取り組み</a></li>
        <li><a href="/sustainability/recycle/">回収・リサイクル</a></li>
        <li><a href="/legal/accessibility/">アクセシビリティ</a></li>
        <li><a href="/legal/">法的情報</a></li>
      </ul>
    </div>
    <div>
      <p class="mega__group-title">パートナー</p>
      <ul class="mega__list">
        <li><a href="/business/">法人のお客様</a></li>
        <li><a href="/business/solutions/">法人向けソリューション</a></li>
        <li><a href="/developers/">開発者向け</a></li>
        <li><a href="/developers/docs/">開発者ドキュメント</a></li>
      </ul>
    </div>
  </div>
</div>"""


# カラーテーマの選択肢(単一ソース)。テーマを追加・変更する場合はここだけを編集すれば、
# ヘッダーのドロップダウンとドロワーのセグメント切替の両方に反映される。
# 各要素: (value, スウォッチのCSS, 正式名称(aria/トースト), 短縮名(ドロワー用))
THEME_OPTS = [
    ("auto", "linear-gradient(90deg,#fafafc 50%,#0b0b10 50%)", "ページ既定", "既定"),
    ("light", "#fafafc", "ライト", "ライト"),
    ("dark", "#0b0b10", "ダーク", "ダーク"),
    ("g", "linear-gradient(135deg,#00e68a,#00c2ff)", "Gモード", "G"),
    ("suzaku", "linear-gradient(135deg,#e8442e,#d9a441)", "朱雀モード", "朱雀"),
]


def theme_menu_buttons():
    """ヘッダーのテーマドロップダウン用ボタン列。"""
    return "".join(
        f'<button type="button" data-theme-opt="{v}" role="menuitemradio"><i style="background:{sw}"></i>{full}</button>'
        for v, sw, full, short in THEME_OPTS
    )


def theme_seg_buttons():
    """ドロワー(モバイル)のテーマセグメント用ボタン列。"""
    return "".join(
        f'<button type="button" data-theme-opt="{v}" data-theme-label="{full}"><i style="background:{sw}"></i>{short}</button>'
        for v, sw, full, short in THEME_OPTS
    )


def header_html():
    return f"""
<a class="skip-link" href="#main">本文へスキップ</a>
<header class="site-header" id="siteHeader">
  <div class="site-header__inner">
    <a class="brand" href="/" aria-label="SUZAKU ホーム">{svg_art.BRAND_MARK}<span>SUZAKU</span></a>
    <nav class="gnav" aria-label="グローバルナビゲーション">
      <div class="gnav__item"><a class="gnav__link" href="/products/">製品</a>{mega_products()}</div>
      <div class="gnav__item"><a class="gnav__link" href="/tech/">テクノロジー</a>{mega_tech()}</div>
      <div class="gnav__item"><a class="gnav__link" href="/os/">OS</a></div>
      <div class="gnav__item"><a class="gnav__link" href="/store/">ストア</a></div>
      <div class="gnav__item"><a class="gnav__link" href="/support/">サポート</a></div>
      <div class="gnav__item"><a class="gnav__link" href="/company/">企業情報</a>{mega_company()}</div>
    </nav>
    <div class="header-actions">
      <div class="theme-menu" id="themeMenu">
        <button class="icon-btn" id="themeBtn" aria-label="カラーテーマを変更" aria-expanded="false" aria-haspopup="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none"/></svg>
        </button>
        <div class="theme-menu__panel" role="menu" aria-label="カラーテーマ">
          <p class="theme-menu__title">カラーテーマ</p>
          {theme_menu_buttons()}
        </div>
      </div>
      <a class="icon-btn" href="/search/" aria-label="検索">{svg_art.ICONS['search']}</a>
      <a class="icon-btn" href="/account/login/" id="accountLink" aria-label="アカウント">{svg_art.ICONS['user']}</a>
      <a class="icon-btn" href="/store/cart/" aria-label="カート">{svg_art.ICONS['cart']}<span class="cart-badge" id="cartBadge"></span></a>
      <button class="icon-btn nav-toggle" id="navToggle" aria-label="メニュー" aria-expanded="false"><span></span></button>
    </div>
  </div>
</header>
<nav class="drawer" id="drawer" aria-label="モバイルナビゲーション">
  <div class="drawer__group">
    <button class="drawer__summary">製品</button>
    <div class="drawer__panel"><div class="drawer__panel-inner">
      <p class="drawer__sub">スマートフォン</p>
      <a href="/products/phone/suzaku-4/">SUZAKU 4</a>
      <a href="/products/phone/neo-3/">SUZAKU Neo 3</a>
      <a href="/products/phone/tsubame-3/">TSUBAME 3</a>
      <a href="/products/phone/tsubame-lite-2/">TSUBAME Lite 2</a>
      <a href="/products/phone/">すべてのスマートフォン</a>
      <p class="drawer__sub">タブレット</p>
      <a href="/products/tablet/pad-2/">SUZAKU Pad 2</a>
      <a href="/products/tablet/">すべてのタブレット</a>
      <p class="drawer__sub">アクセサリ・ツール</p>
      <a href="/products/accessories/">すべてのアクセサリ</a>
      <a href="/products/compare/">製品を比較する</a>
    </div></div>
  </div>
  <div class="drawer__group">
    <button class="drawer__summary">テクノロジー</button>
    <div class="drawer__panel"><div class="drawer__panel-inner">
      <a href="/tech/">テクノロジー トップ</a>
      <a href="/tech/cpu/">雷 RAI(CPU)</a>
      <a href="/tech/gpu/">焔 HOMURA(GPU)</a>
      <a href="/tech/memory/">疾風 HAYATE(メモリ)</a>
      <a href="/tech/storage/">瞬 SHUN(ストレージ)</a>
      <a href="/tech/cooling/">冷却技術</a>
      <a href="/tech/camera/">天眼 カメラ</a>
      <a href="/tech/ai/">神楽 AIエンジン</a>
      <a href="/tech/display/">燐光 ディスプレイ</a>
    </div></div>
  </div>
  <div class="drawer__group">
    <button class="drawer__summary">SUZAKU OS</button>
    <div class="drawer__panel"><div class="drawer__panel-inner">
      <a href="/os/">SUZAKU OS トップ</a>
      <a href="/os/v4/">SUZAKU OS 4.0「不知火」</a>
      <a href="/os/game-space/">ゲームスペース「陣」</a>
    </div></div>
  </div>
  <a class="drawer__direct" href="/store/">ストア</a>
  <a class="drawer__direct" href="/support/">サポート</a>
  <div class="drawer__group">
    <button class="drawer__summary">企業情報</button>
    <div class="drawer__panel"><div class="drawer__panel-inner">
      <a href="/company/">会社概要</a>
      <a href="/company/history/">沿革</a>
      <a href="/news/">ニュースルーム</a>
      <a href="/company/careers/">採用情報</a>
      <a href="/sustainability/">環境への取り組み</a>
      <a href="/business/">法人のお客様</a>
      <a href="/developers/">開発者向け</a>
    </div></div>
  </div>
  <a class="drawer__direct" href="/search/">検索</a>
  <a class="drawer__direct" href="/account/login/">ログイン / マイページ</a>
  <a class="drawer__direct" href="/settings/">設定</a>
  <div class="drawer__theme">
    <p class="drawer__sub">カラーテーマ</p>
    <div class="theme-seg" role="group" aria-label="カラーテーマ">
      {theme_seg_buttons()}
    </div>
  </div>
</nav>"""


def footer_html():
    col = lambda title, items: (
        f'<div><p class="footer-map__title">{title}</p><ul>'
        + "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in items)
        + "</ul></div>"
    )
    cols = [
        col("製品とストア", [
            ("SUZAKU 4", "/products/phone/suzaku-4/"),
            ("SUZAKU Neo 3", "/products/phone/neo-3/"),
            ("TSUBAME 3", "/products/phone/tsubame-3/"),
            ("SUZAKU Pad 2", "/products/tablet/pad-2/"),
            ("アクセサリ", "/products/accessories/"),
            ("SUZAKU ストア", "/store/"),
            ("製品を比較する", "/products/compare/"),
            ("購入ガイド", "/store/guide/"),
        ]),
        col("テクノロジー", [
            ("雷 RAI(CPU)", "/tech/cpu/"),
            ("焔 HOMURA(GPU)", "/tech/gpu/"),
            ("疾風 HAYATE(メモリ)", "/tech/memory/"),
            ("瞬 SHUN(ストレージ)", "/tech/storage/"),
            ("冷却技術", "/tech/cooling/"),
            ("天眼 カメラ", "/tech/camera/"),
            ("SUZAKU OS", "/os/"),
        ]),
        col("サポート", [
            ("サポートトップ", "/support/"),
            ("よくあるご質問", "/support/faq/"),
            ("トラブルシューティング", "/support/troubleshooting/"),
            ("修理のお申し込み", "/support/repair/"),
            ("修理状況の確認", "/support/status/"),
            ("保証について", "/support/warranty/"),
            ("ダウンロード", "/support/downloads/"),
            ("お問い合わせ", "/support/contact/"),
            ("注文状況の確認", "/store/order-status/"),
            ("マイページ / ログイン", "/account/login/"),
            ("メンテナンス情報", "/maintenance/"),
            ("表示設定", "/settings/"),
        ]),
        col("SUZAKUについて", [
            ("会社概要", "/company/"),
            ("沿革", "/company/history/"),
            ("ニュースルーム", "/news/"),
            ("採用情報", "/company/careers/"),
            ("環境への取り組み", "/sustainability/"),
            ("回収・リサイクル", "/sustainability/recycle/"),
        ]),
        col("法人・開発者", [
            ("法人のお客様", "/business/"),
            ("法人向けソリューション", "/business/solutions/"),
            ("導入事例", "/business/cases/"),
            ("法人お問い合わせ", "/business/contact/"),
            ("開発者向け", "/developers/"),
            ("ドキュメント", "/developers/docs/"),
            ("最適化ガイドライン", "/developers/guidelines/"),
            ("対応タイトル", "/developers/showcase/"),
            ("SDKダウンロード", "/developers/sdk/"),
        ]),
    ]
    legal_links = [
        ("プライバシーポリシー", "/legal/privacy/"),
        ("Cookieポリシー", "/legal/cookie/"),
        ("外部送信ポリシー", "/legal/external-transmission/"),
        ("利用規約", "/legal/terms/"),
        ("販売条件", "/legal/sales/"),
        ("特定商取引法に基づく表記", "/legal/tokushoho/"),
        ("保証規定", "/legal/warranty-policy/"),
        ("情報セキュリティ基本方針", "/legal/security/"),
        ("脆弱性開示ポリシー", "/legal/vulnerability-disclosure/"),
        ("AI利用方針", "/legal/ai/"),
        ("コンプライアンス", "/legal/compliance/"),
        ("反社会的勢力への対応", "/legal/anti-social/"),
        ("アクセシビリティ", "/legal/accessibility/"),
        ("知的財産", "/legal/ip/"),
        ("法的情報", "/legal/"),
    ]
    legal = "".join(f'<a href="{u}">{t}</a>' for t, u in legal_links)
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-map">{''.join(cols)}</div>
    <div class="site-footer__legal">
      <p>本サイトは、架空の企業「株式会社朱雀(SUZAKU Inc.)」のデモンストレーションサイトです。掲載されている製品・価格・技術・サービスはすべてフィクションであり、実在の商品・役務の販売を行うものではありません。</p>
      <div class="site-footer__legal-links">{legal}<button type="button" class="cookie-settings-link" id="cookieSettingsBtn">Cookie設定</button></div>
      <div class="spread">
        <p>Copyright © 2022-2026 SUZAKU Inc. All rights reserved.</p>
        <p>日本 — 東京都千代田区外神田(秋葉原)</p>
      </div>
    </div>
  </div>
</footer>
<div class="cookie-banner" id="cookieBanner" role="dialog" aria-label="Cookieの利用について">
  <p class="cookie-banner__title"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="9" cy="10" r="0.5"/><circle cx="14.5" cy="14" r="0.5"/><circle cx="13" cy="8.5" r="0.5"/><circle cx="9.5" cy="15" r="0.5"/><circle cx="15" cy="10.5" r="0.5"/></svg> Cookieの利用について</p>
  <p>当サイトは、サイトの基本機能に必要なCookie等に加え、利便性向上・利用状況分析のためにCookieおよび類似技術を使用します。詳細は<a href="/legal/cookie/">Cookieポリシー</a>および<a href="/legal/external-transmission/">外部送信ポリシー</a>をご覧ください。「設定」からカテゴリごとに選択できます。</p>
  <div class="cluster">
    <button class="btn btn--primary btn--sm" id="consentAcceptAll">すべて同意する</button>
    <button class="btn btn--ghost btn--sm" id="consentRejectAll">必須のみ許可</button>
    <button class="btn btn--soft btn--sm" id="consentOpenSettings">設定</button>
  </div>
</div>
<div class="modal-backdrop" id="consentModal" aria-hidden="true">
  <div class="modal" role="dialog" aria-modal="true" aria-labelledby="consentModalTitle">
    <div class="stack">
      <h2 class="t-h3" id="consentModalTitle">Cookie設定</h2>
      <p class="t-small t-soft">カテゴリごとにCookie等の利用可否を選択できます。選択内容はこの端末に保存され、<a href="/legal/cookie/" style="color:var(--accent);text-decoration:underline">Cookieポリシー</a>のページからいつでも変更できます。</p>
    </div>
    <div>
      <div class="consent-row">
        <div><p class="consent-row__title">必須Cookie</p><p>カート、ログイン状態、Cookie同意の記録など、サイトの動作に不可欠なもの。無効にできません。</p></div>
        <label class="switch"><input type="checkbox" checked disabled><span class="switch__track"></span></label>
      </div>
      <div class="consent-row">
        <div><p class="consent-row__title">分析Cookie</p><p>ページの利用状況を統計的に把握し、サイト改善に役立てます(アクセス解析)。</p></div>
        <label class="switch"><input type="checkbox" id="consentAnalytics"><span class="switch__track"></span></label>
      </div>
      <div class="consent-row">
        <div><p class="consent-row__title">マーケティングCookie</p><p>興味・関心に基づく情報提供や、広告効果の測定に使用します。</p></div>
        <label class="switch"><input type="checkbox" id="consentMarketing"><span class="switch__track"></span></label>
      </div>
    </div>
    <div class="cluster">
      <button class="btn btn--primary" id="consentSave">選択を保存</button>
      <button class="btn btn--ghost" id="consentModalClose">閉じる</button>
    </div>
    <p class="t-micro t-faint">表示が崩れる、更新した内容が反映されない場合は<button type="button" class="cookie-settings-link clear-cache-trigger">キャッシュを削除</button>できます。</p>
  </div>
</div>
<div class="toast" id="toast" role="status" aria-live="polite"></div>"""


# フォントは非ブロッキング読み込み(media=print→onloadでall)。
# 取得がスタールしてもレンダリング・スクリプト実行を阻害しない。
HEAD_FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap"></noscript>"""


def render_page(url, title, desc, body, theme="dark", crumbs=None, group="その他", noindex=False):
    """共通レイアウトでページを組み立ててディスクに書き出す。"""
    full_title = f"{title} | {SITE_NAME}" if url != "/" else f"{SITE_NAME} 公式サイト | {title}"
    crumb_html = ""
    if crumbs:
        items = [('ホーム', '/')] + list(crumbs)
        lis = []
        for i, (label, href) in enumerate(items):
            if i == len(items) - 1 or not href:
                lis.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
            else:
                lis.append(f'<li><a href="{href}">{esc(label)}</a></li>')
        crumb_html = f'<nav class="breadcrumb" aria-label="パンくずリスト"><div class="container container--wide"><ol>{"".join(lis)}</ol></div></nav>'

    html = f"""<!DOCTYPE html>
<html lang="ja" data-theme="{theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta name="theme-color" content="{'#0b0b10' if theme == 'dark' else '#fafafc'}">
<link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
{HEAD_FONTS}
<link rel="stylesheet" href="/assets/css/tokens.css?v={ASSET_V}">
<link rel="stylesheet" href="/assets/css/base.css?v={ASSET_V}">
<link rel="stylesheet" href="/assets/css/components.css?v={ASSET_V}">
<link rel="stylesheet" href="/assets/css/animations.css?v={ASSET_V}">
</head>
<body class="page{url.rstrip('/').replace('/', '-') or '-home'}">
{header_html()}
{crumb_html}
<main id="main">
{body}
</main>
{footer_html()}
<script src="/assets/js/keys.js?v={ASSET_V}" defer></script>
<script src="/assets/js/fmt.js?v={ASSET_V}" defer></script>
<script src="/data/products.js?v={ASSET_V}" defer></script>
<script src="/assets/js/main.js?v={ASSET_V}" defer></script>
<script src="/assets/js/charts.js?v={ASSET_V}" defer></script>
<script src="/assets/js/store.js?v={ASSET_V}" defer></script>
<script src="/assets/js/pages.js?v={ASSET_V}" defer></script>
<script src="/assets/js/auth.js?v={ASSET_V}" defer></script>
</body>
</html>"""

    if url.endswith(".html"):
        out = ROOT / url.lstrip("/")
    elif url != "/":
        out = ROOT / url.strip("/") / "index.html"
    else:
        out = ROOT / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    if not noindex:
        PAGES.append({"url": url, "title": title, "desc": desc, "group": group})


# ==========================================================================
# 部品ビルダー
# ==========================================================================

def stats_html(stats, cols=4):
    cells = "".join(
        f"""<div class="stat"><p class="stat__value" data-count>{s['v']}<span class="unit">{s['u']}</span></p><p class="stat__label">{s['l']}</p></div>"""
        for s in stats)
    return f'<div class="stat-row reveal-stagger" style="--stat-cols:{cols}">{cells}</div>'


def sections_html(sections, glow="#e8442e"):
    out = []
    for i, sec in enumerate(sections):
        rev = " feature-split--rev" if i % 2 else ""
        pts = "".join(f"<li>{p}</li>" for p in sec.get("points", []))
        link = ""
        if sec.get("link"):
            link = f'<a class="link-arrow" href="{sec["link"][0]}">{sec["link"][1]}</a>'
        art = svg_art.svg_art(sec.get("art", "chip"), glow)
        out.append(f"""
<section class="section--sm">
  <div class="container">
    <div class="feature-split{rev}">
      <div class="feature-split__media reveal-scale">{art}</div>
      <div class="stack reveal">
        <p class="eyebrow">{sec['eyebrow']}</p>
        <h2 class="t-h2">{sec['title']}</h2>
        <p class="t-soft">{sec['body']}</p>
        <ul class="check-list">{pts}</ul>
        {link}
      </div>
    </div>
  </div>
</section>""")
    return "".join(out)


def spec_tables_html(specs):
    out = []
    for group, rows in specs:
        trs = "".join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
        out.append(f'<h3 class="spec-group-title">{group}</h3><div class="scroll-x"><table class="spec-table"><tbody>{trs}</tbody></table></div>')
    return "".join(out)


def product_card(p, show_price=True):
    line = LINES[p["line"]]
    badge = ""
    if p.get("flag") == "new":
        badge = '<span class="badge badge--new">NEW</span>'
    elif p["status"] == "old":
        badge = '<span class="badge badge--end">販売終了</span>'
    price = ""
    if show_price:
        price = (f'<p class="product-card__price">{yen(p["price"])} <small>(税込)〜</small></p>'
                 if p["status"] == "current" else '<p class="product-card__price t-faint">販売終了モデル</p>')
    url = product_url(p)
    return f"""<a class="product-card" href="{url}">
  <div class="product-card__media"><img src="/assets/img/products/{p['id']}-0.svg" alt="{esc(p['name'])}" loading="lazy" width="360" height="640"></div>
  <div class="product-card__body">
    <p class="product-card__tag">{line['label']} / {p['year']}</p>
    <p class="product-card__name">{esc(p['name'])} {badge}</p>
    <p class="product-card__copy">{esc(p['tagline'])}</p>
    {price}
  </div>
</a>"""


def product_url(p):
    seg = {"phone": "phone", "tablet": "tablet", "accessory": "accessories"}[p["cat"]]
    return f"/products/{seg}/{p['id']}/"


def cta_band(title, sub, buttons):
    btns = "".join(f'<a class="btn {cls}" href="{href}">{label}</a>' for label, href, cls in buttons)
    return f"""
<section class="section--sm">
  <div class="container">
    <div class="card card--flame t-center reveal" style="padding:clamp(40px,6vw,72px)">
      <h2 class="t-h2">{title}</h2>
      <p class="t-soft" style="max-width:560px;margin-inline:auto">{sub}</p>
      <div class="cluster cluster--center" style="margin-top:12px">{btns}</div>
    </div>
  </div>
</section>"""


# ==========================================================================
# 製品ページ
# ==========================================================================


def related_news_section(keywords, eyebrow="NEWSROOM", title="関連ニュース"):
    """キーワードに合致するニュース記事カード(最大3件)。合致なしなら空。"""
    hits = [n for n in NEWS if any(k and (k in n["title"] or k in n["excerpt"]) for k in keywords)][:3]
    if not hits:
        return ""
    cards = "".join(
        f'''<a class="card card--hover" href="/news/{n['id']}/">
<p class="t-micro t-faint">{n['date'].replace('-', '.')} <span class="badge" style="margin-left:8px">{n['cat']}</span></p>
<h3 class="t-h4">{esc(n['title'])}</h3>
<p class="t-small t-soft">{esc(n['excerpt'][:72])}…</p>
<p class="link-arrow">読む</p></a>'''
        for n in hits)
    return f'''
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">{eyebrow}</p><h2 class="t-h2">{title}</h2></div>
    <div class="grid grid--3 reveal-stagger">{cards}</div>
  </div>
</section>'''


def lineage_section(p):
    """同一ラインの系譜表(2世代以上あるデバイスのみ)。"""
    gens = sorted([x for x in ALL_PRODUCTS if x["cat"] == p["cat"] and x["line"] == p["line"]], key=lambda x: -x["year"])
    if len(gens) < 2:
        return ""
    rows = ""
    for g in gens:
        cur = g["id"] == p["id"]
        state = '<strong style="color:var(--accent)">現行</strong>' if g["status"] == "current" else '<span class="t-faint">販売終了</span>'
        name_cell = (f'<strong>{esc(g["name"])}(このページ)</strong>' if cur
                     else f'<a href="{product_url(g)}" style="color:var(--accent);font-weight:700">{esc(g["name"])}</a>')
        rows += (f'<tr><td>{name_cell}</td><td>{g["release"]}</td><td>{yen(g["price"])}</td>'
                 f'<td>{esc(get_spec(g, ["性能"], "SoC").split("(")[0])}</td><td>{state}</td></tr>')
    line = LINES[p["line"]]
    return f'''
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">LINEAGE</p><h2 class="t-h2">{line['label']}ラインの系譜</h2>
    <p class="t-soft t-small">初代から最新世代まで、このラインの歩みです。販売終了モデルのページもアーカイブとして公開しています。</p></div>
    <div class="scroll-x reveal"><table class="spec-table quick-table">
      <thead><tr><th scope="col">モデル</th><th scope="col">発売日</th><th scope="col">発売時価格</th><th scope="col">SoC</th><th scope="col">販売状況</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
  </div>
</section>'''


def cta_minimal(title, links):
    """カード帯を使わない軽い結び(技術ページ用 — 使い回し感の低減)。"""
    l = "".join(f'<a class="link-arrow" href="{h}">{txt}</a>' for txt, h in links)
    return (f'<section class="section--sm"><div class="container t-center" '
            f'style="display:grid;gap:16px;justify-items:center"><hr class="divider" style="width:min(320px,60%)">' 
            f'<h2 class="t-h3">{title}</h2><div class="cluster cluster--center" style="gap:26px">{l}</div></div></section>')


def build_product_page(p):
    line = LINES[p["line"]]
    glow = line["glow"]
    url = product_url(p)
    is_device = p["cat"] in ("phone", "tablet")
    cat_label = {"phone": "スマートフォン", "tablet": "タブレット", "accessory": "アクセサリ"}[p["cat"]]
    cat_url = {"phone": "/products/phone/", "tablet": "/products/tablet/", "accessory": "/products/accessories/"}[p["cat"]]

    # --- 購入モジュール ---
    swatches = "".join(
        f'<button type="button" class="swatch{" is-active" if i == 0 else ""}" data-color-index="{i}" style="--swatch:{c["hex"]}" aria-label="{esc(c["name"])}" title="{esc(c["name"])}"></button>'
        for i, c in enumerate(p["colors"]))
    storages = "".join(f"""
      <label class="choice">
        <input type="radio" name="storage" value="{i}" {"checked" if i == 0 else ""}>
        <span class="choice__radio"></span>
        <span class="choice__body"><span class="choice__title">{esc(s['label'])}</span></span>
        <span class="choice__price">{yen(p['price'] + s['delta'])}</span>
      </label>""" for i, s in enumerate(p["storage"])) if p["storage"] else ""

    if p["status"] == "current":
        buy_actions = f"""
        <p class="buy-price"><span id="buyPrice">{yen(p['price'])}</span> <small class="t-faint">(税込)</small></p>
        <p class="t-micro t-faint">分割払い(24回)例: 月々 {yen(round(p['price'] / 24 // 10 * 10))} 〜 / 5,000円以上で送料無料</p>
        <div class="cluster">
          <button class="btn btn--primary btn--lg" id="addToCart">カートに追加</button>
          {'<a class="btn btn--ghost btn--lg" href="' + url + 'specs/">スペックを見る</a>' if is_device else ''}
        </div>"""
    else:
        newest = [x for x in ALL_PRODUCTS if x["line"] == p["line"] and x["status"] == "current"]
        alt = f'<a class="btn btn--primary" href="{product_url(newest[0])}">現行モデル {esc(newest[0]["name"])} を見る</a>' if newest else ""
        buy_actions = f"""
        <div class="notice"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3z"/><path d="M12 10.5v4M12 17.6h.01"/></svg> {esc(p['name'])} は販売を終了しました。仕様の記録としてページを公開しています。</div>
        <div class="cluster">{alt}
          {'<a class="btn btn--ghost" href="' + url + 'specs/">スペックを見る</a>' if is_device else ''}
        </div>"""

    color_names = " / ".join(c["name"] for c in p["colors"])
    buy_box = f"""
<section class="section--sm" id="buy">
  <div class="container">
    <div class="buy-grid" data-product="{p['id']}">
      <div class="buy-media reveal-l"><img id="buyImage" src="/assets/img/products/{p['id']}-0.svg" alt="{esc(p['name'])}" width="360" height="640"></div>
      <div class="stack reveal-r">
        <p class="eyebrow">{line['label']}</p>
        <h2 class="t-h3">{esc(p['name'])} を構成する</h2>
        <div class="field"><label>カラー — <span id="colorName">{esc(p['colors'][0]['name'])}</span>(全{len(p['colors'])}色: {esc(color_names)})</label>
          <div class="cluster">{swatches}</div></div>
        {'<div class="field"><label>メモリとストレージ</label><div class="choice-grid">' + storages + '</div></div>' if storages else ''}
        {buy_actions}
        <p class="t-micro t-faint">発売日: {p['release']} / 型番: SZ-{p['id'].upper().replace('-', '')}</p>
      </div>
    </div>
  </div>
</section>"""

    # --- 関連製品 ---
    same_line = [x for x in ALL_PRODUCTS if x["line"] == p["line"] and x["id"] != p["id"]]
    cross = []
    if p["cat"] == "phone":
        cross = [x for x in ACCESSORIES if x["status"] == "current"][:3]
    elif p["cat"] == "tablet":
        cross = [x for x in ACCESSORIES if x["id"] in ("grip-pro", "buds", "raisoku-charger")]
    related_cards = "".join(product_card(x) for x in (same_line[:3] + cross[: max(0, 3 - len(same_line))]))
    related = f"""
<section class="section section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">RELATED</p><h2 class="t-h2">あわせて見たい製品</h2></div>
    <div class="grid grid--3 grid--cards reveal-stagger">{related_cards}</div>
  </div>
</section>""" if related_cards else ""

    chip_link = ""
    if p.get("chip"):
        chip = next(t for t in TECHS if t["id"] == p["chip"])
        chip_link = f'<a class="btn btn--ghost" href="/tech/cpu/{p["chip"]}/">搭載SoC {esc(chip["name"])} を見る</a>'

    # --- データセクション(グラフ+表) ---
    data_section = ""
    if is_device:
        gens = sorted([x for x in ALL_PRODUCTS if x["cat"] == p["cat"] and x["line"] == p["line"]], key=lambda x: x["year"])
        g_labels = [f"{x['name']}({x['year']})" for x in gens]
        antutu_vals = [product_antutu(x) or 0 for x in gens]
        bat_vals = [num(get_spec(x, ["バッテリー"], "バッテリー容量")) for x in gens]
        hi = next(i for i, x in enumerate(gens) if x["id"] == p["id"])
        charts_html = ""
        if len(gens) >= 2 and all(antutu_vals):
            charts_html += chart({"type": "bar", "title": f"{line['label']}ライン — AnTuTuスコアの世代比較", "unit": "万点",
                                  "labels": g_labels, "values": antutu_vals, "highlight": hi})
        if len(gens) >= 2 and all(bat_vals):
            charts_html += chart({"type": "bar", "title": "バッテリー容量の世代推移", "unit": "mAh",
                                  "labels": g_labels, "values": bat_vals, "highlight": hi})
        charts_html += chart({"type": "radar", "title": f"{p['name']} 性能バランス(5軸・当社評価)",
                              "axes": RADAR_AXES, "series": [{"name": p["name"], "values": radar_values(p)}]})
        data_section = f"""
<section class="section--sm" id="data">
  <div class="container">
    <div class="section-head"><p class="eyebrow">DATA</p><h2 class="t-h2">数字は、嘘をつかない。</h2>
    <p class="t-soft t-small">スコア・容量は当社測定条件による参考値です。完全な仕様は<a href="{url}specs/" style="color:var(--accent);text-decoration:underline">スペックページ</a>へ。</p></div>
    <div class="chart-grid">{charts_html}</div>
  </div>
</section>"""
        # ラインの性格を構成に反映する固有セクション
        if p["line"] in GAMING_LINES:
            data_section += game_fps_section(p)
        elif p["line"] in LIFE_LINES:
            data_section += battery_life_section(p)
    elif p["id"] in ACC_CHARTS:
        # アクセサリ: 製品ごとに異なる比較グラフ
        data_section = f"""
<section class="section--sm" id="data">
  <div class="container">
    <div class="section-head"><p class="eyebrow">DATA</p><h2 class="t-h2">数字で見る、{esc(p['name'])}。</h2></div>
    <div class="chart-grid">{chart(ACC_CHARTS[p['id']])}</div>
    <p class="t-micro t-faint" style="margin-top:14px">当社試験条件による参考値です。比較対象は市場の一般的な製品カテゴリの代表値。</p>
  </div>
</section>"""

    # --- 全幅ビジュアルブレイク ---
    bleed_claims = {
        "suzaku": "勝敗を分ける0.01秒のために。",
        "neo": "価格のために、性能は捨てない。",
        "tsubame": "テクノロジーは、そっと寄り添うもの。",
        "lite": "良いものは、高くなくていい。",
        "pad": "大画面は、没入の別名だ。",
        "pad-neo": "どこへでも、戦場を持ち出せ。",
        "t-pad": "家族の時間の、真ん中に。",
        "t-pad-lite": "気軽さこそ、最強の機能。",
    }
    bleed = ""
    if is_device:
        bleed = f"""
<section class="full-bleed" style="--bleed-glow:{glow}59">
  <p class="eyebrow eyebrow--center" style="justify-content:center">{esc(p['kana'])} / {p['year']}</p>
  <h2 class="reveal-scale reveal">{esc(bleed_claims.get(p['line'], p['tagline']))}</h2>
</section>"""

    # --- 同梱物 + 製品FAQ + 対応アクセサリ + サポート ---
    box_html = "".join(f"<li>{esc(x)}</li>" for x in box_items(p))
    faq_items = LINE_FAQ.get(p["line"], LINE_FAQ["acc"])
    faq_html = "".join(
        f'<div class="accordion__item"><button class="accordion__q" aria-expanded="false"><span>{esc(q)}</span></button>'
        f'<div class="accordion__a"><div class="accordion__a-inner"><div class="accordion__a-body"><p>{a}</p></div></div></div></div>'
        for q, a in faq_items)
    extras = f"""
<div class="band-light" data-theme="light">
<section class="section--sm">
  <div class="container">
    <div class="feature-split" style="align-items:start">
      <div class="stack reveal">
        <p class="eyebrow">IN THE BOX</p>
        <h2 class="t-h2">同梱物</h2>
        <ul class="check-list">{box_html}</ul>
        <p class="t-micro t-faint">パッケージはプラスチック使用量を98%削減した再生紙製です。<a href="/sustainability/" style="color:var(--accent)">環境への取り組み</a></p>
      </div>
      <div class="stack reveal">
        <p class="eyebrow">Q&amp;A</p>
        <h2 class="t-h2">よくある質問</h2>
        <div class="accordion">{faq_html}</div>
        <a class="link-arrow" href="/support/faq/">すべてのFAQを見る</a>
      </div>
    </div>
  </div>
</section>"""
    if is_device:
        extras += f"""
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">ACCESSORIES</p><h2 class="t-h2">{esc(p['name'])} で使える純正アクセサリ</h2></div>
    {acc_compat_table(p)}
  </div>
</section>"""
    extras += """
<section class="section--sm">
  <div class="container">
    <div class="grid grid--3 reveal-stagger">
      <a class="card card--hover" href="/support/warranty/">
        <div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l7 4v5c0 4.5-3 8-7 9-4-1-7-4.5-7-9V7z"/><path d="M9.5 12l2 2 3.5-4"/></svg></div>
        <h3 class="t-h4">1年保証 + SUZAKU Care+</h3><p class="t-small t-soft">標準で1年間のメーカー保証。Care+なら落下・水濡れもカバー。</p><p class="link-arrow">保証を見る</p></a>
      <a class="card card--hover" href="/support/repair/">
        <div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 6.5a4 4 0 0 0-5.6 5L4 16.4V20h3.6l4.9-4.9a4 4 0 0 0 5-5.6L15 12l-3-3z"/></svg></div>
        <h3 class="t-h4">最短即日修理</h3><p class="t-small t-soft">秋葉原サービスセンターで画面・電池交換は即日。配送修理も5〜7営業日。</p><p class="link-arrow">修理を申し込む</p></a>
      <a class="card card--hover" href="/sustainability/recycle/">
        <div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21c-5 0-8-3.5-8-8 0-5.5 4.5-9.5 8-10 3.5.5 8 4.5 8 10 0 4.5-3 8-8 8z"/><path d="M12 21c2-3 3-6.5 3-10"/></svg></div>
        <h3 class="t-h4">使い終わったら無償回収</h3><p class="t-small t-soft">古い端末はメーカー問わず無償回収。資源の96%を再利用します。</p><p class="link-arrow">回収について</p></a>
    </div>
  </div>
</section>
</div>"""

    # --- カラーギャラリー(2色以上のデバイス) ---
    color_gallery = ""
    if is_device and len(p["colors"]) >= 2:
        gcards = "".join(
            f"""<figure class="color-card reveal"><img src="/assets/img/products/{p['id']}-{i}.svg" alt="{esc(p['name'])} {esc(c['name'])}" loading="lazy" width="360" height="640"><figcaption><i style="--swatch:{c['hex']}"></i>{esc(c['name'])}</figcaption></figure>"""
            for i, c in enumerate(p["colors"]))
        color_gallery = f"""
<section class="section--sm" id="colors">
  <div class="container">
    <div class="section-head"><p class="eyebrow">COLORS</p><h2 class="t-h2">{len(p['colors'])}つの色。どれも、{esc(p['kana'].split(' ')[0])}。</h2></div>
    <div class="color-gallery">{gcards}</div>
    {'<div class="cluster" style="margin-top:20px"><a class="btn btn--primary" href="#buy">カラーを選んで購入する</a></div>' if p['status'] == 'current' else ''}
  </div>
</section>"""

    # --- ローカルナビ(Apple式・PCのみ表示) ---
    local_links = '<a href="#buy">構成と価格</a>' if p["status"] == "current" else ""
    if is_device:
        local_links += '<a href="#data">性能データ</a>'
        if len(p["colors"]) >= 2:
            local_links += '<a href="#colors">カラー</a>'
        local_links += f'<a href="{url}specs/">仕様</a>'
    local_links += '<a href="/products/compare/">比較</a>'
    local_cta = (f'<span class="localnav__price">{yen(p["price"])}〜</span><a class="btn btn--primary btn--sm" href="#buy">購入へ</a>'
                 if p["status"] == "current" else '<span class="badge badge--end">販売終了</span>')
    localnav = f"""
<div class="localnav" id="localnav" aria-hidden="true">
  <div class="localnav__inner">
    <span class="localnav__name">{esc(p['name'])}</span>
    <nav class="localnav__links" aria-label="{esc(p['name'])}内のセクション">{local_links}</nav>
    {local_cta}
  </div>
</div>"""

    # --- 注記(Apple式footnotes) ---
    note_items = [
        "価格はすべて消費税込みの当社直販価格です。分割払いの月額は24回均等払いの概算で、手数料はカード会社の規定によります。",
        "バッテリー駆動時間は輝度50%・Wi-Fi接続・当社試験環境での測定値です。使用状況・経年により変動します。",
        "ベンチマークスコア・温度・fpsは室温25℃の当社試験環境での測定値であり、性能を保証するものではありません。",
    ]
    if p["line"] in GAMING_LINES:
        note_items.append("実測パフォーマンスの検証タイトルは実在のゲームではなく、当社のベンチマーク用シナリオです。ファン動作音は無響室での測定値です。")
    if is_device:
        note_items.append("防塵防水性能は当社試験条件によるもので、無故障・無破損を保証するものではありません。水没・砂塵環境でのご使用はお避けください。")
    note_items.append("本サイトは架空企業のデモンストレーションであり、記載のすべての製品・数値はフィクションです。")
    footnotes = ('<section class="section--sm"><div class="container container--narrow">'
                 '<hr class="divider" style="margin-bottom:22px"><ol class="footnotes">'
                 + "".join(f"<li>{n}</li>" for n in note_items) + "</ol></div></section>")

    # --- フローティング購入バー(現行モデルのみ) ---
    buy_float = ""
    if p["status"] == "current":
        buy_float = f"""
<div class="buy-float" id="buyFloat" aria-hidden="true">
  <div class="buy-float__inner">
    <img src="/assets/img/products/{p['id']}-0.svg" alt="" width="36" height="52" style="height:44px;width:auto">
    <div>
      <p class="buy-float__name">{esc(p['name'])}</p>
      <p class="buy-float__price">{yen(p['price'])}(税込)〜</p>
    </div>
    <a class="btn btn--primary btn--sm" href="#buy">購入へ</a>
  </div>
</div>"""

    body = f"""
<section class="hero hero--sub" style="--line-glow:{glow}">
  <div class="hero__bg hero__bg--glow" style="background:
    radial-gradient(52% 42% at 50% 66%, {glow}44, transparent 70%),
    radial-gradient(40% 32% at 80% 12%, rgba(217,164,65,0.08), transparent 70%),
    var(--bg-deep)"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">{line['label']} — {p['year']}</p>
    <h1 class="t-hero">{esc(p['name'])}</h1>
    <p class="t-lead" style="max-width:640px">{esc(p['tagline'])}<br><span class="t-small">{esc(p['sub'])}</span></p>
    <div class="hero__actions">
      {'<a class="btn btn--primary btn--lg" href="#buy">' + yen(p['price']) + '(税込)〜 購入へ</a>' if p['status'] == 'current' else '<span class="badge badge--end">販売終了モデル</span>'}
      {chip_link}
    </div>
    {f'<img class="hero-device" src="/assets/img/products/{p["id"]}-0.svg" alt="{esc(p["name"])}" width="340" height="600">' if is_device else ''}
  </div>
</section>
<section class="section--sm"><div class="container">{stats_html(p['stats'])}</div></section>
{buy_box}
{bleed}
{color_gallery}
{sections_html(p['sections'], glow)}
{data_section}
{lineage_section(p) if is_device else ''}
{extras}
{f'''<section class="section--sm"><div class="container"><div class="card t-center" style="padding:clamp(32px,5vw,56px)"><h2 class="t-h3">すべての仕様を確認する</h2><p class="t-soft">サイズ・性能・カメラ・通信仕様の完全なリストをご用意しています。</p><div class="cluster cluster--center"><a class="btn btn--primary" href="{url}specs/">{esc(p['name'])} の仕様を見る</a><a class="btn btn--ghost" href="/products/compare/">他のモデルと比較する</a></div></div></div></section>''' if is_device else ''}
{related}
{related_news_section([p['name']], title=f"{esc(p['name'])} のニュース")}
{cta_band(*(
    ('次の勝利は、ストアから。', '全国送料無料。氷嵐クーラーやGrip Proとの同時購入で、装備を一気にそろえられます。')
    if p['line'] in GAMING_LINES else
    ('毎日の相棒を、ストアで。', '全国送料無料(5,000円以上)。14日間の返品保証と1年間のメーカー保証付き。')
    if p['line'] in LIFE_LINES else
    ('本体と、そろえて。', 'ストアなら本体とアクセサリをまとめて一度に受け取れます。5,000円以上で送料無料。')
), [('ストアで見る', '/store/', 'btn--primary'), ('購入ガイド', '/store/guide/', 'btn--ghost')])}
{footnotes}
{localnav}
{buy_float}
"""
    crumbs = [("製品", "/products/"), (cat_label, cat_url), (p["name"], None)]
    render_page(url, f"{p['name']} — {p['tagline']}", p["sub"], body, "dark", crumbs, "製品")

    # --- specsページ(スマホ・タブレットのみ) ---
    if is_device:
        spec_body = f"""
<section class="hero hero--page">
  <div class="hero__inner hero-enter">
    <p class="eyebrow">{line['label']}</p>
    <h1 class="t-h1">{esc(p['name'])} — 仕様</h1>
    <p class="t-soft">発売日: {p['release']} / {'税込 ' + yen(p['price']) + '〜' if p['status'] == 'current' else '販売終了'}</p>
    <div class="cluster">
      <a class="btn btn--primary" href="{url}#buy">{'購入ページへ' if p['status'] == 'current' else '製品ページへ'}</a>
      <a class="btn btn--ghost" href="/products/compare/">比較する</a>
    </div>
  </div>
</section>
<section class="section--sm"><div class="container container--narrow reveal">{spec_tables_html(p['specs'])}
<p class="t-micro t-faint" style="margin-top:28px">記載の数値は当社測定条件による設計値です。使用環境により変動する場合があります。バッテリー持続時間は輝度50%・Wi-Fi接続時の当社試験値です。</p>
</div></section>
{cta_band('この仕様を、あなたの手に。', 'SUZAKU ストアなら全モデル送料無料でお届けします。', [('ストアで見る', '/store/', 'btn--primary'), (p['name'] + ' 製品ページ', url, 'btn--ghost')])}
"""
        render_page(url + "specs/", f"{p['name']} 仕様", f"{p['name']}の詳細スペック一覧。サイズ、性能、ディスプレイ、カメラ、バッテリー、通信仕様。",
                    spec_body, "dark", crumbs[:-1] + [(p["name"], url), ("仕様", None)], "製品")


# ==========================================================================
# 技術ページ
# ==========================================================================

TECH_HUBS = {
    "cpu": {"title": "雷 RAI", "en": "CPU / SoC", "path": "/tech/cpu/",
            "desc": "自社SoCシリーズ「雷」。旗艦のG1〜G4に加え、エントリー専用のE1/E2まで — 全価格帯を自社シリコンで。"},
    "gpu": {"title": "焔 HOMURA", "en": "GPU", "path": "/tech/gpu/",
            "desc": "自社GPUシリーズ「焔」。レイトレ対応のX系と省電力Lite系、2つのアーキテクチャの進化史。"},
    "memory": {"title": "疾風 HAYATE", "en": "MEMORY", "path": "/tech/memory/",
               "desc": "SoCと同時設計される自社メモリシリーズ「疾風」。エントリーのL1からLPDDR6のM2まで。"},
    "storage": {"title": "瞬 SHUN", "en": "STORAGE", "path": "/tech/storage/",
                "desc": "ロード時間を消しにいく自社ストレージシリーズ「瞬」。エントリーのL1から読込5,800MB/sのS2まで。"},
    "cooling": {"title": "冷却技術", "en": "COOLING", "path": "/tech/cooling/",
                "desc": "氷刃・旋風・液焔・水龍。4つの冷却技術シリーズが、性能の持続を支えます。"},
    "camera": {"title": "天眼 TENGAN", "en": "CAMERA", "path": "/tech/camera/",
               "desc": "自社イメージセンサー「天眼」と神楽ISPによる、SUZAKUのイメージングシステム。"},
}

TYPE_GLOW = {"cpu": "#e8442e", "gpu": "#ff8a3d", "memory": "#3d8bff", "storage": "#38b6a5",
             "cooling": "#4fc3f7", "camera": "#d9a441"}


def tech_bench_charts(t):
    """技術ページ用の世代比較チャート群を生成。"""
    def gen_bar(title, unit, table, fmt=lambda v: v):
        gens = [x for x in TECHS if x["hub"] == t["hub"] and x["id"] in table]
        gens.sort(key=lambda x: x["year"])
        labels = [f"{x['name']}({x['year']})" for x in gens]
        values = [fmt(table[x["id"]]) for x in gens]
        hi = next((i for i, x in enumerate(gens) if x["id"] == t["id"]), None)
        cfg = {"type": "bar", "title": title, "unit": unit, "labels": labels, "values": values}
        if hi is not None:
            cfg["highlight"] = hi
        return chart(cfg)

    out = ""
    if t["id"].startswith("rai-e"):
        hi = 0 if t["id"] == "rai-e1" else 1
        out += chart({"type": "bar", "title": "雷 RAI-Eシリーズ — AnTuTuスコア(参考: 省電力版G4A)", "unit": "万点",
                      "labels": ["RAI-E1(2025)", "RAI-E2(2026)", "参考: RAI-G4A"], "values": [62, 85, 285], "highlight": hi})
        out += chart({"type": "bar", "title": "動画連続再生時間(搭載エントリー機の実測)", "unit": "時間",
                      "labels": ["RAI-E1 搭載機", "RAI-E2 搭載機"], "values": [20, 22], "highlight": hi if hi < 2 else 1})
        return out
    if t["id"].startswith("homura-l"):
        hi = 0 if t["id"] == "homura-l1" else 1
        out += chart({"type": "bar", "title": "焔 Liteシリーズ — 理論演算性能(参考: X2)", "unit": "TFLOPS",
                      "labels": ["HOMURA-L1(2025)", "HOMURA-L2(2026)", "参考: HOMURA-X2"], "values": [0.35, 0.5, 1.6], "highlight": hi})
        return out
    if t["id"] == "hayate-l1":
        out += chart({"type": "bar", "title": "エントリー帯メモリの転送速度比較", "unit": "Mbps",
                      "labels": ["一般的なLPDDR4X", "疾風 HAYATE-L1", "参考: HAYATE-M1"], "values": [4266, 6400, 8533], "highlight": 1})
        return out
    if t["id"] == "shun-l1":
        out += chart({"type": "bar", "title": "エントリー帯ストレージの読込速度比較", "unit": "MB/s",
                      "labels": ["eMMC 5.1", "瞬 SHUN-L1", "参考: SHUN-S1"], "values": [300, 2100, 4300], "highlight": 1})
        return out
    if t["hub"] == "cpu":
        out += gen_bar("雷シリーズ — AnTuTuスコアの世代比較", "万点", ANTUTU)
        out += gen_bar("神楽NPU 推論性能の世代比較", "TOPS", NPU_TOPS)
    elif t["hub"] == "gpu":
        out += gen_bar("焔シリーズ — 理論演算性能の世代比較", "TFLOPS", TFLOPS)
    elif t["hub"] == "memory":
        out += gen_bar("疾風シリーズ — 転送速度の世代比較", "Mbps", MEM_MBPS)
    elif t["hub"] == "storage":
        out += gen_bar("瞬シリーズ — シーケンシャル読込の世代比較", "MB/s", SSD_MBS)
    elif t["id"] == "hyojin":
        out += chart({"type": "bar", "title": "ベイパーチャンバー面積の世代推移", "unit": "mm²",
                      "labels": [k for k, _ in VC_AREA], "values": [v for _, v in VC_AREA], "highlight": 3})
        out += chart({"type": "bar", "title": "表面温度の低下量(当社試験・世代比較)", "unit": "℃",
                      "labels": [k for k, _ in COOL_DELTA], "values": [v for _, v in COOL_DELTA], "highlight": 3})
    elif t["id"] == "senpu":
        out += chart({"type": "bar", "title": "旋風ファン 回転数の世代推移", "unit": "rpm",
                      "labels": [k for k, _ in FAN_RPM], "values": [v for _, v in FAN_RPM], "highlight": 2})
    elif t["id"] == "ekien":
        out += chart({"type": "bar", "title": "サーマル素材の熱伝導率比較", "unit": "W/mK",
                      "labels": ["シリコングリス", "サーマルシート", "液焔(液体金属)"], "values": [4.2, 12, 73], "highlight": 2})
    elif t["id"] == "suiryu":
        out += chart({"type": "bar", "title": "熱輸送量の相対比較(氷刃V4 = 100)", "unit": "",
                      "labels": ["氷刃 V1(2023)", "氷刃 V4(2026)", "水龍(2027予定)"], "values": [52, 100, 320], "highlight": 2})
    elif t["id"] == "tengan-rs2":
        out += chart({"type": "bar", "title": "センサー相対受光面積(RS-1 = 100)", "unit": "",
                      "labels": ["天眼 RS-1(1/1.5型)", "天眼 RS-2(1/1.28型)"], "values": [100, 137], "highlight": 1})
    elif t["id"] == "tengan-rs1":
        out += chart({"type": "bar", "title": "センサー相対受光面積(RS-1 = 100)", "unit": "",
                      "labels": ["天眼 RS-1(1/1.5型)", "天眼 RS-2(1/1.28型)"], "values": [100, 137], "highlight": 0})
    return out


def build_tech_page(t):
    """技術詳細ページ — 左サイド目次(章立て)+ 右本文のドキュメント型レイアウト。"""
    hub = TECH_HUBS[t["hub"]]
    glow = TYPE_GLOW[t["type"]]
    url = f"/tech/{t['hub']}/{t['id']}/"
    hero_art = svg_art.svg_die(t["id"], t["en"], f"SUZAKU {t['type'].upper()} / {t['year']}", glow) \
        if t["type"] in ("cpu", "gpu", "memory", "storage") else svg_art.svg_art(
            {"cooling": "cooling", "camera": "camera"}.get(t["type"], "chip"), glow)
    if t["id"] == "senpu":
        hero_art = svg_art.svg_art("fan", glow)
    if t["id"] in ("ekien", "suiryu"):
        hero_art = svg_art.svg_art("liquid", glow)

    bench = tech_bench_charts(t)

    # 目次
    toc = ['<a href="#overview">概要と主要数値</a>']
    if bench:
        toc.append('<a href="#bench">ベンチマーク・世代比較</a>')
    sec_html = []
    for i, sec in enumerate(t["sections"]):
        title_plain = re.sub(r"<[^>]+>", "", sec["title"])
        toc.append(f'<a href="#sec-{i}">{esc(title_plain)}</a>')
        rev = " feature-split--rev" if i % 2 else ""
        pts = "".join(f"<li>{p}</li>" for p in sec.get("points", []))
        link = f'<a class="link-arrow" href="{sec["link"][0]}">{sec["link"][1]}</a>' if sec.get("link") else ""
        sec_html.append(f"""
<div class="feature-split{rev}" id="sec-{i}" style="scroll-margin-top:90px">
  <div class="feature-split__media reveal-scale">{svg_art.svg_art(sec.get('art', 'chip'), glow)}</div>
  <div class="stack reveal">
    <p class="eyebrow">{sec['eyebrow']}</p>
    <h2 class="t-h3">{sec['title']}</h2>
    <p class="t-soft t-small">{sec['body']}</p>
    <ul class="check-list">{pts}</ul>
    {link}
  </div>
</div>""")
    toc.append('<a href="#spec">仕様</a>')

    prods = [x for x in ALL_PRODUCTS if x["id"] in t.get("products", [])]
    prods_html = ""
    if prods:
        toc.append('<a href="#products">搭載製品</a>')
        prods_html = f"""
<div id="products" style="scroll-margin-top:90px">
  <h2 class="t-h3" style="margin-bottom:18px">{esc(t['name'])} 搭載製品</h2>
  <div class="grid grid--3 grid--cards reveal-stagger">{''.join(product_card(x) for x in prods[:3])}</div>
</div>"""

    siblings = sorted([x for x in TECHS if x["hub"] == t["hub"] and x["id"] != t["id"]], key=lambda x: -x["year"])
    sib_side = "".join(
        f'<a href="/tech/{x["hub"]}/{x["id"]}/">{esc(x["name"])}<small style="color:var(--text-faint)">({x["year"]})</small></a>'
        for x in siblings)

    body = f"""
<section class="hero hero--page">
  <div class="hero__inner hero-enter">
    <p class="eyebrow">{hub['en']} — {t['announce']} 発表</p>
    <h1 class="t-display">{esc(t['name'])}</h1>
    <p class="t-lead" style="max-width:680px">{esc(t['tagline'])}</p>
    <p class="t-soft t-small" style="max-width:680px">{esc(t['sub'])}</p>
  </div>
</section>
<section class="section--sm section--flush-top" style="padding-top:var(--sp-5)">
  <div class="container">
    <div class="doc-layout">
      <aside class="doc-side">
        <p class="doc-side__title">このページの内容</p>
        {''.join(toc)}
        <p class="doc-side__title">{hub['title']} の他の世代</p>
        {sib_side}
        <p class="doc-side__title">シリーズ</p>
        <a href="{hub['path']}">{hub['title']} トップ</a>
        <a href="/tech/">テクノロジー トップ</a>
      </aside>
      <div class="stack" style="gap:var(--sp-8)">
        <div id="overview" style="scroll-margin-top:90px" class="stack stack--lg">
          <div class="chip-visual reveal-scale" style="max-width:520px">{hero_art}</div>
          {stats_html(t['stats'])}
        </div>
        {f'<div id="bench" style="scroll-margin-top:90px" class="chart-grid">{bench}</div>' if bench else ''}
        {''.join(sec_html)}
        <div id="spec" style="scroll-margin-top:90px" class="reveal">{spec_tables_html(t['specs'])}</div>
        {prods_html}
      </div>
    </div>
  </div>
</section>
{related_news_section([t['name'], t['en']], title=f"{esc(t['name'])} 関連ニュース")}
{cta_minimal('技術は、体験のためにある。', [('搭載製品をストアで見る', '/store/'), (hub['title'] + ' トップ', hub['path']), ('テクノロジー トップ', '/tech/')])}
"""
    crumbs = [("テクノロジー", "/tech/"), (hub["title"], hub["path"]), (t["name"], None)]
    render_page(url, f"{t['name']} — {t['tagline']}", t["sub"], body, "dark", crumbs, "テクノロジー")


HUB_TRENDS = {
    "cpu": [("AnTuTuスコアの推移", "万点", ANTUTU), ("最大クロックの推移", "GHz", CLOCK), ("神楽NPU 推論性能の推移", "TOPS", NPU_TOPS)],
    "gpu": [("理論演算性能の推移", "TFLOPS", TFLOPS)],
    "memory": [("転送速度の推移", "Mbps", MEM_MBPS)],
    "storage": [("シーケンシャル読込の推移", "MB/s", SSD_MBS)],
}


def build_tech_hub(hub_key):
    """技術ハブ — 世代タイムライン横スクロール + トレンドグラフ。"""
    hub = TECH_HUBS[hub_key]
    glow = TYPE_GLOW[hub_key]
    gens = sorted([t for t in TECHS if t["hub"] == hub_key], key=lambda x: x["year"])

    # 世代タイムライン(古い→新しい、横スクロール)
    rail_cards = "".join(f"""
<a class="card card--hover" href="/tech/{hub_key}/{t['id']}/">
  <p class="gen-rail__year">{t['year']}</p>
  <h2 class="t-h3">{esc(t['name'])}</h2>
  <p class="t-soft t-small">{esc(t['tagline'])}</p>
  <p class="t-micro t-faint">{esc(t['sub'][:64])}…</p>
  <p class="link-arrow">技術詳細を見る</p>
</a>""" for t in gens)

    # トレンド折れ線グラフ
    trend_charts = ""
    for title, unit, table in HUB_TRENDS.get(hub_key, []):
        pts = [(t["year"], table[t["id"]]) for t in gens if t["id"] in table]
        if len(pts) >= 2:
            trend_charts += chart({"type": "line", "title": f"{hub['title']} — {title}", "unit": unit, "area": True,
                                   "labels": [f"{y}年" for y, _ in pts], "series": [{"name": hub["title"], "values": [v for _, v in pts]}]})
    if hub_key == "cpu":
        trend_charts += chart({"type": "bar", "title": "エントリー向け 雷 RAI-Eシリーズ(参考: 省電力版G4A)", "unit": "万点",
                               "labels": ["RAI-E1(2025)", "RAI-E2(2026)", "参考: RAI-G4A"], "values": [62, 85, 285], "highlight": 1})
    if hub_key == "gpu":
        trend_charts += chart({"type": "bar", "title": "省電力Liteシリーズ 焔 HOMURA-L", "unit": "TFLOPS",
                               "labels": ["HOMURA-L1(2025)", "HOMURA-L2(2026)", "参考: HOMURA-X2"], "values": [0.35, 0.5, 1.6], "highlight": 1})
    if hub_key == "memory":
        trend_charts += chart({"type": "bar", "title": "エントリー向け 疾風 HAYATE-L1", "unit": "Mbps",
                               "labels": ["一般的なLPDDR4X", "HAYATE-L1", "HAYATE-M2"], "values": [4266, 6400, 10667], "highlight": 1})
    if hub_key == "storage":
        trend_charts += chart({"type": "bar", "title": "エントリー向け 瞬 SHUN-L1", "unit": "MB/s",
                               "labels": ["eMMC 5.1", "SHUN-L1", "SHUN-S2"], "values": [300, 2100, 5800], "highlight": 1})
    if hub_key == "cooling":
        trend_charts += chart({"type": "line", "title": "氷刃 ベイパーチャンバー面積の推移", "unit": "mm²", "area": True,
                               "labels": ["2023年", "2024年", "2025年", "2026年"],
                               "series": [{"name": "氷刃", "values": [v for _, v in VC_AREA]}]})
        trend_charts += chart({"type": "bar", "title": "表面温度の低下量(当社試験)", "unit": "℃",
                               "labels": [k for k, _ in COOL_DELTA], "values": [v for _, v in COOL_DELTA], "highlight": 3})
    if hub_key == "camera":
        trend_charts += chart({"type": "bar", "title": "センサー相対受光面積(RS-1 = 100)", "unit": "",
                               "labels": ["天眼 RS-1(2024)", "天眼 RS-2(2025)"], "values": [100, 137], "highlight": 1})

    trend_html = f"""
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">TREND</p><h2 class="t-h2">数字で見る進化</h2></div>
    <div class="chart-grid">{trend_charts}</div>
  </div>
</section>""" if trend_charts else ""

    body = f"""
<section class="hero hero--sub">
  <div class="hero__bg hero__bg--glow" style="background:radial-gradient(50% 40% at 50% 70%, {glow}3d, transparent 70%), var(--bg-deep)"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">{hub['en']}</p>
    <h1 class="t-hero">{hub['title']}</h1>
    <p class="t-lead" style="max-width:660px">{hub['desc']}</p>
  </div>
</section>
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">GENERATIONS</p><h2 class="t-h2">世代タイムライン</h2>
    <p class="t-soft t-small">横にスクロールして、{gens[0]['year']}年から{gens[-1]['year']}年までの進化をたどれます。</p></div>
    <div class="gen-rail">{rail_cards}</div>
  </div>
</section>
{trend_html}
{cta_band('すべての技術は、つながっている。', 'SoC・メモリ・冷却・OSの垂直統合こそ、SUZAKUの体験の正体です。', [('テクノロジー トップ', '/tech/', 'btn--primary'), ('製品を見る', '/products/', 'btn--ghost')])}
"""
    render_page(hub["path"], f"{hub['title']}({hub['en']})", hub["desc"], body, "dark",
                [("テクノロジー", "/tech/"), (hub["title"], None)], "テクノロジー")


# ==========================================================================
# OSページ
# ==========================================================================

def build_os_pages():
    latest = OS_VERSIONS[0]
    # ハブ
    ver_cards = "".join(f"""
<a class="card card--hover reveal" href="/os/{v['path']}/">
  <p class="eyebrow">{v['announce']} / {v['base']}ベース</p>
  <h2 class="t-h3">{esc(v['name'])} <span class="grad-text">「{v['code']}」</span></h2>
  <p class="t-soft t-small">{esc(v['sub'])}</p>
  <p class="link-arrow">詳細を見る</p>
</a>""" for v in OS_VERSIONS)
    body = f"""
<section class="hero">
  <canvas class="hero__canvas" id="emberCanvas" aria-hidden="true"></canvas>
  <div class="hero__bg hero__bg--glow"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">SUZAKU OS</p>
    <h1 class="t-hero">ゲームのために<br>生まれた<span class="grad-text">OS</span>。</h1>
    <p class="t-lead" style="max-width:640px">タッチの一瞬を最優先するスケジューラ、冷却と性能の自動最適化、そしてゲームスペース「陣」。SUZAKU OSは、ハードウェアと同じ設計思想で書かれています。</p>
    <div class="hero__actions">
      <a class="btn btn--primary btn--lg" href="/os/v4/">最新 {esc(latest['name'])}「{latest['code']}」</a>
      <a class="btn btn--ghost btn--lg" href="/os/game-space/">ゲームスペース「陣」</a>
    </div>
  </div>
  <div class="hero__scroll-cue" aria-hidden="true"></div>
</section>
<section class="section">
  <div class="container">
    <div class="section-head"><p class="eyebrow">VERSIONS</p><h2 class="t-h2">SUZAKU OS、4つの章。</h2>
    <p class="t-soft">2023年の1.0「暁」から、毎年ひとつの章を重ねてきました。全バージョンの記録です。</p></div>
    <div class="grid grid--2">{ver_cards}</div>
  </div>
</section>
{cta_band('OSも、アップデートも、無償で。', 'SUZAKU OSは全対応端末に無償提供。フラッグシップは3世代、TSUBAMEは4世代のアップデートを保証します。', [('対応製品を見る', '/products/', 'btn--primary'), ('アップデート情報', '/support/downloads/', 'btn--ghost')])}
"""
    render_page("/os/", "SUZAKU OS — ゲームのために生まれたOS",
                "独自OS「SUZAKU OS」の全バージョンとゲームスペース「陣」。タッチ最優先スケジューラと冷却×性能の自動最適化。",
                body, "dark", [("SUZAKU OS", None)], "OS")

    # 各バージョン
    for i, v in enumerate(OS_VERSIONS):
        feats = "".join(f"""
<div class="card reveal"><div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3l2.5 5.5L20 10l-5.5 1.5L12 17l-2.5-5.5L4 10l5.5-1.5z"/></svg></div>
<h3 class="t-h4">{esc(f['t'])}</h3><p class="t-small t-soft">{esc(f['d'])}</p></div>""" for f in v["features"])
        others = "".join(
            f'<a class="tab{" is-active" if o["id"] == v["id"] else ""}" href="/os/{o["path"]}/">{o["name"].replace("SUZAKU OS ", "")}「{o["code"]}」</a>'
            for o in reversed(OS_VERSIONS))
        body = f"""
<section class="hero hero--sub">
  <div class="hero__bg hero__bg--glow"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">{v['announce']} / {v['base']}ベース</p>
    <h1 class="t-display">{esc(v['name'])}<br><span class="grad-text">「{v['code']} — {v['en']}」</span></h1>
    <p class="t-lead" style="max-width:640px">{esc(v['tagline'])}<br><span class="t-small">{esc(v['sub'])}</span></p>
  </div>
</section>
<section class="section--sm"><div class="container"><div class="tabs" style="justify-content:center">{others}</div></div></section>
<section class="section--sm"><div class="container">{stats_html(v['stats'])}</div></section>
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">FEATURES</p><h2 class="t-h2">{esc(v['name'])} の主な機能</h2></div>
    <div class="grid grid--3">{feats}</div>
  </div>
</section>
{svg_os_showcase(v)}
<section class="section--sm">
  <div class="container container--narrow">
    <div class="section-head"><p class="eyebrow">RELEASE NOTES</p><h2 class="t-h2">配信履歴</h2></div>
    <div class="scroll-x reveal"><table class="spec-table">
      <thead><tr><th scope="col" style="padding:12px 18px;text-align:left">バージョン</th><th scope="col" style="padding:12px 18px;text-align:left">配信日</th><th scope="col" style="padding:12px 18px;text-align:left">主な内容</th></tr></thead>
      <tbody>{''.join(f'<tr><th scope="row">{ver}</th><td style="white-space:nowrap">{date}</td><td>{note}</td></tr>' for ver, date, note in v.get('patches', []))}</tbody>
    </table></div>
    <p class="t-micro t-faint" style="margin-top:14px">機種ごとの配信状況は<a href="/support/downloads/" style="color:var(--accent);text-decoration:underline">ダウンロード</a>ページをご確認ください。</p>
  </div>
</section>
{cta_band('「陣」で、すべてのゲームをひとつに。', 'SUZAKU OSの中核、ゲームスペース「陣」の全機能をご覧ください。', [('ゲームスペース「陣」', '/os/game-space/', 'btn--primary'), ('OS トップへ', '/os/', 'btn--ghost')])}
"""
        render_page(f"/os/{v['path']}/", f"{v['name']}「{v['code']}」",
                    v["sub"], body, "dark", [("SUZAKU OS", "/os/"), (f"{v['name']}「{v['code']}」", None)], "OS")


def svg_os_showcase(v):
    art = svg_art.svg_art("os", "#e8442e")
    return f"""
<section class="section--sm">
  <div class="container">
    <div class="feature-split">
      <div class="feature-split__media reveal-scale">{art}</div>
      <div class="stack reveal">
        <p class="eyebrow">DESIGN</p>
        <h2 class="t-h2">「{v['code']}」のデザイン言語。</h2>
        <p class="t-soft">SUZAKU OSの各バージョンには日本語の開発コードが与えられ、その名を冠したテーマ・サウンド・ライブ壁紙が同梱されます。{esc(v['name'])}「{v['code']}」も、朱と黒を基調にした独自のビジュアルシステムを備えています。</p>
        <ul class="check-list"><li>ダイナミックカラーテーマ「{v['code']}」</li><li>144Hz駆動のシステムアニメーション</li><li>プリインストール広告ゼロ</li></ul>
      </div>
    </div>
  </div>
</section>"""


# ==========================================================================
# ニュース
# ==========================================================================

def build_news_pages():
    for i, n in enumerate(NEWS):
        paras = "".join(f"<p>{p}</p>" for p in n["body"])
        prev_link = f'<a class="btn btn--ghost btn--sm" href="/news/{NEWS[i + 1]["id"]}/">← 前の記事</a>' if i + 1 < len(NEWS) else ""
        next_link = f'<a class="btn btn--ghost btn--sm" href="/news/{NEWS[i - 1]["id"]}/">次の記事 →</a>' if i > 0 else ""
        body = f"""
<section class="hero hero--page">
  <div class="hero__inner hero-enter">
    <p class="eyebrow">ニュースルーム — {n['cat']}</p>
    <h1 class="t-h1" style="max-width:840px">{esc(n['title'])}</h1>
    <p class="t-soft t-small">{n['date'].replace('-', '.')} — 株式会社朱雀</p>
  </div>
</section>
<article class="section--sm">
  <div class="container container--text">
    <div class="prose reveal">{paras}</div>
    <hr class="divider" style="margin-block:40px">
    <div class="prose t-small t-soft">
      <p><strong>株式会社朱雀(SUZAKU Inc.)について</strong><br>
      2022年5月1日設立。「限界を、燃やし尽くせ。」をタグラインに、ゲーミングスマートフォン・タブレットとその中核半導体(SoC・GPU・メモリ・ストレージ)、冷却技術、独自OSを自社開発する日本のハードウェアメーカーです。本社: 東京都千代田区外神田。</p>
      <p>本件に関する報道関係者からのお問い合わせ: <a href="/support/contact/">お問い合わせフォーム</a>(広報宛)</p>
    </div>
    <div class="spread" style="margin-top:36px">{prev_link}<a class="btn btn--soft btn--sm" href="/news/">ニュース一覧</a>{next_link}</div>
  </div>
</article>
"""
        render_page(f"/news/{n['id']}/", n["title"], n["excerpt"], body, "light",
                    [("ニュースルーム", "/news/"), (n["date"][:4] + "年", None)], "ニュース")


# ==========================================================================
# 製品ハブ
# ==========================================================================

def build_line_section(cat, line_key, blurb):
    line = LINES[line_key]
    items = sorted([p for p in ALL_PRODUCTS if p["cat"] == cat and p["line"] == line_key], key=lambda x: -x["year"])
    if not items:
        return ""
    cards = "".join(product_card(p) for p in items)
    cols = min(4, max(2, len(items)))
    return f"""
<section class="section--sm" id="{line_key}">
  <div class="container">
    <div class="section-head"><p class="eyebrow">{line['label']}</p>
    <h2 class="t-h2">{esc(items[0]['name'].rsplit(' ', 1)[0]) if line_key != 'suzaku' else 'SUZAKU'} シリーズ</h2>
    <p class="t-soft">{blurb}</p></div>
    <div class="grid grid--{cols} grid--cards reveal-stagger">{cards}</div>
  </div>
</section>"""


def quick_table(cat):
    """現行モデルの早見表(仕様データから自動生成)。"""
    items = sorted([p for p in ALL_PRODUCTS if p["cat"] == cat and p["status"] == "current"],
                   key=lambda x: -x["price"])
    rows = ""
    for p in items:
        rows += f"""<tr>
<td><a href="{product_url(p)}">{esc(p['name'])}</a><br><small class="t-faint">{LINES[p['line']]['label']}</small></td>
<td>{yen(p['price'])}〜</td>
<td>{esc(get_spec(p, ['ディスプレイ'], 'パネル'))}</td>
<td>{esc(get_spec(p, ['性能'], 'SoC').split('(')[0])}</td>
<td>{esc(get_spec(p, ['バッテリー'], 'バッテリー容量').split('(')[0])}</td>
<td>{esc(get_spec(p, ['本体'], '重量'))}</td>
</tr>"""
    return f"""
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">QUICK REFERENCE</p><h2 class="t-h2">現行モデル早見表</h2>
    <p class="t-soft t-small">価格はすべて税込。詳細は各製品名のリンク、より詳しい比較は<a href="/products/compare/" style="color:var(--accent);text-decoration:underline">比較ツール</a>へ。</p></div>
    <div class="scroll-x reveal"><table class="spec-table quick-table">
      <thead><tr><th scope="col">モデル</th><th scope="col">価格</th><th scope="col">ディスプレイ</th><th scope="col">SoC</th><th scope="col">バッテリー</th><th scope="col">重量</th></tr></thead>
      <tbody>{rows}</tbody>
    </table></div>
  </div>
</section>"""


def build_product_hubs():
    # スマートフォンハブ
    body = f"""
<section class="hero hero--sub">
  <div class="hero__bg hero__bg--glow"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">SMARTPHONES</p>
    <h1 class="t-hero">スマートフォン</h1>
    <p class="t-lead" style="max-width:660px">頂点のゲーミングから、毎日のスタンダードまで。4つのライン、すべての世代。</p>
    <div class="hero__actions">
      <a class="btn btn--soft btn--sm" href="#suzaku">SUZAKU</a>
      <a class="btn btn--soft btn--sm" href="#neo">Neo</a>
      <a class="btn btn--soft btn--sm" href="#tsubame">TSUBAME</a>
      <a class="btn btn--soft btn--sm" href="#lite">Lite</a>
      <a class="btn btn--ghost btn--sm" href="/products/compare/">比較する</a>
    </div>
  </div>
</section>
{build_line_section('phone', 'suzaku', '自社SoC・多層冷却・独自OSのすべてを注ぎ込む、SUZAKUの旗艦ライン。2023年の初代から毎年更新。')}
{build_line_section('phone', 'neo', '前年フラッグシップの技術を受け継ぎ、価格を抑えたゲーミングスタンダード。「去年の頂点を、今年の普通に」。')}
{build_line_section('phone', 'tsubame', 'ゲーミングで培った技術を日常へ。軽さ・カメラ・電池持ちを磨いた一般向けライン。')}
{build_line_section('phone', 'lite', '3万円台から、SUZAKU品質。はじめての一台にも2台目にも応えるエントリーライン。')}
{quick_table('phone')}
{cta_band('迷ったら、比較ツールへ。', '全12機種をスペックで並べて比較できます。', [('製品を比較する', '/products/compare/', 'btn--primary'), ('ストアで見る', '/store/', 'btn--ghost')])}
"""
    render_page("/products/phone/", "スマートフォン — 全ライン・全世代",
                "SUZAKU(ゲーミング旗艦)・Neo(ゲーミングスタンダード)・TSUBAME(スタンダード)・Lite(エントリー)。4ライン全世代のスマートフォン一覧。",
                body, "dark", [("製品", "/products/"), ("スマートフォン", None)], "製品")

    # タブレットハブ
    body = f"""
<section class="hero hero--sub">
  <div class="hero__bg hero__bg--glow"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">TABLETS</p>
    <h1 class="t-hero">タブレット</h1>
    <p class="t-lead" style="max-width:660px">ゲーミングの大画面から、家族のための一枚まで。タブレットも4つのラインで。</p>
  </div>
</section>
{build_line_section('tablet', 'pad', '氷刃冷却とフラッグシップSoCを大画面に解き放つ、ゲーミングタブレットの旗艦。')}
{build_line_section('tablet', 'pad-neo', 'フラッグシップ級SoCを薄型軽量ボディに。持ち出せるゲーミング。')}
{build_line_section('tablet', 't-pad', '動画・学習・ビデオ通話。暮らしの真ん中で活躍するスタンダード。')}
{build_line_section('tablet', 't-pad-lite', '動画と読書に最適化した、気軽なエントリータブレット。')}
{quick_table('tablet')}
{cta_band('タブレットも、ストアで。', '全モデル送料無料。純正アクセサリとの同時購入がおすすめです。', [('ストアで見る', '/store/', 'btn--primary'), ('アクセサリを見る', '/products/accessories/', 'btn--ghost')])}
"""
    render_page("/products/tablet/", "タブレット — 全ライン・全世代",
                "ゲーミングのSUZAKU Pad、スタンダードのTSUBAME Pad。4ライン全世代のタブレット一覧。",
                body, "dark", [("製品", "/products/"), ("タブレット", None)], "製品")

    # アクセサリハブ
    acc_cards = "".join(product_card(p) for p in ACCESSORIES)
    body = f"""
<section class="hero hero--sub">
  <div class="hero__bg hero__bg--glow" style="background:radial-gradient(50% 40% at 50% 70%, rgba(217,164,65,0.22), transparent 70%), var(--bg-deep)"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">ACCESSORIES</p>
    <h1 class="t-hero">純正アクセサリ</h1>
    <p class="t-lead" style="max-width:660px">冷却・操作・音・電力。SUZAKU製品のために設計された、公式アクセサリ。</p>
  </div>
</section>
<section class="section--sm"><div class="container"><div class="grid grid--3 grid--cards reveal-stagger">{acc_cards}</div></div></section>
{cta_band('本体と一緒に、そろえる。', 'ストアなら本体とアクセサリをまとめて購入できます。', [('ストアで見る', '/store/', 'btn--primary')])}
"""
    render_page("/products/accessories/", "純正アクセサリ",
                "氷嵐クーラー、SUZAKU Grip Pro、SUZAKU Buds、雷速チャージャーなど、SUZAKU純正アクセサリの一覧。",
                body, "dark", [("製品", "/products/"), ("アクセサリ", None)], "製品")

    # 製品トップ
    featured = [p for p in ALL_PRODUCTS if p.get("flag") == "new"]
    feat_cards = "".join(product_card(p) for p in featured[:4])
    cat_cards = f"""
<a class="card card--hover reveal" href="/products/phone/">
  <div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/></svg></div>
  <h2 class="t-h3">スマートフォン</h2><p class="t-small t-soft">4ライン・全12機種。ゲーミングの頂点から3万円台まで。</p><p class="link-arrow">一覧を見る</p></a>
<a class="card card--hover reveal" href="/products/tablet/">
  <div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2.5"/></svg></div>
  <h2 class="t-h3">タブレット</h2><p class="t-small t-soft">大画面ゲーミングから家族の一枚まで、全6機種。</p><p class="link-arrow">一覧を見る</p></a>
<a class="card card--hover reveal" href="/products/accessories/">
  <div class="card__icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.5"/></svg></div>
  <h2 class="t-h3">アクセサリ</h2><p class="t-small t-soft">クーラー、コントローラー、イヤホンなど純正6製品。</p><p class="link-arrow">一覧を見る</p></a>
"""
    body = f"""
<section class="hero hero--sub">
  <div class="hero__bg hero__bg--glow"></div>
  <div class="hero__inner hero-enter">
    <p class="eyebrow eyebrow--center">PRODUCTS</p>
    <h1 class="t-hero">製品</h1>
    <p class="t-lead" style="max-width:640px">すべての製品に、自社シリコンと冷却技術と独自OS。SUZAKUのフルラインナップ。</p>
    <div class="hero__actions"><a class="btn btn--primary btn--lg" href="/store/">ストアで購入する</a><a class="btn btn--ghost btn--lg" href="/products/compare/">比較する</a></div>
  </div>
</section>
<section class="section--sm"><div class="container"><div class="grid grid--3">{cat_cards}</div></div></section>
<section class="section--sm">
  <div class="container">
    <div class="section-head"><p class="eyebrow">2026 NEW</p><h2 class="t-h2">2026年の新製品</h2></div>
    <div class="grid grid--4 grid--cards reveal-stagger">{feat_cards}</div>
  </div>
</section>
{cta_band('どの一台から、始める?', '比較ツールとストアで、あなたの一台を見つけてください。', [('ストアで見る', '/store/', 'btn--primary'), ('比較ツール', '/products/compare/', 'btn--ghost')])}
"""
    render_page("/products/", "製品 — スマートフォン・タブレット・アクセサリ",
                "SUZAKUの全製品ラインナップ。ゲーミングスマートフォン、タブレット、純正アクセサリ。",
                body, "dark", [("製品", None)], "製品")


# ==========================================================================
# クライアントデータ / sitemap / フラグメント
# ==========================================================================

def get_spec(p, group_keys, row_key):
    for g, rows in p["specs"]:
        if any(k in g for k in group_keys):
            for k, v in rows:
                if row_key in k:
                    return v
    return "—"


def build_client_data():
    prods = []
    for p in ALL_PRODUCTS:
        cmp_data = None
        if p["cat"] in ("phone", "tablet"):
            cmp_data = {
                "発売日": p["release"],
                "価格": (yen(p["price"]) + "(税込)〜") if p["status"] == "current" else "販売終了",
                "ディスプレイ": get_spec(p, ["ディスプレイ"], "パネル"),
                "リフレッシュレート": get_spec(p, ["ディスプレイ"], "リフレッシュレート"),
                "SoC": get_spec(p, ["性能"], "SoC"),
                "GPU": get_spec(p, ["性能"], "GPU"),
                "メモリ": get_spec(p, ["性能"], "メモリ"),
                "ストレージ": get_spec(p, ["性能"], "ストレージ"),
                "冷却": get_spec(p, ["冷却"], "冷却システム"),
                "バッテリー": get_spec(p, ["バッテリー"], "バッテリー容量"),
                "充電": get_spec(p, ["バッテリー"], "有線充電"),
                "重量": get_spec(p, ["本体"], "重量"),
                "OS": get_spec(p, ["ソフトウェア"], "OS"),
            }
        prods.append({
            "id": p["id"], "name": p["name"], "kana": p["kana"], "cat": p["cat"],
            "line": p["line"], "lineLabel": LINES[p["line"]]["label"], "year": p["year"],
            "status": p["status"], "flag": p.get("flag"), "price": p["price"],
            "tagline": p["tagline"], "release": p["release"],
            "colors": p["colors"], "storage": p["storage"],
            "img": f"/assets/img/products/{p['id']}-0.svg",
            "url": product_url(p), "cmp": cmp_data,
            "radar": radar_values(p) if cmp_data else None,
        })
    news = [{"id": n["id"], "date": n["date"], "cat": n["cat"], "title": n["title"],
             "excerpt": n["excerpt"], "url": f"/news/{n['id']}/"} for n in NEWS]
    data = {
        "products": prods,
        "news": news,
        "faq": FAQ,
        "docs": DOCS,
        "pages": PAGES,
        "tax": 0.10,
        "freeShipping": 5000,
        "shippingFee": 550,
    }
    js = "// 自動生成: scripts/gen.py — 編集しないでください\nwindow.SZ = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out = ROOT / "data" / "products.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(js, encoding="utf-8")


def build_assets():
    img = ROOT / "assets" / "img"
    (img / "products").mkdir(parents=True, exist_ok=True)
    (img / "favicon.svg").write_text(svg_art.FAVICON, encoding="utf-8")
    for p in ALL_PRODUCTS:
        glow = LINES[p["line"]]["glow"]
        hz = f"{num(get_spec(p, ['ディスプレイ'], 'リフレッシュレート')) or 60}Hz" if p["cat"] in ("phone", "tablet") else "60Hz"
        for i, c in enumerate(p["colors"]):
            if p["cat"] == "phone":
                svg = svg_art.svg_phone(f"{p['id']}{i}", c["hex"], glow, p["name"], p["kana"], p["line"], hz)
            elif p["cat"] == "tablet":
                svg = svg_art.svg_tablet(f"{p['id']}{i}", c["hex"], glow, p["name"], p["kana"], p["line"], hz)
            else:
                svg = svg_art.svg_art(p.get("art", "chip"), glow if i == 0 else c["hex"])
            (img / "products" / f"{p['id']}-{i}.svg").write_text(svg, encoding="utf-8")


def build_fragments():
    if not SRC.exists():
        return
    for f in sorted(SRC.rglob("*.html")):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--META\s*(\{.*?\})\s*-->", text, re.S)
        if not m:
            raise SystemExit(f"METAコメントがありません: {f}")
        meta = json.loads(m.group(1))
        body = text[m.end():]
        rel = f.relative_to(SRC)
        if rel.as_posix() == "home.html":
            url = "/"
        else:
            url = "/" + rel.as_posix()[:-5].removesuffix("/index") + "/"
        if meta.get("root_file"):
            url = "/" + meta["root_file"]
        render_page(url, meta["title"], meta["desc"], body,
                    meta.get("theme", "dark"),
                    [tuple(c) for c in meta.get("crumbs", [])] or None,
                    meta.get("group", "その他"),
                    noindex=meta.get("noindex", False))


def build_sitemap():
    urls = "".join(f"<url><loc>{BASE_URL}{p['url']}</loc></url>" for p in PAGES)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")


def main():
    build_assets()
    for p in ALL_PRODUCTS:
        build_product_page(p)
    for t in TECHS:
        build_tech_page(t)
    for hub in TECH_HUBS:
        build_tech_hub(hub)
    build_os_pages()
    build_news_pages()
    build_product_hubs()
    build_fragments()
    build_client_data()  # PAGES確定後
    build_sitemap()
    print(f"生成完了: {len(PAGES)}ページ")


if __name__ == "__main__":
    main()
