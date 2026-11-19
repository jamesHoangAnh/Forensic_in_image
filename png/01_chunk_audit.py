"""Audit PNG chunk boundaries, CRCs, ordering, and trailing data."""

from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
KNOWN_CRITICAL_CHUNKS = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}


def audit_png(input_path: Path, output_dir: Path) -> dict[str, object]:
    data = input_path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Input does not have a PNG signature")

    chunks: list[dict[str, object]] = []
    issues: list[str] = []
    offset = len(PNG_SIGNATURE)
    saw_iend = False

    while offset < len(data):
        if len(data) - offset < 12:
            issues.append("Truncated chunk header or CRC at end of file")
            break

        length = struct.unpack_from(">I", data, offset)[0]
        chunk_type = data[offset + 4 : offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        chunk_end = payload_end + 4
        if chunk_end > len(data):
            issues.append(f"Truncated {chunk_type.decode('ascii', 'replace')} chunk")
            break

        expected_crc = struct.unpack_from(">I", data, payload_end)[0]
        actual_crc = zlib.crc32(data[offset + 4 : payload_end]) & 0xFFFFFFFF
        chunk_name = chunk_type.decode("ascii", "replace")
        chunks.append(
            {
                "type": chunk_name,
                "length": length,
                "crc_valid": expected_crc == actual_crc,
            }
        )
        if expected_crc != actual_crc:
            issues.append(f"CRC mismatch in {chunk_name}")
        if not chunks[:-1] and chunk_type != b"IHDR":
            issues.append("IHDR is not the first chunk")
        if chunk_type == b"IHDR" and (len(chunks) != 1 or length != 13):
            issues.append("IHDR is duplicated or has an invalid length")
        if chunk_type == b"IEND":
            if length != 0:
                issues.append("IEND must have zero data length")
            saw_iend = True
            offset = chunk_end
            break
        if chunk_type[0] & 0x20 == 0 and chunk_type not in KNOWN_CRITICAL_CHUNKS:
            issues.append(f"Unknown critical chunk {chunk_name}")
        offset = chunk_end

    chunk_types = [str(chunk["type"]) for chunk in chunks]
    if chunk_types.count("IHDR") != 1:
        issues.append("PNG must contain exactly one IHDR chunk")
    if "IDAT" not in chunk_types:
        issues.append("PNG has no IDAT chunk")
    if not saw_iend:
        issues.append("PNG has no complete IEND chunk")
    if saw_iend and offset < len(data):
        issues.append("Trailing bytes after IEND")

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{input_path.stem}_chunk_audit.json"
    report: dict[str, object] = {
        "input": str(input_path),
        "format": "PNG",
        "file_size_bytes": len(data),
        "chunks": chunks,
        "trailing_bytes_after_iend": len(data) - offset if saw_iend else None,
        "structural_issues": issues,
        "report": str(report_path),
        "interpretation": (
            "A valid structure and CRC indicate internal consistency only; they "
            "do not prove image authenticity or rule out editing."
        ),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Path to a PNG image")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
    )
    args = parser.parse_args()
    report = audit_png(args.image, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
