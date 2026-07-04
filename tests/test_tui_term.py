from anbani.tui.keys import parse_keys, make_parser_state, flush_escape
from anbani.tui.ui import width
from anbani.tui.clipboard import osc52

# KEEP IN SYNC WITH anbani.js/test/tui.term.test.mjs


def feed(byte_list, state=None):
    events, state = parse_keys(bytes(byte_list), state or make_parser_state())
    return events, state


def test_plain_ascii():
    events, _ = feed([0x61])
    assert events == [{"type": "char", "char": "a"}]


def test_enter_tab_backspace():
    assert feed([0x0D])[0][0]["name"] == "enter"
    assert feed([0x0A])[0][0]["name"] == "enter"
    assert feed([0x09])[0][0]["name"] == "tab"
    assert feed([0x7F])[0][0]["name"] == "backspace"
    assert feed([0x08])[0][0]["name"] == "backspace"


def test_ctrl_combos():
    assert feed([0x03])[0][0]["name"] == "ctrl+c"
    assert feed([0x04])[0][0]["name"] == "ctrl+d"
    assert feed([0x15])[0][0]["name"] == "ctrl+u"
    assert feed([0x17])[0][0]["name"] == "ctrl+w"
    assert feed([0x0B])[0][0]["name"] == "ctrl+k"


def test_csi_nav():
    assert feed([0x1B, 0x5B, 0x41])[0][0]["name"] == "up"
    assert feed([0x1B, 0x5B, 0x42])[0][0]["name"] == "down"
    assert feed([0x1B, 0x5B, 0x43])[0][0]["name"] == "right"
    assert feed([0x1B, 0x5B, 0x44])[0][0]["name"] == "left"
    assert feed([0x1B, 0x5B, 0x5A])[0][0]["name"] == "shift+tab"
    assert feed([0x1B, 0x5B, 0x48])[0][0]["name"] == "home"
    assert feed([0x1B, 0x5B, 0x46])[0][0]["name"] == "end"
    assert feed([0x1B, 0x5B, 0x33, 0x7E])[0][0]["name"] == "delete"
    assert feed([0x1B, 0x5B, 0x35, 0x7E])[0][0]["name"] == "pageup"
    assert feed([0x1B, 0x5B, 0x36, 0x7E])[0][0]["name"] == "pagedown"


def test_ss3():
    assert feed([0x1B, 0x4F, 0x41])[0][0]["name"] == "up"
    assert feed([0x1B, 0x4F, 0x46])[0][0]["name"] == "end"


def test_utf8_codepoint():
    events, _ = feed([0xE1, 0x83, 0x94])
    assert events == [{"type": "char", "char": "ე"}]


def test_utf8_split_chunks():
    st = make_parser_state()
    a, st = parse_keys(bytes([0xE1]), st)
    assert a == []
    b, st = parse_keys(bytes([0x83, 0x94]), st)
    assert b == [{"type": "char", "char": "ე"}]


def test_bracketed_paste_split():
    start = [0x1B, 0x5B, 0x32, 0x30, 0x30, 0x7E]
    end = [0x1B, 0x5B, 0x32, 0x30, 0x31, 0x7E]
    body = list("აბ".encode("utf-8"))
    st = make_parser_state()
    parse_keys(bytes(start + body), st)
    ev, st = parse_keys(bytes(end), st)
    assert ev == [{"type": "paste", "text": "აბ"}]


def test_lone_esc_flush():
    st = make_parser_state()
    a, st = parse_keys(bytes([0x1B]), st)
    assert a == []
    assert st["mode"] == "ESC"
    ev, st = flush_escape(st)
    assert ev[0]["name"] == "escape"


def test_esc_then_char():
    ev, _ = feed([0x1B, 0x78])
    assert ev[0]["name"] == "escape"
    assert ev[1] == {"type": "char", "char": "x"}


def test_width():
    for ch in ["ა", "Ა", "Ⴀ", "ⴀ"]:
        assert width(ch) == 1
    assert width("ა̈") == 1
    assert width("t͡ʃ") == 2
    assert width("漢") == 2
    assert width("😀") == 2
    assert width("\x1b[31mab\x1b[0m") == 2


def test_osc52():
    assert osc52("აბ") == "\x1b]52;c;4YOQ4YOR\x07"
    s = osc52("x", {"TMUX": "1"})
    assert s.startswith("\x1bPtmux;")
    assert s.endswith("\x1b\\")
    assert "\x1b\x1b]52;c;" in s
