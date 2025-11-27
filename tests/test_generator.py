import pytest
from src.imapsync_scriptgen.generator import ScriptGenerator

from .fixtures import cfg as CONFIG, gen as GEN

gen = GEN
cfg = CONFIG


# Test match_domain
@pytest.mark.parametrize(
    "input_line, expected",
    (
        ["user@domain.com", "domain.com"],
        ["no-at-symbol.com.pt ", None],
        ["user@sub.domain.net ", "sub.domain.net"],
        ["john.doe@sub.domain.co.uk", "sub.domain.co.uk"],
    ),
)
def test_match_domain(gen, input_line, expected):
    assert gen.match_domain(input_line) == expected


# Test extract_domains_from_credentials
@pytest.mark.parametrize(
    "input_line, expected_domains",
    [
        ("user@domain.com Pass1", ["domain.com"]),
        ("no-at-symbol.com.pt YouShallNotP@ssw.ord", []),
        ("Invalid", []),
        ("user@sub.domain.net Password@123!", ["sub.domain.net"]),
        ("john.doe@sub.domain.co.uk Testing123!", ["sub.domain.co.uk"]),
        ("chegg@x.y.z.com Password1 bob@ross.com P$ss0rd!", ["x.y.z.com", "ross.com"]),
    ],
)
def test_extract_domains_from_credentials(
    gen: ScriptGenerator, input_line, expected_domains
):
    assert set(gen.extract_domains_from_credentials(input_line)) == set(
        expected_domains
    )


# Test make_command
def test_make_command_basic(gen):
    cmd = gen.make_command("jeff", "p1", "john", "p2")

    assert "--host1 imap.source.tld" in cmd
    assert "--host2 imap.dest.tld" in cmd
    assert "--user1 jeff" in cmd
    assert "--user2 john" in cmd
    assert "--password1 'p1'" in cmd
    assert "--password2 'p2'" in cmd

    # logfile name should match expected format
    assert "imap.source.tld__imap.dest.tld__jeff--john.log" in cmd


def test_make_command_extra_args(gen):
    gen.extra_args = "--nossl1 --notls1"
    cmd = gen.make_command("jeff", "p1", "john", "p2")

    assert cmd.endswith("--nossl1 --notls1")


# Test process_line
def test_process_line_valid(gen):
    result = gen.process_line("jeff p1 john p2")
    assert "jeff" in result
    assert "john" in result
    assert "--password1 'p1'" in result
    assert "--password2 'p2'" in result


def test_process_line_invalid(gen):
    # Missing password
    result = gen.process_line("user1")
    assert result is None


# Test line_generator
def test_line_generator(gen):
    lines = ["a1 p1", "a2 p2"]
    out = list(gen.line_generator(lines))
    assert len(out) == 2
    assert "a1" in out[0]
    assert "a2" in out[1]


def test_line_generator_collects_domains(gen):
    domain_set = set()
    list(gen.line_generator(["user@domain.tld pass"], domain_set))
    assert domain_set == {"domain.tld"}


# Test process_strings
def test_process_strings(gen):
    out = gen.process_strings(["a1 p1", "a2 p2"])
    assert len(out) == 2
    assert "--user1 a1" in out[0]


# Test write_output
def test_write_output_creates_file(gen, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    gen.write_output(["cmd1", "cmd2"])

    expected_file = tmp_path / "sync_0.sh"
    assert expected_file.exists()

    contents = expected_file.read_text().splitlines()
    assert contents == ["cmd1", "cmd2"]


def test_write_output_dry_run(cfg, capsys, tmp_path, monkeypatch):
    cfg.dry_run = True
    gen = ScriptGenerator(cfg)

    monkeypatch.chdir(tmp_path)

    gen.write_output(["cmd1", "cmd2"])

    # Read and return the captured output so far, resetting the internal buffer.
    captured = capsys.readouterr()
    assert "Dry-run" in captured.out
    assert "cmd1" in captured.out
    assert "cmd2" in captured.out

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
