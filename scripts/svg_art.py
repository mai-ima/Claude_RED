# -*- coding: utf-8 -*-
"""SUZAKU サイト用SVGアート生成。

製品ビジュアル・技術ダイアグラム・アイコン類をすべてコードから生成する。
外部画像に一切依存しないため、画像のリンク切れが構造的に発生しない。
"""

import math


def _shade(hex_color, f):
    """hex色を明暗調整する。f>0 で白へ、f<0 で黒へ混ぜる(0〜±1)。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    if f >= 0:
        r, g, b = (round(c + (255 - c) * f) for c in (r, g, b))
    else:
        r, g, b = (round(c * (1 + f)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _is_light(hex_color):
    """ボディ色が明色かどうか(白銀・白練などで刻印を黒系に反転するため)。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) > 150


def svg_phone(pid, body_hex, glow, label, kana="", line="suzaku", hz="144Hz"):
    """スマートフォン背面ビュー(実機比率 約76.5×164mm ≒ 1:2.15)。

    カラー選択で切り替わる画像のため、実機のカラバリ訴求と同じ「背面」を描く。
    ボディカラーの多段グラデーション・蒸着テクスチャ・ガラスの斜めシーン・
    金属フレーム・カメラモジュールで質感を出し、ゲーミング系ラインには
    冷却ファン窓とLEDスラッシュを載せる。"""
    gid = pid.replace("-", "")
    gaming = line in ("suzaku", "neo", "collab")
    lite = _shade(body_hex, 0.42)
    lite2 = _shade(body_hex, 0.16)
    dark = _shade(body_hex, -0.38)
    dark2 = _shade(body_hex, -0.6)
    plate = _shade(body_hex, -0.3)
    # 明色ボディ(白銀・白練など)では刻印・ブレードを黒系に反転して視認性を保つ
    light_body = _is_light(body_hex)
    ink = "#1c1c26" if light_body else "#ffffff"
    blade = _shade(body_hex, -0.35) if light_body else _shade(body_hex, 0.22)

    defs = f"""<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.9" y2="1">
  <stop offset="0" stop-color="{lite}"/>
  <stop offset="0.28" stop-color="{lite2}"/>
  <stop offset="0.62" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{dark}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/>
  <stop offset="0.35" stop-color="#141821"/>
  <stop offset="1" stop-color="#04040a"/>
</radialGradient>
<linearGradient id="sheen{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.28"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.03"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
<pattern id="tex{gid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
  <path d="M0 0 V7" stroke="#ffffff" stroke-opacity="0.045" stroke-width="1"/>
</pattern>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
</defs>"""

    # カメラモジュール(天眼トリプル+フラッシュ)
    lenses = ""
    for cx in (108, 170, 232):
        lenses += f"""
<circle cx="{cx}" cy="116" r="25" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.6"/>
<circle cx="{cx}" cy="116" r="19" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.3"/>
<circle cx="{cx}" cy="116" r="15" fill="url(#lens{gid})"/>
<circle cx="{cx}" cy="116" r="5.5" fill="#04040a"/>
<circle cx="{cx - 5.5}" cy="110" r="3.4" fill="#ffffff" opacity="0.55"/>"""
    camera = f"""
<rect x="66" y="64" width="208" height="90" rx="26" fill="{plate}"/>
<rect x="66" y="64" width="208" height="90" rx="26" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="66.7" y="64.7" width="206.6" height="88.6" rx="25.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.4"/>
<circle cx="86" cy="80" r="5" fill="#f4efdf" opacity="0.9"/>
<text x="262" y="83" font-family="'Noto Sans JP',sans-serif" font-size="8.5" font-weight="700" fill="{ink}" opacity="0.5" text-anchor="end" letter-spacing="2">TENGAN</text>
{lenses}"""

    if gaming:
        # LEDスラッシュ + 冷却ファン窓
        slashes = "".join(
            f'<path d="M{66 + i * 66} 178 h44 l-13 13 h-44 z" fill="{glow}" opacity="{o}"/>'
            for i, o in enumerate((0.92, 0.55, 0.28)))
        blades = "".join(
            f'<path d="M170 328 L170 296" stroke="{blade}" stroke-width="9" stroke-linecap="round" transform="rotate({a} 170 328)"/>'
            for a in range(0, 360, 40))
        feature = f"""
{slashes}
<circle cx="170" cy="328" r="50" fill="{dark2}"/>
<circle cx="170" cy="328" r="50" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="2"/>
<circle cx="170" cy="328" r="42" fill="#0a0b10"/>
{blades}
<circle cx="170" cy="328" r="13" fill="#101018" stroke="{glow}" stroke-opacity="0.8" stroke-width="1.6"/>
<circle cx="170" cy="328" r="4" fill="{glow}"/>
<text x="170" y="398" font-family="'Noto Sans JP',sans-serif" font-size="9" font-weight="700" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="3">SENPU COOLING</text>"""
        side_r = f"""
<rect x="292.5" y="112" width="5" height="44" rx="2.5" fill="{glow}"/>
<rect x="292.5" y="172" width="5" height="44" rx="2.5" fill="{glow}"/>
<rect x="292.5" y="250" width="5" height="48" rx="2.5" fill="{dark2}"/>"""
    else:
        # 一般ライン: 朱雀エンブレムの型押し
        feature = f"""
<g transform="translate(122 268) scale(2)" opacity="0.9">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{glow}" stroke-width="2.6" stroke-linejoin="round"/>
  <circle cx="24" cy="31.5" r="3.2" fill="{glow}"/>
</g>"""
        side_r = f'<rect x="292.5" y="162" width="5" height="56" rx="2.5" fill="{dark2}"/>'

    # 刻印(長いコラボ名は「×」で2行に分割してはみ出しを防ぐ)
    if "×" in label and len(label) > 14:
        l1, l2 = (s.strip() for s in label.split("×", 1))
        etched = f"""
<text x="170" y="452" font-family="'Noto Sans JP',sans-serif" font-size="13" font-weight="800" fill="{ink}" opacity="0.72" text-anchor="middle" letter-spacing="1.5">{l1} ×</text>
<text x="170" y="470" font-family="'Noto Sans JP',sans-serif" font-size="12" font-weight="700" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="1">{l2}</text>"""
    else:
        etched = f"""
<text x="170" y="462" font-family="'Noto Sans JP',sans-serif" font-size="14.5" font-weight="800" fill="{ink}" opacity="0.72" text-anchor="middle" letter-spacing="2.5">{label}</text>"""
    if kana:
        etched += f"""
<text x="170" y="487" font-family="'Noto Sans JP',sans-serif" font-size="9" fill="{ink}" opacity="0.4" text-anchor="middle" letter-spacing="4">{kana}</text>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label}">
{defs}
<ellipse cx="170" cy="577" rx="116" ry="13" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="43" y="30" width="254" height="540" rx="47" fill="url(#frame{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="{body_hex}"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="url(#body{gid})"/>
<rect x="49" y="36" width="242" height="528" rx="42" fill="url(#tex{gid})"/>
<rect x="50" y="37" width="240" height="526" rx="41" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.6"/>
<path d="M43 128 h6 M43 448 h6 M291 128 h6 M291 448 h6" stroke="{dark2}" stroke-width="3"/>
{camera}
{feature}
{etched}
<text x="170" y="546" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="middle" letter-spacing="2">DESIGNED BY SUZAKU ・ {hz}</text>
<path d="M78 36 L206 36 L96 564 L49 564 L49 300 Z" fill="url(#sheen{gid})"/>
<path d="M232 36 L262 36 L150 564 L124 564 Z" fill="#ffffff" opacity="0.05"/>
{side_r}
<rect x="42.5" y="146" width="5" height="62" rx="2.5" fill="{dark2}"/>
</svg>"""


