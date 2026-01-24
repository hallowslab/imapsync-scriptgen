import pytest
from src.imapsync_scriptgen.cli_adapter import UnsafeScriptGenerator
from src.imapsync_scriptgen.utils import GeneratorConfig


@pytest.fixture
def cfg():
    return GeneratorConfig(
        host1="imap.source.tld",
        host2="imap.dest.tld",
        split=2,  # small batch size for testing
        destination="sync",
        dry_run=False,
    )


@pytest.fixture
def gen(cfg):
    return UnsafeScriptGenerator(cfg)
