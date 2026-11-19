"""Read a privacy-conscious inventory of selected JPEG EXIF fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import ExifTags, Image


SELECTED_TAGS = {
    "Make",
    "Model",
    "Software",
    "DateTime",
    "DateTimeOriginal",
    "DateTimeDigitized",
    "Orientation",
    "XResolution",
    "YResolution",
    "FNumber",
    "ExposureTime",
    "ISOSpeedRatings",
    "FocalLength",
}


def inventory_exif(input_path: Path, output_dir: Path) -> dict[str, object]:
    with Image.open(input_path) as image:
        if image.format != "JPEG":
            raise ValueError(f"Expected a JPEG image, got {image.format!r}")
        exif = image.getexif()
        fields = {
            ExifTags.TAGS.get(tag_id, str(tag_id)): str(value)
            for tag_id, value in exif.items()
            if ExifTags.TAGS.get(tag_id, str(tag_id)) in SELECTED_TAGS
        }
        report: dict[str, object] = {
            "input": str(input_path),
            "format": "JPEG",
            "width": image.width,
            "height": image.height,
            "exif_present": bool(exif),
            "selected_exif_fields": fields,
            "interpretation": (
                "Metadata is editable and may be absent or stripped. Its presence "
                "does not establish image authenticity. GPS fields are intentionally "
                "omitted from this report."
            ),
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{input_path.stem}_exif.json"
    report["report"] = str(report_path)
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
    args = parser.parse_args()
    report = inventory_exif(args.image, args.output_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
