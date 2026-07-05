# -*- coding: utf-8 -*-
"""SUZAKU サイト用SVGアート生成。

製品ビジュアル・技術ダイアグラム・アイコン類をすべてコードから生成する。
外部画像に一切依存しないため、画像のリンク切れが構造的に発生しない。
"""


def _defs(gid, glow):
    return f"""<defs>
<linearGradient id="scr{gid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1b1b26"/>
  <stop offset="0.45" stop-color="{glow}" stop-opacity="0.34"/>
  <stop offset="1" stop-color="#07070b"/>
</linearGradient>
<radialGradient id="flare{gid}" cx="0.5" cy="0.35" r="0.75">
  <stop offset="0" stop-color="{glow}" stop-opacity="0.42"/>
  <stop offset="0.55" stop-color="{glow}" stop-opacity="0.12"/>
  <stop offset="1" stop-color="{glow}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="metal{gid}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>
  <stop offset="0.5" stop-color="#ffffff" stop-opacity="0.04"/>
  <stop offset="1" stop-color="#000000" stop-opacity="0.25"/>
</linearGradient>
</defs>"""


def svg_phone(pid, body_hex, glow, label, kana="", line="suzaku", hz="144Hz"):
    """スマートフォン正面ビュー(ステータスバー・HUD/ドック・反射付き)。"""
    gid = pid.replace("-", "")
    gaming = line in ("suzaku", "neo")
    # パンチホールカメラ(旗艦SUZAKUはアンダーディスプレイのため無し)
    hole = "" if line == "suzaku" else f'<circle cx="180" cy="56" r="5" fill="#050508" stroke="#33333f" stroke-width="1.5"/>'
    # ステータスバー
    status = f"""
<text x="96" y="62" font-family="'Noto Sans JP',sans-serif" font-size="13" font-weight="700" fill="#e6e6ee">12:34</text>
<rect x="228" y="52" width="3.5" height="5" rx="1" fill="#c9c9d6"/>
<rect x="233" y="49.5" width="3.5" height="7.5" rx="1" fill="#c9c9d6"/>
<rect x="238" y="47" width="3.5" height="10" rx="1" fill="#c9c9d6"/>
<rect x="247" y="49" width="19" height="9.5" rx="3.5" fill="none" stroke="#c9c9d6" stroke-width="1.4"/>
<rect x="249" y="51" width="11" height="5.5" rx="1.5" fill="{glow}"/>"""
    # 下部: ゲーミング=fps HUD / 一般=アプリドック
    if gaming:
        bottom = f"""
<rect x="118" y="540" width="124" height="27" rx="13.5" fill="#07070b" stroke="{glow}" stroke-opacity="0.65" stroke-width="1.4"/>
<circle cx="134" cy="553.5" r="4.5" fill="{glow}"/>
<text x="188" y="558" font-family="'Noto Sans JP',sans-serif" font-size="12.5" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">{hz} 陣</text>"""
    else:
        docks = "".join(
            f'<rect x="{116 + i * 36}" y="540" width="24" height="24" rx="7" fill="#ffffff" opacity="{o}"/>'
            for i, o in enumerate((0.16, 0.24, 0.18, 0.22)))
        bottom = docks
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 640" role="img" aria-label="{label}">
{_defs(gid, glow)}
<rect x="70" y="20" width="220" height="600" rx="38" fill="{body_hex}"/>
<rect x="70" y="20" width="220" height="600" rx="38" fill="url(#metal{gid})"/>
<rect x="70.8" y="20.8" width="218.4" height="598.4" rx="37.2" fill="none" stroke="{glow}" stroke-opacity="0.55" stroke-width="1.6"/>
<path d="M70 132 h4 M70 470 h4 M286 132 h4 M286 470 h4" stroke="#4a4a5a" stroke-width="2.5"/>
<rect x="80" y="30" width="200" height="580" rx="30" fill="url(#scr{gid})"/>
<ellipse cx="180" cy="235" rx="110" ry="130" fill="url(#flare{gid})"/>
{hole}{status}
<path d="M180 158 c-9 39 -48 56 -48 97 a48 48 0 0 0 96 0 c0 -41 -39 -58 -48 -97z" fill="none" stroke="{glow}" stroke-width="4.5" stroke-linejoin="round" opacity="0.95"/>
<circle cx="180" cy="262" r="12" fill="{glow}"/>
<text x="180" y="348" font-family="'Noto Sans JP',sans-serif" font-size="24" font-weight="800" fill="#f4f4f8" text-anchor="middle" letter-spacing="2">{label}</text>
<text x="180" y="373" font-family="'Noto Sans JP',sans-serif" font-size="12" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">{kana}</text>
<text x="180" y="430" font-family="'Noto Sans JP',sans-serif" font-size="11" fill="#7a7a90" text-anchor="middle" letter-spacing="1.5">{'GAME SPACE 準備完了' if gaming else 'こんにちは'}</text>
{bottom}
<rect x="140" y="596" width="80" height="4" rx="2" fill="#ffffff" opacity="0.35"/>
<path d="M92 30 L268 30 L120 610 L80 610 L80 480 Z" fill="#ffffff" opacity="0.035"/>
<rect x="292" y="150" width="5" height="52" rx="2.5" fill="{glow}"/>
<rect x="292" y="220" width="5" height="52" rx="2.5" fill="{glow}"/>
<rect x="63" y="180" width="5" height="70" rx="2.5" fill="#3d3d4e"/>
</svg>"""


def svg_tablet(pid, body_hex, glow, label, kana="", line="pad", hz="120Hz"):
    gid = pid.replace("-", "")
    gaming = line in ("pad", "pad-neo")
    if gaming:
        bottom = f"""
