"""Screen an image for exact duplicate grayscale blocks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def screen_copy_move(
    input_path: Path,
    output_dir: Path,
    block_size: int,
    stride: int,
    min_distance: int,
    max_blocks: int,
    min_texture_stddev: float,
) -> dict[str, object]:
    with Image.open(input_path) as image:
        gray = np.asarray(image.convert("L"), dtype=np.uint8)

    height, width = gray.shape
    if height < block_size or width < block_size:
        raise ValueError("Image dimensions must be at least the block size")

    y_positions = range(0, height - block_size + 1, stride)
    x_positions = range(0, width - block_size + 1, stride)
    block_count = len(y_positions) * len(x_positions)
    if block_count > max_blocks:
        raise ValueError(
            f"{block_count} blocks exceed --max-blocks={max_blocks}; "
            "increase --stride or analyze a smaller image"
        )

    locations: dict[bytes, list[tuple[int, int]]] = {}
    mask = np.zeros((height, width), dtype=np.uint8)
    duplicate_blocks = 0
    duplicate_pairs = 0
    low_texture_blocks_skipped = 0

    for y in y_positions:
        for x in x_positions:
            block = gray[y : y + block_size, x : x + block_size]
            if float(block.std()) < min_texture_stddev:
                low_texture_blocks_skipped += 1
                continue
            signature = block.tobytes()
            previous = locations.setdefault(signature, [])
            matched = [
                (prior_y, prior_x)
                for prior_y, prior_x in previous
                if max(abs(y - prior_y), abs(x - prior_x)) >= min_distance
            ]
            if matched:
                duplicate_blocks += 1
                duplicate_pairs += len(matched)
                mask[y : y + block_size, x : x + block_size] = 255
                for prior_y, prior_x in matched:
                    mask[
                        prior_y : prior_y + block_size,
                        prior_x : prior_x + block_size,
                    ] = 255
            if len(previous) < 16:
                previous.append((y, x))

    output_dir.mkdir(parents=True, exist_ok=True)
    mask_path = output_dir / f"{input_path.stem}_copy_move_mask.png"
    report_path = output_dir / f"{input_path.stem}_copy_move.json"
    Image.fromarray(mask).save(mask_path)

    report: dict[str, object] = {
        "input": str(input_path),
        "width": width,
        "height": height,
        "block_size": block_size,
        "stride": stride,
        "minimum_separation_pixels": min_distance,
        "minimum_texture_standard_deviation": min_texture_stddev,
        "blocks_examined": block_count,
        "low_texture_blocks_skipped": low_texture_blocks_skipped,
        "duplicate_blocks_marked": duplicate_blocks,
        "duplicate_block_pairs": duplicate_pairs,
        "mask": str(mask_path),
        "report": str(report_path),
        "interpretation": (
            "Exact grayscale block matches are candidate regions only. Repeated "
            "textures can produce false positives; transformed or resampled copies "
            "may be missed. This is not a forensic verdict."
        ),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Path to an image")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
    )
    parser.add_argument("--block-size", type=int, default=8)
    parser.add_argument("--stride", type=int, default=4)
    parser.add_argument("--min-distance", type=int, default=16)
    parser.add_argument("--max-blocks", type=int, default=1_000_000)
    parser.add_argument("--min-texture-stddev", type=float, default=2.0)
    args = parser.parse_args()
    if min(args.block_size, args.stride, args.min_distance, args.max_blocks) <= 0:
        parser.error("block size, stride, minimum distance, and block limit must be positive")
    if args.min_texture_stddev < 0:
        parser.error("--min-texture-stddev cannot be negative")

    report = screen_copy_move(
        args.image,
        args.output_dir,
        args.block_size,
        args.stride,
        args.min_distance,
        args.max_blocks,
        args.min_texture_stddev,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
