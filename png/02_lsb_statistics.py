"""Summarize RGB least-significant-bit statistics in a PNG image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def _transition_ratio(bits: np.ndarray) -> float | None:
    if bits.shape[1] < 2:
        return None
    return float(np.mean(bits[:, 1:] != bits[:, :-1]))


def analyze_lsb(input_path: Path, output_dir: Path) -> dict[str, object]:
    with Image.open(input_path) as image:
        if image.format != "PNG":
            raise ValueError(f"Expected a PNG image, got {image.format!r}")
        rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)

    bit_planes = rgb & 1
    channel_names = ("red", "green", "blue")
    statistics: dict[str, dict[str, float | int | None]] = {}
    for channel_index, channel_name in enumerate(channel_names):
        bits = bit_planes[:, :, channel_index]
        statistics[channel_name] = {
            "ones_ratio": float(bits.mean()),
            "horizontal_transition_ratio": _transition_ratio(bits),
            "vertical_transition_ratio": (
                float(np.mean(bits[1:, :] != bits[:-1, :]))
                if bits.shape[0] > 1
                else None
            ),
            "sample_count": int(bits.size),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    visualization_path = output_dir / f"{input_path.stem}_lsb_rgb.png"
    report_path = output_dir / f"{input_path.stem}_lsb_statistics.json"
    visualization = (bit_planes * 255).astype(np.uint8)
    Image.fromarray(visualization).save(visualization_path)

    report: dict[str, object] = {
        "input": str(input_path),
        "format": "PNG",
        "width": int(rgb.shape[1]),
        "height": int(rgb.shape[0]),
        "analyzed_channels": list(channel_names),
        "alpha_channel_analyzed": False,
        "lsb_statistics": statistics,
        "lsb_visualization": str(visualization_path),
        "report": str(report_path),
        "interpretation": (
            "Low-bit statistics and visualizations are screening indicators, not "
            "proof of hidden data. Natural image content can look statistically "
            "similar, and this experiment does not extract or execute content."
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
    report = analyze_lsb(args.image, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