def svg_tablet(pid, body_hex, glow, label, kana="", line="pad", hz="120Hz"):
    """タブレット背面ビュー(横持ち)。スマホ背面と同じ質感エンジンで描く。

    ゲーミング系(pad/pad-neo)は冷却ファン窓+LEDスラッシュ、
    スタンダード系(t-pad)は朱雀エンブレム型押し+キーボード用ポゴピン。"""
    gid = pid.replace("-", "")
    gaming = line in ("pad", "pad-neo")
    lite = _shade(body_hex, 0.42)
    lite2 = _shade(body_hex, 0.16)
    dark = _shade(body_hex, -0.38)
    dark2 = _shade(body_hex, -0.6)
    plate = _shade(body_hex, -0.3)
    light_body = _is_light(body_hex)
    ink = "#1c1c26" if light_body else "#ffffff"
    blade = _shade(body_hex, -0.35) if light_body else _shade(body_hex, 0.22)

    defs = f"""<defs>
<linearGradient id="body{gid}" x1="0" y1="0" x2="0.9" y2="1">
  <stop offset="0" stop-color="{lite}"/>
  <stop offset="0.28" stop-color="{lite2}"/>
  <stop offset="0.62" stop-color="{body_hex}"/>
  <stop offset="1" stop-color="{dark}"/>
</linearGradient>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<radialGradient id="lens{gid}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#3c4454"/>
  <stop offset="0.35" stop-color="#141821"/>
  <stop offset="1" stop-color="#04040a"/>
</radialGradient>
<linearGradient id="sheen{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.26"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.03"/>
  <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</linearGradient>
<pattern id="tex{gid}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
  <path d="M0 0 V7" stroke="#ffffff" stroke-opacity="0.045" stroke-width="1"/>
</pattern>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
</defs>"""

    # デュアルカメラ(左上・横持ち基準)
    lenses = ""
    for cx in (104, 156):
        lenses += f"""
<circle cx="{cx}" cy="92" r="19" fill="#0b0d13" stroke="{_shade(body_hex, 0.3)}" stroke-width="1.5"/>
<circle cx="{cx}" cy="92" r="14" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.2"/>
<circle cx="{cx}" cy="92" r="11" fill="url(#lens{gid})"/>
<circle cx="{cx}" cy="92" r="4" fill="#04040a"/>
<circle cx="{cx - 4}" cy="87.5" r="2.6" fill="#ffffff" opacity="0.55"/>"""
    camera = f"""
<rect x="72" y="62" width="118" height="60" rx="20" fill="{plate}"/>
<rect x="72" y="62" width="118" height="60" rx="20" fill="url(#sheen{gid})" opacity="0.5"/>
<rect x="72.7" y="62.7" width="116.6" height="58.6" rx="19.3" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.3"/>
<circle cx="178" cy="76" r="4" fill="#f4efdf" opacity="0.9"/>
{lenses}"""

    if gaming:
        slashes = "".join(
            f'<path d="M{224 + i * 58} 78 h38 l-11 11 h-38 z" fill="{glow}" opacity="{o}"/>'
            for i, o in enumerate((0.92, 0.55, 0.28)))
        blades = "".join(
            f'<path d="M320 238 L320 210" stroke="{blade}" stroke-width="8" stroke-linecap="round" transform="rotate({a} 320 238)"/>'
            for a in range(0, 360, 40))
        feature = f"""
{slashes}
<circle cx="320" cy="238" r="44" fill="{dark2}"/>
<circle cx="320" cy="238" r="44" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="2"/>
<circle cx="320" cy="238" r="37" fill="#0a0b10"/>
{blades}
<circle cx="320" cy="238" r="11" fill="#101018" stroke="{glow}" stroke-opacity="0.8" stroke-width="1.5"/>
<circle cx="320" cy="238" r="3.5" fill="{glow}"/>
<text x="320" y="300" font-family="'Noto Sans JP',sans-serif" font-size="9" font-weight="700" fill="{ink}" opacity="0.5" text-anchor="middle" letter-spacing="3">SENPU COOLING</text>"""
        top_btn = f"""
<rect x="128" y="17.5" width="52" height="5" rx="2.5" fill="{glow}"/>
<rect x="196" y="17.5" width="40" height="5" rx="2.5" fill="{dark2}"/>"""
    else:
        feature = f"""
<g transform="translate(276 194) scale(1.85)" opacity="0.9">
  <path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="{glow}" stroke-width="2.6" stroke-linejoin="round"/>
  <circle cx="24" cy="31.5" r="3.2" fill="{glow}"/>
</g>
{"".join(f'<circle cx="{296 + i * 24}" cy="436" r="4" fill="{dark2}" stroke="#ffffff" stroke-opacity="0.25" stroke-width="1"/>' for i in range(3))}"""
        top_btn = f'<rect x="128" y="17.5" width="52" height="5" rx="2.5" fill="{dark2}"/>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="{label}">
{defs}
<ellipse cx="320" cy="459" rx="216" ry="11" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="36" y="22" width="568" height="428" rx="35" fill="url(#frame{gid})"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="{body_hex}"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="url(#body{gid})"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="url(#tex{gid})"/>
<rect x="43" y="29" width="554" height="414" rx="29" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.5"/>
<path d="M120 22 v6 M520 22 v6 M120 444 v6 M520 444 v6" stroke="{dark2}" stroke-width="3"/>
{camera}
{feature}
<text x="320" y="368" font-family="'Noto Sans JP',sans-serif" font-size="17" font-weight="800" fill="{ink}" opacity="0.72" text-anchor="middle" letter-spacing="3">{label}</text>
<text x="320" y="392" font-family="'Noto Sans JP',sans-serif" font-size="9.5" fill="{ink}" opacity="0.4" text-anchor="middle" letter-spacing="4">{kana}</text>
<text x="556" y="430" font-family="'Noto Sans JP',sans-serif" font-size="8" fill="{ink}" opacity="0.38" text-anchor="end" letter-spacing="2">DESIGNED BY SUZAKU ・ {hz}</text>
<path d="M92 28 L300 28 L136 444 L42 444 L42 240 Z" fill="url(#sheen{gid})"/>
<path d="M350 28 L400 28 L212 444 L168 444 Z" fill="#ffffff" opacity="0.05"/>
{top_btn}
</svg>"""


def _front_scene_phone(line, glow, hz, motif):
    """スマホ正面ビューの画面内シーン(ライン/コラボ作品ごとに差し替え)。
    画面領域: x54〜286, y41〜559(中心 x=170)。"""
    fps = hz.replace("Hz", "")
    fjp = "'Noto Sans JP',sans-serif"
    if motif == "genshin":
        # 七元素ホイール(元素の頂 Edition)
        cols = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
        dots = ""
        for i, col in enumerate(cols):
            a = math.radians(-90 + i * 360 / 7)
            x, y = 170 + 74 * math.cos(a), 250 + 74 * math.sin(a)
            dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{col}" opacity="0.92"/><circle cx="{x:.1f}" cy="{y:.1f}" r="15.5" fill="none" stroke="{col}" stroke-opacity="0.4" stroke-width="1.5"/>'
        stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" opacity="{o}"/>'
                        for x, y, r, o in ((92, 110, 1.5, 0.6), (250, 96, 1, 0.45), (270, 170, 1.3, 0.5), (80, 330, 1, 0.4), (238, 396, 1.4, 0.5)))
        return f"""{stars}
