from src.imapsync_scriptgen.cli import main


def test_cli_runs(monkeypatch, tmp_path):
    input_file = tmp_path / "input.txt"
    input_file.write_text("user@example.com;pass\n")

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
            return ["user@example.com pass"]

        def write_output(self, lines):
            called["lines"] = lines

    monkeypatch.setattr("src.imapsync_scriptgen.cli.ScriptGenerator", DummyGen)

    main()

    assert called["cfg"].host1 == "old.example.com"
    assert called["cfg"].dry_run is True
    assert called["lines"] == ["user@example.com pass"]
