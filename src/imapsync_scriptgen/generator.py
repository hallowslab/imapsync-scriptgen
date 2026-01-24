import shlex
import logging
from typing import List, Set, Dict

from .models import ImapSyncCommand, ImapSyncSpec
from .utils import DomainHelper

logger = logging.getLogger("pymap_core")


def redact_argv(argv: List[str], passwords: Set[str]) -> List[str]:
    """
    Returns a new argv list where any string in passwords is replaced by '********'.
    This is the centralized redaction logic.
    """
    redacted = []
    for arg in argv:
        if arg in passwords:
            redacted.append("********")
        else:
            redacted.append(arg)
    return redacted


def generate(spec: ImapSyncSpec, runtime_secrets: Dict[str, str]) -> ImapSyncCommand:
    """
    Library-Facing API (Safe)
    - uses credential references from spec
    - injects secrets only from runtime_secrets
    - never parses credential files
    - never writes shell scripts
    """
    pass1 = runtime_secrets.get(spec.pass1_ref)
    pass2 = runtime_secrets.get(spec.pass2_ref)

    if pass1 is None or pass2 is None:
        raise ValueError(
            f"Missing runtime values for references: "
            f"{spec.pass1_ref if pass1 is None else ''} "
            f"{spec.pass2_ref if pass2 is None else ''}".strip()
        )

    argv = [
        "imapsync",
        "--host1",
        spec.host1,
        "--user1",
        spec.user1,
        "--password1",
        pass1,
        "--host2",
        spec.host2,
        "--user2",
        spec.user2,
        "--password2",
        pass2,
        "--log",
        "--logdir",
        spec.logdir,
        "--logfile",
        spec.logfile,
        "--addheader",
    ]

    if spec.extra_args:
        argv.extend(shlex.split(spec.extra_args))

    redacted = redact_argv(argv, {pass1, pass2})

    domains_str = DomainHelper.domains_as_string(spec)

    return ImapSyncCommand(
        argv=argv,
        redacted_argv=redacted,
        logfile=spec.logfile,
        metadata={
            "user1": spec.user1,
            "user2": spec.user2,
            "host1": spec.host1,
            "host2": spec.host2,
            "domains": domains_str,
        },
    )
