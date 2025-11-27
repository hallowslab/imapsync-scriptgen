import logging
from dataclasses import dataclass, field
from typing import Optional, List, Iterable, Generator, Dict
import re

logger = logging.getLogger("pymap_core.utils")


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


def batch_lines(
    lines: Iterable[str], batch_size: int
) -> Generator[List[str], None, None]:
    """
    Yield lists of lines, each of length batch_size (except possibly the last one).
    """
    buffer: List[str] = []
    for line in lines:
        buffer.append(line)
        if len(buffer) >= batch_size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer
