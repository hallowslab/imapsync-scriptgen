"""Python package for generating imapsync scripts.

This module exposes the class `ScriptGenerator` and any helper utilities.

Example:

from imapsync_scriptgen import ScriptGenerator
from imapsync_scriptgen.utils import GeneratorConfig
cfg = GeneratorConfig(
        host1="imap.source.tld",
        host2="imap.dest.tld",
        split=2,
        destination="sync",
        dry_run=False,
    )
gen = ScriptGenerator(cfg)
commands = gen.process_strings(['user1@domain.com pass1 user2@domain.com pass2'])
# commands will be a list of ImapSyncCommand objects
print(commands[0].redacted_argv)
"""

from .generator import generate as generate
from .models import ImapSyncCommand as ImapSyncCommand, ImapSyncSpec as ImapSyncSpec
