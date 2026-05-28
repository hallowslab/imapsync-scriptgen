import pytest
from src.imapsync_scriptgen.cli_adapter import UnsafeScriptGenerator

from .fixtures import cfg as CONFIG, gen as GEN

gen = GEN
cfg = CONFIG


# Test process_line
def test_process_line_valid(gen):
    result = gen.process_line("jeff p1 john p2")
    assert result.metadata["user1"] == "jeff"
    assert result.metadata["user2"] == "john"
    assert "p1" in result.argv
    assert "p2" in result.argv


def test_process_line_invalid(gen):
    # Missing password
    result = gen.process_line("user1")
    assert result is None


# Test line_generator
def test_line_generator(gen):
    lines = ["a1 p1", "a2 p2"]
    out = list(gen.line_generator(lines))
    assert len(out) == 2
    assert out[0].metadata["user1"] == "a1"
    assert out[1].metadata["user1"] == "a2"


# Test write_output
def test_write_output_creates_file(gen, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    cmd1 = gen.process_line("u1 p1")
    cmd2 = gen.process_line("u2 p2")
    gen.write_output([cmd1, cmd2])

    expected_file = tmp_path / "sync_0.sh"
    assert expected_file.exists()

    contents = expected_file.read_text().splitlines()
    assert len(contents) == 2
    assert "p1" in contents[0]
    assert "p2" in contents[1]


def test_write_output_dry_run(cfg, capsys, tmp_path, monkeypatch):
    cfg.dry_run = True
    gen = UnsafeScriptGenerator(cfg)

    monkeypatch.chdir(tmp_path)

    cmd1 = gen.process_line("u1 p1")
    gen.write_output([cmd1])

    # Read and return the captured output so far, resetting the internal buffer.
    captured = capsys.readouterr()
    assert "Dry-run" in captured.out
    assert "********" in captured.out
    assert "p1" not in captured.out

    # No files should be written
    assert not list(tmp_path.iterdir())


# Test process_file
def test_process_file(gen, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    # Create an input file
    f = tmp_path / "input.txt"
    f.write_text("john p1\njeff p2\ncoral p3\n")

    # split=2, 2 batches: ("john", "jeff") and ("coral")
    gen.process_file(str(f))

    # Expected output files
    f0 = tmp_path / "sync_0.sh"
    f1 = tmp_path / "sync_1.sh"

    assert f0.exists()
    assert f1.exists()

    c0 = f0.read_text().splitlines()
    c1 = f1.read_text().splitlines()

    assert len(c0) == 2
    assert len(c1) == 1


def test_process_file_invalid(gen):
    with pytest.raises(ValueError):
        gen.process_file("not_a_file")
