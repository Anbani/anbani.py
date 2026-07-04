import pytest

from anbani.cli import main


def test_convert(capsys):
    assert main(["convert", "ანბანი", "-f", "mkhedruli", "-t", "asomtavruli"]) == 0
    assert capsys.readouterr().out.strip() == "ႠႬႡႠႬႨ"


def test_interpret_default_target(capsys):
    assert main(["interpret", "anbani"]) == 0
    # qwerty -> mtavruli (default)
    assert capsys.readouterr().out.strip() == "ᲐᲜᲑᲐᲜᲘ"


def test_expand(capsys):
    assert main(["expand", "ვნახოთ ა. შ."]) == 0
    assert capsys.readouterr().out.strip() == "ვნახოთ ასე შემდეგ"


def test_contract(capsys):
    assert main(["contract", "ვნახოთ ასე შემდეგ"]) == 0
    assert capsys.readouterr().out.strip() == "ვნახოთ ა.შ."


def test_lorem_names(capsys):
    assert main(["lorem", "--names", "2", "--seed", "7"]) == 0
    out = capsys.readouterr().out.strip().split("\n")
    assert len(out) == 2


def test_bad_target_exits_nonzero(capsys):
    assert main(["convert", "ა", "-f", "mkhedruli", "-t", "klingon"]) == 2
    assert "error" in capsys.readouterr().err.lower()


def test_missing_subcommand_errors():
    with pytest.raises(SystemExit):
        main([])
