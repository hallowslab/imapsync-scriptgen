import pytest
from src.imapsync_scriptgen.parser import parse_credentials


@pytest.mark.parametrize(
    "input_line, expected",
    [
        # Basic two-field
        (
            "john@email.com Password123!",
            ("john@email.com", "Password123!", "john@email.com", "Password123!"),
        ),
        # Tabs, multispaces
        (
            "   jeff@jeffmail.com\t   pass123   ",
            ("jeff@jeffmail.com", "pass123", "jeff@jeffmail.com", "pass123"),
        ),
        # Full four-field
        ("u1 p1 u2 p2", ("u1", "p1", "u2", "p2")),
        # Extra fields should be ignored
        ("u1 p1 u2 p2 uno dos tres catorze", ("u1", "p1", "u2", "p2")),
        # Leading/trailing whitespace
        (
            "\n   user1@email.com Pa$$w0rd!  \t",
            ("user1@email.com", "Pa$$w0rd!", "user1@email.com", "Pa$$w0rd!"),
        ),
    ],
)
def test_parse_credentials_valid(input_line, expected):
    assert parse_credentials(input_line) == expected


@pytest.mark.parametrize(
    "bad_input",
    [
        "",  # Empty string
        "   ",  # Just whitespace
        "u1",  # only 1 value
        "u1   ",  # still only one value
        "\t  u1",  # whitespace only after stripping
    ],
)
def test_parse_credentials_invalid(bad_input):
    with pytest.raises(ValueError):
        parse_credentials(bad_input)
