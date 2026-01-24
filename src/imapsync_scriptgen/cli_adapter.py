import os
import logging
from typing import List, Optional, Iterable, Generator
from pathlib import Path

from .generator import generate
from .utils import verify_host, batch_lines, GeneratorConfig
from .parser import parse_credentials
from .models import ImapSyncCommand, ImapSyncSpec

logger = logging.getLogger("pymap_core.cli")


class UnsafeScriptGenerator:
    """
    EXPLICITLY UNSAFE Adapter for CLI usage.
    This class handles plaintext passwords and writes .sh files.
    """

    def __init__(self, cfg: GeneratorConfig) -> None:
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
        self.LOGDIR: str = (
            "/var/log/pymap"
            if self.config is None
            else self.config.get("LOGDIR", "/var/log/pymap")
        )

    def get_known_hosts(self) -> Optional[List[List[str]]]:
        config_hosts: Optional[List[List[str]]] = (
            None if self.config is None else self.config.get("HOSTS", None)
        )
        if self.additional_known_hosts:
            return self.additional_known_hosts
        return config_hosts

    def process_file(self, fpath: str) -> None:
        if not fpath or not os.path.isfile(fpath):
            raise ValueError(f"File path was not supplied or invalid: {fpath}")

        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                for lines_batch in batch_lines(
                    self.line_generator(fh), self.line_count
                ):
                    self.write_output(lines_batch)
        except Exception as e:
            logger.critical("Unhandled exception: %s", str(e), exc_info=True)
            raise

    def line_generator(
        self, uinput: Iterable[str]
    ) -> Generator[ImapSyncCommand, None, None]:
        for line in uinput:
            if line and len(line) > 1:
                cmd = self.process_line(line)
                if cmd:
                    yield cmd

    def process_line(self, line: str) -> Optional[ImapSyncCommand]:
        try:
            user1, pass1, user2, pass2 = parse_credentials(line)
        except ValueError as e:
            logger.warning(str(e))
            return None

        logfile = f"{self.host1}__{self.host2}__{user1}--{user2}.log"
        spec = ImapSyncSpec(
            host1=self.host1,
            user1=user1,
            pass1_ref="pw1",
            host2=self.host2,
            user2=user2,
            pass2_ref="pw2",
            logfile=logfile,
            extra_args=self.extra_args,
            logdir=self.LOGDIR,
        )
        return generate(spec, runtime_secrets={"pw1": pass1, "pw2": pass2})

    def write_output(self, commands: List[ImapSyncCommand]) -> None:
        dest_file = Path(f"{self.dest}_{self.file_count}.sh")
        if self.dry_run:
            print(f"# Dry-run: would write {len(commands)} lines to {dest_file}")
            for cmd in commands:
                print(str(cmd))
        else:
            lines_to_write = [cmd.to_shell_string() + "\n" for cmd in commands]
            dest_file.write_text("".join(lines_to_write), encoding="utf-8")
        self.file_count += 1
