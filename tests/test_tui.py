from anbani.tui import app
from anbani.tui.style import Style
from anbani.tui.ui import width

# KEEP IN SYNC WITH anbani.js/test/tui.test.mjs

STYLE_OFF = Style({"colors": "none"})
SIZE = {"cols": 80, "rows": 24}


def K(name):
    return {"type": "key", "name": name}


def CH(ch):
    return {"type": "char", "char": ch}


def typ(s):
    return [CH(c) for c in s]


def feed(state, events, ctx=None):
    for e in events:
        state = app.update(state, e, ctx or {})
    return state


def frame_of(state, size=None):
    return app.render(state, size or SIZE, STYLE_OFF)


def test_frame_invariants():
    base = app.initial_state()
    states = []
    for digit in ["1", "2", "3", "4", "5"]:
        states.append(feed(base, [CH(digit)]))
    states.append(feed(base, [CH("?")]))
    states.append(base)
    for st in states:
        for size in [SIZE, {"cols": 100, "rows": 30}, {"cols": 62, "rows": 18}]:
            lines = frame_of(st, size)
            assert len(lines) == size["rows"]
            for l in lines:
                assert width(l) == size["cols"], (size, repr(l))


def test_min_size_notice():
    lines = frame_of(app.initial_state(), {"cols": 50, "rows": 10})
    assert "Terminal too small" in "\n".join(lines)


def test_help_toggle():
    s = feed(app.initial_state(), [CH("?")])
    assert s["help"] is True
    s = feed(s, [CH("x")])
    assert s["help"] is False


def test_tab_wrap():
    s = feed(app.initial_state(), [K("shift+tab")])
    assert s["tab"] == "toolkit"


def test_ctrlc_quits_in_insert_and_q_types():
    s = feed(app.initial_state(), [CH("i")])
    assert s["screens"]["converter"]["focus"] == "input"
    typed = feed(s, [CH("q")])
    assert typed["quit"] is not True
    assert typed["screens"]["converter"]["input"]["text"] == "q"
    quit_s = feed(s, [K("ctrl+c")])
    assert quit_s["quit"] is True


def test_converter_auto():
    s = feed(app.initial_state(), [CH("i")] + typ("gamarjoba") + [K("escape")])
    assert s["screens"]["converter"]["output"] == "ᲒᲐᲛᲐᲠᲯᲝᲑᲐ"
    assert s["screens"]["converter"]["detected"] == "latin"
    assert "ᲒᲐᲛᲐᲠᲯᲝᲑᲐ" in "\n".join(frame_of(s))


def test_converter_error_survives():
    s = feed(app.initial_state(), [CH("i")] + typ("!!!"))
    assert s["screens"]["converter"]["error"]
    s = feed(s, [K("escape"), CH("2")])
    assert s["tab"] == "alphabet"


def test_converter_bad_swap_toasts():
    # manual mode, then cycle `to` to a non-source target (homoglyph)
    s = feed(app.initial_state(), [CH("m"), CH("o"), CH("o"), CH("o")])
    assert s["screens"]["converter"]["to"] == "homoglyph"
    before = (s["screens"]["converter"]["from"], s["screens"]["converter"]["to"])
    s = feed(s, [CH("s")])
    assert s["toast"] and "cannot swap" in s["toast"]["text"]
    assert (s["screens"]["converter"]["from"], s["screens"]["converter"]["to"]) == before


def test_converter_valid_swap():
    # to=nuskhuri (a source) via two `o` cycles from mtavruli
    s = feed(app.initial_state(), [CH("m"), CH("o"), CH("o")])
    assert s["screens"]["converter"]["to"] == "nuskhuri"
    s = feed(s, [CH("s")])
    assert s["screens"]["converter"]["from"] == "nuskhuri"
    assert s["screens"]["converter"]["to"] == "mkhedruli"


def test_alphabet():
    copied = []
    ctx = {"copy": lambda t: copied.append(t)}
    s = feed(app.initial_state(), [CH("2"), CH("l"), CH("l"), CH("l")], ctx)
    assert s["screens"]["alphabet"]["cursor"] == 3
    f = "\n".join(frame_of(s))
    for token in ["დონ", "Ⴃ", "⠙", "4"]:
        assert token in f, token
    s = feed(s, [CH("a")], ctx)
    assert s["screens"]["alphabet"]["archaic"] is True
    assert s["screens"]["alphabet"]["cursor"] == 3
    s = feed(s, [K("enter")], ctx)
    assert copied == ["დ"]


class _FakeLorem:
    def sentences(self, n):
        return ("სიტყვა " * n).strip() + "."

    def paragraphs(self, w, p):
        return (("სიტყვა " * w).strip() + ".\n\n") * p

    def names(self, n):
        return ["სახელი გვარი"] * n


def test_lorem():
    ctx = {"lorem": _FakeLorem()}
    s = feed(app.initial_state(), [CH("3"), CH("g")], ctx)
    assert len(s["screens"]["lorem"]["output"]) > 0
    s = feed(s, [CH("k")], ctx)
    assert s["screens"]["lorem"]["kind"] == "paragraphs"
    s = feed(app.initial_state(), [CH("3")], ctx)
    s = feed(s, [CH("-")] * 30, ctx)
    assert s["screens"]["lorem"]["words"] == 1


def test_nlp_lazy_and_accurate_available():
    loads = [0]

    def req():
        loads[0] += 1

    ctx = {"request_nlp_load": req}
    s = feed(app.initial_state(), [CH("4")], ctx)
    assert loads[0] == 1
    assert s["screens"]["nlp"]["loading"] is True
    s = feed(s, [CH("1"), CH("4")], ctx)
    assert loads[0] == 1
    from anbani.nlp import georgianisation, contractions

    ctx["nlp"] = {"georgianisation": georgianisation, "contractions": contractions}
    s = app.update(s, {"type": "nlp:loaded"}, ctx)
    assert s["screens"]["nlp"]["loaded"] is True
    s = feed(s, [CH("i")] + typ("gamarjoba"), ctx)
    import re

    assert re.search("[ა-ჰ]", s["screens"]["nlp"]["output"])
    # Python exposes accurate; cycling reaches it
    s = feed(s, [K("escape")], ctx)
    seen = set()
    for _ in range(4):
        s = feed(s, [CH("b")], ctx)
        seen.add(s["screens"]["nlp"]["gmode"])
    assert "accurate" in seen


def test_splash():
    for size in [SIZE, {"cols": 100, "rows": 30}, {"cols": 62, "rows": 18}]:
        lines = app.splash_frame(size, STYLE_OFF)
        assert len(lines) == size["rows"]
        for l in lines:
            assert width(l) == size["cols"]
    assert "loading…" in "\n".join(app.splash_frame(SIZE, STYLE_OFF))


def test_toolkit():
    s = feed(app.initial_state(), [CH("5"), CH("i")] + typ("აააბბგ"))
    st = s["screens"]["toolkit"]["stats"]
    assert st["total"] == 6
    assert st["unique"] == 3
    assert st["entries"][0][1] == 3
    assert st["entries"][1][1] == 2
    assert st["entries"][2][1] == 1
