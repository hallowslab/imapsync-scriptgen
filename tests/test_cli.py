from src.imapsync_scriptgen.cli import main
from src.imapsync_scriptgen.models import ImapSyncCommand


def test_cli_runs(monkeypatch, tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("user@example.com pass\n")

    # Mock argv
    monkeypatch.setattr(
        "sys.argv",
        [
            "imapsync-gen",
            str(input_file),
            "--host1",
            "old.example.com",
            "--host2",
            "new.example.com",
            "--split",
            "1",
            "--dry-run",
        ],
    )

    # Mock ScriptGenerator to avoid side effects
    called = {}

    class DummyGen:
        def __init__(self, cfg):
            called["cfg"] = cfg

        def line_generator(self, fh):
            # Should return objects
            return [
                ImapSyncCommand(
                    argv=["imapsync", "arg1"],
                    redacted_argv=["imapsync", "arg1"],
                    logfile="log",
                )
            ]

        def write_output(self, lines):
            called["lines"] = lines

    monkeypatch.setattr("src.imapsync_scriptgen.cli.UnsafeScriptGenerator", DummyGen)

    main()

    assert called["cfg"].host1 == "old.example.com"
    assert called["cfg"].dry_run is True
    assert len(called["lines"]) == 1
    assert called["lines"][0].argv == ["imapsync", "arg1"]