<circle cx="170" cy="250" r="74" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.2" stroke-dasharray="3 6"/>
{dots}
<path d="M170 218 c-6 24 -29 34 -29 59 a29 29 0 0 0 58 0 c0 -25 -23 -35 -29 -59z" fill="none" stroke="{glow}" stroke-width="3.4" stroke-linejoin="round"/>
<circle cx="170" cy="284" r="6" fill="{glow}"/>
<text x="170" y="392" font-family="{fjp}" font-size="15" font-weight="800" fill="#efe7d2" text-anchor="middle" letter-spacing="6">七元素共鳴</text>
<text x="170" y="414" font-family="{fjp}" font-size="8.5" fill="#b9b2a0" text-anchor="middle" letter-spacing="3">ELEMENTAL BACKGLOW</text>
<rect x="106" y="452" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="471.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="2">元素の頂 Edition</text>"""
    if motif == "wuwa":
        # 共鳴波形HUD(共鳴 Edition)
        wave = "M62 300 " + " ".join(
            f"Q {74 + i * 24} {300 - a} {86 + i * 24} 300"
            for i, a in enumerate((14, -38, 82, -120, 96, -60, 26, -12, 6)))
        bars = "".join(
            f'<rect x="{84 + i * 16}" y="{392 - h}" width="8" height="{h}" rx="2" fill="{glow}" opacity="{0.9 - i * 0.07:.2f}"/>'
            for i, h in enumerate((14, 26, 40, 30, 48, 22, 34, 16, 24, 10, 18)))
        return f"""
<path d="M66 84 h30 M66 84 v30 M274 84 h-30 M274 84 v30 M66 516 h30 M66 516 v-30 M274 516 h-30 M274 516 v-30" stroke="{glow}" stroke-opacity="0.75" stroke-width="2"/>
<text x="170" y="140" font-family="{fjp}" font-size="10" fill="#9adfe8" text-anchor="middle" letter-spacing="6" opacity="0.85">RESONANCE HUD</text>
<text x="170" y="216" font-family="{fjp}" font-size="52" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="1">4.0<tspan font-size="20" fill="{glow}">GHz</tspan></text>
<text x="170" y="242" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">MAX CLOCK ・ ANTUTU 412万</text>
<path d="{wave}" fill="none" stroke="{glow}" stroke-width="2.6" stroke-linecap="round"/>
<path d="M62 300 H278" stroke="{glow}" stroke-opacity="0.25" stroke-width="1"/>
{bars}
<text x="170" y="428" font-family="{fjp}" font-size="9" fill="#9adfe8" text-anchor="middle" letter-spacing="3" opacity="0.8">RESONANCE HAPTICS 3200Hz</text>
<rect x="106" y="452" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="471.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="2">共鳴 Edition</text>"""
    if motif == "nte":
        # ネオン都市の夜景(ネオンシティ Edition)
        bl = "#191327"
        buildings = "".join(
            f'<rect x="{x}" y="{y}" width="{w}" height="{460 - y}" fill="{bl}" opacity="{o}"/>'
            for x, y, w, o in ((58, 300, 36, 0.9), (98, 252, 44, 1), (146, 286, 34, 0.85), (184, 224, 48, 1), (236, 268, 42, 0.9)))
        windows = "".join(
            f'<rect x="{x}" y="{y}" width="5" height="7" fill="{c}" opacity="{o}"/>'
            for x, y, c, o in ((106, 266, "#ff2d78", 0.9), (120, 266, "#39d7f5", 0.7), (106, 284, "#ffd166", 0.6),
                               (192, 240, "#39d7f5", 0.9), (206, 240, "#ff2d78", 0.8), (220, 240, "#ffd166", 0.55),
                               (192, 260, "#ff2d78", 0.6), (220, 260, "#39d7f5", 0.75), (66, 316, "#ffd166", 0.6),
                               (80, 316, "#ff2d78", 0.7), (244, 282, "#39d7f5", 0.8), (258, 282, "#ff2d78", 0.6),
                               (152, 300, "#ffd166", 0.7), (164, 300, "#39d7f5", 0.6)))
        return f"""
<circle cx="236" cy="118" r="26" fill="#f2ecdc" opacity="0.9"/>
<circle cx="228" cy="112" r="24" fill="#0d0a14"/>
{buildings}
{windows}
<path d="M58 460 H282" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.5"/>
<rect x="84" y="150" width="172" height="52" rx="12" fill="none" stroke="{glow}" stroke-width="2" filter="url(#fzf)" opacity="0.8"/>
<rect x="84" y="150" width="172" height="52" rx="12" fill="none" stroke="{glow}" stroke-width="1.6"/>
<text x="170" y="184" font-family="{fjp}" font-size="21" font-weight="900" fill="{glow}" text-anchor="middle" letter-spacing="4">NEON CITY</text>
<text x="170" y="228" font-family="{fjp}" font-size="8.5" fill="#c9a7d6" text-anchor="middle" letter-spacing="3">NIGHT ISP ・ 2TB</text>
<rect x="106" y="486" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="505.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="1">ネオンシティ Edition</text>"""
    if motif == "endfield":
        # 産業ターミナル(開拓 Edition)
        hazard = "".join(
            f'<path d="M{64 + i * 30} 96 l16 0 -10 14 -16 0 z" fill="{glow}" opacity="{0.9 if i % 2 == 0 else 0.35}"/>'
            for i in range(8))
        lines = (("SYSTEM CHECK", "OK", 0.95), ("POWER CELL 8200mAh", "OK", 0.8),
                 ("IP68 / MIL-STD-810H", "OK", 0.65), ("SUSTAIN MODE", "READY", 0.5))
        rows = "".join(
            f'<text x="66" y="{176 + i * 30}" font-family="monospace" font-size="11" fill="#ffb066" opacity="{o}">&gt; {t}</text>'
            f'<text x="274" y="{176 + i * 30}" font-family="monospace" font-size="11" fill="#7ee787" opacity="{o}" text-anchor="end">[{s}]</text>'
            for i, (t, s, o) in enumerate(lines))
        return f"""
{hazard}
<path d="M62 118 H278" stroke="{glow}" stroke-opacity="0.4" stroke-width="1"/>
{rows}
<rect x="66" y="306" width="208" height="10" rx="3" fill="#241c14"/>
<rect x="66" y="306" width="152" height="10" rx="3" fill="{glow}" opacity="0.85"/>
<text x="66" y="336" font-family="monospace" font-size="10" fill="#c9b8a4">UPTIME 73%</text>
<rect x="66" y="360" width="9" height="14" fill="{glow}"/>
<text x="170" y="418" font-family="{fjp}" font-size="13" font-weight="800" fill="#ead9c4" text-anchor="middle" letter-spacing="4">TERMINAL HUD</text>
<rect x="106" y="452" width="128" height="30" rx="15" fill="none" stroke="{glow}" stroke-opacity="0.7" stroke-width="1.4"/>
<text x="170" y="471.5" font-family="{fjp}" font-size="10" font-weight="700" fill="{glow}" text-anchor="middle" letter-spacing="2">開拓 Edition</text>"""
    if line in ("suzaku", "neo", "collab"):
        # ゲーミング: パフォーマンスHUD
        ring_c = 2 * math.pi * 66
        stats = (("GPU", 0.82), ("CPU", 0.64), ("温度", 0.38))
        bars = "".join(
            f'<text x="70" y="{392 + i * 34}" font-family="{fjp}" font-size="10" font-weight="700" fill="#9c9cb0">{l}</text>'
            f'<rect x="104" y="{384 + i * 34}" width="166" height="9" rx="3" fill="#ffffff" opacity="0.08"/>'
            f'<rect x="104" y="{384 + i * 34}" width="{166 * v:.0f}" height="9" rx="3" fill="{glow}" opacity="{0.95 - i * 0.18}"/>'
            for i, (l, v) in enumerate(stats))
        return f"""
<text x="170" y="118" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">GAME SPACE</text>
<circle cx="170" cy="240" r="66" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="9"/>
<circle cx="170" cy="240" r="66" fill="none" stroke="{glow}" stroke-width="9" stroke-linecap="round"
  stroke-dasharray="{ring_c * 0.8:.0f} {ring_c:.0f}" transform="rotate(-90 170 240)"/>
<text x="170" y="252" font-family="{fjp}" font-size="46" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="170" y="278" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="middle" letter-spacing="5">FPS</text>
<text x="170" y="344" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">フレーム安定率 99.4%</text>
{bars}
<rect x="70" y="486" width="96" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="118" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">Lトリガー ON</text>
<rect x="174" y="486" width="96" height="26" rx="13" fill="#ffffff" opacity="0.07"/>
<text x="222" y="503" font-family="{fjp}" font-size="9" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">Rトリガー ON</text>"""
    # スタンダード/エントリー: ホーム画面
    dock = "".join(
        f'<rect x="{82 + i * 46}" y="472" width="38" height="38" rx="11" fill="{c}" opacity="{o}"/>'
        for i, (c, o) in enumerate(((glow, 0.85), ("#ffffff", 0.14), ("#ffffff", 0.11), ("#ffffff", 0.14))))
    return f"""
<text x="170" y="172" font-family="{fjp}" font-size="52" font-weight="300" fill="#ffffff" text-anchor="middle" letter-spacing="2">12:34</text>
<text x="170" y="198" font-family="{fjp}" font-size="11" fill="#b9b9c8" text-anchor="middle" letter-spacing="2">7月10日(金)</text>
<rect x="70" y="232" width="200" height="66" rx="16" fill="#ffffff" opacity="0.07"/>
<circle cx="106" cy="265" r="15" fill="none" stroke="#f2c14e" stroke-width="2.5"/>
{"".join(f'<path d="M106 243 v-6" stroke="#f2c14e" stroke-width="2.5" stroke-linecap="round" transform="rotate({a} 106 265)"/>' for a in range(0, 360, 45))}
<text x="136" y="261" font-family="{fjp}" font-size="15" font-weight="800" fill="#ffffff">24℃</text>
<text x="136" y="281" font-family="{fjp}" font-size="9.5" fill="#b9b9c8">東京 ・ 晴れ</text>
<rect x="70" y="312" width="200" height="52" rx="14" fill="#ffffff" opacity="0.05"/>
<path d="M92 352 c-3.5 -12 4 -19 8 -26 c4 7 11.5 14 8 26 a8 8 0 0 1 -16 0z" fill="none" stroke="{glow}" stroke-width="2"/>
<text x="118" y="336" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">バッテリー 82%</text>
<text x="118" y="352" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">あと1日と4時間</text>
{dock}"""


