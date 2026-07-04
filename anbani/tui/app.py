"""App shell: chrome (hero / tabs / status / footer), the pure reducer that
routes events to the active screen, the help overlay, the min-size guard, and
the runtime event loop. init/update/render are pure and TTY-free for tests;
run() wires the real terminal.

KEEP IN SYNC WITH anbani.js/src/tui/app.mjs
"""

import os
import sys

from anbani.core import converter as _core
from . import ui
from .style import detect_caps, Style
from .term import Term, CUR_HIDE, EL, move_to
from .clipboard import osc52
from .screens import converter, alphabet, lorem as lorem_screen, nlp, toolkit

VERSION = "3.1.0"
SCREENS = [converter, alphabet, lorem_screen, nlp, toolkit]
BY_ID = {s.id: s for s in SCREENS}


def _mtavruli(title):
    try:
        return _core.convert(title, "mkhedruli", "mtavruli")
    except Exception:
        return title


def initial_state():
    screens = {s.id: s.init() for s in SCREENS}
    return {
        "tab": "converter",
        "help": False,
        "toast": None,
        "quit": False,
        "size": {"cols": 80, "rows": 24},
        "screens": screens,
    }


def _set_screen(state, id_, scr):
    screens = dict(state["screens"])
    screens[id_] = scr
    s = dict(state)
    s["screens"] = screens
    return s


def _switch_tab(state, id_, ctx):
    nxt = dict(state)
    nxt["tab"] = id_
    nxt["toast"] = None
    screen = BY_ID[id_]
    if hasattr(screen, "on_enter_tab"):
        nxt = _set_screen(nxt, id_, screen.on_enter_tab(state["screens"][id_], ctx))
    return nxt


def _apply_screen(state, screen, scr, event, ctx):
    ns = screen.update(scr, event, ctx)
    toast = None
    if ns and "_toast" in ns:
        toast = {"text": ns["_toast"]}
        ns = dict(ns)
        del ns["_toast"]
    if ns and "_copy" in ns:
        text = ns["_copy"]
        ns = dict(ns)
        del ns["_copy"]
        if ctx and ctx.get("copy"):
            ctx["copy"](text)
        toast = {"text": "copied to clipboard (OSC 52)"}
    s = dict(state)
    s["toast"] = toast
    return _set_screen(s, state["tab"], ns)


def update(state, event, ctx=None):
    ctx = ctx or {}
    if event["type"] == "resize":
        s = dict(state)
        s["size"] = {"cols": event["cols"], "rows": event["rows"]}
        return s
    if event["type"] == "nlp:loaded":
        return _set_screen(state, "nlp", nlp.on_loaded(state["screens"]["nlp"], ctx))
    if event["type"] == "key" and event.get("name") == "ctrl+c":
        s = dict(state)
        s["quit"] = True
        return s
    if state["help"]:
        if event["type"] in ("key", "char"):
            s = dict(state)
            s["help"] = False
            return s
        return state

    screen = BY_ID[state["tab"]]
    scr = state["screens"][state["tab"]]

    if getattr(screen, "can_input", False) and scr.get("focus") == "input":
        if event["type"] == "key" and event.get("name") == "escape":
            s2 = dict(scr)
            s2["focus"] = "normal"
            return _set_screen(state, state["tab"], s2)
        return _apply_screen(state, screen, scr, event, ctx)

    name = event["char"] if event["type"] == "char" else event.get("name")
    idx = next(i for i, s in enumerate(SCREENS) if s.id == state["tab"])
    if name and len(name) == 1 and "1" <= name <= "5":
        i = int(name) - 1
        if i < len(SCREENS):
            return _switch_tab(state, SCREENS[i].id, ctx)
    if name == "tab":
        return _switch_tab(state, SCREENS[(idx + 1) % len(SCREENS)].id, ctx)
    if name == "shift+tab":
        return _switch_tab(state, SCREENS[(idx - 1) % len(SCREENS)].id, ctx)
    if name == "?":
        s = dict(state)
        s["help"] = True
        return s
    if name == "q":
        s = dict(state)
        s["quit"] = True
        return s
    if name == "y":
        text = screen.get_copy_text(scr) if hasattr(screen, "get_copy_text") else None
        if text and ctx.get("copy"):
            ctx["copy"](text)
        s = dict(state)
        s["toast"] = {"text": "copied to clipboard (OSC 52)" if text else "nothing to copy"}
        return s
    return _apply_screen(state, screen, scr, event, ctx)


# ---- chrome / render -------------------------------------------------------

def _too_small(C, R):
    lines = []
    mid = R // 2 - 1
    for i in range(R):
        if i == mid:
            lines.append(ui.center("Terminal too small", C))
        elif i == mid + 1:
            lines.append(ui.center("need ≥ 60x16 (now {}x{})".format(C, R), C))
        else:
            lines.append(ui.blank(C))
    return ui.frame(lines, C, R)


