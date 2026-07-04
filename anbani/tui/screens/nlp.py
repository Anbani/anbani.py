"""NLP lab screen: georgianise / latinise / expand / contract. The NLP modules
are heavy, so they load lazily the first time this tab opens (app wires the
import and dispatches an "nlp:loaded" event). Python exposes the extra
"accurate" gmode -- the one sanctioned cross-language difference.

KEEP IN SYNC WITH anbani.js/src/tui/screens/nlp.mjs
"""

from .. import ui

id = "nlp"
label = "NLP"
title = "ენის ლაბი"
can_input = True

MODES = ["georgianise", "latinise", "expand", "contract"]
GMODES = ["fast", "balanced", "accurate"]  # Python: includes "accurate"


def init():
    return {
        "mode": "georgianise",
        "gmode": "balanced",
        "input": ui.make_input(""),
        "output": "",
        "error": None,
        "loaded": False,
        "loading": False,
        "focus": "normal",
    }


def _recompute(s, ctx):
    text = s["input"]["text"]
    nlp = (ctx or {}).get("nlp")
    if not s["loaded"] or not nlp:
        s2 = dict(s)
        s2["output"] = ""
        s2["error"] = None
        return s2
    output = ""
    error = None
    if text:
        try:
            g = nlp["georgianisation"]
            c = nlp["contractions"]
            if s["mode"] == "georgianise":
                output = g.georgianise(text, s["gmode"])
            elif s["mode"] == "latinise":
                output = g.latinise(text)
            elif s["mode"] == "expand":
                output = c.expand_text(text)
            else:
                output = c.contract_text(text)
        except Exception as e:
            error = str(e)
            output = ""
    s2 = dict(s)
    s2["output"] = output
    s2["error"] = error
    return s2


def on_enter_tab(s, ctx):
    if s["loaded"] or s["loading"]:
        return s
    if ctx and ctx.get("request_nlp_load"):
        ctx["request_nlp_load"]()
    s2 = dict(s)
    s2["loading"] = True
    return s2


def on_loaded(s, ctx):
    s2 = dict(s)
    s2["loaded"] = True
    s2["loading"] = False
    return _recompute(s2, ctx)


def update(s, event, ctx=None):
    if s["focus"] == "input":
        s2 = dict(s)
        s2["input"] = ui.input_handle(s["input"], event)
        return _recompute(s2, ctx)
    name = event["char"] if event["type"] == "char" else event.get("name")
    s2 = dict(s)
    if name in ("i", "enter"):
        s2["focus"] = "input"
        return s2
    if name == "m":
        s2["mode"] = MODES[(MODES.index(s["mode"]) + 1) % len(MODES)]
        return _recompute(s2, ctx)
    if name == "M":
        s2["mode"] = MODES[(MODES.index(s["mode"]) - 1) % len(MODES)]
        return _recompute(s2, ctx)
    if name == "b":
        if s["mode"] != "georgianise":
            return s
        s2["gmode"] = GMODES[(GMODES.index(s["gmode"]) + 1) % len(GMODES)]
        return _recompute(s2, ctx)
    if name == "x":
        s2["input"] = ui.make_input("")
        return _recompute(s2, ctx)
    return s


def get_copy_text(s):
    return s["output"] or None


def status(s):
    if s["error"]:
        return {"error": "error: {}".format(s["error"])}
    if s["loading"] and not s["loaded"]:
        return {"hint": "loading nlp…"}
    return {"hint": "{} · {}".format(s["mode"], s["gmode"]) if s["mode"] == "georgianise" else s["mode"]}


def footer(s=None):
    return "i edit  m mode  b gmode  x clear  y copy"


def render(s, box, style):
    C = box["cols"]
    R = box["rows"]
    lines = []
    lines.append(ui.tabs(MODES, MODES.index(s["mode"]), C, style))
    if s["mode"] == "georgianise":
        lines.append("gmode:  " + "".join(ui.pill(g, g == s["gmode"], style) for g in GMODES))
    else:
        lines.append(ui.blank(C))
    lines.append(ui.blank(C))
    lines.append(ui.box_top(C, "input"))
    lines.append(ui.box_line_rich(ui.input_render(s["input"], C - 4, style, s["focus"] == "input"), C))
    lines.append(ui.box_bottom(C))
    lines.append(ui.blank(C))

    header = len(lines)
    body_rows = max(1, R - header - 2)
    if s["loading"] and not s["loaded"]:
        for l in ui.callout(["loading nlp…"], C, style):
            lines.append(l)
    else:
        body = []
        if not s["input"]["text"]:
            body.append(style.dim() + "type text…" + style.reset() if style.on else "type text…")
        else:
            for l in ui.wrap_text(s["output"], C - 4):
                body.append(l)
        while len(body) < body_rows:
            body.append("")
        lines.append(ui.box_top(C, "output"))
        for i in range(body_rows):
            lines.append(ui.box_line(body[i] if i < len(body) else "", C))
        lines.append(ui.box_bottom(C))

    return ui.frame(lines, C, R)