def svg_phone_front(pid, body_hex, glow, label, line="suzaku", hz="144Hz", motif=None):
    """スマートフォン正面ビュー(ディスプレイ点灯状態)。

    ライン/コラボ作品ごとに画面内シーンを差し替えて差別化する。
    旗艦系はアンダーディスプレイカメラのためパンチホール無し。"""
    gid = "f" + pid.replace("-", "")
    dark2 = _shade(body_hex, -0.6)
    punch = line in ("tsubame", "lite")
    defs = f"""<defs>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<linearGradient id="scr{gid}" x1="0" y1="0" x2="0.8" y2="1">
  <stop offset="0" stop-color="#171722"/>
  <stop offset="0.5" stop-color="#0d0d14"/>
  <stop offset="1" stop-color="#07070c"/>
</linearGradient>
<radialGradient id="flare{gid}" cx="0.5" cy="0.32" r="0.85">
  <stop offset="0" stop-color="{glow}" stop-opacity="0.3"/>
  <stop offset="0.55" stop-color="{glow}" stop-opacity="0.09"/>
  <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
<filter id="fzf" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="5"/></filter>
<clipPath id="clip{gid}"><rect x="54" y="41" width="232" height="518" rx="37"/></clipPath>
</defs>"""
    scene = _front_scene_phone(line, glow, hz, motif)
    status = f"""
<text x="70" y="72" font-family="'Noto Sans JP',sans-serif" font-size="11" font-weight="700" fill="#e6e6ee">12:34</text>
{"".join(f'<rect x="{222 + i * 6}" y="{70 - i * 2.5}" width="3.5" height="{5 + i * 2.5}" rx="1" fill="#c9c9d6" opacity="{0.55 + i * 0.15}"/>' for i in range(3))}
<rect x="248" y="61.5" width="20" height="10" rx="3" fill="none" stroke="#c9c9d6" stroke-width="1.3"/>
<rect x="250" y="63.5" width="13" height="6" rx="1.5" fill="{glow}"/>
<rect x="268.6" y="64" width="2.4" height="5" rx="1" fill="#c9c9d6"/>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 600" role="img" aria-label="{label} 正面">
{defs}
<ellipse cx="170" cy="577" rx="116" ry="13" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="43" y="30" width="254" height="540" rx="47" fill="url(#frame{gid})"/>
<rect x="48" y="35" width="244" height="530" rx="42" fill="#06060a"/>
<rect x="54" y="41" width="232" height="518" rx="37" fill="url(#scr{gid})"/>
<g clip-path="url(#clip{gid})">
<ellipse cx="170" cy="210" rx="180" ry="200" fill="url(#flare{gid})"/>
{scene}
{status}
{f'<circle cx="170" cy="62" r="5.5" fill="#04040a" stroke="#2a2a36" stroke-width="1.4"/>' if punch else ''}
<rect x="125" y="544" width="90" height="4.5" rx="2.25" fill="#ffffff" opacity="0.55"/>
<path d="M54 41 L206 41 L84 559 L54 559 Z" fill="#ffffff" opacity="0.035"/>
</g>
<rect x="54.8" y="41.8" width="230.4" height="516.4" rx="36.4" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1.4"/>
<rect x="292.5" y="140" width="5" height="46" rx="2.5" fill="{dark2}"/>
<rect x="292.5" y="200" width="5" height="70" rx="2.5" fill="{dark2}"/>
</svg>"""


def svg_tablet_front(pid, body_hex, glow, label, line="pad", hz="120Hz"):
    """タブレット正面ビュー(横持ち・ディスプレイ点灯状態)。
    ゲーミング系はfps HUD、スタンダード系はホーム画面を映す。"""
    gid = "f" + pid.replace("-", "")
    gaming = line in ("pad", "pad-neo")
    dark2 = _shade(body_hex, -0.6)
    fps = hz.replace("Hz", "")
    fjp = "'Noto Sans JP',sans-serif"
    if gaming:
        ring_c = 2 * math.pi * 62
        bars = "".join(
            f'<text x="368" y="{170 + i * 44}" font-family="{fjp}" font-size="11" font-weight="700" fill="#9c9cb0">{l}</text>'
            f'<rect x="410" y="{161 + i * 44}" width="150" height="10" rx="3" fill="#ffffff" opacity="0.08"/>'
            f'<rect x="410" y="{161 + i * 44}" width="{150 * v:.0f}" height="10" rx="3" fill="{glow}" opacity="{0.95 - i * 0.18}"/>'
            for i, (l, v) in enumerate((("GPU", 0.84), ("CPU", 0.62), ("温度", 0.36))))
        scene = f"""
<text x="210" y="122" font-family="{fjp}" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">GAME SPACE</text>
<circle cx="210" cy="240" r="62" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="9"/>
<circle cx="210" cy="240" r="62" fill="none" stroke="{glow}" stroke-width="9" stroke-linecap="round"
  stroke-dasharray="{ring_c * 0.8:.0f} {ring_c:.0f}" transform="rotate(-90 210 240)"/>
<text x="210" y="252" font-family="{fjp}" font-size="42" font-weight="900" fill="#ffffff" text-anchor="middle">{fps}</text>
<text x="210" y="278" font-family="{fjp}" font-size="10" fill="{glow}" text-anchor="middle" letter-spacing="5">FPS</text>
<text x="210" y="342" font-family="{fjp}" font-size="9" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">フレーム安定率 99.2%</text>
{bars}
<rect x="368" y="300" width="192" height="46" rx="12" fill="#ffffff" opacity="0.05"/>
<text x="380" y="320" font-family="{fjp}" font-size="9.5" font-weight="700" fill="#ececf2">旋風ファン 21,000rpm</text>
<text x="380" y="336" font-family="{fjp}" font-size="8.5" fill="#9c9cb0">表面温度 38.2℃ ・ 静音モード</text>"""
    else:
        scene = f"""
<text x="200" y="200" font-family="{fjp}" font-size="58" font-weight="300" fill="#ffffff" text-anchor="middle" letter-spacing="2">12:34</text>
<text x="200" y="228" font-family="{fjp}" font-size="12" fill="#b9b9c8" text-anchor="middle" letter-spacing="2">7月10日(金)</text>
<rect x="356" y="140" width="204" height="92" rx="16" fill="#ffffff" opacity="0.07"/>
<circle cx="396" cy="186" r="17" fill="none" stroke="#f2c14e" stroke-width="2.5"/>
{"".join(f'<path d="M396 162 v-7" stroke="#f2c14e" stroke-width="2.5" stroke-linecap="round" transform="rotate({a} 396 186)"/>' for a in range(0, 360, 45))}
<text x="428" y="182" font-family="{fjp}" font-size="17" font-weight="800" fill="#ffffff">24℃</text>
<text x="428" y="204" font-family="{fjp}" font-size="10" fill="#b9b9c8">東京 ・ 晴れ</text>
<rect x="356" y="248" width="204" height="66" rx="16" fill="#ffffff" opacity="0.05"/>
<path d="M382 302 c-4 -13 4.5 -21 9 -29 c4.5 8 13 16 9 29 a9 9 0 0 1 -18 0z" fill="none" stroke="{glow}" stroke-width="2.2"/>
<text x="410" y="280" font-family="{fjp}" font-size="10.5" font-weight="700" fill="#ececf2">バッテリー 88%</text>
<text x="410" y="298" font-family="{fjp}" font-size="9" fill="#9c9cb0">あと2日と1時間</text>
{"".join(f'<rect x="{110 + i * 60}" y="264" width="44" height="44" rx="12" fill="{c}" opacity="{o}"/>' for i, (c, o) in enumerate(((glow, 0.85), ("#ffffff", 0.14), ("#ffffff", 0.11))))}"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="{label} 正面">
<defs>
<linearGradient id="frame{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{_shade(body_hex, 0.55)}"/>
  <stop offset="0.12" stop-color="{_shade(body_hex, -0.15)}"/>
  <stop offset="0.5" stop-color="{dark2}"/>
  <stop offset="0.88" stop-color="{_shade(body_hex, -0.2)}"/>
  <stop offset="1" stop-color="{_shade(body_hex, 0.35)}"/>
</linearGradient>
<linearGradient id="scr{gid}" x1="0" y1="0" x2="0.8" y2="1">
  <stop offset="0" stop-color="#171722"/>
  <stop offset="0.5" stop-color="#0d0d14"/>
  <stop offset="1" stop-color="#07070c"/>
</linearGradient>
<radialGradient id="flare{gid}" cx="0.5" cy="0.35" r="0.85">
  <stop offset="0" stop-color="{glow}" stop-opacity="0.28"/>
  <stop offset="0.55" stop-color="{glow}" stop-opacity="0.08"/>
  <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<filter id="soft{gid}" x="-40%" y="-40%" width="180%" height="180%">
  <feGaussianBlur stdDeviation="7"/>
</filter>
<clipPath id="clip{gid}"><rect x="58" y="44" width="524" height="388" rx="22"/></clipPath>
</defs>
<ellipse cx="320" cy="459" rx="216" ry="11" fill="#000000" opacity="0.4" filter="url(#soft{gid})"/>
<rect x="36" y="22" width="568" height="428" rx="35" fill="url(#frame{gid})"/>
<rect x="42" y="28" width="556" height="416" rx="30" fill="#06060a"/>
<rect x="58" y="44" width="524" height="388" rx="22" fill="url(#scr{gid})"/>
<g clip-path="url(#clip{gid})">
<ellipse cx="320" cy="200" rx="300" ry="180" fill="url(#flare{gid})"/>
{scene}
<text x="78" y="74" font-family="{fjp}" font-size="11" font-weight="700" fill="#e6e6ee">12:34</text>
<rect x="536" y="63.5" width="20" height="10" rx="3" fill="none" stroke="#c9c9d6" stroke-width="1.3"/>
<rect x="538" y="65.5" width="13" height="6" rx="1.5" fill="{glow}"/>
<rect x="556.6" y="66" width="2.4" height="5" rx="1" fill="#c9c9d6"/>
<rect x="275" y="418" width="90" height="4.5" rx="2.25" fill="#ffffff" opacity="0.5"/>
<path d="M58 44 L300 44 L120 432 L58 432 Z" fill="#ffffff" opacity="0.035"/>
</g>
<rect x="58.8" y="44.8" width="522.4" height="386.4" rx="21.4" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1.4"/>
<circle cx="320" cy="36" r="4" fill="#04040a" stroke="#2a2a36" stroke-width="1.2"/>
</svg>"""


