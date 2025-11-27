# imapsync-scriptgen

Generate `imapsync` command scripts from user credential lists.

![Tests Status](./tests-badge.svg?dummy=8484744)
![Coverage Status](./coverage-badge.svg?dummy=8484744)
![Flake8 Status](./flake8-badge.svg?dummy=8484744)

---

## Overview

`imapsync-scriptgen` is a Python module and CLI tool that takes lists of email credentials and generates `imapsync` commands for synchronizing mailboxes between two hosts. It supports:

- Single or multiple user/password pairs per line
- Customizable batch sizes and output files
- Dry-run mode for testing

---

## Features

- Python module for programmatic usage
- Command-line interface (`imapsync-scriptgen`) for file-based input
- Configurable logging directory and output file prefixes
- Batch output for large user lists

---

## Installation

### Development mode

Clone the repository and install in editable mode:

```sh
git clone https://github.com/hallowslab/imapsync-scriptgen.git
cd imapsync-scriptgen
pip install -e .
```

### From GitHub as a dependency

```sh
pip install "imapsync-scriptgen @ git+https://github.com/hallowslab/imapsync-scriptgen.git"
```

---

## Usage

### CLI

```sh
imapsync-scriptgen input_file.txt --host1 mail.source.com --host2 mail.dest.com --split 30 --extra "--ssl1 --ssl2" --dry-run
```

Options:

- `input_file` — path to the input file containing email credentials
- `--host1` — source host
- `--host2` — destination host
- `--split` — number of lines per output file
- `--extra` — additional arguments to append to each command
- `--dry-run` — print commands instead of writing files

---

### Python Module

```python
from imapsync_scriptgen.generator import ScriptGenerator
from imapsync_scriptgen.utils import GeneratorConfig

cfg = GeneratorConfig(
    host1="mail.source.com",
    host2="mail.dest.com",
    extra_args="--ssl1 --ssl2",
    split=30,
    dry_run=True
)

gen = ScriptGenerator(cfg)
lines = ["user1@example.com password1", "user2@example.com password2"]
scripts = list(gen.process_strings(lines))

for cmd in scripts:
    print(cmd)
```

---

## Development

- Run tests:

`poetry run task test`

- Check coverage:
`poetry run task coverage`

- Lint with:

`poetry run task all`

### ran in order

```sh
black . && ruff check
mypy -p src.imapsync_scriptgen
pytest --cov=src.imapsync_scriptgen --cov-report=term-missing
coverage html
```

---

## Contributing

Pull requests and issues are welcome! Please follow Python best practices and maintain test coverage.
