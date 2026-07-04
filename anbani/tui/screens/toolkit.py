"""Toolkit screen: letter-frequency bar chart + Friedman index of coincidence.
count()/frequency()/friedman() upper-case their input, so Georgian keys come
back as MTAVRULI -- we display them as returned.

KEEP IN SYNC WITH anbani.js/src/tui/screens/toolkit.mjs
"""

import re

from anbani import toolkit
from .. import ui

id = "toolkit"
label = "Toolkit"
title = "ხელსაწყოები"
can_input = True

_GEO_RE = re.compile("[Ⴀ-ჿᲐ-Ჿⴀ-⴯]")
_WS_RE = re.compile(r"\s+")


def _recompute(s):
    text = s["input"]["text"]
    stats = None
    if text:
        try:
            counts = toolkit.count(text)
            friedman = toolkit.friedman(text)
            entries = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            total = 0
            geo = 0
            for k, n in entries:
                total += n
                if _GEO_RE.search(k):
                    geo += n
            words = len(_WS_RE.split(text.strip())) if text.strip() else 0
            stats = {
                "entries": entries,
                "friedman": friedman,
                "total": total,
                "geo": geo,
                "other": total - geo,
                "unique": len(entries),
                "words": words,
            }
        except Exception:
            stats = None
    s2 = dict(s)
    s2["stats"] = stats
    return s2


def init():
    return _recompute({"input": ui.make_input(""), "focus": "normal", "scroll": 0, "stats": None})


def update(s, event, ctx=None):
    if s["focus"] == "input":
        s2 = dict(s)
        s2["input"] = ui.input_handle(s["input"], event)
        return _recompute(s2)
    name = event["char"] if event["type"] == "char" else event.get("name")
    s2 = dict(s)
    if name in ("i", "enter"):
        s2["focus"] = "input"
    elif name == "x":
        s2["input"] = ui.make_input("")
        s2["scroll"] = 0
        return _recompute(s2)
    elif name == "down":
        s2["scroll"] = s["scroll"] + 1
    elif name == "up":
        s2["scroll"] = max(0, s["scroll"] - 1)
    else:
        return s
    return s2


def _report(s):
    if not s["stats"]:
        return None
    st = s["stats"]
    lines = ["{} {}".format(k, n) for k, n in st["entries"]]
    head = "friedman {:.4f}  total {}  unique {}".format(st["friedman"], st["total"], st["unique"])
    return head + "\n" + "\n".join(lines)


def get_copy_text(s):
    return _report(s)


def status(s):
    if not s["stats"]:
        return {"hint": "paste or type text to analyse"}
    return {"hint": "friedman {:.4f} · {} letters".format(s["stats"]["friedman"], s["stats"]["total"])}


def footer(s=None):
    return "i edit  x clear  ↑↓ scroll  y copy"


def _bars_box(s, w, rows, style):
    lines = [ui.box_top(w, "frequency")]
    if not s["stats"]:
        msg = "paste or type text to analyse"
        lines.append(ui.box_line(style.dim() + msg + style.reset() if style.on else msg, w))
    else:
        body_rows = rows - 2
        inner = w - 4
        key_w = 3
        num_w = 5
        bar_max = max(1, inner - key_w - 1 - num_w - 1)
        entries = s["stats"]["entries"]
        max_n = entries[0][1] if entries else 1
        start = max(0, min(s["scroll"], max(0, len(entries) - body_rows)))
        for i in range(start, len(entries)):
            k, n = entries[i]
            bar_len = max(1, round((n / max_n) * bar_max))
            line = ui.pad_end(k, key_w) + " " + ui.pad_end(str(n), num_w) + " " + "█" * bar_len
            lines.append(ui.box_line(line, w))
    lines.append(ui.box_bottom(w))
    return ui.frame(lines, w, rows)


def _stats_box(s, w, rows, style):
    lines = [ui.box_top(w, "stats")]
    if s["stats"]:
        st = s["stats"]
        interp = "~ georgian-like" if st["friedman"] >= 0.05 else "~ uniform-ish"
        rows_arr = [
            "total     {}".format(st["total"]),
            "unique    {}".format(st["unique"]),
            "georgian  {}".format(st["geo"]),
            "other     {}".format(st["other"]),
            "words     {}".format(st["words"]),
            "",
            "friedman  {:.4f}".format(st["friedman"]),
            interp,
        ]
        for r in rows_arr:
            lines.append(ui.box_line(r, w))
    else:
        lines.append(ui.box_line("", w))
    lines.append(ui.box_bottom(w))
    return ui.frame(lines, w, rows)


def render(s, box, style):
    C = box["cols"]
    R = box["rows"]
    lines = []
    lines.append(ui.box_top(C, "text", "toolkit"))
    lines.append(ui.box_line_rich(ui.input_render(s["input"], C - 4, style, s["focus"] == "input"), C))
    lines.append(ui.box_bottom(C))
    lines.append(ui.blank(C))

    panel_rows = R - len(lines)
    right_w = min(30, max(22, int(C * 0.36)))
    left_w = C - right_w - 1
    left = _bars_box(s, left_w, panel_rows, style)
    right = _stats_box(s, right_w, panel_rows, style)
    for i in range(panel_rows):
        lines.append(left[i] + " " + right[i])

    return ui.frame(lines, C, R)