<rect x="252" y="392" width="136" height="26" rx="13" fill="#07070b" stroke="{glow}" stroke-opacity="0.65" stroke-width="1.4"/>
<circle cx="270" cy="405" r="4.5" fill="{glow}"/>
<text x="328" y="409.5" font-family="'Noto Sans JP',sans-serif" font-size="12" font-weight="700" fill="#ececf2" text-anchor="middle" letter-spacing="1">{hz} 陣</text>"""
    else:
        bottom = "".join(
            f'<rect x="{250 + i * 38} " y="394" width="26" height="26" rx="7" fill="#ffffff" opacity="{o}"/>'
            for i, o in enumerate((0.16, 0.24, 0.18, 0.22)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480" role="img" aria-label="{label}">
{_defs(gid, glow)}
<rect x="40" y="30" width="560" height="420" rx="30" fill="{body_hex}"/>
<rect x="40" y="30" width="560" height="420" rx="30" fill="url(#metal{gid})"/>
<rect x="40.8" y="30.8" width="558.4" height="418.4" rx="29.2" fill="none" stroke="{glow}" stroke-opacity="0.5" stroke-width="1.6"/>
<rect x="54" y="44" width="532" height="392" rx="20" fill="url(#scr{gid})"/>
<ellipse cx="320" cy="195" rx="190" ry="115" fill="url(#flare{gid})"/>
<circle cx="320" cy="58" r="4.5" fill="#050508" stroke="#33333f" stroke-width="1.5"/>
<text x="76" y="72" font-family="'Noto Sans JP',sans-serif" font-size="13" font-weight="700" fill="#e6e6ee">12:34</text>
<rect x="536" y="59" width="19" height="9.5" rx="3.5" fill="none" stroke="#c9c9d6" stroke-width="1.4"/>
<rect x="538" y="61" width="11" height="5.5" rx="1.5" fill="{glow}"/>
<path d="M320 122 c-8 34 -42 48 -42 84 a42 42 0 0 0 84 0 c0 -36 -34 -50 -42 -84z" fill="none" stroke="{glow}" stroke-width="4.5" stroke-linejoin="round"/>
<circle cx="320" cy="212" r="10" fill="{glow}"/>
<text x="320" y="288" font-family="'Noto Sans JP',sans-serif" font-size="24" font-weight="800" fill="#f4f4f8" text-anchor="middle" letter-spacing="2">{label}</text>
<text x="320" y="312" font-family="'Noto Sans JP',sans-serif" font-size="12" fill="#9c9cb0" text-anchor="middle" letter-spacing="4">{kana}</text>
{bottom}
<path d="M70 44 L360 44 L150 436 L54 436 L54 300 Z" fill="#ffffff" opacity="0.035"/>
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


def svg_art(kind, glow="#e8442e"):
    """feature-split用の抽象アートパネル。"""
    g = glow
    common = f"""<defs>
