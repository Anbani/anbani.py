"""Alphabet screen: a grid of the letters in the chosen Georgian script with a
detail card (GlyphTip analog) for the focused letter.

KEEP IN SYNC WITH anbani.js/src/tui/screens/alphabet.mjs
"""

from anbani.core import converter as _conv
from .. import ui

id = "alphabet"
label = "Alphabet"
title = "ანბანი"
can_input = False

A = _conv.data["alphabets"]
SCRIPTS = ["mkhedruli", "mtavruli", "asomtavruli", "nuskhuri"]
CORE = 33
ARCHAIC = 38
COLS = 11


def init():
    return {"script": "mkhedruli", "archaic": False, "cursor": 0}


def _count(s):
    return ARCHAIC if s["archaic"] else CORE


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def update(s, event, ctx=None):
    name = event["char"] if event["type"] == "char" else event.get("name")
    n = _count(s)
    s2 = dict(s)
    if name in ("h", "left"):
        s2["cursor"] = _clamp(s["cursor"] - 1, 0, n - 1)
    elif name in ("l", "right"):
        s2["cursor"] = _clamp(s["cursor"] + 1, 0, n - 1)
    elif name in ("k", "up"):
        s2["cursor"] = _clamp(s["cursor"] - COLS, 0, n - 1)
    elif name in ("j", "down"):
        s2["cursor"] = _clamp(s["cursor"] + COLS, 0, n - 1)
    elif name == "g":
        s2["cursor"] = 0
    elif name == "G":
        s2["cursor"] = n - 1
    elif name == "c":
        s2["script"] = SCRIPTS[(SCRIPTS.index(s["script"]) + 1) % len(SCRIPTS)]
    elif name == "a":
        archaic = not s["archaic"]
        nn = ARCHAIC if archaic else CORE
        s2["archaic"] = archaic
        s2["cursor"] = _clamp(s["cursor"], 0, nn - 1)
    elif name == "enter":
        glyph = A[s["script"]][s["cursor"]] or ""
        if glyph:
            s2["_copy"] = glyph
    else:
        return s
    return s2


def get_copy_text(s):
    return A[s["script"]][s["cursor"]] or None


def status(s):
    return {"hint": "{} · {}/{}".format(s["script"], s["cursor"] + 1, _count(s))}


def footer(s=None):
    return "hjkl move  c script  a archaic  enter copy"


def _grid_box(s, w, rows, style):
    n = _count(s)
    inner = w - 4
    cell_w = 4 if inner >= COLS * 4 else 3  # narrow panels drop the inter-cell gap
    grid_rows = (n + COLS - 1) // COLS
    cells = ["" for _ in range(grid_rows)]
    off = not style.on
    for i in range(n):
        r = i // COLS
        g = A[s["script"]][i] or "—"
        if i == s["cursor"]:
            cell = "▐" + g + "▌" if off else style.inverse() + " " + g + " " + style.reset()
        else:
            cell = " " + g + " "
        cells[r] += cell + " " * (cell_w - 3)
    lines = [ui.box_top(w, s["script"], "archaic" if s["archaic"] else "core")]
    lines.append(ui.box_line_rich("", w))
    for row in cells:
        lines.append(ui.box_line_rich(row, w))
    lines.append(ui.box_bottom(w))
    return ui.frame(lines, w, rows)


def _detail_box(s, w, rows, style):
    i = s["cursor"]

    def g(key):
        return A[key][i] or "—"

    rows_arr = [
        A["names"][i] or "—",
        "",
        "mkhedruli   " + g("mkhedruli"),
        "mtavruli    " + g("mtavruli"),
        "asomtavruli " + g("asomtavruli"),
        "nuskhuri    " + g("nuskhuri"),
        "",
        "ipa         " + g("phonetic"),
        "braille     " + g("braille"),
        "numeric     " + g("numeric"),
        "qwerty      " + g("qwerty"),
    ]
    lines = [ui.box_top(w, "letter")]
    for r in rows_arr:
        lines.append(ui.box_line(r, w))
    lines.append(ui.box_bottom(w))
    return ui.frame(lines, w, rows)


def render(s, box, style):
    C = box["cols"]
    R = box["rows"]
    detail_w = min(28, max(20, int(C * 0.34)))
    left_w = C - detail_w - 1
    left = _grid_box(s, left_w, R, style)
    right = _detail_box(s, detail_w, R, style)
    out = [left[i] + " " + right[i] for i in range(R)]
    return ui.frame(out, C, R)
