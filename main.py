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


# Magic-byte prefixes for the two image formats the grader accepts.
# The file is delivered under the name ``entry.png`` regardless of
# which of these formats it actually contains.
PNG_MAGIC = b"\x89PNG"
JPEG_MAGIC = b"\xff\xd8\xff"

# The grader rejects outputs larger than 1 MiB.
MAX_OUTPUT_BYTES = 1_048_576


def validate_image_bytes(path: Path) -> int:
    """Validate the magic bytes and size of the image at ``path``.

    Returns the file size in bytes. Raises ``ValueError`` if the
    file does not start with a PNG or JPEG signature, or if it
    exceeds the grader's size limit.
    """
    size = path.stat().st_size
    if size > MAX_OUTPUT_BYTES:
        raise ValueError(
            f"{path} is {size} bytes, over the {MAX_OUTPUT_BYTES}-byte limit"
        )
    with path.open("rb") as handle:
        header = handle.read(4)
    if not (header.startswith(PNG_MAGIC) or header.startswith(JPEG_MAGIC)):
        raise ValueError(
            f"{path} has unrecognised magic bytes {header!r}; "
            "expected a PNG or JPEG image"
        )
    return size


def main() -> int:
    source = locate_source()
    source_size = validate_image_bytes(source)

    output_dir = resolve_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    destination = output_dir / "entry.png"
    shutil.copyfile(source, destination)

    # Post-copy verification: the delivered file must still be a
    # valid-format image and exactly the same size as the source,
    # so a truncated or corrupted copy can never pass silently.
    destination_size = validate_image_bytes(destination)
    if destination_size != source_size:
        raise IOError(
            f"copy verification failed: source is {source_size} bytes "
            f"but destination is {destination_size} bytes"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