<radialGradient id="ag" cx="0.5" cy="0.4" r="0.8">
  <stop offset="0" stop-color="{g}" stop-opacity="0.75"/>
  <stop offset="0.55" stop-color="{g}" stop-opacity="0.18"/>
  <stop offset="1" stop-color="{g}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="al" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{g}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{g}"/>
  <stop offset="1" stop-color="{g}" stop-opacity="0"/>
</linearGradient>
</defs>
<rect width="480" height="360" fill="#0b0b10"/>
<ellipse cx="240" cy="170" rx="220" ry="140" fill="url(#ag)"/>"""
    body = ""
    if kind == "chip" or kind == "npu":
        traces = "".join(
            f'<path d="M240 180 L{x} {y}" stroke="{g}" stroke-opacity="0.5" stroke-width="1.6"/><circle cx="{x}" cy="{y}" r="4" fill="{g}" opacity="0.8"/>'
            for x, y in [(80, 70), (60, 180), (90, 290), (400, 70), (420, 180), (390, 290), (170, 40), (310, 40), (170, 320), (310, 320)])
        body = f"""{traces}
<rect x="175" y="115" width="130" height="130" rx="14" fill="#10101a" stroke="{g}" stroke-width="2"/>
<rect x="197" y="137" width="86" height="86" rx="8" fill="#07070b" stroke="{g}" stroke-opacity="0.6"/>
<path d="M240 152 c-6 24 -30 34 -30 59 a30 30 0 0 0 60 0 c0 -25 -24 -35 -30 -59z" fill="none" stroke="{g}" stroke-width="3.5"/>"""
        if kind == "npu":
            body += "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="none" stroke="{g}" stroke-width="2" opacity="0.85"/>'
                            for x, y in [(120, 110), (120, 250), (360, 110), (360, 250)])
    elif kind == "gpu":
        rows = "".join(
            f'<rect x="{150 + c * 34}" y="{112 + r * 34}" width="26" height="26" rx="4" fill="{g}" opacity="{0.25 + ((r * 5 + c * 3) % 10) * 0.06:.2f}"/>'
            for r in range(4) for c in range(6))
        body = f"""<rect x="138" y="100" width="216" height="160" rx="14" fill="#10101a" stroke="{g}" stroke-width="2"/>{rows}
<path d="M60 300 L420 300" stroke="url(#al)" stroke-width="2"/>"""
    elif kind == "memory":
        body = "".join(
            f'<rect x="{96 + i * 60}" y="120" width="44" height="120" rx="6" fill="#10101a" stroke="{g}" stroke-opacity="{0.9 - i * 0.12}" stroke-width="2"/>'
            f'<rect x="{106 + i * 60}" y="136" width="24" height="60" rx="3" fill="{g}" opacity="{0.6 - i * 0.08}"/>'
            f'<rect x="{104 + i * 60}" y="244" width="28" height="6" rx="2" fill="#3d3d4e"/>'
            for i in range(5))
    elif kind == "storage":
        body = f"""<rect x="120" y="120" width="240" height="120" rx="12" fill="#10101a" stroke="{g}" stroke-width="2"/>
<rect x="140" y="140" width="80" height="80" rx="8" fill="{g}" opacity="0.5"/>
<rect x="238" y="140" width="38" height="80" rx="6" fill="{g}" opacity="0.3"/>
<rect x="288" y="140" width="38" height="80" rx="6" fill="{g}" opacity="0.3"/>
{"".join(f'<path d="M60 {150 + i * 24} L110 {150 + i * 24}" stroke="{g}" stroke-opacity="{0.7 - i * 0.15}" stroke-width="3" stroke-linecap="round"/>' for i in range(4))}
{"".join(f'<path d="M370 {150 + i * 24} L430 {150 + i * 24}" stroke="{g}" stroke-opacity="{0.7 - i * 0.15}" stroke-width="3" stroke-linecap="round"/>' for i in range(4))}"""
    elif kind == "cooling":
        layers = "".join(
            f'<rect x="{120 + i * 6}" y="{96 + i * 26}" width="{240 - i * 12}" height="14" rx="7" fill="{g}" opacity="{0.85 - i * 0.11}"/>'
            for i in range(7))
        body = f"""{layers}<path d="M150 310 q30 -18 60 0 t60 0 t60 0" fill="none" stroke="{g}" stroke-width="2.5" opacity="0.7"/>"""
    elif kind == "fan":
        import math
        blades = ""
        for i in range(9):
            a = i * 40
            blades += f'<path d="M240 180 q34 -36 78 -22" fill="none" stroke="{g}" stroke-width="9" stroke-linecap="round" opacity="0.85" transform="rotate({a} 240 180)"/>'
        body = f"""<circle cx="240" cy="180" r="112" fill="#10101a" stroke="{g}" stroke-opacity="0.5" stroke-width="2"/>{blades}
<circle cx="240" cy="180" r="26" fill="#07070b" stroke="{g}" stroke-width="2.5"/>"""
    elif kind == "liquid":
        body = f"""<rect x="110" y="96" width="260" height="168" rx="18" fill="#10101a" stroke="{g}" stroke-opacity="0.6" stroke-width="2"/>
<path d="M140 180 q50 -60 100 0 t100 0" fill="none" stroke="{g}" stroke-width="6" stroke-linecap="round"/>
<path d="M140 180 q50 60 100 0 t100 0" fill="none" stroke="{g}" stroke-width="6" stroke-linecap="round" opacity="0.45"/>
<circle cx="240" cy="180" r="18" fill="#07070b" stroke="{g}" stroke-width="3"/>
<circle cx="240" cy="180" r="7" fill="{g}"/>"""
    elif kind == "display":
        body = f"""<rect x="110" y="80" width="260" height="176" rx="14" fill="#07070b" stroke="{g}" stroke-width="2"/>
<rect x="122" y="92" width="236" height="152" rx="8" fill="url(#ag)"/>
<path d="M240 116 c-7 28 -35 40 -35 69 a35 35 0 0 0 70 0 c0 -29 -28 -41 -35 -69z" fill="none" stroke="{g}" stroke-width="3.5"/>
<text x="240" y="300" font-family="sans-serif" font-size="15" fill="#9c9cb0" text-anchor="middle" letter-spacing="6">175Hz</text>"""
    elif kind == "camera":
        body = f"""<circle cx="240" cy="176" r="104" fill="#10101a" stroke="{g}" stroke-width="2.5"/>
<circle cx="240" cy="176" r="76" fill="#07070b" stroke="{g}" stroke-opacity="0.7" stroke-width="2"/>
<circle cx="240" cy="176" r="46" fill="url(#ag)"/>
<circle cx="240" cy="176" r="20" fill="#07070b"/>
<circle cx="214" cy="150" r="10" fill="#ffffff" opacity="0.35"/>"""
    elif kind == "battery":
        body = f"""<rect x="140" y="110" width="180" height="140" rx="18" fill="#10101a" stroke="{g}" stroke-width="2.5"/>
<rect x="320" y="152" width="18" height="56" rx="7" fill="{g}"/>
<path d="M244 128 l-42 66 h30 l-14 58 l52 -74 h-30 l22 -50z" fill="{g}"/>"""
    elif kind == "os":
        tiles = "".join(
            f'<rect x="{136 + (i % 3) * 74}" y="{112 + (i // 3) * 74}" width="60" height="60" rx="12" fill="{g}" opacity="{0.24 + (i % 4) * 0.14}"/>'
            for i in range(6))
        body = f"""<rect x="120" y="84" width="240" height="192" rx="16" fill="#07070b" stroke="{g}" stroke-opacity="0.7" stroke-width="2"/>{tiles}
<rect x="200" y="290" width="80" height="5" rx="2.5" fill="#3d3d4e"/>"""
    elif kind == "cooler":
        blades = "".join(
            f'<path d="M240 176 q28 -30 64 -18" fill="none" stroke="{g}" stroke-width="8" stroke-linecap="round" opacity="0.9" transform="rotate({i * 51.4:.0f} 240 176)"/>'
            for i in range(7))
        body = f"""<rect x="150" y="76" width="180" height="220" rx="26" fill="#10101a" stroke="{g}" stroke-opacity="0.6" stroke-width="2"/>
<circle cx="240" cy="176" r="78" fill="#07070b" stroke="{g}" stroke-width="2.5"/>{blades}
<circle cx="240" cy="176" r="20" fill="#07070b" stroke="{g}" stroke-width="2.5"/>
<rect x="216" y="300" width="48" height="10" rx="5" fill="#3d3d4e"/>"""
    elif kind == "grip":
        body = f"""<rect x="96" y="130" width="288" height="96" rx="22" fill="#10101a" stroke="{g}" stroke-opacity="0.6" stroke-width="2"/>
