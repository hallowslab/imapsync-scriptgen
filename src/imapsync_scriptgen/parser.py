import re
from typing import Tuple


def parse_credentials(line: str) -> Tuple[str, str, str, str]:
    """
    Parses a line into (user1, pass1, user2, pass2).

    Supports:
        user pass
        user pass user2 pass2
    Tabs & multi-spaces are automatically normalized.
    """
    # Normalize whitespace
    normalized = re.sub(r"\s+", " ", line.strip())
    parts = normalized.split(" ")

    if len(parts) < 2:
        raise ValueError(f"Cannot parse credentials from line: {line!r}")

    user1, p1 = parts[0], parts[1]

    # Default: user2/p2 = user1/p1
    if len(parts) >= 4:
        user2, p2 = parts[2], parts[3]
    else:
        user2, p2 = user1, p1

    return user1, p1, user2, p2
