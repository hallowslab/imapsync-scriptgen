from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class ImapSyncCommand:
    argv: List[str]  # may contain secrets (runtime-only)
    redacted_argv: List[str]  # never contains secrets
    logfile: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Returns the redacted command as a string for logging."""
        return " ".join(self.redacted_argv)

    def to_shell_string(self) -> str:
        """Returns the full command as a string for shell execution (use with caution)."""
        return " ".join(self.argv)


@dataclass(frozen=True)
class ImapSyncSpec:
    host1: str
    user1: str
    pass1_ref: str
    host2: str
    user2: str
    pass2_ref: str
    logfile: str
    extra_args: Optional[str] = None
    logdir: str = "/var/log/pymap"
