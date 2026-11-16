#!/usr/bin/env python3
"""Deliver the ai-excited-01 artwork byte for byte.

The competition entry is a single image: a colossal glowing manta ray
soaring over a tiny fishing boat at sunset. That image is shipped in
this repository as ``entry.png`` (a JPEG file, delivered under the
name ``entry.png`` as the grader requires).

This program's job is deliberately simple and deterministic:

1. Locate the shipped ``entry.png`` beside this script, falling back
   to ``/bot/entry.png`` (where the grader mounts the repository
   read-only).
2. Copy it byte-for-byte to ``entry.png`` inside the output
   directory, creating that directory if needed.

The output directory is taken from the ``MAKEFUN_OUTPUT_DIR``
environment variable when set, and defaults to ``/output``.

Because the program performs a pure byte copy of a fixed file, two
runs always produce byte-identical output. Only the Python standard
library is used, and no network access is required.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def locate_source() -> Path:
    """Return the path of the shipped artwork.

    Prefers ``entry.png`` beside this script; falls back to
    ``/bot/entry.png`` for the grader sandbox layout.
    """
    beside_script = Path(__file__).resolve().parent / "entry.png"
    if beside_script.is_file():
        return beside_script

    fallback = Path("/bot/entry.png")
    if fallback.is_file():
        return fallback

    raise FileNotFoundError(
        f"entry.png not found beside the script ({beside_script}) "
        f"or at the fallback location ({fallback})"
    )


def resolve_output_dir() -> Path:
    """Return the output directory from the environment or default."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if raw:
        return Path(raw)
    return Path("/output")


def main() -> int:
    source = locate_source()
    output_dir = resolve_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    destination = output_dir / "entry.png"
    shutil.copyfile(source, destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())
