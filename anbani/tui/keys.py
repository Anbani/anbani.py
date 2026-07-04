"""Pure key parser: a byte state machine turning raw terminal input into a
stream of normalised events. No timers, no I/O (the ESC-disambiguation timer
lives in term.py and calls flush_escape). Handles UTF-8 (Georgian is 3-byte),
arrow/nav keys, ctrl combos and bracketed paste, all resilient to a sequence
being split across read chunks.

Event dicts:
    {"type": "char", "char": c}
    {"type": "key", "name": name, "ctrl": bool, "shift": bool}
    {"type": "paste", "text": text}

KEEP IN SYNC WITH anbani.js/src/tui/keys.mjs
"""

import re

PASTE_END = (0x1B, 0x5B, 0x32, 0x30, 0x31, 0x7E)  # ESC [ 2 0 1 ~
PASTE_MAX = 65536

_C0_STRIP = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f]")


def make_parser_state():
    return {
        "mode": "GROUND",  # GROUND | ESC | CSI | SS3 | PASTE | UTF8
        "csi": "",
        "utf8_need": 0,
        "utf8_bytes": [],
        "paste_bytes": [],
        "esc_pending": False,
    }


def _key(name, ctrl=False, shift=False):
    return {"type": "key", "name": name, "ctrl": ctrl, "shift": shift}


def _chr(c):
    return {"type": "char", "char": c}


def _decode(byte_list):
    return bytes(byte_list).decode("utf-8", "replace")


def _ground_byte(b, events, st):
    if b in (0x0D, 0x0A):
        events.append(_key("enter"))
    elif b == 0x09:
        events.append(_key("tab"))
    elif b in (0x7F, 0x08):
        events.append(_key("backspace"))
    elif b == 0x03:
        events.append(_key("ctrl+c", ctrl=True))
    elif b == 0x04:
        events.append(_key("ctrl+d", ctrl=True))
    elif b == 0x01:
        events.append(_key("home"))
    elif b == 0x05:
        events.append(_key("end"))
    elif b == 0x15:
        events.append(_key("ctrl+u", ctrl=True))
    elif b == 0x17:
        events.append(_key("ctrl+w", ctrl=True))
    elif b == 0x0B:
        events.append(_key("ctrl+k", ctrl=True))
    elif b == 0x1B:
        st["mode"] = "ESC"
        st["esc_pending"] = True
    elif 0x20 <= b <= 0x7E:
        events.append(_chr(chr(b)))
    elif 0xC2 <= b <= 0xF4:
        st["mode"] = "UTF8"
        st["utf8_need"] = 2 if b < 0xE0 else 3 if b < 0xF0 else 4
        st["utf8_bytes"] = [b]
    # other C0 / stray continuation bytes: ignored


def _esc_byte(b, events, st):
    """Return True if consumed, False if the byte must be reprocessed."""
    if b == 0x5B:
        st["mode"] = "CSI"
        st["csi"] = ""
        st["esc_pending"] = False
        return True
    if b == 0x4F:
        st["mode"] = "SS3"
        st["esc_pending"] = False
        return True
    events.append(_key("escape"))
    st["esc_pending"] = False
    st["mode"] = "GROUND"
    return False


_ARROW = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end"}


def _interpret_csi(params, final, events, st):
    letter = chr(final)
    if letter == "Z":
        events.append(_key("shift+tab", shift=True))
        return
    if final == 0x7E:
        head = params.split(";")[0]
        num = int(head) if head.isdigit() else -1
        if num == 200:
            st["mode"] = "PASTE"
            st["paste_bytes"] = []
            return
        mapping = {1: "home", 7: "home", 4: "end", 8: "end", 3: "delete", 5: "pageup", 6: "pagedown"}
        if num in mapping:
            events.append(_key(mapping[num]))
        return
    if letter in _ARROW:
        parts = params.split(";")
        ctrl = shift = False
        if len(parts) >= 2 and parts[1].isdigit():
            mod = int(parts[1]) - 1
            shift = bool(mod & 1)
            ctrl = bool(mod & 4)
        events.append(_key(_ARROW[letter], ctrl=ctrl, shift=shift))


def _ends_with(lst, suffix):
    n = len(suffix)
    if len(lst) < n:
        return False
    return tuple(lst[-n:]) == tuple(suffix)


def _normalize_paste(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return _C0_STRIP.sub("", text)


def parse_keys(buf, state):
    st = state if state is not None else make_parser_state()
    events = []
    i = 0
    n = len(buf)
    while i < n:
        b = buf[i]
        mode = st["mode"]
        if mode == "GROUND":
            _ground_byte(b, events, st)
            i += 1
        elif mode == "ESC":
            if _esc_byte(b, events, st):
                i += 1
        elif mode == "CSI":
            if 0x40 <= b <= 0x7E:
                _interpret_csi(st["csi"], b, events, st)
                if st["mode"] == "CSI":
                    st["mode"] = "GROUND"
            else:
                st["csi"] += chr(b)
            i += 1
        elif mode == "SS3":
            m = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end"}
            letter = chr(b)
            if letter in m:
                events.append(_key(m[letter]))
            st["mode"] = "GROUND"
            i += 1
        elif mode == "UTF8":
            if 0x80 <= b <= 0xBF:
                st["utf8_bytes"].append(b)
                if len(st["utf8_bytes"]) == st["utf8_need"]:
                    events.append(_chr(_decode(st["utf8_bytes"])))
                    st["mode"] = "GROUND"
                i += 1
            else:
                events.append(_chr("�"))
                st["mode"] = "GROUND"
                # reprocess b in GROUND (do not advance)
        elif mode == "PASTE":
            st["paste_bytes"].append(b)
            if _ends_with(st["paste_bytes"], PASTE_END):
                content = st["paste_bytes"][: len(st["paste_bytes"]) - len(PASTE_END)]
                text = _normalize_paste(_decode(content[:PASTE_MAX]))
                events.append({"type": "paste", "text": text})
                st["paste_bytes"] = []
                st["mode"] = "GROUND"
            i += 1
        else:
            st["mode"] = "GROUND"
            i += 1
    return events, st


def flush_escape(state):
    events = []
    if state and state.get("mode") == "ESC":
        events.append(_key("escape"))
        state["mode"] = "GROUND"
        state["esc_pending"] = False
    return events, state
