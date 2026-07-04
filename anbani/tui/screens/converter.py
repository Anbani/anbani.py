"""Converter screen: live script transliteration. Auto mode uses interpret()
(source auto-detected); manual mode uses convert() with explicit from/to.

KEEP IN SYNC WITH anbani.js/src/tui/screens/converter.mjs
"""

from anbani.core import converter as _conv
from .. import ui

id = "converter"
label = "Converter"
title = "გადაყვანა"
can_input = True

SOURCES = ["mkhedruli", "mtavruli", "asomtavruli", "nuskhuri", "qwerty", "braille"]
BICAMERAL = ["khutsuri", "shanidziseuli", "tfileliseuli", "sasataure"]
TO_TARGETS = [k for k in _conv.data["alphabets"].keys() if k != "names"] + BICAMERAL


def _recompute(s):
    text = s["input"]["text"]
    detected = None
    output = ""
    error = None
    if text:
        try:
            detected = _conv.classify_text(text)
        except Exception:
            detected = None
        try:
            if s["mode"] == "auto":
                output = _conv.interpret(text, s["to"])
            else:
                output = _conv.convert(text, s["from"], s["to"])
        except Exception as e:
            error = str(e)
            output = ""
    s = dict(s)
    s["detected"] = detected
    s["output"] = output
    s["error"] = error
    return s


def init():
    return _recompute({
        "input": ui.make_input(""),
        "mode": "auto",
        "from": "mkhedruli",
        "to": "mtavruli",
        "detected": None,
        "output": "",
        "error": None,
        "focus": "normal",
    })


def _cycle(lst, cur, direction):
    i = lst.index(cur)
    n = len(lst)
    return lst[(i + direction) % n]


def update(s, event, ctx):
    if s["focus"] == "input":
        inp = ui.input_handle(s["input"], event)
        s2 = dict(s)
        s2["input"] = inp
        return _recompute(s2)
    name = event["char"] if event["type"] == "char" else event.get("name")
    if name in ("i", "enter"):
        s2 = dict(s)
        s2["focus"] = "input"
        return s2
    if name == "m":
        s2 = dict(s)
        s2["mode"] = "manual" if s["mode"] == "auto" else "auto"
        return _recompute(s2)
    if name in ("f", "F"):
        if s["mode"] != "manual":
            s2 = dict(s)
            s2["_toast"] = "switch to manual (m) to pick a source"
            return s2
        s2 = dict(s)
        s2["from"] = _cycle(SOURCES, s["from"], 1 if name == "f" else -1)
        return _recompute(s2)
    if name in ("o", "O"):
        s2 = dict(s)
        s2["to"] = _cycle(TO_TARGETS, s["to"], 1 if name == "o" else -1)
        return _recompute(s2)
    if name == "s":
        if s["mode"] != "manual":
            s2 = dict(s)
            s2["_toast"] = "swap works in manual mode (m)"
            return s2
        if s["to"] not in SOURCES:
            s2 = dict(s)
            s2["_toast"] = "cannot swap: '{}' is not a source script".format(s["to"])
            return s2
        s2 = dict(s)
        s2["from"], s2["to"] = s["to"], s["from"]
        return _recompute(s2)
    if name == "x":
        s2 = dict(s)
        s2["input"] = ui.make_input("")
        return _recompute(s2)
    return s


def get_copy_text(s):
    return s["output"] or None


def status(s):
    if s["error"]:
        return {"error": "error: {}".format(s["error"])}
    if s["mode"] == "auto":
        return {"hint": "auto · detected: {}".format(s["detected"] or "—")}
    return {"hint": "{} → {}".format(s["from"], s["to"])}


def footer(s=None):
    return "i edit  m mode  f/o pick  s swap  x clear  y copy"


def _chip_row(prefix, items, current, style, dim):
    parts = [ui.pill(it, it == current, style) for it in items]
    s = prefix + "".join(parts)
    if dim and style.on:
        s = style.dim() + s + style.reset()
    return s


def _to_row(current, style):
    # Compact "to" selector: current target pill + position (21 targets would
    # overflow a full row). o/O cycles through them.
    idx = TO_TARGETS.index(current)
    return "to:    " + ui.pill(current, True, style) + "   " + "{}/{}  ‹o/O›".format(idx + 1, len(TO_TARGETS))


def render(s, box, style):
    C = box["cols"]
    R = box["rows"]
    lines = []
    badge = "auto" if s["mode"] == "auto" else "{}→{}".format(s["from"], s["to"])
    lines.append(ui.box_top(C, "input", badge))
    lines.append(ui.box_line_rich(ui.input_render(s["input"], C - 4, style, s["focus"] == "input"), C))
    lines.append(ui.box_bottom(C))
    lines.append(ui.blank(C))
    lines.append(_chip_row("mode:  ", ["auto", "manual"], s["mode"], style, False))
    lines.append(_chip_row("from:  ", SOURCES, s["from"], style, s["mode"] == "auto"))
    lines.append(_to_row(s["to"], style))
    lines.append(ui.blank(C))

    header_rows = len(lines)
    out_top = ui.box_top(C, "output")
    out_bottom = ui.box_bottom(C)
    body_rows = max(1, R - header_rows - 2)
    body = []
    if not s["input"]["text"]:
        body.append(style.dim() + "type to convert…" + style.reset() if style.on else "type to convert…")
    else:
        for l in ui.wrap_text(s["output"], C - 4):
            body.append(l)
    while len(body) < body_rows:
        body.append("")
    lines.append(out_top)
    for i in range(body_rows):
        lines.append(ui.box_line(body[i] if i < len(body) else "", C))
    lines.append(out_bottom)

    return ui.frame(lines, C, R)