def _status_line(state, screen, scr, C, style):
    st = screen.status(scr) if hasattr(screen, "status") else {}
    text = ""
    token = "textMinor"
    if st.get("error"):
        text = st["error"]
        token = "danger"
    elif state["toast"]:
        text = state["toast"]["text"]
        token = "warn"
    elif st.get("hint"):
        text = st["hint"]
        token = "textMinor"
    cell = ui.fit(" " + text, C)
    return style.fg(token) + cell + style.reset() if style.on else cell


def _footer_line(screen, scr, C, style):
    global_hints = "? help  ↹ tabs  q quit"
    screen_hints = screen.footer(scr) if hasattr(screen, "footer") else ""
    cell = ui.fit(" " + global_hints + "   " + screen_hints, C)
    return style.fg("textMinor") + cell + style.reset() if style.on else cell


def _help_lines(state, C, rows, style):
    screen = BY_ID[state["tab"]]
    body = [
        "Global",
        "  1–5             switch tabs",
        "  tab / shift+tab  cycle tabs",
        "  ?               toggle this help",
        "  i / enter       edit / select",
        "  y               copy output (OSC 52)",
        "  q   ctrl+c      quit",
        "",
        "Screen: {}".format(screen.label),
        "  " + (screen.footer(state["screens"][state["tab"]]) if hasattr(screen, "footer") else ""),
        "",
        "Tip: paste Georgian with your terminal's paste — works in insert mode.",
        "",
        "press any key to close",
    ]
    lines = [ui.box_top(C, "help")]
    for b in body:
        lines.append(ui.box_line(b, C))
    lines.append(ui.box_bottom(C))
    return ui.frame(lines, C, rows)


def render(state, size, style):
    C = size["cols"]
    R = size["rows"]
    if C < 60 or R < 16:
        return _too_small(C, R)
    screen = BY_ID[state["tab"]]
    scr = state["screens"][state["tab"]]
    hero = ui.hero(_mtavruli(screen.title), C, style, "anbani v{}".format(VERSION))
    labels = ["{} {}".format(i + 1, s.label) for i, s in enumerate(SCREENS)]
    active_idx = next(i for i, s in enumerate(SCREENS) if s.id == state["tab"])
    tabs_line = ui.tabs(labels, active_idx, C, style)
    content_rows = R - 6
    if state["help"]:
        content = _help_lines(state, C, content_rows, style)
    else:
        content = screen.render(scr, {"cols": C, "rows": content_rows}, style)
    all_lines = hero + [tabs_line] + list(content) + [_status_line(state, screen, scr, C, style)] + [_footer_line(screen, scr, C, style)]
    return ui.frame(all_lines, C, R)


# ---- runtime loop ----------------------------------------------------------

def run(term=None, caps=None):
    if sys.platform == "win32" and term is None:
        print("error: anbani tui is not supported on Windows; try the npm package: npx anbani", file=sys.stderr)
        return 2
    term = term or Term()
    if not term.is_tty():
        print("error: anbani tui requires an interactive terminal", file=sys.stderr)
        return 2
    caps = caps or detect_caps(dict(os.environ), True)
    style = Style(caps)
    state = initial_state()
    cols, rows = term.size()
    state["size"] = {"cols": cols, "rows": rows}

    nlp_pending = [False]

    ctx = {
        "copy": lambda text: term.write(osc52(text, dict(os.environ))),
        "request_nlp_load": lambda: nlp_pending.__setitem__(0, True),
        "nlp": None,
        "lorem": None,
    }

    def paint():
        c, r = term.size()
        lines = render(state, {"cols": c, "rows": r}, style)
        frame = CUR_HIDE + "".join(move_to(i + 1, 1) + lines[i] + EL for i in range(len(lines)))
        term.write(frame)

    def load_nlp():
        from anbani.nlp import georgianisation, contractions

        ctx["nlp"] = {"georgianisation": georgianisation, "contractions": contractions}
        return update(state, {"type": "nlp:loaded"}, ctx)

    term.start()
    try:
        paint()
        while True:
            timeout = 0.04 if term.parser_esc_pending else 0.25
            events = term.read_events(timeout)
            changed = False
            if term.size_changed():
                c, r = term.size()
                state = update(state, {"type": "resize", "cols": c, "rows": r}, ctx)
                changed = True
            for ev in events:
                state = update(state, ev, ctx)
                changed = True
                if state["quit"]:
                    return 0
            if changed:
                paint()
            if nlp_pending[0]:
                nlp_pending[0] = False
                state = load_nlp()
                paint()
    finally:
        term.stop()
