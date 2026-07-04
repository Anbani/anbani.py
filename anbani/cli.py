"""Command-line interface for anbani, mirroring the anbani.js `anbani` binary.

Subcommands (same names on both sides): convert, interpret, georgianise,
latinise, expand, contract, lorem. Heavy submodules are imported lazily inside
each handler so `anbani convert` never loads the NLP data tables.
"""

import argparse
import sys


def _version():
    try:
        from importlib.metadata import version

        return version("anbani")
    except Exception:  # pragma: no cover - metadata always present once installed
        return "unknown"


def _text(value):
    # Positional text; "-" or omitted reads stdin (handy for pipes).
    if value is None or value == "-":
        return sys.stdin.read().rstrip("\n")
    return value


def _convert(args):
    from anbani.core.converter import convert

    print(convert(_text(args.text), args.source, args.target))


def _interpret(args):
    from anbani.core.converter import interpret

    print(interpret(_text(args.text), args.target))


def _georgianise(args):
    from anbani.nlp.georgianisation import georgianise

    print(georgianise(_text(args.text), mode=args.mode))


def _latinise(args):
    from anbani.nlp.georgianisation import latinise

    print(latinise(_text(args.text)))


def _expand(args):
    from anbani.nlp.contractions import expand_text

    print(expand_text(_text(args.text)))


def _contract(args):
    from anbani.nlp.contractions import contract_text

    print(contract_text(_text(args.text)))


def _lorem(args):
    from anbani import lorem

    if args.seed is not None:
        lorem.seed(args.seed)
    if args.names:
        print("\n".join(lorem.names(args.names)))
    elif args.paragraphs:
        print(lorem.paragraphs(args.words, args.paragraphs), end="")
    else:
        print(lorem.sentences(args.words))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="anbani", description="Georgian alphabet & language toolkit"
    )
    parser.add_argument(
        "--version", action="version", version=f"anbani.py {_version()}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("convert", help="convert between scripts")
    p.add_argument("text", nargs="?")
    p.add_argument("-f", "--from", dest="source", required=True)
    p.add_argument("-t", "--to", dest="target", required=True)
    p.set_defaults(func=_convert)

    p = sub.add_parser("interpret", help="auto-detect the source script and convert")
    p.add_argument("text", nargs="?")
    p.add_argument("-t", "--to", dest="target", default="mtavruli")
    p.set_defaults(func=_interpret)

    p = sub.add_parser("georgianise", help="transliterate Latin -> Georgian")
    p.add_argument("text", nargs="?")
    p.add_argument(
        "-m", "--mode", default="balanced", choices=["fast", "balanced", "accurate"]
    )
    p.set_defaults(func=_georgianise)

    p = sub.add_parser("latinise", help="transliterate Georgian -> Latin")
    p.add_argument("text", nargs="?")
    p.set_defaults(func=_latinise)

    p = sub.add_parser("expand", help="expand contractions")
    p.add_argument("text", nargs="?")
    p.set_defaults(func=_expand)

    p = sub.add_parser("contract", help="contract expansions")
    p.add_argument("text", nargs="?")
    p.set_defaults(func=_contract)

    p = sub.add_parser("lorem", help="generate fake Georgian text")
    p.add_argument("-w", "--words", type=int, default=8)
    p.add_argument("-p", "--paragraphs", type=int)
    p.add_argument("-n", "--names", type=int)
    p.add_argument("--seed", type=int)
    p.set_defaults(func=_lorem)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
