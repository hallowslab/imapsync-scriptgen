import pytest
from src.imapsync_scriptgen.generator import generate, redact_argv
from src.imapsync_scriptgen.models import ImapSyncSpec, ImapSyncCommand


# Test redact_argv
def test_redact_argv():
    argv = ["imapsync", "--pass", "secret123", "--other", "data"]
    passwords = {"secret123"}
    redacted = redact_argv(argv, passwords)
    assert "secret123" not in redacted
    assert "********" in redacted
    assert "--other" in redacted


# Test generate (Safe Library API)
def test_generate_basic():
    spec = ImapSyncSpec(
        host1="host1.tld",
        user1="user1",
        pass1_ref="ref1",
        host2="host2.tld",
        user2="user2",
        pass2_ref="ref2",
        logfile="sync.log",
    )
    runtime_secrets = {"ref1": "pass1", "ref2": "pass2"}

    cmd = generate(spec, runtime_secrets)

    assert isinstance(cmd, ImapSyncCommand)
    assert "--password1" in cmd.argv
    assert "pass1" in cmd.argv
    assert "pass2" in cmd.argv

    # Verify Redaction
    assert "pass1" not in cmd.redacted_argv
    assert "pass2" not in cmd.redacted_argv
    assert "********" in cmd.redacted_argv

    assert cmd.logfile == "sync.log"
    assert cmd.metadata["user1"] == "user1"


def test_generate_missing_secret():
    spec = ImapSyncSpec(
        host1="h1",
        user1="u1",
        pass1_ref="ref1",
        host2="h2",
        user2="u2",
        pass2_ref="ref2",
        logfile="log",
    )
    with pytest.raises(ValueError, match="Missing runtime values"):
        generate(spec, {"ref1": "only_one"})


def test_generate_extra_args():
    spec = ImapSyncSpec(
        host1="h1",
        user1="u1",
        pass1_ref="ref1",
        host2="h2",
        user2="u2",
        pass2_ref="ref2",
        logfile="log",
        extra_args="--skipsize --maxsize 100",
    )
    cmd = generate(spec, {"ref1": "p1", "ref2": "p2"})
    assert "--skipsize" in cmd.argv
    assert "--maxsize" in cmd.argv
    assert "100" in cmd.argv
