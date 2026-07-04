"""TUI widget/layout primitives: display-width-aware text, square-cornered
panels (anbaniCard), hero band, pills, tabs, callout, and a single-line text
input. Layout math runs on PLAIN text; colour is applied to already-fitted
cells so an SGR sequence is never truncated mid-code.

KEEP IN SYNC WITH anbani.js/src/tui/ui.mjs
"""

from .style import strip_sgr

# ---- display width ---------------------------------------------------------

_ZERO_RANGES = (
    (0x0300, 0x036F), (0x1AB0, 0x1AFF), (0x1DC0, 0x1DFF),
    (0x20D0, 0x20FF), (0xFE00, 0xFE0F), (0xFE20, 0xFE2F), (0x200B, 0x200D),
)
_WIDE_RANGES = (
    (0x1100, 0x115F), (0x2E80, 0x303E), (0x3041, 0x33FF), (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF), (0xA000, 0xA4CF), (0xAC00, 0xD7A3), (0xF900, 0xFAFF),
    (0xFE30, 0xFE4F), (0xFF00, 0xFF60), (0xFFE0, 0xFFE6),
    (0x1F300, 0x1F64F), (0x1F900, 0x1F9FF), (0x20000, 0x2FFFD),
)


def _in_ranges(cp, ranges):
    for lo, hi in ranges:
        if lo <= cp <= hi:
            return True
    return False


def char_width(ch):
    cp = ord(ch)
    if _in_ranges(cp, _ZERO_RANGES):
        return 0
    if _in_ranges(cp, _WIDE_RANGES):
        return 2
    return 1


def width(s):
    plain = strip_sgr(s)
    return sum(char_width(ch) for ch in plain)


# ---- pad / truncate / fit (PLAIN text) ------------------------------------

def pad_end(s, w):
    cur = width(s)
    return s if cur >= w else s + " " * (w - cur)


def truncate(s, w, ellipsis="…"):
    if width(s) <= w:
        return s
    ell_w = width(ellipsis)
    out = []
    acc = 0
    for ch in s:
        cw = char_width(ch)
        if acc + cw > w - ell_w:
            break
        out.append(ch)
        acc += cw
    return "".join(out) + ellipsis


def fit(s, w):
    return pad_end(truncate(s, w), w)


def center(s, w):
    cur = width(s)
    if cur >= w:
        return truncate(s, w)
    left = (w - cur) // 2
    return " " * left + s + " " * (w - cur - left)


def pad_row(s, w):
    cur = width(s)
    return s if cur >= w else s + " " * (w - cur)


# ---- panels (square corners only) -----------------------------------------

def box_top(w, title=None, right=None):
    open_ = "┌─ {} ".format(title) if title else "┌"
    close = " {} ─┐".format(right) if right else "─┐"
    mid = w - width(open_) - width(close)
    if mid < 0:
        open_ = "┌"
        close = "─┐"
        mid = w - width(open_) - width(close)
    return open_ + "─" * max(0, mid) + close


def box_bottom(w):
    return "└" + "─" * max(0, w - 2) + "┘"


def box_line(content, w):
    return "│ " + fit(content, w - 4) + " │"


def box_line_rich(content, w):
    return "│ " + pad_row(content, w - 4) + " │"


# ---- hero / pill / tabs / callout -----------------------------------------

def hero(title, w, style, right=""):
    bg = style.bg("heroBg")
    fgw = style.fg("textOnHero")
    rst = style.reset()
    bold = style.bold()
    inner = w
    blank = bg + " " * inner + rst
    if right:
        gap = inner - 2 - width(title) - width(right) - 2
        mid = " " + title + " " * max(1, gap) + right + " "
        mid = fit(mid, inner)
    else:
        mid = fit(" " + title, inner)
    mid_line = bg + bold + fgw + mid + rst
    return [blank, mid_line, blank]


def pill(label, active, style):
    if not style.on:
        return "·{}·".format(label) if active else " {} ".format(label)
    if active:
        return style.bg("accent") + style.fg("textOnHero") + " {} ".format(label) + style.reset()
    return style.fg("textMinor") + " {} ".format(label) + style.reset()


