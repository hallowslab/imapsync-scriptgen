import argparse
from .cli_adapter import UnsafeScriptGenerator
from .utils import GeneratorConfig, batch_lines


def main():
    parser = argparse.ArgumentParser(description="Generate imapsync scripts")
    parser.add_argument("input_file")
    parser.add_argument("--host1", required=True)
    parser.add_argument("--host2", required=True)
    parser.add_argument("--split", type=int, default=30)
    parser.add_argument("--extra", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = GeneratorConfig(
        host1=args.host1,
        host2=args.host2,
        extra_args=args.extra,
        split=args.split,
        dry_run=args.dry_run,
    )

    generator = UnsafeScriptGenerator(cfg)

    with open(args.input_file) as fh:
        for lines_batch in batch_lines(generator.line_generator(fh), cfg.split):
            generator.write_output(lines_batch)


if __name__ == "__main__":
    main()
