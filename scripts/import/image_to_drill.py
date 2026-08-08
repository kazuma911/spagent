"""Prepare a drill image for vision processing.

ドリル資料画像の Exif を削除し、必要に応じて縮小する。実際の画像解析は
Skill 側の Vision 呼び出しに委譲する。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MAX_LONG_SIDE = 2000


def default_output_path(path: Path) -> Path:
    """Build the default preprocessed image path.

    元ファイル名に `.preprocessed` を付ける。
    """
    return path.with_name(f"{path.stem}.preprocessed{path.suffix}")


def preprocess_image(path: Path, out_path: Path | None = None) -> dict[str, Any]:
    """Strip Exif data and resize a drill image.

    GPS 等のメタデータを保持しない形で画像を再保存する。
    """
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow is required. Install with: python -m pip install -r scripts/requirements.txt") from exc

    if not path.exists():
        raise FileNotFoundError(f"missing image: {path}")
    out_path = out_path or default_output_path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        original_size = image.size
        longest = max(image.size)
        resized = False
        if longest > MAX_LONG_SIDE:
            scale = MAX_LONG_SIDE / longest
            new_size = (round(image.width * scale), round(image.height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            resized = True
        clean = Image.new(image.mode, image.size)
        clean.putdata(list(image.getdata()))
        save_kwargs: dict[str, Any] = {}
        if out_path.suffix.lower() in {".jpg", ".jpeg"}:
            save_kwargs["quality"] = 92
            if clean.mode not in {"RGB", "L"}:
                clean = clean.convert("RGB")
        clean.save(out_path, **save_kwargs)

    return {
        "status": "ready for vision processing",
        "mode": "drill preprocessing",
        "source_path": str(path),
        "output_path": str(out_path),
        "exif_stripped": True,
        "resized": resized,
        "original_size": {"width": original_size[0], "height": original_size[1]},
    }


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    入力画像と任意の出力先を受け取る。
    """
    parser = argparse.ArgumentParser(description="Prepare a drill image for Claude/GPT Vision processing.")
    parser.add_argument("path", type=Path, help="Input image path.")
    parser.add_argument("--out", type=Path, help="Output image path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the image preprocessing CLI.

    Vision 処理用のメタデータ JSON を出力する。
    """
    args = build_parser().parse_args(argv)
    try:
        result = preprocess_image(args.path, args.out)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
