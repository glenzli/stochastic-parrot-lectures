#!/usr/bin/env python3
"""Fetch the small, exact Commons photo set used beside principle diagrams.

Unlike the 160 train portraits, these photographs show components that a child
can also see in the real world.  Exact Commons filenames are kept in
``principle_photo_targets.json`` so a rebuild cannot silently choose a
different mechanism or railway system.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fetch_commons_images import (
    download,
    md_safe,
    meta_value,
    plain_text,
    resolve_targets,
    save_webp,
)


BOOK_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = Path(__file__).resolve().parent
TARGETS_PATH = TOOLS_DIR / "principle_photo_targets.json"
OUTPUT_DIR = BOOK_DIR / "images" / "principles" / "photos"
METADATA_PATH = BOOK_DIR / "principle_photo_metadata.json"
CREDITS_PATH = BOOK_DIR / "PRINCIPLE_PHOTO_CREDITS.md"


def write_credits(records: list[dict[str, object]]) -> None:
    lines = [
        "# 原理实拍图来源与许可",
        "",
        "这些照片只用来回答“真实东西长什么样”。箭头、剖面和看不见的内部过程，",
        "仍由本书的原创原理图解释。照片只做等比例缩小与 WebP 格式转换，没有裁切。",
        "",
        "重新使用前，请打开 Commons 原文件页核对作者、许可与其他可能适用的权利。",
        "",
        "| 图号 | 画面内容 | 作者/来源 | 许可/版权状态 | Commons 原文件页 | 本地文件 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in sorted(records, key=lambda item: str(item["id"])):
        identifier = str(record["id"])
        anchor = f'<a id="principle-photo-{identifier}"></a>'
        source = f'[{md_safe(str(record["file_title"]))}]({record["description_url"]})'
        creator = md_safe(str(record.get("attribution") or record["artist"]))
        license_name = md_safe(str(record["license"]))
        if record.get("license_url"):
            license_name = f'[{license_name}]({record["license_url"]})'
        lines.append(
            "| "
            + " | ".join(
                [
                    anchor + identifier,
                    md_safe(str(record["subject"])),
                    creator,
                    license_name,
                    source,
                    f'`images/principles/photos/{identifier}.webp`',
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 构建说明",
            "",
            "- 元数据快照见 [`principle_photo_metadata.json`](principle_photo_metadata.json)。",
            "- 精确目标表见 [`tools/principle_photo_targets.json`](tools/principle_photo_targets.json)。",
            "- 获取脚本见 [`tools/fetch_principle_photos.py`](tools/fetch_principle_photos.py)。",
        ]
    )
    CREDITS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def persist(
    records: list[dict[str, object]], previous: dict[str, dict[str, object]]
) -> None:
    current_ids = {str(item["id"]) for item in records}
    snapshot = records + [
        item for identifier, item in previous.items() if identifier not in current_ids
    ]
    snapshot.sort(key=lambda item: str(item["id"]))
    METADATA_PATH.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_credits(snapshot)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    selected = set(args.only)
    if selected:
        targets = [target for target in targets if target["id"] in selected]

    previous: dict[str, dict[str, object]] = {}
    if METADATA_PATH.exists():
        for item in json.loads(METADATA_PATH.read_text(encoding="utf-8")):
            previous[str(item["id"])] = item

    resolved = resolve_targets(targets, args.width)
    records: list[dict[str, object]] = []
    failures: list[str] = []
    for target in targets:
        identifier = target["id"]
        output = OUTPUT_DIR / f"{identifier}.webp"
        if output.exists() and identifier in previous and not args.refresh:
            records.append({**previous[identifier], **target})
            print(f"keep {identifier}")
            continue

        info = resolved.get(identifier)
        if not info or not info.get("download_url"):
            failures.append(identifier)
            print(f"no suitable freely licensed image: {identifier}", file=sys.stderr)
            continue

        raw = download(info["download_url"])
        width, height, digest = save_webp(raw, output, args.width)
        metadata = info["metadata"]
        artist = plain_text(meta_value(metadata, "Artist"))
        attribution = plain_text(meta_value(metadata, "Attribution"))
        if attribution == "未注明":
            attribution = artist
        records.append(
            {
                **target,
                "file_title": info["file_title"],
                "description_url": info["description_url"],
                "original_url": info["original_url"],
                "download_url": info["download_url"],
                "selection": info["selection"],
                "artist": artist,
                "attribution": attribution,
                "license": plain_text(meta_value(metadata, "LicenseShortName")),
                "license_url": meta_value(metadata, "LicenseUrl"),
                "date_time_original": plain_text(meta_value(metadata, "DateTimeOriginal")),
                "local_width": width,
                "local_height": height,
                "sha256": digest,
                "technical_changes": "resized proportionally and converted to WebP; not cropped",
            }
        )
        persist(records, previous)
        print(f"saved {identifier}")

    persist(records, previous)
    print(f"saved {len(records)} principle photos; {len(failures)} unresolved")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