<circle cx="150" cy="178" r="40" fill="#15151e" stroke="{g}" stroke-width="2.5"/>
<circle cx="150" cy="178" r="16" fill="{g}" opacity="0.85"/>
<circle cx="330" cy="178" r="40" fill="#15151e" stroke="{g}" stroke-width="2.5"/>
{"".join(f'<circle cx="{330 + dx}" cy="{178 + dy}" r="7" fill="{g}" opacity="0.85"/>' for dx, dy in [(0, -18), (18, 0), (0, 18), (-18, 0)])}
<rect x="210" y="156" width="60" height="10" rx="5" fill="{g}" opacity="0.4"/>
<rect x="122" y="108" width="56, 14" height="14" rx="7" fill="{g}" opacity="0.6"/>
<rect x="122" y="108" width="56" height="14" rx="7" fill="{g}" opacity="0.6"/>
<rect x="302" y="108" width="56" height="14" rx="7" fill="{g}" opacity="0.6"/>"""
    elif kind == "buds":
        body = f"""<circle cx="185" cy="165" r="52" fill="#10101a" stroke="{g}" stroke-width="2.5"/>
<rect x="172" y="200" width="26" height="70" rx="13" fill="#10101a" stroke="{g}" stroke-opacity="0.6" stroke-width="2"/>
<circle cx="185" cy="165" r="20" fill="{g}" opacity="0.75"/>
<circle cx="295" cy="165" r="52" fill="#10101a" stroke="{g}" stroke-width="2.5"/>
<rect x="282" y="200" width="26" height="70" rx="13" fill="#10101a" stroke="{g}" stroke-opacity="0.6" stroke-width="2"/>
<circle cx="295" cy="165" r="20" fill="{g}" opacity="0.75"/>
<path d="M120 110 q-18 18 0 36 M105 96 q-30 32 0 64" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
<path d="M360 110 q18 18 0 36 M375 96 q30 32 0 64" fill="none" stroke="{g}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>"""
    elif kind == "charger":
        body = f"""<rect x="160" y="96" width="160" height="160" rx="30" fill="#10101a" stroke="{g}" stroke-opacity="0.7" stroke-width="2.5"/>
<path d="M248 120 l-44 64 h30 l-16 56 l54 -72 h-30 l22 -48z" fill="{g}"/>
<rect x="196" y="256" width="14" height="30" rx="4" fill="#3d3d4e"/>
<rect x="268" y="256" width="14" height="30" rx="4" fill="#3d3d4e"/>
<text x="240" y="320" font-family="sans-serif" font-size="17" font-weight="700" fill="#9c9cb0" text-anchor="middle" letter-spacing="3">120W GaN</text>"""
    elif kind == "case":
        body = f"""<rect x="150" y="60" width="180" height="252" rx="30" fill="#10101a" stroke="{g}" stroke-width="2.5"/>
<rect x="166" y="76" width="148" height="220" rx="20" fill="#07070b"/>
<circle cx="196" cy="110" r="17" fill="none" stroke="{g}" stroke-width="2.5"/>
<circle cx="240" cy="110" r="17" fill="none" stroke="{g}" stroke-width="2.5"/>
{"".join(f'<path d="M186 {160 + i * 22} L294 {160 + i * 22}" stroke="{g}" stroke-opacity="0.35" stroke-width="4" stroke-linecap="round"/>' for i in range(5))}
<path d="M240 282 c-5 18 -22 26 -22 44 a22 22 0 0 0 44 0 c0 -18 -17 -26 -22 -44z" fill="none" stroke="{g}" stroke-width="2.5" transform="translate(0,-40)"/>"""
    elif kind == "dock":
        body = f"""<path d="M140 270 L340 270 L316 150 L164 150 Z" fill="#10101a" stroke="{g}" stroke-opacity="0.7" stroke-width="2.5"/>
<rect x="190" y="70" width="100" height="170" rx="14" fill="#07070b" stroke="{g}" stroke-width="2"/>
<rect x="198" y="78" width="84" height="154" rx="9" fill="url(#ag)"/>
<rect x="160" y="270" width="160" height="16" rx="8" fill="#15151e" stroke="{g}" stroke-opacity="0.4"/>
{"".join(f'<circle cx="{210 + i * 30}" cy="296" r="4" fill="{g}" opacity="0.7"/>' for i in range(3))}"""
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
}
