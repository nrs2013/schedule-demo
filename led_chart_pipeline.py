#!/usr/bin/env python3
"""
LED chart material validation and compositing pipeline.

This CLI keeps the chart mask authoritative:
- alpha == 0 is paintable LED area
- alpha != 0 is protected and forced to RGB black in the final output
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont


TOP_BOX = (1172, 5, 1856, 256)
V_BOXES = [
    (1124, 280, 192, 512),
    (1476, 280, 192, 512),
    (1828, 280, 192, 512),
    (2180, 280, 192, 512),
    (2532, 280, 192, 512),
    (2884, 280, 192, 512),
]
H_BOXES = [
    (68, 810, 192, 256),
    (420, 810, 192, 256),
    (772, 810, 192, 256),
    (1124, 810, 192, 256),
    (2884, 810, 192, 256),
    (3236, 810, 192, 256),
    (3588, 810, 192, 256),
    (3940, 810, 192, 256),
]

TOP_TARGET_RATIO = TOP_BOX[2] / TOP_BOX[3]
V_TARGET_RATIO = 192 / 512
H_TARGET_RATIO = 192 / 256
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def safe_stem(path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", path.stem).strip("_")
    return stem or "candidate"


def iter_image_paths(paths: Sequence[Path], top_dir: Path | None) -> List[Path]:
    found: List[Path] = []
    if top_dir:
        found.extend(
            p for p in sorted(top_dir.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
    for path in paths:
        if path.is_dir():
            found.extend(
                p for p in sorted(path.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
            )
        elif path.suffix.lower() in IMAGE_EXTENSIONS:
            found.append(path)

    seen = set()
    unique = []
    for path in found:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(path)
    return unique


def load_font(size: int, bold: bool = False, italic: bool = False, japanese: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc" if japanese and bold else "",
        "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc" if japanese and bold else "",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc" if japanese else "",
        "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc" if japanese and italic else "",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf" if japanese else "",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "",
        "/System/Library/Fonts/Supplemental/Arial Italic.ttf" if italic else "",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "",
        "/Library/Fonts/Arial Italic.ttf" if italic else "",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf" if italic else "",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def detect_body_bbox(img: Image.Image, bg: str = "auto") -> Tuple[int, int, int, int]:
    rgb = np.asarray(img.convert("RGB"), dtype=np.int16)
    maxc = rgb.max(axis=2)
    minc = rgb.min(axis=2)
    sat = maxc - minc

    if bg == "white":
        not_bg = (maxc < 245) | (sat > 20)
    elif bg == "black":
        not_bg = (maxc > 35) & ((sat > 10) | (maxc > 95))
    else:
        corner = 24
        corners = np.concatenate(
            [
                rgb[:corner, :corner].reshape(-1, 3),
                rgb[:corner, -corner:].reshape(-1, 3),
                rgb[-corner:, :corner].reshape(-1, 3),
                rgb[-corner:, -corner:].reshape(-1, 3),
            ]
        )
        if float(corners.mean()) > 180:
            not_bg = (maxc < 245) | (sat > 20)
        else:
            not_bg = (maxc > 35) & ((sat > 10) | (maxc > 95))

    ys, xs = np.where(not_bg)
    if len(xs) == 0:
        return (0, 0, img.width, img.height)

    pad = 2
    return (
        max(0, int(xs.min()) - pad),
        max(0, int(ys.min()) - pad),
        min(img.width, int(xs.max()) + 1 + pad),
        min(img.height, int(ys.max()) + 1 + pad),
    )


def validate_top_candidate(
    path: Path,
    pass_min: float,
    pass_max: float,
    bg: str,
    min_width_coverage: float,
    min_height_coverage: float,
) -> Dict[str, Any]:
    img = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = detect_body_bbox(img, bg=bg)
    bw, bh = x2 - x1, y2 - y1
    ratio = bw / bh if bh else 0.0
    width_coverage = bw / img.width if img.width else 0.0
    height_coverage = bh / img.height if img.height else 0.0
    edge_touch = {
        "left": x1 <= 4,
        "right": img.width - x2 <= 4,
        "top": y1 <= 4,
        "bottom": img.height - y2 <= 4,
    }
    passed = (
        pass_min <= ratio <= pass_max
        and width_coverage >= min_width_coverage
        and height_coverage >= min_height_coverage
    )
    reasons: List[str] = []
    if ratio < pass_min:
        reasons.append("body_ratio_too_low_thick")
    if ratio > pass_max:
        reasons.append("body_ratio_too_high_thin")
    if width_coverage < min_width_coverage:
        reasons.append("complete_block_not_wide_enough_in_source")
    if height_coverage < min_height_coverage:
        reasons.append("complete_block_too_small_vertically")

    return {
        "path": str(path),
        "source_size": [img.width, img.height],
        "bbox": [x1, y1, x2, y2],
        "body_size": [bw, bh],
        "body_ratio": ratio,
        "target_ratio": TOP_TARGET_RATIO,
        "delta": abs(ratio - TOP_TARGET_RATIO),
        "width_coverage": width_coverage,
        "height_coverage": height_coverage,
        "edge_touch": edge_touch,
        "pass": passed,
        "reasons": reasons,
    }


def validate_top_crop_scene_candidate(path: Path) -> Dict[str, Any]:
    img = Image.open(path).convert("RGB")
    ratio = img.width / img.height if img.height else 0.0
    return {
        "path": str(path),
        "source_size": [img.width, img.height],
        "source_ratio": ratio,
        "target_ratio": TOP_TARGET_RATIO,
        "delta": abs(ratio - TOP_TARGET_RATIO),
        "pass": True,
        "reasons": [],
        "fit": "cover_crop_to_top_slot",
    }


def validate_v_source(path: Path) -> Dict[str, Any]:
    img = Image.open(path).convert("RGB")
    cw, ch = img.width // 3, img.height // 2
    divisible = img.width % 3 == 0 and img.height % 2 == 0
    ratio = cw / ch if ch else 0.0
    passed = divisible and math.isclose(ratio, V_TARGET_RATIO, abs_tol=0.005)
    return {
        "path": str(path),
        "source_size": [img.width, img.height],
        "grid": [3, 2],
        "cell_size": [cw, ch],
        "cell_ratio": ratio,
        "target_ratio": V_TARGET_RATIO,
        "pass": passed,
    }


def validate_h_source(path: Path) -> Dict[str, Any]:
    img = Image.open(path).convert("RGB")
    cw, ch = img.width // 4, img.height // 2
    divisible = img.width % 4 == 0 and img.height % 2 == 0
    ratio = cw / ch if ch else 0.0
    passed = divisible and math.isclose(ratio, H_TARGET_RATIO, abs_tol=0.005)
    return {
        "path": str(path),
        "source_size": [img.width, img.height],
        "grid": [4, 2],
        "cell_size": [cw, ch],
        "cell_ratio": ratio,
        "target_ratio": H_TARGET_RATIO,
        "pass": passed,
    }


def split_tiles(img: Image.Image, columns: int, rows: int, target_size: Tuple[int, int]) -> List[Image.Image]:
    cw, ch = img.width // columns, img.height // rows
    tiles = []
    for row in range(rows):
        for col in range(columns):
            tile = img.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
            tiles.append(tile.resize(target_size, Image.Resampling.LANCZOS))
    return tiles


def add_marquee_text(top_tile: Image.Image, title_text: str, subtitle_text: str) -> Image.Image:
    tile = top_tile.convert("RGBA")
    if not title_text and not subtitle_text:
        return tile

    overlay = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((360, 56, 1510, 199), radius=28, fill=(0, 0, 0, 84))
    tile = Image.alpha_composite(tile, overlay)

    draw = ImageDraw.Draw(tile)
    has_japanese = any(ord(ch) > 127 for ch in title_text + subtitle_text)
    main_font = load_font(60, bold=True, japanese=has_japanese)
    sub_font = load_font(42, italic=True, japanese=has_japanese)

    main = title_text
    sub = subtitle_text
    main_box = draw.textbbox((0, 0), main, font=main_font)
    sub_box = draw.textbbox((0, 0), sub, font=sub_font)
    main_x = 442
    main_y = 82
    sub_x = 1128
    sub_y = 98

    if main:
        for offset in [(0, 0), (2, 0), (-2, 0), (0, 2), (0, -2)]:
            draw.text((main_x + offset[0], main_y + offset[1]), main, font=main_font, fill=(90, 40, 100, 230))
        draw.text((main_x, main_y), main, font=main_font, fill=(255, 244, 250, 255))
    if sub:
        draw.text((sub_x + 2, sub_y + 2), sub, font=sub_font, fill=(40, 20, 60, 220))
        draw.text((sub_x, sub_y), sub, font=sub_font, fill=(206, 255, 255, 255))

    # Small warm bulbs around the main title keep the text in marquee territory.
    bulb_y = main_y + main_box[3] + 14
    for x in range(main_x + 8, main_x + (main_box[2] - main_box[0]) - 8, 34):
        draw.ellipse((x - 4, bulb_y - 4, x + 4, bulb_y + 4), fill=(255, 226, 142, 245))
    for x in range(sub_x + 4, sub_x + (sub_box[2] - sub_box[0]) - 4, 28):
        draw.ellipse((x - 3, sub_y - 12, x + 3, sub_y - 6), fill=(145, 255, 255, 210))

    return tile


def cover_resize(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    target_w, target_h = target_size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = img.resize((math.ceil(src_w * scale), math.ceil(src_h * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_w) // 2)
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def prepare_top_tile(
    top_path: Path,
    top_info: Dict[str, Any],
    top_mode: str,
    title_text: str,
    subtitle_text: str,
) -> Image.Image:
    img = Image.open(top_path).convert("RGB")
    if top_mode in {"block", "strict"}:
        x1, y1, x2, y2 = top_info["bbox"]
        img = img.crop((x1, y1, x2, y2))
        tile = img.resize((TOP_BOX[2], TOP_BOX[3]), Image.Resampling.LANCZOS)
    else:
        tile = cover_resize(img, (TOP_BOX[2], TOP_BOX[3]))
    return add_marquee_text(tile, title_text, subtitle_text)


def paste_to_mask(out: np.ndarray, tile: Image.Image, bbox: Tuple[int, int, int, int], paint_mask: np.ndarray) -> None:
    x, y, w, h = bbox
    arr = np.asarray(tile.convert("RGBA"), dtype=np.uint8)
    region_mask = paint_mask[y : y + h, x : x + w]
    out_region = out[y : y + h, x : x + w]
    out_region[:, :, :3][region_mask] = arr[:, :, :3][region_mask]
    out_region[:, :, 3][region_mask] = 255


def composite(
    chart_path: Path,
    v_path: Path,
    h_path: Path,
    top_path: Path,
    top_info: Dict[str, Any],
    top_mode: str,
    title_text: str,
    subtitle_text: str,
    out_path: Path,
) -> Dict[str, Any]:
    chart = Image.open(chart_path).convert("RGBA")
    if chart.size != (4200, 1080):
        raise ValueError(f"Chart size must be 4200x1080, got {chart.size}")

    chart_arr = np.asarray(chart, dtype=np.uint8)
    paint_mask = chart_arr[:, :, 3] == 0
    out = np.zeros((chart.height, chart.width, 4), dtype=np.uint8)
    out[:, :, 3] = 255

    v_tiles = split_tiles(Image.open(v_path).convert("RGB"), 3, 2, (192, 512))
    h_tiles = split_tiles(Image.open(h_path).convert("RGB"), 4, 2, (192, 256))
    top_tile = prepare_top_tile(top_path, top_info, top_mode, title_text, subtitle_text)

    paste_to_mask(out, top_tile, TOP_BOX, paint_mask)
    for tile, box in zip(v_tiles, V_BOXES):
        paste_to_mask(out, tile, box, paint_mask)
    for tile, box in zip(h_tiles, H_BOXES):
        paste_to_mask(out, tile, box, paint_mask)

    out[~paint_mask, :3] = 0
    out[:, :, 3] = 255
    Image.fromarray(out, "RGBA").save(out_path)

    outside_color_leak = bool(np.any(out[:, :, :3][~paint_mask] != 0))
    drawn_pixels = int(np.count_nonzero(np.any(out[:, :, :3][paint_mask] != 0, axis=1)))
    return {
        "output": str(out_path),
        "size": [chart.width, chart.height],
        "outside_color_leak": outside_color_leak,
        "drawn_pixels_in_led": drawn_pixels,
    }


def copy_candidate(src: Path, dest_dir: Path, info: Dict[str, Any], prefix: str) -> str:
    dest_dir.mkdir(parents=True, exist_ok=True)
    ratio = info.get("body_ratio", info.get("source_ratio", 0.0))
    dest = dest_dir / f"{prefix}_{safe_stem(src)}_ratio_{ratio:.3f}{src.suffix.lower()}"
    shutil.copy2(src, dest)
    return str(dest)


def write_text_report(report: Dict[str, Any], path: Path) -> None:
    lines = [
        "LED chart pipeline report",
        "",
        f"chart: {report['inputs']['chart']}",
        f"v: {report['inputs']['v']}",
        f"h: {report['inputs']['h']}",
        f"top_candidates: {len(report['top_candidates'])}",
        "",
        f"V pass: {report['v_validation']['pass']} ratio={report['v_validation']['cell_ratio']:.3f}",
        f"H pass: {report['h_validation']['pass']} ratio={report['h_validation']['cell_ratio']:.3f}",
        "",
        "TOP materials:",
    ]
    for item in report["top_candidates"]:
        status = "PASS" if item["pass"] else "REJECT"
        reasons = ",".join(item["reasons"]) if item["reasons"] else "-"
        ratio = item.get("body_ratio", item.get("source_ratio", 0.0))
        body = item.get("body_size", item.get("source_size", []))
        width_coverage = item.get("width_coverage", 1.0)
        height_coverage = item.get("height_coverage", 1.0)
        lines.append(
            f"- {status} ratio={ratio:.3f} delta={item['delta']:.3f} "
            f"size={body} coverage=({width_coverage:.3f},"
            f"{height_coverage:.3f}) file={item['path']} reasons={reasons}"
        )
    selected_top = report.get("selected_top")
    selected_top_path = selected_top.get("path", "none") if isinstance(selected_top, dict) else "none"
    lines.extend(["", f"selected_top: {selected_top_path}"])
    if report.get("composite"):
        lines.append(f"output: {report['composite']['output']}")
        lines.append(f"outside_color_leak: {report['composite']['outside_color_leak']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> Dict[str, Any]:
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    passed_dir = out_dir / "PASSED_TOP"
    rejected_dir = out_dir / "REJECTED_TOP"

    v_validation = validate_v_source(args.v)
    h_validation = validate_h_source(args.h)
    if not v_validation["pass"]:
        raise ValueError(f"V source rejected: {v_validation}")
    if not h_validation["pass"]:
        raise ValueError(f"H source rejected: {h_validation}")

    candidates = iter_image_paths(args.top, args.top_dir)
    if not candidates:
        raise ValueError("No TOP image candidates found.")

    if args.top_mode in {"block", "strict"}:
        top_infos = [
            validate_top_candidate(
                path,
                pass_min=args.pass_min,
                pass_max=args.pass_max,
                bg=args.bg,
                min_width_coverage=args.min_width_coverage,
                min_height_coverage=args.min_height_coverage,
            )
            for path in candidates
        ]
    else:
        top_infos = [validate_top_crop_scene_candidate(path) for path in candidates]
    for path, info in zip(candidates, top_infos):
        copy_path = copy_candidate(path, passed_dir if info["pass"] else rejected_dir, info, "top")
        info["copy_path"] = copy_path

    passed = [info for info in top_infos if info["pass"]]
    selected = min(passed, key=lambda item: item["delta"]) if passed else None

    report: Dict[str, Any] = {
        "inputs": {
            "chart": str(args.chart),
            "v": str(args.v),
            "h": str(args.h),
            "top_dir": str(args.top_dir) if args.top_dir else None,
            "top": [str(p) for p in args.top],
        },
        "thresholds": {
            "top_mode": args.top_mode,
            "top_pass_min": args.pass_min,
            "top_pass_max": args.pass_max,
            "min_width_coverage": args.min_width_coverage,
            "min_height_coverage": args.min_height_coverage,
        },
        "v_validation": v_validation,
        "h_validation": h_validation,
        "top_candidates": top_infos,
        "selected_top": selected,
        "composite": None,
        "outputs": {
            "report_json": str(out_dir / "report.json"),
            "report_txt": str(out_dir / "report.txt"),
            "passed_top_dir": str(passed_dir),
            "rejected_top_dir": str(rejected_dir),
        },
    }

    if selected is not None:
        top_path = Path(selected["path"])
        output_name = args.output_name or f"led_chart_final_{safe_stem(top_path)}.png"
        local_title = args.title_text if args.legacy_local_text and not args.no_text else ""
        local_subtitle = args.subtitle_text if args.legacy_local_text and not args.no_text else ""
        report["composite"] = composite(
            args.chart,
            args.v,
            args.h,
            top_path,
            selected,
            args.top_mode,
            local_title,
            local_subtitle,
            out_dir / output_name,
        )

    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_text_report(report, out_dir / "report.txt")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate LED chart materials and composite passing TOP candidates.")
    parser.add_argument("--chart", required=True, type=Path)
    parser.add_argument("--v", required=True, type=Path)
    parser.add_argument("--h", required=True, type=Path)
    parser.add_argument("--top_dir", type=Path)
    parser.add_argument("--top", action="append", default=[], type=Path, help="TOP candidate image or directory. Repeatable.")
    parser.add_argument("--out_dir", required=True, type=Path)
    parser.add_argument("--output_name", default="")
    parser.add_argument("--pass_min", type=float, default=6.9)
    parser.add_argument("--pass_max", type=float, default=7.6)
    parser.add_argument("--bg", choices=["auto", "black", "white"], default="auto")
    parser.add_argument("--min_width_coverage", type=float, default=0.80)
    parser.add_argument("--min_height_coverage", type=float, default=0.18)
    parser.add_argument("--title_text", default="")
    parser.add_argument("--subtitle_text", default="")
    parser.add_argument("--no_text", action="store_true")
    parser.add_argument(
        "--legacy_local_text",
        action="store_true",
        help="Legacy fallback only. Normal workflow keeps text out of Python and integrates requested text during image generation.",
    )
    parser.add_argument(
        "--top_mode",
        choices=["block", "strict", "crop_scene"],
        default="block",
        help=(
            "block requires a complete 1856x256-like design block and crops only outer margin; "
            "crop_scene is legacy cover-crop behavior for experiments."
        ),
    )
    return parser.parse_args()


def main() -> None:
    report = run(parse_args())
    passed_count = sum(1 for item in report["top_candidates"] if item["pass"])
    print(f"V pass: {report['v_validation']['pass']} ratio={report['v_validation']['cell_ratio']:.3f}")
    print(f"H pass: {report['h_validation']['pass']} ratio={report['h_validation']['cell_ratio']:.3f}")
    print(f"TOP blocks: {len(report['top_candidates'])}, passed: {passed_count}")
    print(f"report_json: {report['outputs']['report_json']}")
    print(f"report_txt: {report['outputs']['report_txt']}")
    if report["selected_top"] is None:
        raise SystemExit("TOP materials rejected: no final composite was created.")
    print(f"selected_top: {report['selected_top']['path']}")
    print(f"output: {report['composite']['output']}")


if __name__ == "__main__":
    main()
