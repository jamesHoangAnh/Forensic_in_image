"""Create a JPEG Error Level Analysis (ELA) visualization and JSON summary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops


def analyze_ela(
    input_path: Path, output_dir: Path, quality: int, display_scale: float
) -> dict[str, object]:
    with Image.open(input_path) as source:
        if source.format != "JPEG":
            raise ValueError(f"Expected a JPEG image, got {source.format!r}")
        original = source.convert("RGB")

    recompressed_path = output_dir / f"{input_path.stem}_recompressed_q{quality}.jpg"
    ela_path = output_dir / f"{input_path.stem}_ela_q{quality}.png"
    report_path = output_dir / f"{input_path.stem}_ela_q{quality}.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    original.save(recompressed_path, format="JPEG", quality=quality)
    with Image.open(recompressed_path) as recompressed:
        difference = ImageChops.difference(original, recompressed.convert("RGB"))

    difference_array = np.asarray(difference, dtype=np.uint8)
    scaled = np.clip(
        difference_array.astype(np.float32) * display_scale, 0, 255
    ).astype(np.uint8)
    Image.fromarray(scaled).save(ela_path)

    report: dict[str, object] = {
        "input": str(input_path),
        "format": "JPEG",
        "width": original.width,
        "height": original.height,
        "recompression_quality": quality,
        "display_scale": display_scale,
        "mean_absolute_channel_difference": float(difference_array.mean()),
        "maximum_channel_difference": int(difference_array.max()),
        "mean_scaled_ela_intensity": float(scaled.mean()),
        "recompressed_image": str(recompressed_path),
        "ela_image": str(ela_path),
        "report": str(report_path),
        "interpretation": (
            "Heuristic visualization only. Bright regions are not proof of editing; "
            "results depend on image history, JPEG quality, and processing."
        ),
    }
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Path to a JPEG image")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "output",
    )
    parser.add_argument("--quality", type=int, default=90, choices=range(1, 96))
    parser.add_argument("--scale", type=float, default=10.0)
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale must be greater than zero")

    report = analyze_ela(args.image, args.output_dir, args.quality, args.scale)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
