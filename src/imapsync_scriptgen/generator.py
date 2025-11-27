import re
import os
from typing import Generator, Iterable, List, Optional
import logging
from pathlib import Path

from .utils import verify_host, batch_lines, GeneratorConfig
from .parser import parse_credentials

logger = logging.getLogger("pymap_core")


class ScriptGenerator:
    # RFC / DNS constraints for domains
    # 1. Domain consists of labels separated by dots
    # 2. Each label: 1–63 characters, letters, digits, or -
    # 3. Label cannot start or end with -
    # 4. Entire domain ≤ 255 characters
    # 5. TLD: at least 2 characters
    # 6. Subdomains allowed, IDN optional (if needed)

    # Extract domain part after @, allow subdomains, optional trailing dot
    # Leaves TLD/length enforcement to a separate validation if needed
    DOMAIN_IDENTIFIER = re.compile(r"^.+@(?P<domain>[^\s]+)")

    def __init__(self, cfg: GeneratorConfig) -> None:
        """
        Initializes a ScriptGenerator instance for generating synchronization scripts.

        Args:
            host1: The source host name or address.
            host2: The destination host name or address.
            extra_args: Additional arguments to append to generated commands.
            **kwargs: Optional configuration parameters, including:
                - config: Dictionary of configuration options.
                - additional_known_hosts: List of additional known host patterns.
                - destination: Output filename prefix.
                - split: Number of lines per output file.
                - dry_run: If True, disables file writing.
                - pymap_logdir: Directory for log files.

        The constructor verifies hostnames, sets up output and logging parameters,
            and prepares internal state for script generation.
        """
        self.cfg = cfg
        self.config = cfg.config
        self.additional_known_hosts = cfg.additional_known_hosts
        self.host1 = verify_host(cfg.host1, self.get_known_hosts())
        self.host2 = verify_host(cfg.host2, self.get_known_hosts())
        self.extra_args = cfg.extra_args
        self.dest = cfg.destination
        self.line_count = cfg.split
        self.dry_run = cfg.dry_run
        self.file_count: int = 0
        # self.domains: List[str] = []
        # STATIC VARIABLES
        self.LOGDIR: str = (
            "/var/log/pymap"
            if self.config is None
            else self.config.get("LOGDIR", "/var/log/pymap")
        )
        self.FORMAT_STRING: str = (
            "imapsync --host1 {} --user1 {} --password1 '{}'"
            + " --host2 {}  --user2 {} --password2 '{}'"
            + " --log --logdir="
            + self.LOGDIR
            + " --logfile={} --addheader"
        )

    def match_domain(self, domain: str) -> Optional[str]:
        """
        Uses the regex DOMAIN_IDENTIFIER and tries to match it to the string,
            returns the match or None
        """
        has_match = re.match(self.DOMAIN_IDENTIFIER, domain)
        if has_match:
            return has_match.group("domain")
        return None

    def extract_domains_from_credentials(self, line: str) -> List[str]:
        "Return domains only from usernames, ignoring passwords."
        try:
            user1, _, user2, _ = parse_credentials(line)
        except ValueError:
            return []

        domains = []
        for user in (user1, user2):
            domain = self.match_domain(user)
            if domain:
                domains.append(domain)
        return domains

    def get_known_hosts(self) -> Optional[List[List[str]]]:
        """
        Returns the list of host regex patterns for host verification.

        If additional known hosts are provided, returns them.
            Otherwise, returns the hosts from the configuration.
        """
        config_hosts: Optional[List[List[str]]] = (
            None if self.config is None else self.config.get("HOSTS", None)
        )
        if self.additional_known_hosts:
            return self.additional_known_hosts
        return config_hosts

    def process_file(self, fpath: str) -> None:
        """
        Processes an input file, generating and writing script lines to output files in batches.
        """
        if not fpath or not os.path.isfile(fpath):
            raise ValueError(f"File path was not supplied or invalid: {fpath}")

        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                # line_generator already yields processed script lines
                for lines_batch in batch_lines(
                    self.line_generator(fh), self.line_count
                ):
                    self.write_output(lines_batch)

        except Exception as e:
            logger.critical("Unhandled exception: %s", str(e), exc_info=True)
            raise

    def process_strings(self, strings: List[str]) -> List[str]:
        """
        Processes data from a list with strings, uses self.line_generator to create the scripts,
            returns a list with all scripts
        """
        # logger.debug("STRINGS:\n%s", type(strings))
        scripts = [x for x in self.line_generator(strings) if len(x) > 0]
        return scripts

    # processes input -> yields str
    def line_generator(
        self, uinput: Iterable[str], domain_collector: Optional[set] = None
    ) -> Generator[str, None, None]:
        """
        Generates script lines from input strings using process_line,
            appending extra arguments if set.

        Iterates over each non-empty input line,
            if domain_collector set is provided append extracted domains,
            processes the line into a script command
        """
        new_line: Optional[str] = ""
        for line in uinput:
            if line and len(line) > 1:
                if domain_collector is not None:
                    # Check for domains
                    domain_collector.update(self.extract_domains_from_credentials(line))
                # Process line
                new_line = self.process_line(line)
                if new_line:
                    yield new_line

    def process_line(self, line: str) -> Optional[str]:
        try:
            user1, pass1, user2, pass2 = parse_credentials(line)
        except ValueError as e:
            logger.warning(str(e))
            return None

        # Generate final command
        return self.make_command(user1, pass1, user2, pass2)

    def make_command(
        self, user1: str, password1: str, user2: str, password2: str
    ) -> str:
        """
        Generates a single imapsync command string for the given credentials.
        """
        logfile = f"{self.host1}__{self.host2}__{user1}--{user2}.log"
        cmd = (
            f"imapsync --host1 {self.host1} --user1 {user1} --password1 '{password1}' "
            f"--host2 {self.host2} --user2 {user2} --password2 '{password2}' "
            f"--log --logdir={self.LOGDIR} --logfile={logfile} --addheader"
        )

        if self.extra_args:
            cmd += f" {self.extra_args}"

        return cmd

    def write_output(self, lines: List[str]) -> None:
        """
        Writes a batch of script lines to an output file.

        if self.dry_run is True, prints lines to stdout instead of writing.
        """
        dest_file = Path(f"{self.dest}_{self.file_count}.sh")

        if self.dry_run:
            print(f"# Dry-run: would write {len(lines)} lines to {dest_file}")
            for line in lines:
                print(line)
        else:
            lines_to_write = [line + "\n" for line in lines]
            dest_file.write_text("".join(lines_to_write), encoding="utf-8")
            logger.debug("Wrote %d lines to %s", len(lines), dest_file)

        self.file_count += 1
