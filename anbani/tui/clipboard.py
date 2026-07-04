"""OSC 52 clipboard write (pure string builder). Some terminals block OSC 52;
there is no ack channel, so a failed copy degrades silently.

KEEP IN SYNC WITH anbani.js/src/tui/clipboard.mjs
"""

import base64

OSC52_MAX = 100000


def osc52(text, env=None):
    env = env or {}
    t = text or ""
    data = t.encode("utf-8")
    if len(data) > OSC52_MAX:
        data = data[:OSC52_MAX]
        # avoid splitting a multibyte char at the cut
        t = data.decode("utf-8", "ignore")
        data = t.encode("utf-8")
    b64 = base64.b64encode(data).decode("ascii")
    seq = "\x1b]52;c;" + b64 + "\x07"
    if env.get("TMUX"):
        return "\x1bPtmux;" + seq.replace("\x1b", "\x1b\x1b") + "\x1b\\"
    return seq
