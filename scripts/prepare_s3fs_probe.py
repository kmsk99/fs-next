"""Adapt an unpacked fs-s3fs 1.1.1 source tree for a local migration probe.

Only dependency metadata and the local version label change. This is not an
upstream release and must not be uploaded to a public package index.
"""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    source = parser.parse_args().source
    setup = source / "setup.py"
    version = source / "fs_s3fs" / "_version.py"
    setup_text = setup.read_text(encoding="utf-8")
    version_text = version.read_text(encoding="utf-8")
    if (
        setup_text.count('"fs~=2.4"') != 1
        or version_text.strip() != '__version__ = "1.1.1"'
    ):
        raise SystemExit("Expected an unmodified fs-s3fs 1.1.1 source tree")
    setup.write_text(
        setup_text.replace('"fs~=2.4"', '"fs-next>=0.1.0a1,<0.2"'),
        encoding="utf-8",
    )
    version.write_text('__version__ = "1.1.1+fsnext.1"\n', encoding="utf-8")
    print("Prepared local fs-s3fs 1.1.1+fsnext.1 migration probe")


if __name__ == "__main__":
    main()
