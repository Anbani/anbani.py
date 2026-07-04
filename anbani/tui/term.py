"""Terminal I/O: raw mode, alt-screen, cursor, bracketed paste, resize, and the
mandatory cleanup that must always restore the terminal. Pure key parsing is
delegated to keys.py and re-exported for tests.

KEEP IN SYNC WITH anbani.js/src/tui/term.mjs
"""

import atexit
import os
import signal
import sys

from .keys import parse_keys, flush_escape, make_parser_state  # noqa: F401

ESC = "\x1b"
CSI = "\x1b["
ALT_ON = "\x1b[?1049h"
ALT_OFF = "\x1b[?1049l"
CUR_HIDE = "\x1b[?25l"
CUR_SHOW = "\x1b[?25h"
PASTE_ON = "\x1b[?2004h"
PASTE_OFF = "\x1b[?2004l"
CLEAR = "\x1b[2J"
HOME = "\x1b[H"
EL = "\x1b[K"
SGR0 = "\x1b[0m"

ENTER_SEQ = ALT_ON + CLEAR + HOME + CUR_HIDE + PASTE_ON
EXIT_SEQ = SGR0 + PASTE_OFF + CUR_SHOW + ALT_OFF


def move_to(row, col):
    return "\x1b[{};{}H".format(row, col)


class Term:
    def __init__(self, in_=None, out=None, size=None, interactive=True):
        self.in_ = in_ if in_ is not None else sys.stdin
        self.out = out if out is not None else sys.stdout
        self._size = size
        self.interactive = interactive
        self._started = False
        self._restored = False
        self._saved = None
        self._fd = None
        self._winch = False
        self.pstate = make_parser_state()

    def is_tty(self):
        try:
            return bool(self.in_.isatty() and self.out.isatty())
        except Exception:
            return self._size is not None

    def size(self):
        if self._size:
            return self._size
        try:
            ts = os.get_terminal_size(self.out.fileno())
            return (ts.columns, ts.lines)
        except Exception:
            return (80, 24)

    @property
    def parser_esc_pending(self):
        return self.pstate.get("mode") == "ESC"

    def size_changed(self):
        if self._winch:
            self._winch = False
            return True
        return False

    def _on_winch(self, *a):
        self._winch = True

    def start(self):
        if self._started:
            return
        self._started = True
        if self.interactive and self.is_tty():
            import termios
            import tty

            self._fd = self.in_.fileno()
            self._saved = termios.tcgetattr(self._fd)
            tty.setraw(self._fd)
            self.write(ENTER_SEQ)
            atexit.register(self.stop)
            for sig in (getattr(signal, "SIGTERM", None), getattr(signal, "SIGHUP", None)):
                if sig is not None:
                    try:
                        signal.signal(sig, self._sig_stop)
                    except (ValueError, OSError):
                        pass
            if hasattr(signal, "SIGWINCH"):
                try:
                    signal.signal(signal.SIGWINCH, self._on_winch)
                except (ValueError, OSError):
                    pass

    def _sig_stop(self, *a):
        self.stop()
        raise SystemExit(0)

    def stop(self):
        if self._restored:
            return
        self._restored = True
        if self.interactive and self._saved is not None:
            import termios

            try:
                self.write(EXIT_SEQ)
            except Exception:
                pass
            try:
                termios.tcsetattr(self._fd, termios.TCSADRAIN, self._saved)
            except Exception:
                pass

    def write(self, s):
        self.out.write(s)
        try:
            self.out.flush()
        except Exception:
            pass

    def read_events(self, timeout):
        """Block up to `timeout` seconds. On timeout, flush a pending lone ESC."""
        if not (self.interactive and self.is_tty()):
            return []
        import select

        try:
            r, _, _ = select.select([self._fd], [], [], timeout)
        except (InterruptedError, OSError):
            return []
        if not r:
            if self.pstate.get("mode") == "ESC":
                evs, _ = flush_escape(self.pstate)
                return evs
            return []
        try:
            data = os.read(self._fd, 1024)
        except OSError:
            return []
        if not data:
            return []
        evs, _ = parse_keys(data, self.pstate)
        return evs
