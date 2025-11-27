from src.imapsync_scriptgen.utils import GeneratorConfig, verify_host, batch_lines


# GeneratorConfig Tests
def test_generator_config_defaults():
    cfg = GeneratorConfig(host1="a", host2="b")

    assert cfg.host1 == "a"
    assert cfg.host2 == "b"
    assert cfg.extra_args == ""
    assert cfg.destination == "sync"
    assert cfg.split == 30
    assert cfg.dry_run is False
    assert cfg.logdir == "/var/log/pymap"
    assert cfg.additional_known_hosts == []
    assert cfg.config == {}


def test_generator_config_override_values():
    cfg = GeneratorConfig(
        host1="source",
        host2="dest",
        extra_args="--ssl",
        destination="out",
        split=5,
        dry_run=True,
        logdir="/tmp/logs",
        additional_known_hosts=[["foo.*", "_X"]],
        config={"LOGDIR": "/custom"},
    )

    assert cfg.extra_args == "--ssl"
    assert cfg.destination == "out"
    assert cfg.split == 5
    assert cfg.dry_run is True
    assert cfg.logdir == "/tmp/logs"
    assert cfg.additional_known_hosts == [["foo.*", "_X"]]
    assert cfg.config == {"LOGDIR": "/custom"}


# verify_host Tests
def test_verify_host_no_known_hosts_returns_original():
    assert verify_host("mail.example.com", None) == "mail.example.com"
    assert verify_host("mail.example.com", []) == "mail.example.com"


def test_verify_host_pattern_matches():
    known = [
        [r"mail\.example\.com", "_A"],
        [r"imap\.example\.org", "_B"],
    ]

    assert verify_host("mail.example.com", known) == "mail.example.com_A"
    assert verify_host("imap.example.org", known) == "imap.example.org_B"


def test_verify_host_pattern_no_match_returns_original():
    known = [[r"foo.*", "_X"]]
    assert verify_host("bar.example.com", known) == "bar.example.com"


def test_verify_host_regex_error_is_ignored(caplog):
    # invalid regex
    known = [["[invalid", "_X"], ["mail.*", "_OK"]]

    with caplog.at_level("WARNING"):
        result = verify_host("mail.example.com", known)

    # Should ignore invalid pattern and match the second one
    assert result == "mail.example.com_OK"

    # Should log a warning about the invalid regex pattern
    assert any("Regex error in pattern" in rec.message for rec in caplog.records)


# batch_lines Tests
def test_batch_lines_exact_batches():
    items = ["a", "b", "c", "d"]
    batches = list(batch_lines(items, 2))
    assert batches == [["a", "b"], ["c", "d"]]


def test_batch_lines_with_remainder():
    items = ["a", "b", "c"]
    batches = list(batch_lines(items, 2))
    assert batches == [["a", "b"], ["c"]]


def test_batch_lines_single_batch():
    assert list(batch_lines(["x"], 10)) == [["x"]]


def test_batch_lines_empty_iterable():
    assert list(batch_lines([], 3)) == []


def test_batch_lines_batch_size_one():
    items = ["a", "b", "c"]
    batches = list(batch_lines(items, 1))
    assert batches == [["a"], ["b"], ["c"]]


def test_batch_lines_large_batch_size():
    items = ["a", "b"]
    batches = list(batch_lines(items, 100))
    assert batches == [["a", "b"]]