def svg_die(gid, label, sub, glow):
    """半導体ダイショット風ビジュアル(CPU/GPU/メモリ/ストレージ)。"""
    gid = gid.replace("-", "")
    cells = []
    import random
    rnd = random.Random(gid)
    for r in range(6):
        for c in range(6):
            if 1 <= r <= 4 and 1 <= c <= 4:
                continue
            o = 0.16 + rnd.random() * 0.3
            cells.append(
                f'<rect x="{86 + c * 46}" y="{86 + r * 46}" width="40" height="40" rx="3" fill="{glow}" opacity="{o:.2f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" role="img" aria-label="{label}">
<defs>
<linearGradient id="pcb{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#15151e"/><stop offset="1" stop-color="#0b0b10"/>
</linearGradient>
<radialGradient id="core{gid}" cx="0.5" cy="0.5" r="0.7">
  <stop offset="0" stop-color="{glow}" stop-opacity="0.85"/>
  <stop offset="0.65" stop-color="{glow}" stop-opacity="0.2"/>
  <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
</defs>
<rect x="30" y="30" width="420" height="420" rx="26" fill="url(#pcb{gid})" stroke="{glow}" stroke-opacity="0.4" stroke-width="1.5"/>
{"".join(f'<line x1="{60 + i * 40}" y1="30" x2="{60 + i * 40}" y2="14" stroke="#3d3d4e" stroke-width="5"/>' for i in range(10))}
{"".join(f'<line x1="{60 + i * 40}" y1="450" x2="{60 + i * 40}" y2="466" stroke="#3d3d4e" stroke-width="5"/>' for i in range(10))}
{"".join(f'<line x1="30" y1="{60 + i * 40}" x2="14" y2="{60 + i * 40}" stroke="#3d3d4e" stroke-width="5"/>' for i in range(10))}
{"".join(f'<line x1="450" y1="{60 + i * 40}" x2="466" y2="{60 + i * 40}" stroke="#3d3d4e" stroke-width="5"/>' for i in range(10))}
{''.join(cells)}
<rect x="132" y="132" width="216" height="216" rx="10" fill="#0a0a10" stroke="{glow}" stroke-opacity="0.8" stroke-width="2"/>
<circle cx="240" cy="240" r="130" fill="url(#core{gid})"/>
<path d="M240 168 c-9 37 -46 53 -46 92 a46 46 0 0 0 92 0 c0 -39 -37 -55 -46 -92z" fill="none" stroke="{glow}" stroke-width="5" stroke-linejoin="round"/>
<text x="240" y="298" font-family="'Noto Sans JP',sans-serif" font-size="26" font-weight="900" fill="#ffffff" text-anchor="middle" letter-spacing="3">{label}</text>
<text x="240" y="322" font-family="'Noto Sans JP',sans-serif" font-size="12" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">{sub}</text>
</svg>"""


def svg_art(kind, glow="#e8442e", body_hex="#181820", motif=None):
    """feature-split・アクセサリ用のアートパネル(480×360)。

    kind ごとに専用の造形を描く。アクセサリ系(cooler/grip/buds/charger/case/
    dock/powerbank)は body_hex を筐体色として質感グラデーションで塗り、
    powerbank は motif(コラボslug)で意匠を差別化する。"""
    g = glow
    b = body_hex
    # 同一ページに複数インライン展開しても勾配定義が衝突しないよう、
    # パラメータ由来の決定的なID接尾辞を付ける
    u = (kind + glow + body_hex + (motif or "")).replace("#", "")
    bl = _shade(b, 0.4)
    bl2 = _shade(b, 0.14)
    bd = _shade(b, -0.4)
    bd2 = _shade(b, -0.62)
    ink = "#1c1c26" if _is_light(b) else "#e9e9f2"
    grid = "".join(f'<path d="M{x} 0 V360" stroke="#ffffff" stroke-opacity="0.03"/>' for x in range(40, 480, 40)) + \
           "".join(f'<path d="M0 {y} H480" stroke="#ffffff" stroke-opacity="0.03"/>' for y in range(40, 360, 40))
    common = f"""<defs>
<radialGradient id="ag{u}" cx="0.5" cy="0.4" r="0.8">
  <stop offset="0" stop-color="{g}" stop-opacity="0.7"/>
  <stop offset="0.55" stop-color="{g}" stop-opacity="0.16"/>
  <stop offset="1" stop-color="{g}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="al{u}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{g}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{g}"/>
  <stop offset="1" stop-color="{g}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="mb{u}" x1="0" y1="0" x2="0.85" y2="1">
  <stop offset="0" stop-color="{bl}"/>
  <stop offset="0.3" stop-color="{bl2}"/>
  <stop offset="0.65" stop-color="{b}"/>
  <stop offset="1" stop-color="{bd}"/>
</linearGradient>
<linearGradient id="mt{u}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.3"/>
  <stop offset="0.4" stop-color="#ffffff" stop-opacity="0.05"/>
  <stop offset="1" stop-color="#000000" stop-opacity="0.3"/>
</linearGradient>
<radialGradient id="gl{u}" cx="0.38" cy="0.32" r="0.95">
  <stop offset="0" stop-color="#39414f"/>
  <stop offset="0.4" stop-color="#12151d"/>
  <stop offset="1" stop-color="#04040a"/>
</radialGradient>
<filter id="fz{u}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="480" height="360" fill="#0b0b10"/>
{grid}
<ellipse cx="240" cy="176" rx="225" ry="145" fill="url(#ag{u})"/>"""

    def shadow(cx, cy, rx):
        return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="10" fill="#000" opacity="0.45" filter="url(#fz{u})"/>'

    body = ""
    if kind in ("chip", "npu"):
        traces = "".join(
            f'<path d="M240 180 L{x} {y}" stroke="{g}" stroke-opacity="0.45" stroke-width="1.6"/><circle cx="{x}" cy="{y}" r="4" fill="{g}" opacity="0.85"/><circle cx="{x}" cy="{y}" r="7.5" fill="none" stroke="{g}" stroke-opacity="0.3"/>'
            for x, y in [(78, 66), (56, 180), (88, 292), (402, 66), (424, 180), (392, 292), (168, 36), (312, 36), (168, 324), (312, 324)])
        pins = "".join(f'<circle cx="{190 + c * 20}" cy="{262}" r="3" fill="#8a8a9c" opacity="0.8"/>' for c in range(6))
        body = f"""{traces}
{shadow(240, 268, 90)}
<rect x="168" y="104" width="144" height="144" rx="16" fill="#151520" stroke="{_shade('#151520', 0.35)}" stroke-width="1.6"/>
<rect x="168" y="104" width="144" height="144" rx="16" fill="url(#mt{u})"/>
<rect x="188" y="124" width="104" height="104" rx="10" fill="#07070c" stroke="{g}" stroke-width="1.8"/>
<rect x="188" y="124" width="104" height="104" rx="10" fill="url(#ag{u})" opacity="0.5"/>
<path d="M240 142 c-7 27 -33 38 -33 66 a33 33 0 0 0 66 0 c0 -28 -26 -39 -33 -66z" fill="none" stroke="{g}" stroke-width="3.6" stroke-linejoin="round"/>
<circle cx="240" cy="216" r="7" fill="{g}"/>
{pins}
<text x="240" y="290" font-family="sans-serif" font-size="10" fill="{g}" text-anchor="middle" letter-spacing="4" opacity="0.85">SUZAKU SILICON</text>"""
        if kind == "npu":
            mesh = "".join(f'<circle cx="{x}" cy="{y}" r="6.5" fill="none" stroke="{g}" stroke-width="2" opacity="0.9"/>'
                           for x, y in [(120, 108), (120, 252), (360, 108), (360, 252)])
            links = "".join(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{g}" stroke-opacity="0.35" stroke-width="1.4"/>'
                            for x1, y1, x2, y2 in [(120, 108, 120, 252), (360, 108, 360, 252), (120, 108, 360, 108), (120, 252, 360, 252)])
            body += links + mesh
    elif kind == "gpu":
        rows = "".join(
            f'<rect x="{158 + c * 30}" y="{118 + r * 30}" width="24" height="24" rx="4" fill="{g}" opacity="{0.2 + ((r * 5 + c * 3) % 10) * 0.07:.2f}"/>'
            for r in range(4) for c in range(6))
        body = f"""{shadow(240, 272, 110)}
<rect x="140" y="98" width="200" height="168" rx="16" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.6"/>
<rect x="140" y="98" width="200" height="168" rx="16" fill="url(#mt{u})"/>
<rect x="150" y="108" width="180" height="148" rx="10" fill="#0a0a12"/>
{rows}
<rect x="352" y="120" width="46" height="30" rx="6" fill="#0f0f18" stroke="{g}" stroke-opacity="0.7" stroke-width="1.5"/>
<text x="375" y="139" font-family="sans-serif" font-size="10" font-weight="700" fill="{g}" text-anchor="middle">RT</text>
<rect x="352" y="160" width="46" height="30" rx="6" fill="#0f0f18" stroke="{g}" stroke-opacity="0.45" stroke-width="1.5"/>
<text x="375" y="179" font-family="sans-serif" font-size="10" font-weight="700" fill="{g}" opacity="0.7" text-anchor="middle">AI</text>
<path d="M60 306 L420 306" stroke="url(#al{u})" stroke-width="2.5"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">HOMURA GRAPHICS</text>"""
    elif kind == "memory":
        sticks = ""
        for i in range(4):
            x = 104 + i * 74
            op = 1 - i * 0.14
            sticks += f"""
<g opacity="{op:.2f}">{shadow(x + 24, 268, 34)}
<rect x="{x}" y="96" width="48" height="164" rx="7" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.5"/>
<rect x="{x}" y="96" width="48" height="164" rx="7" fill="url(#mt{u})"/>
<rect x="{x + 9}" y="112" width="30" height="52" rx="4" fill="{g}" opacity="0.75"/>
<rect x="{x + 9}" y="172" width="30" height="52" rx="4" fill="{g}" opacity="0.35"/>
{"".join(f'<rect x="{x + 7 + j * 9}" y="248" width="5" height="10" fill="#c8a24a"/>' for j in range(4))}</g>"""
        body = f"""{sticks}
<path d="M70 60 h340" stroke="url(#al{u})" stroke-width="2" opacity="0.8"/>
<text x="240" y="326" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">HAYATE LPDDR6</text>"""
    elif kind == "storage":
        arrows = "".join(
            f'<path d="M{58} {138 + i * 26} h56" stroke="{g}" stroke-opacity="{0.85 - i * 0.2}" stroke-width="4" stroke-linecap="round"/><path d="M{106} {132 + i * 26} l10 6 -10 6" fill="none" stroke="{g}" stroke-opacity="{0.85 - i * 0.2}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
            for i in range(4))
        body = f"""{shadow(248, 262, 120)}
<rect x="128" y="112" width="240" height="136" rx="14" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.6"/>
<rect x="128" y="112" width="240" height="136" rx="14" fill="url(#mt{u})"/>
<rect x="146" y="132" width="86" height="96" rx="9" fill="#0a0a12" stroke="{g}" stroke-width="1.8"/>
<path d="M189 150 c-5 20 -25 28 -25 49 a25 25 0 0 0 50 0 c0 -21 -20 -29 -25 -49z" fill="none" stroke="{g}" stroke-width="2.8"/>
<rect x="248" y="132" width="50" height="96" rx="7" fill="{g}" opacity="0.35"/>
<rect x="306" y="132" width="50" height="96" rx="7" fill="{g}" opacity="0.22"/>
{arrows}
<text x="240" y="292" font-family="sans-serif" font-size="11" font-weight="700" fill="{g}" text-anchor="middle" letter-spacing="3" opacity="0.9">5,800 MB/s</text>
<text x="240" y="326" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">SHUN UFS 4.1</text>"""
    elif kind == "cooling":
        layers = ""
        for i in range(7):
            w = 250 - i * 14
            x = 240 - w / 2
            y = 84 + i * 27
            layers += f"""{shadow(240, y + 20, w / 2)}
<rect x="{x}" y="{y}" width="{w}" height="16" rx="8" fill="{g}" opacity="{0.9 - i * 0.11:.2f}"/>
<rect x="{x}" y="{y}" width="{w}" height="16" rx="8" fill="url(#mt{u})"/>"""
        body = f"""{layers}
<path d="M140 312 q30 -20 60 0 t60 0 t60 0 t60 0" fill="none" stroke="{g}" stroke-width="3" opacity="0.75"/>
<text x="240" y="345" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">11-LAYER COOLING</text>"""
    elif kind == "fan":
        blades = "".join(
            f'<path d="M240 180 q34 -36 80 -22" fill="none" stroke="{g}" stroke-width="10" stroke-linecap="round" opacity="0.9" transform="rotate({i * 40} 240 180)"/>'
            for i in range(9))
        vents = "".join(f'<path d="M240 180 m0 -122 a122 122 0 0 1 0 244" fill="none" stroke="{g}" stroke-opacity="0.25" stroke-width="2" transform="rotate({a} 240 180)"/>' for a in (0, 90))
        body = f"""{shadow(240, 312, 120)}
<circle cx="240" cy="180" r="122" fill="#10101a" stroke="{_shade('#10101a', 0.35)}" stroke-width="2"/>
<circle cx="240" cy="180" r="122" fill="url(#mt{u})"/>
<circle cx="240" cy="180" r="106" fill="#07070c"/>
{vents}{blades}
<circle cx="240" cy="180" r="27" fill="#0d0d16" stroke="{g}" stroke-width="2.6"/>
<circle cx="240" cy="180" r="8" fill="{g}"/>
<text x="240" y="336" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">24,000 RPM</text>"""
    elif kind == "liquid":
        body = f"""{shadow(240, 276, 130)}
<rect x="104" y="88" width="272" height="180" rx="20" fill="#151520" stroke="{_shade('#151520', 0.3)}" stroke-width="1.8"/>
<rect x="104" y="88" width="272" height="180" rx="20" fill="url(#mt{u})"/>
<path d="M132 178 q54 -66 108 0 t108 0" fill="none" stroke="{g}" stroke-width="7" stroke-linecap="round"/>
<path d="M132 178 q54 66 108 0 t108 0" fill="none" stroke="{g}" stroke-width="7" stroke-linecap="round" opacity="0.4"/>
<circle cx="240" cy="178" r="24" fill="#07070c" stroke="{g}" stroke-width="3.2"/>
<circle cx="240" cy="178" r="9" fill="{g}"/>
<circle cx="168" cy="128" r="4" fill="{g}" opacity="0.7"/><circle cx="318" cy="228" r="4" fill="{g}" opacity="0.7"/>
<text x="240" y="304" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">ACTIVE LIQUID LOOP</text>"""
    elif kind == "display":
        rays = "".join(f'<path d="M240 60 l0 -18" stroke="{g}" stroke-opacity="0.6" stroke-width="3" stroke-linecap="round" transform="rotate({a} 240 168)"/>' for a in range(-60, 61, 30))
        body = f"""{shadow(240, 276, 140)}
<rect x="104" y="72" width="272" height="192" rx="16" fill="#0c0c14" stroke="{_shade('#0c0c14', 0.4)}" stroke-width="2"/>
<rect x="112" y="80" width="256" height="176" rx="10" fill="#07070b"/>
<rect x="112" y="80" width="256" height="176" rx="10" fill="url(#ag{u})"/>
<path d="M112 80 L368 80 L220 256 L112 256 Z" fill="#ffffff" opacity="0.05"/>
{rays}
<path d="M240 118 c-8 30 -38 43 -38 74 a38 38 0 0 0 76 0 c0 -31 -30 -44 -38 -74z" fill="none" stroke="{g}" stroke-width="3.8" stroke-linejoin="round"/>
<rect x="196" y="276" width="88" height="26" rx="13" fill="#0f0f18" stroke="{g}" stroke-opacity="0.7" stroke-width="1.5"/>
<text x="240" y="294" font-family="sans-serif" font-size="13" font-weight="700" fill="{g}" text-anchor="middle" letter-spacing="2">175Hz</text>"""
    elif kind == "camera":
        aperture = "".join(f'<path d="M240 176 L240 118 A58 58 0 0 1 290 147 Z" fill="#0b0e15" stroke="#2a2f3c" stroke-width="1" transform="rotate({a} 240 176)"/>' for a in range(0, 360, 60))
        body = f"""{shadow(240, 296, 120)}
<circle cx="240" cy="176" r="112" fill="#151520" stroke="{_shade('#151520', 0.35)}" stroke-width="2.5"/>
<circle cx="240" cy="176" r="112" fill="url(#mt{u})"/>
<circle cx="240" cy="176" r="88" fill="#0a0d14" stroke="{g}" stroke-opacity="0.8" stroke-width="2"/>
<circle cx="240" cy="176" r="72" fill="url(#gl{u})"/>
{aperture}
<circle cx="240" cy="176" r="30" fill="url(#gl{u})"/>
<circle cx="240" cy="176" r="12" fill="#04040a"/>
<circle cx="216" cy="150" r="12" fill="#ffffff" opacity="0.4"/>
<circle cx="262" cy="204" r="6" fill="{g}" opacity="0.5"/>
<path d="M120 70 L180 110" stroke="#ffffff" stroke-opacity="0.25" stroke-width="3" stroke-linecap="round"/>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">TENGAN OPTICS</text>"""
    elif kind == "battery":
        cells = "".join(f'<rect x="{160 + i * 34}" y="150" width="24" height="60" rx="5" fill="{g}" opacity="{0.85 - i * 0.16:.2f}"/>' for i in range(4))
        body = f"""{shadow(240, 268, 110)}
<rect x="136" y="104" width="192" height="152" rx="20" fill="#151520" stroke="{_shade('#151520', 0.32)}" stroke-width="2"/>
<rect x="136" y="104" width="192" height="152" rx="20" fill="url(#mt{u})"/>
<rect x="328" y="150" width="20" height="60" rx="8" fill="{_shade('#151520', 0.25)}"/>
<rect x="148" y="116" width="168" height="128" rx="12" fill="#0a0a12"/>
{cells}
<path d="M252 120 l-46 70 h32 l-16 62 l56 -80 h-32 l24 -52z" fill="{g}" stroke="#0b0b10" stroke-width="5" stroke-linejoin="round" opacity="0.98"/>
<text x="240" y="298" font-family="sans-serif" font-size="11" font-weight="700" fill="{g}" text-anchor="middle" letter-spacing="2" opacity="0.9">120W HYPERCHARGE</text>"""
    elif kind == "os":
        tiles = "".join(
            f'<rect x="{140 + (i % 3) * 70}" y="{116 + (i // 3) * 70}" width="58" height="58" rx="13" fill="{g}" opacity="{0.22 + (i % 4) * 0.15:.2f}"/><rect x="{140 + (i % 3) * 70}" y="{116 + (i // 3) * 70}" width="58" height="58" rx="13" fill="url(#mt{u})" opacity="0.5"/>'
            for i in range(6))
        body = f"""{shadow(240, 292, 130)}
<rect x="118" y="76" width="244" height="212" rx="18" fill="#0c0c14" stroke="{_shade('#0c0c14', 0.4)}" stroke-width="2"/>
<rect x="126" y="84" width="228" height="196" rx="12" fill="#07070b"/>
<rect x="126" y="84" width="228" height="196" rx="12" fill="url(#ag{u})" opacity="0.45"/>
<text x="140" y="106" font-family="sans-serif" font-size="10" font-weight="700" fill="#e6e6ee">12:34</text>
<circle cx="340" cy="102" r="3.5" fill="{g}"/>
{tiles}
<rect x="196" y="296" width="88" height="5" rx="2.5" fill="#4a4a5c"/>
<path d="M240 128 c-5 18 -22 25 -22 43 a22 22 0 0 0 44 0 c0 -18 -17 -25 -22 -43z" fill="none" stroke="{g}" stroke-width="2.6" transform="translate(0 60)" opacity="0.9"/>"""
    elif kind == "cooler":
        blades = "".join(
            f'<path d="M240 168 q30 -32 68 -19" fill="none" stroke="{g}" stroke-width="9" stroke-linecap="round" opacity="0.92" transform="rotate({i * 51.4:.0f} 240 168)"/>'
            for i in range(7))
        body = f"""{shadow(240, 322, 110)}
<path d="M150 96 h180 a26 26 0 0 1 26 26 v150 a26 26 0 0 1 -26 26 h-180 a26 26 0 0 1 -26 -26 v-150 a26 26 0 0 1 26 -26z" fill="url(#mb{u})"/>
<path d="M150 96 h180 a26 26 0 0 1 26 26 v150 a26 26 0 0 1 -26 26 h-180 a26 26 0 0 1 -26 -26 v-150 a26 26 0 0 1 26 -26z" fill="url(#mt{u})"/>
<path d="M104 140 q-26 10 -26 34 M376 140 q26 10 26 34" fill="none" stroke="{bd2}" stroke-width="10" stroke-linecap="round"/>
<circle cx="240" cy="168" r="84" fill="#07070c" stroke="{g}" stroke-width="2.6"/>
{blades}
<circle cx="240" cy="168" r="22" fill="#0d0d16" stroke="{g}" stroke-width="2.6"/>
<circle cx="240" cy="168" r="7" fill="{g}"/>
{"".join(f'<circle cx="{c}" cy="82" r="3" fill="#bfe8ff" opacity="0.8"/>' for c in (196, 240, 284))}
<rect x="214" y="300" width="52" height="12" rx="6" fill="{bd2}"/>
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="3">PELTIER -28℃</text>"""
    elif kind == "grip":
        abxy = "".join(
            f'<circle cx="{352 + dx}" cy="{172 + dy}" r="8.5" fill="{c}"/>'
            for (dx, dy), c in zip([(0, -20), (20, 0), (0, 20), (-20, 0)], ("#e8b23a", "#e8442e", "#3d8bff", "#38b67a")))
        body = f"""{shadow(240, 262, 150)}
<rect x="168" y="140" width="144" height="66" rx="12" fill="{bd2}"/>
<rect x="176" y="146" width="128" height="54" rx="8" fill="#07070b"/>
<rect x="176" y="146" width="128" height="54" rx="8" fill="url(#ag{u})" opacity="0.6"/>
<path d="M96 128 h72 a14 14 0 0 1 14 14 v64 a14 14 0 0 1 -14 14 h-72 a40 40 0 0 1 -40 -40 v-12 a40 40 0 0 1 40 -40z" fill="url(#mb{u})"/>
<path d="M96 128 h72 a14 14 0 0 1 14 14 v64 a14 14 0 0 1 -14 14 h-72 a40 40 0 0 1 -40 -40 v-12 a40 40 0 0 1 40 -40z" fill="url(#mt{u})"/>
<path d="M384 128 h-72 a14 14 0 0 0 -14 14 v64 a14 14 0 0 0 14 14 h72 a40 40 0 0 0 40 -40 v-12 a40 40 0 0 0 -40 -40z" fill="url(#mb{u})"/>
<path d="M384 128 h-72 a14 14 0 0 0 -14 14 v64 a14 14 0 0 0 14 14 h72 a40 40 0 0 0 40 -40 v-12 a40 40 0 0 0 -40 -40z" fill="url(#mt{u})"/>
<circle cx="128" cy="172" r="30" fill="#101018" stroke="{_shade(b, 0.3)}" stroke-width="2"/>
<circle cx="128" cy="172" r="30" fill="none" stroke="{g}" stroke-opacity="0.5" stroke-width="1.4"/>
<circle cx="128" cy="172" r="13" fill="url(#gl{u})" stroke="{g}" stroke-width="1.6"/>
{abxy}
<rect x="98" y="108" width="52" height="12" rx="6" fill="{g}"/>
<rect x="330" y="108" width="52" height="12" rx="6" fill="{g}"/>
<circle cx="222" cy="216" r="5" fill="{g}"/><circle cx="258" cy="216" r="5" fill="{g}" opacity="0.5"/>
<text x="240" y="300" font-family="sans-serif" font-size="10" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="3">HALL EFFECT ・ 0.8ms</text>"""
    elif kind == "buds":
        def bud(cx, flip):
            s = -1 if flip else 1
            return f"""
<g transform="translate({cx} 0)">
<path d="M0 132 a34 34 0 0 1 34 34 v10 a20 20 0 0 1 -40 0 z" fill="url(#mb{u})" transform="scale({s} 1)"/>
<path d="M0 132 a34 34 0 0 1 34 34 v10 a20 20 0 0 1 -40 0 z" fill="url(#mt{u})" transform="scale({s} 1)"/>
<rect x="{-8 if flip else -12}" y="176" width="20" height="58" rx="10" fill="url(#mb{u})"/>
<rect x="{-8 if flip else -12}" y="176" width="20" height="58" rx="10" fill="url(#mt{u})"/>
<circle cx="{s * 14}" cy="160" r="9" fill="url(#gl{u})" stroke="{g}" stroke-width="1.6"/>
<circle cx="{-2 if flip else 2}" cy="226" r="3" fill="{g}"/>
</g>"""
        body = f"""{shadow(240, 306, 130)}
<path d="M132 236 a108 62 0 0 1 216 0 v18 a108 46 0 0 1 -216 0 z" fill="url(#mb{u})"/>
<path d="M132 236 a108 62 0 0 1 216 0 v18 a108 46 0 0 1 -216 0 z" fill="url(#mt{u})"/>
<path d="M132 236 a108 62 0 0 1 216 0" fill="none" stroke="{_shade(b, 0.35)}" stroke-width="2"/>
<rect x="216" y="252" width="48" height="7" rx="3.5" fill="{g}" opacity="0.9"/>
{bud(186, False)}{bud(294, True)}
<path d="M112 96 q-18 20 0 40 M96 82 q-30 34 0 68" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
<path d="M368 96 q18 20 0 40 M384 82 q30 34 0 68" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
<text x="240" y="340" font-family="sans-serif" font-size="10" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="3">38ms LOW LATENCY</text>"""
    elif kind == "charger":
        body = f"""{shadow(240, 292, 110)}
<rect x="152" y="84" width="176" height="176" rx="34" fill="url(#mb{u})"/>
<rect x="152" y="84" width="176" height="176" rx="34" fill="url(#mt{u})"/>
<rect x="153.2" y="85.2" width="173.6" height="173.6" rx="32.8" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.6"/>
<path d="M250 108 l-46 66 h32 l-17 58 l56 -74 h-32 l23 -50z" fill="{g}" stroke="{bd2}" stroke-width="4" stroke-linejoin="round"/>
<rect x="192" y="260" width="16" height="34" rx="5" fill="url(#mt{u})" stroke="{bd2}" stroke-width="1"/>
<rect x="272" y="260" width="16" height="34" rx="5" fill="url(#mt{u})" stroke="{bd2}" stroke-width="1"/>
<rect x="222" y="176" width="36" height="14" rx="7" fill="#07070b" stroke="{g}" stroke-opacity="0.7" stroke-width="1.4" transform="translate(0 62)"/>
<text x="240" y="330" font-family="sans-serif" font-size="12" font-weight="700" fill="{ink}" opacity="0.7" text-anchor="middle" letter-spacing="3">120W GaN</text>"""
    elif kind == "case":
        lattice = "".join(
            f'<path d="M{200 + i * 22} 150 l14 24 l-14 24 l-14 -24 z" fill="none" stroke="{g}" stroke-opacity="0.35" stroke-width="2"/>'
            for i in range(5))
        body = f"""{shadow(240, 322, 100)}
<rect x="152" y="48" width="176" height="266" rx="32" fill="url(#mb{u})"/>
<rect x="152" y="48" width="176" height="266" rx="32" fill="url(#mt{u})"/>
<rect x="153.4" y="49.4" width="173.2" height="263.2" rx="30.6" fill="none" stroke="#ffffff" stroke-opacity="0.13" stroke-width="1.8"/>
<rect x="170" y="64" width="140" height="96" rx="22" fill="{bd2}"/>
{"".join(f'<circle cx="{198 + i * 42}" cy="100" r="16" fill="#0a0d13" stroke="{_shade(b, 0.35)}" stroke-width="1.6"/><circle cx="{198 + i * 42}" cy="100" r="10" fill="url(#gl{u})"/>' for i in range(3))}
{lattice}
<path d="M240 232 c-6 20 -25 29 -25 49 a25 25 0 0 0 50 0 c0 -20 -19 -29 -25 -49z" fill="none" stroke="{g}" stroke-width="2.8" stroke-linejoin="round"/>
<rect x="326" y="120" width="6" height="42" rx="3" fill="{bd2}"/>
<rect x="326" y="176" width="6" height="30" rx="3" fill="{bd2}"/>
<text x="240" y="342" font-family="sans-serif" font-size="10" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="3">MIL-STD-810H</text>"""
    elif kind == "dock":
        body = f"""{shadow(240, 316, 150)}
<path d="M120 296 L360 296 L332 176 L148 176 Z" fill="url(#mb{u})"/>
<path d="M120 296 L360 296 L332 176 L148 176 Z" fill="url(#mt{u})"/>
<rect x="108" y="292" width="264" height="20" rx="10" fill="{bd2}"/>
{"".join(f'<rect x="{150 + i * 20}" y="298" width="10" height="8" rx="2" fill="#07070b"/>' for i in range(9))}
<rect x="146" y="70" width="188" height="118" rx="14" fill="#0c0c14" stroke="{_shade(b, 0.3)}" stroke-width="2"/>
<rect x="154" y="78" width="172" height="102" rx="9" fill="#07070b"/>
<rect x="154" y="78" width="172" height="102" rx="9" fill="url(#ag{u})"/>
<path d="M240 100 c-6 22 -28 31 -28 54 a28 28 0 0 0 56 0 c0 -23 -22 -32 -28 -54z" fill="none" stroke="{g}" stroke-width="3" stroke-linejoin="round"/>
<rect x="196" y="196" width="88 " height="10" rx="5" fill="{bd2}"/>
<circle cx="348" cy="248" r="5" fill="{g}"/>
<text x="240" y="342" font-family="sans-serif" font-size="10" fill="{ink}" opacity="0.6" text-anchor="middle" letter-spacing="3">4K/120 ・ 80W</text>"""
    elif kind == "powerbank":
        # コラボ・モバイルバッテリー。motif(slug)ごとに意匠を差し替える
        deco = ""
        if motif == "genshin":
            elems = ("#74c2a8", "#d8b45c", "#a68cc8", "#9ac546", "#4cc2f1", "#ef7938", "#9fd6e3")
            deco = "".join(
                f'<circle cx="{240 + 54 * math.cos(math.radians(-90 + i * 360 / 7)):.1f}" cy="{150 + 54 * math.sin(math.radians(-90 + i * 360 / 7)):.1f}" r="7" fill="none" stroke="{c}" stroke-width="2.4" opacity="0.95"/>'
                for i, c in enumerate(elems)) + f'<circle cx="240" cy="150" r="54" fill="none" stroke="{g}" stroke-opacity="0.35" stroke-width="1.5"/>'
        elif motif == "wuwa":
            deco = f'<path d="M162 150 l14 0 6 -22 10 44 10 -34 8 12 h68" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>' \
                   f'<path d="M162 150 h156" stroke="{g}" stroke-opacity="0.25" stroke-width="1.5"/>'
        elif motif == "nte":
            deco = f'<path d="M190 128 h100 v44 h-100 z" fill="none" stroke="{g}" stroke-width="2.5" opacity="0.9"/>' \
                   f'<path d="M204 172 v14 M240 172 v20 M276 172 v14" stroke="{g}" stroke-width="2.5" opacity="0.7"/>' \
                   f'<text x="240" y="157" font-family="sans-serif" font-size="15" font-weight="800" fill="{g}" text-anchor="middle" letter-spacing="4">NEON</text>'
        elif motif == "endfield":
            deco = "".join(f'<path d="M{170 + i * 30} 128 l16 0 l-12 44 l-16 0 z" fill="{g}" opacity="{0.85 - i * 0.15:.2f}"/>' for i in range(4))
        else:
            deco = f'<path d="M240 118 c-7 26 -32 37 -32 64 a32 32 0 0 0 64 0 c0 -27 -25 -38 -32 -64z" fill="none" stroke="{g}" stroke-width="3.4"/>'
        leds = "".join(f'<circle cx="{204 + i * 24}" cy="238" r="5" fill="{g}" opacity="{0.95 - i * 0.22:.2f}"/>' for i in range(4))
        body = f"""{shadow(240, 302, 120)}
<rect x="140" y="72" width="200" height="216" rx="30" fill="url(#mb{u})"/>
<rect x="140" y="72" width="200" height="216" rx="30" fill="url(#mt{u})"/>
<rect x="141.4" y="73.4" width="197.2" height="213.2" rx="28.6" fill="none" stroke="#ffffff" stroke-opacity="0.14" stroke-width="1.8"/>
<circle cx="240" cy="150" r="66" fill="none" stroke="{_shade(b, 0.28)}" stroke-width="2" stroke-dasharray="7 7" opacity="0.9"/>
{deco}
{leds}
<rect x="286" y="230" width="34" height="16" rx="8" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<rect x="222" y="286" width="36" height="9" rx="4.5" fill="#07070b" stroke="{_shade(b, 0.3)}" stroke-width="1.4"/>
<text x="240" y="270" font-family="sans-serif" font-size="12" font-weight="800" fill="{ink}" opacity="0.75" text-anchor="middle" letter-spacing="2">10000mAh ・ 45W</text>
<text x="240" y="330" font-family="sans-serif" font-size="10" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">MAGNETIC WIRELESS</text>"""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 360" role="img" aria-label="">{common}{body}</svg>'


BRAND_MARK = """<svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
<path class="brand-mark__flame" d="M24 4 C21 16 10 21 10 31 a14 14 0 0 0 28 0 C38 21 27 16 24 4 Z" stroke="url(#bm-g)" stroke-width="3" stroke-linejoin="round"/>
<circle cx="24" cy="33" r="4.2" fill="#e8442e"/>
<defs><linearGradient id="bm-g" x1="10" y1="4" x2="38" y2="45"><stop stop-color="#ff6a3c"/><stop offset="1" stop-color="#e8442e"/></linearGradient></defs>
</svg>"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="10" fill="#0b0b10"/><path d="M24 6 C21.4 16.5 12 21 12 30 a12 12 0 0 0 24 0 C36 21 26.6 16.5 24 6 Z" fill="none" stroke="#e8442e" stroke-width="3" stroke-linejoin="round"/><circle cx="24" cy="31.5" r="3.6" fill="#ff6a3c"/></svg>"""

ICONS = {
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    "cart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 7h13l-1.5 9h-10z"/><path d="M6 7L5 4H2.5"/><circle cx="9" cy="20" r="1.6"/><circle cx="16" cy="20" r="1.6"/></svg>',
    "user": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="8.5" r="4"/><path d="M4.5 20c1.5-3.5 4.2-5 7.5-5s6 1.5 7.5 5"/></svg>',
}
