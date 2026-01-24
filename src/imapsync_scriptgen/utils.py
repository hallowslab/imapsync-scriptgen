import re
import logging
from dataclasses import dataclass, field
from typing import Optional, TypeVar, List, Iterable, Generator, Dict

from .models import ImapSyncSpec

logger = logging.getLogger("pymap_core.utils")

T = TypeVar("T")


@dataclass
class GeneratorConfig:
    host1: str
    host2: str
    extra_args: str = ""
    destination: str = "sync"
    split: int = 30
    dry_run: bool = False
    logdir: str = "/var/log/pymap"
    additional_known_hosts: Optional[List[List[str]]] = field(default_factory=list)
    config: Optional[Dict] = field(default_factory=dict)


class DomainHelper:
    """
    Safe helper for domain-related operations.
    Works directly with ImapSyncSpec; no plaintext passwords required.
    """

    DOMAIN_IDENTIFIER = re.compile(r"^.+@(?P<domain>[^\s]+)")

    @classmethod
    def match_domain(cls, email: str) -> Optional[str]:
        """
        Extracts domain from a single email string.
        Returns None if no valid domain is found.
        """
        match = cls.DOMAIN_IDENTIFIER.match(email)
        if match:
            return match.group("domain")
        return None

    @classmethod
    def extract_domains_from_spec(cls, spec: ImapSyncSpec) -> List[str]:
        """
        Returns a list of unique domains from the usernames in the spec.
        """
        domains = []
        for user in (spec.user1, spec.user2):
            domain = cls.match_domain(user)
            if domain and domain not in domains:
                domains.append(domain)
        return domains

    @classmethod
    def domains_as_string(cls, spec: ImapSyncSpec) -> str:
        """
        Returns a comma-separated string of domains.
        """
        return ",".join(cls.extract_domains_from_spec(spec))


def verify_host(hostname: str, known_hosts: Optional[List[List[str]]] = None) -> str:
    """
    Checks if a hostname matches any regex pattern in a list and appends a string if matched.

    If the hostname matches a pattern in the provided known_hosts list, returns the hostname
    concatenated with the corresponding append string. If no patterns match or known_hosts is
    not provided, returns the original hostname.
    """
    logger.debug("Verifying hostname: %s", hostname)

    if known_hosts:
        for pattern, append_str in known_hosts:
            try:
                has_match = re.match(pattern, hostname)
                if has_match:
                    logger.debug("Matched hostname pattern: %s", pattern)
                    return f"{hostname}{append_str}"
            except Exception as e:
                logger.warning("Regex error in pattern %s: %s", pattern, e)
                continue

    logger.debug("No matches found for hostname: %s", hostname)
    return hostname


def batch_lines(lines: Iterable[T], batch_size: int) -> Generator[List[T], None, None]:
    """
    Yield lists of lines, each of length batch_size (except possibly the last one).
    """
    buffer: List[T] = []
    for line in lines:
        buffer.append(line)
        if len(buffer) >= batch_size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer
