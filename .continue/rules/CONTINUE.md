# imapsync-scriptgen Project Guide

## Project Overview

`imapsync-scriptgen` is a Python module and CLI tool that generates `imapsync` command scripts from user credential lists. The tool enables automated mailbox synchronization between two email hosts by parsing input files containing user credentials and producing batched, configurable imapsync commands.

Key technologies:

- Python 3
- argparse for CLI interface
- dataclasses and typing for configuration
- Regular expressions for parsing and validation
- Logging and file I/O operations

High-level architecture:

1. Input parsing: Reads credential lists from files or strings
2. Configuration: Uses `GeneratorConfig` to define host settings and output parameters
3. Command generation: Processes credentials into imapsync commands
4. Output: Creates batched shell scripts with configurable splitting and dry-run modes

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip or poetry for Python package management
- `imapsync` command-line tool installed on the system (required for script execution)

### Installation

**Development mode** (recommended for local development):

```sh
git clone https://github.com/hallowslab/imapsync-scriptgen.git
cd imapsync-scriptgen
pip install -e .
```

**As a dependency** (for integration into other projects):

```sh
pip install "imapsync-scriptgen @ git+https://github.com/hallowslab/imapsync-scriptgen.git"
```

### Basic Usage

**CLI Usage**:

```sh
imapsync-scriptgen input_file.txt --host1 mail.source.com --host2 mail.dest.com --split 30 --extra "--ssl1 --ssl2" --dry-run
```

**Python Module Usage**:

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

### Running Tests

```sh
poetry run task test
poetry run task coverage
poetry run task all  # runs black, ruff check, mypy, and pytest
```

## Project Structure

- `src/imapsync_scriptgen/`: Main source code
  - `__init__.py`: Exposes `ScriptGenerator` class and utilities
  - `utils.py`: Configuration and utility functions (dataclasses, regex patterns, batch processing)
  - `parser.py`: Parses credential lines into user/password pairs
  - `generator.py`: Core logic for command generation and file output
  - `cli.py`: Command-line interface with argparse

- `tests/`: Test suite for functionality validation
- `poetry.toml`: Project dependencies and configuration
- `README.md`: Project documentation and usage instructions

## Development Workflow

### Coding Standards

- Follow Python PEP 8 style guidelines
- Use type hints and dataclasses for configuration
- Maintain consistent formatting with `black`
- Include comprehensive type annotations and docstrings

### Testing Approach

- Unit tests for core functionality (parser, generator)
- Integration tests for CLI and module usage
- Coverage validation via `pytest --cov=src.imapsync_scriptgen`

### Build and Deployment

- Development: Install in editable mode using `pip install -e .`
- Production: Install via pip with `pip install imapsync-scriptgen`

### Contribution Guidelines

- Follow Python best practices
- Maintain test coverage (target ≥ 80%)
- Submit pull requests with clear descriptions
- Include tests for new features

## Key Concepts

- **GeneratorConfig**: Configuration object defining host settings, batch size, and output options
- **ScriptGenerator**: Core class that processes credentials and generates imapsync commands
- **Domain Extraction**: Validates email domains against RFC standards and extracts domains for logging
- **Batch Processing**: Splits large input files into manageable batches to avoid memory issues
- **Dry-Run Mode**: Simulates command generation without writing output files

## Common Tasks

### Generate Scripts from File

1. Prepare a file with one credential per line (e.g., `credentials.txt`):

   ```ssv
   user1@example.com password1
   user2@example.com password2
   ```

2. Run the CLI:

   ```sh
   imapsync-scriptgen credentials.txt --host1 mail.source.com --host2 mail.dest.com --split 50
   ```

3. Output will be written to files like `sync_0.sh`, `sync_1.sh`, etc.

### Generate Scripts Programmatically

```python
from imapsync_scriptgen.generator import ScriptGenerator
from imapsync_scriptgen.utils import GeneratorConfig

cfg = GeneratorConfig(
    host1="mail.source.com",
    host2="mail.dest.com",
    split=20,
    dry_run=True
)

gen = ScriptGenerator(cfg)
scripts = gen.process_strings(["user1@example.com pass1", "user2@example.com pass2"])
for script in scripts:
    print(script)
```

### Debugging

- Use `--dry-run` to verify commands without writing files
- Check logs in `/var/log/pymap` directory (configurable via `LOGDIR`)
- Validate email domain formats using RFC standards

## Troubleshooting

### Common Issues

- **Missing imapsync command**: Ensure `imapsync` is installed on the system
- **Invalid credentials**: Verify email addresses and passwords are correctly formatted
- **File not found**: Confirm input file path exists and is readable
- **Permission errors**: Ensure write permissions for output directory

### Debug Tips

- Use `--dry-run` to preview generated commands before execution
- Check `LOGDIR` configuration for log file paths
- Validate input format with a simple test script
- Review regex patterns in `parser.py` for domain matching

## References

- [imapsync official documentation](https://imapsync.lamiral.info/#doc)
- [Python PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [RFC 1034-1035: Domain Name System](https://tools.ietf.org/html/rfc1034)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- [Python argparse documentation](https://docs.python.org/3/library/argparse.html)