def tabs(items, active_idx, w, style):
    off = not style.on
    parts = []
    for i, it in enumerate(items):
        if i == active_idx:
            if off:
                parts.append("[{}]".format(it))
            else:
                parts.append(style.bold() + style.underline() + style.fg("accent") + it + style.reset())
        else:
            if off:
                parts.append(" {} ".format(it))
            else:
                parts.append(style.fg("textMinor") + it + style.reset())
    return pad_row("  " + "   ".join(parts), w)


def callout(lines, w, style):
    bg = style.bg("heroBg")
    fgw = style.fg("textOnHero")
    rst = style.reset()
    out = [bg + " " * w + rst]
    for l in lines:
        out.append(bg + fgw + fit(" " + l, w) + rst)
    out.append(bg + " " * w + rst)
    return out


# ---- single-line text input ------------------------------------------------

def make_input(text=""):
    return {"text": text, "cursor": len(text), "scroll": 0}


def input_handle(state, event):
    arr = list(state["text"])
    cursor = state["cursor"]
    et = event.get("type")
    if et == "char":
        arr.insert(cursor, event["char"])
        cursor += 1
    elif et == "paste":
        flat = event["text"].replace("\n", " ")
        chars = list(flat)
        arr[cursor:cursor] = chars
        cursor += len(chars)
    elif et == "key":
        name = event.get("name")
        if name == "backspace":
            if cursor > 0:
                del arr[cursor - 1]
                cursor -= 1
        elif name == "delete":
            if cursor < len(arr):
                del arr[cursor]
        elif name == "left":
            if cursor > 0:
                cursor -= 1
        elif name == "right":
            if cursor < len(arr):
                cursor += 1
        elif name == "home":
            cursor = 0
        elif name == "end":
            cursor = len(arr)
        elif name == "ctrl+u":
            arr = []
            cursor = 0
        elif name == "ctrl+k":
            del arr[cursor:]
        elif name == "ctrl+w":
            c = cursor
            while c > 0 and arr[c - 1] == " ":
                c -= 1
            while c > 0 and arr[c - 1] != " ":
                c -= 1
            del arr[c:cursor]
            cursor = c
    return {"text": "".join(arr), "cursor": cursor, "scroll": state.get("scroll", 0)}


def input_render(state, w, style, focused):
    arr = list(state["text"])
    scroll = state.get("scroll", 0) or 0
    if state["cursor"] < scroll + 1:
        scroll = max(0, state["cursor"] - 1)
    if state["cursor"] > scroll + w - 2:
        scroll = state["cursor"] - (w - 2)
    if scroll < 0:
        scroll = 0

    off = not style.on
    out = []
    col = 0
    i = scroll
    while i < len(arr) and col < w:
        ch = arr[i]
        cw = char_width(ch) or 1
        if col + cw > w:
            break
        if i == state["cursor"] and focused and not off:
            out.append(style.inverse() + ch + style.reset())
        else:
            out.append(ch)
        col += cw
        i += 1
    if state["cursor"] >= len(arr) and focused and col < w:
        if not off:
            out.append(style.inverse() + " " + style.reset())
            col += 1
    if col < w:
        out.append(" " * (w - col))
    return "".join(out)


def frame(lines, cols, rows):
    """Normalise to EXACTLY rows lines, each exactly cols columns."""
    out = []
    for l in lines:
        wv = width(l)
        if wv < cols:
            out.append(l + " " * (cols - wv))
        elif wv > cols:
            out.append(truncate(l, cols))
        else:
            out.append(l)
    while len(out) < rows:
        out.append(" " * cols)
    return out[:rows]


def blank(cols):
    return " " * cols


def wrap_text(s, w):
    """Greedy word-wrap to width w. Splits on spaces; hard-breaks long tokens."""
    out = []
    for para in str(s).split("\n"):
        if para == "":
            out.append("")
            continue
        line = ""
        for word in para.split(" "):
            piece = word
            while width(piece) > w:
                take = ""
                for ch in piece:
                    if width(take) + char_width(ch) > w:
                        break
                    take += ch
                if line:
                    out.append(line)
                    line = ""
                out.append(take)
                piece = piece[len(take):]
            cand = (line + " " + piece) if line else piece
            if width(cand) > w:
                if line:
                    out.append(line)
                line = piece
            else:
                line = cand
        out.append(line)
    return out
