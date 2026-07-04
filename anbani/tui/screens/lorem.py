"""Lorem screen: generate fake Georgian text (sentences / paragraphs / names).
Generation runs on demand (g) via the injected lorem module.

KEEP IN SYNC WITH anbani.js/src/tui/screens/lorem.mjs
"""

from .. import ui

id = "lorem"
label = "Lorem"
title = "ლორემი"
can_input = False

KINDS = ["sentences", "paragraphs", "names"]


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def init():
    return {"kind": "sentences", "words": 8, "paragraphs": 2, "names": 5, "output": "", "scroll": 0}


def _generate(s, ctx):
    L = (ctx or {}).get("lorem")
    if L is None:
        from anbani import lorem as L
    if s["kind"] == "sentences":
        out = L.sentences(s["words"])
    elif s["kind"] == "paragraphs":
        out = L.paragraphs(s["words"], s["paragraphs"])
    else:
        out = "\n".join(L.names(s["names"]))
    s2 = dict(s)
    s2["output"] = out
    s2["scroll"] = 0
    return s2


def update(s, event, ctx=None):
    name = event["char"] if event["type"] == "char" else event.get("name")
    s2 = dict(s)
    if name == "k":
        s2["kind"] = KINDS[(KINDS.index(s["kind"]) + 1) % len(KINDS)]
    elif name in ("+", "="):
        if s["kind"] == "names":
            s2["names"] = _clamp(s["names"] + 1, 1, 20)
        else:
            s2["words"] = _clamp(s["words"] + 1, 1, 200)
    elif name in ("-", "_"):
        if s["kind"] == "names":
            s2["names"] = _clamp(s["names"] - 1, 1, 20)
        else:
            s2["words"] = _clamp(s["words"] - 1, 1, 200)
    elif name == "p":
        s2["paragraphs"] = _clamp(s["paragraphs"] + 1, 1, 10)
    elif name == "P":
        s2["paragraphs"] = _clamp(s["paragraphs"] - 1, 1, 10)
    elif name == "g":
        return _generate(s, ctx)
    elif name == "down":
        s2["scroll"] = s["scroll"] + 1
    elif name == "up":
        s2["scroll"] = max(0, s["scroll"] - 1)
    else:
        return s
    return s2


def get_copy_text(s):
    return s["output"] or None


def status(s):
    if s["kind"] == "names":
        amt = "names: {}".format(s["names"])
    else:
        amt = "words: {}".format(s["words"])
        if s["kind"] == "paragraphs":
            amt += "  paragraphs: {}".format(s["paragraphs"])
    return {"hint": "kind: {}  {}".format(s["kind"], amt)}


def footer(s=None):
    return "k kind  +/- amount  p paras  g gen  ↑↓ scroll  y copy"


def render(s, box, style):
    C = box["cols"]
    R = box["rows"]
    lines = []
    kind_pills = "".join(ui.pill(k, k == s["kind"], style) for k in KINDS)
    lines.append("kind:   " + kind_pills)
    if s["kind"] == "names":
        amt = "count: {}".format(s["names"])
    else:
        amt = "words: {}".format(s["words"])
        if s["kind"] == "paragraphs":
            amt += "   paragraphs: {}".format(s["paragraphs"])
    lines.append(ui.pad_end(amt, C))
    lines.append(ui.blank(C))

    header = len(lines)
    body_rows = max(1, R - header - 2)
    body = []
    if not s["output"]:
        body.append(style.dim() + "press g to generate" + style.reset() if style.on else "press g to generate")
    else:
        wrapped = ui.wrap_text(s["output"], C - 4)
        start = _clamp(s["scroll"], 0, max(0, len(wrapped) - body_rows))
        for i in range(start, len(wrapped)):
            body.append(wrapped[i])
    while len(body) < body_rows:
        body.append("")
    lines.append(ui.box_top(C, "output"))
    for i in range(body_rows):
        lines.append(ui.box_line(body[i] if i < len(body) else "", C))
    lines.append(ui.box_bottom(C))

    return ui.frame(lines, C, R)
