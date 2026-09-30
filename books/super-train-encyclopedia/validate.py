#!/usr/bin/env python3
"""Validate the structure and local assets of the train encyclopedia."""

from __future__ import annotations

import html
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent

NUMBERED_CHAPTERS = (
    "01_how_trains_move.md",
    "02_steam_origins.md",
    "03_power_revolution.md",
    "04_high_speed_pioneers.md",
    "05_high_speed_specialists.md",
    "06_city_trains.md",
    "07_regional_trains.md",
    "08_express_airport.md",
    "09_sleeper_scenic.md",
    "10_work_trains.md",
    "11_unusual_guideways.md",
    "12_mountain_railways.md",
)
CARD_CHAPTERS = NUMBERED_CHAPTERS[1:]
EXPECTED_CARD_NUMBERS = {f"{number:03d}" for number in range(1, 161)}
EXPECTED_PRINCIPLE_SVG_COUNT = 25
EXPECTED_PRINCIPLE_PHOTO_COUNT = 8
EXPECTED_GENERATED_PRINCIPLE_FILES = {
    "diesel-electric-cutaway.webp",
    "track-layers-cutaway.webp",
}
EXPECTED_PRINCIPLE_AFTER_CARD = {
    "004": "steam-power.svg",
    "005": "steel-wheel-rail.svg",
    "008": "wheel-flange.svg",
    "020": "diesel-paths.svg",
    "032": "overhead-ac-dc.svg",
    "052": "aerodynamic-nose.svg",
    "056": "pantograph.svg",
    "069": "third-rail.svg",
    "075": "points.svg",
    "080": "curve-cant.svg",
    "083": "suspension-comfort.svg",
    "100": "coupler-force.svg",
    "101": "air-brake.svg",
    "102": "track-layers.svg",
    "104": "straddle-monorail.svg",
    "106": "suspended-monorail.svg",
    "110": "maglev.svg",
    "116": "rack-rail.svg",
    "117": "funicular-cable.svg",
    "124": "adhesion-traction.svg",
    "127": "regenerative-braking.svg",
    "129": "axle-bogie.svg",
    "138": "rubber-guideway.svg",
    "159": "signals.svg",
}

ATX_HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)")
CARD_HEADING_RE = re.compile(
    r"^ {0,3}##[ \t]+(?P<number>\d{3})(?=[^\d]|$)", re.MULTILINE
)
FENCE_RE = re.compile(r"^ {0,3}(?P<mark>\x60{3,}|~{3,})(?P<rest>.*)$")
INLINE_LINK_RE = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(?P<target><[^>\n]+>|(?:\\.|[^)\s])+)",
)
REFERENCE_LINK_RE = re.compile(
    r"^ {0,3}\[[^\]\n]+\]:[ \t]*(?P<target><[^>\n]+>|(?:\\.|\S)+)"
)
HTML_LINK_RE = re.compile(
    r"<(?:a|img)\b[^>]*?\b(?:href|src)[ \t]*=[ \t]*"
    r"(?P<quote>['\"])(?P<target>.*?)(?P=quote)",
    re.IGNORECASE,
)
TRAIN_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\./)?images/trains/"
    r"(?P<filename>[^\s)'\"<>]+\.webp)",
    re.IGNORECASE,
)
PRINCIPLE_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\./)?images/principles/"
    r"(?P<filename>[^\s)'\"<>]+\.svg)",
    re.IGNORECASE,
)
PRINCIPLE_PHOTO_CREDIT_LINK_RE = re.compile(
    r"\[[^\]\n]+\]\(\s*(?:\./)?PRINCIPLE_PHOTO_CREDITS\.md#"
    r"principle-photo-(?P<id>[A-Za-z0-9._-]+)(?:\s+[^)]*)?\)",
)
CREDIT_LINK_RE = re.compile(
    r"\[[^\]\n]+\]\(\s*(?:\./)?IMAGE_CREDITS\.md#img-"
    r"(?P<id>[A-Za-z0-9._-]+)(?:\s+[^)]*)?\)",
)
BIRTH_CARD_RE = re.compile(
    r"^ {0,3}(?:\*\*)?出生卡[：:](?:\*\*)?", re.MULTILINE
)
LOOK_FOR_RE = re.compile(
    r"^ {0,3}(?:\*\*)?找找看[：:](?:\*\*)?", re.MULTILINE
)
LEGACY_GROWNUP_RE = re.compile(r"^ {0,3}>[ \t]*给大人[：:]", re.MULTILINE)
CARD_GROWNUP_SUMMARY = "<summary>🔎 给大人看细节</summary>"
PRINCIPLE_GROWNUP_SUMMARY = "<summary>🔎 给大人再讲一点</summary>"
ROUTE_PICKER_SUMMARY = "<summary>🚉 选一个小站</summary>"
INTEGRATED_BLOCK_RE = re.compile(
    r"<!-- integrated-learning:after-(?P<number>\d{3}):start -->\n"
    r"(?P<body>.*?)\n"
    r"<!-- integrated-learning:after-(?P=number):end -->",
    re.DOTALL,
)
INTEGRATED_MARKER_RE = re.compile(
    r"<!-- integrated-learning:after-(?P<number>\d{3}):(?P<edge>start|end) -->"
)
WORK_MARKER_RE = re.compile(r"\b(?:TODO|FIXME)\b", re.IGNORECASE)
HTML_ID_RE = re.compile(r"\bid[ \t]*=[ \t]*(['\"])(?P<id>.*?)\1", re.IGNORECASE)


@dataclass(frozen=True)
class Problem:
    path: str
    line: int | None
    message: str


@dataclass(frozen=True)
class Reference:
    line: int
    target: str
    resolved: Path | None


@dataclass(frozen=True)
class Card:
    number: str
    path: Path
    line: int
    image_id: str | None
    credit_id: str | None


class Reporter:
    def __init__(self) -> None:
        self.problems: list[Problem] = []

    def add(self, path: Path | str, message: str, line: int | None = None) -> None:
        if isinstance(path, Path):
            try:
                label = path.resolve().relative_to(ROOT).as_posix()
            except ValueError:
                label = str(path)
        else:
            label = path
        self.problems.append(Problem(label, line, message))

    def finish(
        self,
        *,
        cards: int,
        images: int,
        principle_svgs: int,
        principle_photos: int,
        generated_principles: int,
    ) -> int:
        if self.problems:
            for problem in sorted(
                self.problems,
                key=lambda item: (item.path, item.line or 0, item.message),
            ):
                location = problem.path
                if problem.line is not None:
                    location += f":{problem.line}"
                print(f"ERROR {location}: {problem.message}")
            count = len(self.problems)
            noun = "problem" if count == 1 else "problems"
            print(f"\nFAILED: {count} {noun} found.")
            return 1

        print(
            "OK: validated "
            f"{len(NUMBERED_CHAPTERS)} numbered chapters, "
            f"{cards} train cards, {images} train WebPs, "
            f"{principle_svgs} principle SVGs, "
            f"{principle_photos} principle photos, and "
            f"{generated_principles} generated cutaway WebPs."
        )
        return 0


def read_utf8(path: Path, reporter: Reporter) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        reporter.add(path, "file is missing")
    except UnicodeDecodeError as exc:
        reporter.add(path, f"is not valid UTF-8 ({exc})")
    except OSError as exc:
        reporter.add(path, f"could not be read ({exc})")
    return None


def scan_markdown(
    path: Path, text: str, reporter: Reporter
) -> tuple[list[tuple[int, int]], list[tuple[int, str]]]:
    """Check Markdown hygiene and return headings and non-fenced content lines."""
    lines = text.splitlines()
    headings: list[tuple[int, int]] = []
    content_lines: list[tuple[int, str]] = []
    previous_heading_level: int | None = None
    fence_char: str | None = None
    fence_length = 0
    fence_open_line: int | None = None

    for line_number, line in enumerate(lines, start=1):
        if re.search(r"[ \t]+$", line):
            reporter.add(path, "trailing whitespace", line_number)
        if WORK_MARKER_RE.search(line):
            reporter.add(path, "unfinished-work marker is not allowed", line_number)

        if fence_char is not None:
            closing = re.match(
                rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*$",
                line,
            )
            if closing:
                fence_char = None
                fence_length = 0
                fence_open_line = None
            continue

        fence = FENCE_RE.match(line)
        if fence:
            mark = fence.group("mark")
            fence_char = mark[0]
            fence_length = len(mark)
            fence_open_line = line_number
            continue

        content_lines.append((line_number, line))
        heading = ATX_HEADING_RE.match(line)
        if not heading:
            continue
        level = len(heading.group(1))
        headings.append((line_number, level))
        if previous_heading_level is not None and level > previous_heading_level + 1:
            reporter.add(
                path,
                f"heading level jumps from H{previous_heading_level} to H{level}",
                line_number,
            )
        previous_heading_level = level

    if fence_char is not None:
        reporter.add(
            path,
            f"unclosed {fence_char * fence_length} code fence",
            fence_open_line,
        )

    return headings, content_lines


def clean_destination(raw_target: str) -> str:
    target = html.unescape(raw_target.strip())
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return re.sub(r"\\([\\\x60*{}\[\]()#+.! _>~-])", r"\1", target)


def resolve_local_reference(source: Path, target: str) -> Path | None:
    target = clean_destination(target)
    if not target or target.startswith("#") or target.startswith("//"):
        return None
    parsed = urlsplit(target)
    if parsed.scheme or not parsed.path:
        return None
    decoded_path = unquote(parsed.path)
    local_path = Path(decoded_path)
    if not local_path.is_absolute():
        local_path = source.parent / local_path
    return local_path.resolve()


def collect_references(
    path: Path,
    content_lines: list[tuple[int, str]],
    reporter: Reporter,
) -> list[Reference]:
    references: list[Reference] = []
    for line_number, line in content_lines:
        raw_targets = [match.group("target") for match in INLINE_LINK_RE.finditer(line)]
        definition = REFERENCE_LINK_RE.match(line)
        if definition:
            raw_targets.append(definition.group("target"))
        raw_targets.extend(match.group("target") for match in HTML_LINK_RE.finditer(line))

        for raw_target in raw_targets:
            target = clean_destination(raw_target)
            resolved = resolve_local_reference(path, target)
            references.append(Reference(line_number, target, resolved))
            if resolved is not None and not resolved.exists():
                reporter.add(path, f"local link target does not exist: {target}", line_number)
    return references


def check_chapters(
    texts: dict[Path, str],
    headings: dict[Path, list[tuple[int, int]]],
    references: dict[Path, list[Reference]],
    reporter: Reporter,
) -> None:
    readme = ROOT / "README.md"
    if readme not in texts:
        if not readme.exists():
            reporter.add(readme, "file is missing")
        return

    linked_files = {
        reference.resolved
        for reference in references.get(readme, [])
        if reference.resolved is not None
    }
    for chapter_name in NUMBERED_CHAPTERS:
        chapter = (ROOT / chapter_name).resolve()
        if chapter not in linked_files:
            reporter.add(readme, f"does not link numbered chapter {chapter_name}")

    for chapter_name in NUMBERED_CHAPTERS[1:]:
        chapter = ROOT / chapter_name
        if chapter not in texts:
            if not chapter.exists():
                reporter.add(chapter, "numbered chapter is missing")
            continue
        h1_lines = [line for line, level in headings.get(chapter, []) if level == 1]
        if len(h1_lines) != 1:
            detail = "none" if not h1_lines else ", ".join(map(str, h1_lines))
            reporter.add(
                chapter,
                f"must contain exactly one H1 heading (found {len(h1_lines)}; lines: {detail})",
            )

    for index, chapter_name in enumerate(NUMBERED_CHAPTERS):
        chapter = ROOT / chapter_name
        if chapter not in texts:
            continue
        linked_files = {
            reference.resolved
            for reference in references.get(chapter, [])
            if reference.resolved is not None
        }
        neighbours: list[tuple[str, str]] = []
        if index > 0:
            neighbours.append(("previous", NUMBERED_CHAPTERS[index - 1]))
        if index + 1 < len(NUMBERED_CHAPTERS):
            neighbours.append(("next", NUMBERED_CHAPTERS[index + 1]))
        for direction, neighbour_name in neighbours:
            if (ROOT / neighbour_name).resolve() not in linked_files:
                reporter.add(
                    chapter,
                    f"does not link {direction} numbered chapter {neighbour_name}",
                )


def line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_marker_count(
    reporter: Reporter,
    path: Path,
    card_number: str,
    card_line: int,
    label: str,
    count: int,
) -> None:
    if count != 1:
        reporter.add(
            path,
            f"card {card_number} must have exactly one {label} (found {count})",
            card_line,
        )


def collect_cards(texts: dict[Path, str], reporter: Reporter) -> list[Card]:
    cards: list[Card] = []
    number_locations: dict[str, list[str]] = {}

    for chapter_name in CARD_CHAPTERS:
        path = ROOT / chapter_name
        text = texts.get(path)
        if text is None:
            continue
        matches = list(CARD_HEADING_RE.finditer(text))
        for index, match in enumerate(matches):
            number = match.group("number")
            card_line = line_at(text, match.start())
            expected_anchor = f'<a id="train-{number}"></a>\n\n'
            if not text[: match.start()].endswith(expected_anchor):
                reporter.add(
                    path,
                    f"card {number} heading must be immediately preceded by "
                    f"the stable anchor #train-{number}",
                    card_line,
                )
            candidate_end = (
                matches[index + 1].start() if index + 1 < len(matches) else len(text)
            )
            candidate = text[match.start():candidate_end]
            horizontal_rule = re.search(r"\n---[ \t]*(?:\n|\Z)", candidate)
            block_end = horizontal_rule.start() if horizontal_rule else len(candidate)
            block = candidate[:block_end]
            number_locations.setdefault(number, []).append(f"{chapter_name}:{card_line}")

            train_paths = [item.group("filename") for item in TRAIN_PATH_RE.finditer(block)]
            credit_ids = [item.group("id") for item in CREDIT_LINK_RE.finditer(block)]
            check_marker_count(
                reporter, path, number, card_line, "images/trains WebP path", len(train_paths)
            )
            check_marker_count(
                reporter, path, number, card_line, "image-credit anchor link", len(credit_ids)
            )
            check_marker_count(
                reporter,
                path,
                number,
                card_line,
                "出生卡",
                len(BIRTH_CARD_RE.findall(block)),
            )
            check_marker_count(
                reporter,
                path,
                number,
                card_line,
                "找找看",
                len(LOOK_FOR_RE.findall(block)),
            )
            check_marker_count(
                reporter,
                path,
                number,
                card_line,
                "folded grownup summary",
                block.count(CARD_GROWNUP_SUMMARY),
            )
            check_marker_count(
                reporter,
                path,
                number,
                card_line,
                "<details> opening tag",
                block.count("<details>"),
            )
            check_marker_count(
                reporter,
                path,
                number,
                card_line,
                "</details> closing tag",
                block.count("</details>"),
            )
            legacy_grownup_count = len(LEGACY_GROWNUP_RE.findall(block))
            if legacy_grownup_count:
                reporter.add(
                    path,
                    f"card {number} still has {legacy_grownup_count} expanded "
                    "grownup blockquote(s)",
                    card_line,
                )

            image_id = Path(train_paths[0]).stem if len(train_paths) == 1 else None
            credit_id = credit_ids[0] if len(credit_ids) == 1 else None
            if image_id is not None and credit_id is not None and image_id != credit_id:
                reporter.add(
                    path,
                    f"card {number} image basename {image_id!r} does not match "
                    f"credit anchor {credit_id!r}",
                    card_line,
                )
            if image_id is not None and not image_id.startswith(f"t{number}-"):
                reporter.add(
                    path,
                    f"card {number} image ID {image_id!r} does not start with t{number}-",
                    card_line,
                )
            cards.append(Card(number, path, card_line, image_id, credit_id))

    found_numbers = set(number_locations)
    missing_numbers = sorted(EXPECTED_CARD_NUMBERS - found_numbers)
    unexpected_numbers = sorted(found_numbers - EXPECTED_CARD_NUMBERS)
    if missing_numbers:
        reporter.add(
            "train-card chapters",
            "missing train card numbers: " + ", ".join(missing_numbers),
        )
    if unexpected_numbers:
        reporter.add(
            "train-card chapters",
            "unexpected train card numbers: " + ", ".join(unexpected_numbers),
        )
    for number, locations in sorted(number_locations.items()):
        if len(locations) != 1:
            reporter.add(
                "train-card chapters",
                f"train card {number} occurs {len(locations)} times: " + ", ".join(locations),
            )

    return cards


def load_json_records(
    path: Path, label: str, reporter: Reporter
) -> tuple[list[dict[str, object]], bool]:
    text = read_utf8(path, reporter)
    if text is None:
        return [], False
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        reporter.add(path, f"invalid JSON: {exc.msg}", exc.lineno)
        return [], False
    if not isinstance(data, list):
        reporter.add(path, f"{label} must be a JSON array")
        return [], False

    records: list[dict[str, object]] = []
    ids: list[str] = []
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            reporter.add(path, f"{label} item {index + 1} is not an object")
            continue
        records.append(record)
        identifier = record.get("id")
        if not isinstance(identifier, str) or not identifier.strip():
            reporter.add(path, f"{label} item {index + 1} has no non-empty string id")
            continue
        ids.append(identifier)

    counts = Counter(ids)
    for identifier, count in sorted(counts.items()):
        if count > 1:
            reporter.add(path, f"duplicate ID {identifier!r} occurs {count} times")
    return records, True


def load_json_ids(path: Path, label: str, reporter: Reporter) -> tuple[set[str], bool]:
    records, loaded = load_json_records(path, label, reporter)
    ids = {
        identifier
        for record in records
        if isinstance((identifier := record.get("id")), str) and identifier.strip()
    }
    return ids, loaded


def check_json_chapters(
    path: Path,
    label: str,
    cards: list[Card],
    reporter: Reporter,
) -> None:
    text = read_utf8(path, reporter)
    if text is None:
        return
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return
    if not isinstance(data, list):
        return

    chapter_numbers = {
        chapter_name: f"{index + 2:02d}"
        for index, chapter_name in enumerate(CARD_CHAPTERS)
    }
    expected = {
        card.image_id: chapter_numbers[card.path.name]
        for card in cards
        if card.image_id is not None
    }
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            continue
        identifier = record.get("id")
        if not isinstance(identifier, str) or identifier not in expected:
            continue
        actual_chapter = record.get("chapter")
        expected_chapter = expected[identifier]
        if actual_chapter != expected_chapter:
            reporter.add(
                path,
                f"{label} item {index + 1} ({identifier}) has chapter "
                f"{actual_chapter!r}; expected {expected_chapter!r}",
            )


def compare_ids(
    reporter: Reporter,
    path: Path | str,
    actual: set[str],
    expected: set[str],
    actual_label: str,
    expected_label: str,
) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        reporter.add(
            path,
            f"{actual_label} missing IDs from {expected_label}: " + ", ".join(missing),
        )
    if extra:
        reporter.add(
            path,
            f"{actual_label} has IDs absent from {expected_label}: " + ", ".join(extra),
        )


def check_image_inventory(cards: list[Card], reporter: Reporter) -> int:
    card_ids_list = [card.image_id for card in cards if card.image_id is not None]
    card_ids = set(card_ids_list)
    for identifier, count in sorted(Counter(card_ids_list).items()):
        if count > 1:
            reporter.add("train cards", f"image ID {identifier!r} is used by {count} cards")

    targets_path = ROOT / "tools" / "image_targets.json"
    target_ids, targets_loaded = load_json_ids(targets_path, "image target", reporter)
    if targets_loaded:
        compare_ids(
            reporter,
            targets_path,
            target_ids,
            card_ids,
            "image_targets.json",
            "train cards",
        )
        check_json_chapters(targets_path, "image target", cards, reporter)
    inventory_ids = target_ids if targets_loaded else card_ids

    metadata_path = ROOT / "image_metadata.json"
    metadata_ids, metadata_loaded = load_json_ids(metadata_path, "image metadata", reporter)
    if metadata_loaded:
        compare_ids(
            reporter,
            metadata_path,
            metadata_ids,
            inventory_ids,
            "image metadata",
            "image targets",
        )
        check_json_chapters(metadata_path, "image metadata", cards, reporter)

    train_dir = ROOT / "images" / "trains"
    files: list[Path] = []
    if not train_dir.is_dir():
        reporter.add(train_dir, "train image directory is missing")
    else:
        files = sorted(
            path for path in train_dir.iterdir() if path.is_file() and path.suffix.lower() == ".webp"
        )
    file_ids_list = [path.stem for path in files]
    file_ids = set(file_ids_list)
    for identifier, count in sorted(Counter(file_ids_list).items()):
        if count > 1:
            reporter.add(train_dir, f"multiple WebP files have ID {identifier!r}")
    compare_ids(
        reporter,
        train_dir,
        file_ids,
        inventory_ids,
        "train WebP files",
        "image targets",
    )
    return len(files)


def check_credit_anchors(cards: list[Card], texts: dict[Path, str], reporter: Reporter) -> None:
    credits_path = ROOT / "IMAGE_CREDITS.md"
    credits_text = texts.get(credits_path)
    if credits_text is None:
        return
    anchor_ids = [match.group("id") for match in HTML_ID_RE.finditer(credits_text)]
    anchor_counts = Counter(anchor_ids)
    for card in cards:
        if card.credit_id is None:
            continue
        expected_anchor = f"img-{card.credit_id}"
        count = anchor_counts[expected_anchor]
        if count != 1:
            reporter.add(
                card.path,
                f"card {card.number} links anchor #{expected_anchor}, "
                f"but IMAGE_CREDITS.md defines it {count} times",
                card.line,
            )


def check_principle_photo_inventory(
    photos: list[Path],
    texts: dict[Path, str],
    references: dict[Path, list[Reference]],
    reporter: Reporter,
) -> None:
    targets_path = ROOT / "tools" / "principle_photo_targets.json"
    metadata_path = ROOT / "principle_photo_metadata.json"
    credits_path = ROOT / "PRINCIPLE_PHOTO_CREDITS.md"

    target_records, targets_loaded = load_json_records(
        targets_path, "principle photo target", reporter
    )
    metadata_records, metadata_loaded = load_json_records(
        metadata_path, "principle photo metadata", reporter
    )
    target_ids = {
        identifier
        for record in target_records
        if isinstance((identifier := record.get("id")), str) and identifier.strip()
    }
    metadata_ids = {
        identifier
        for record in metadata_records
        if isinstance((identifier := record.get("id")), str) and identifier.strip()
    }
    if targets_loaded and metadata_loaded:
        compare_ids(
            reporter,
            metadata_path,
            metadata_ids,
            target_ids,
            "principle photo metadata",
            "principle photo targets",
        )

        targets_by_id = {
            record["id"]: record
            for record in target_records
            if isinstance(record.get("id"), str)
        }
        metadata_by_id = {
            record["id"]: record
            for record in metadata_records
            if isinstance(record.get("id"), str)
        }
        for identifier in sorted(target_ids & metadata_ids):
            for field in ("subject", "commons_file"):
                target_value = targets_by_id[identifier].get(field)
                metadata_value = metadata_by_id[identifier].get(field)
                if target_value != metadata_value:
                    reporter.add(
                        metadata_path,
                        f"principle photo {identifier!r} has {field}={metadata_value!r}; "
                        f"target file has {target_value!r}",
                    )

    file_ids = {path.stem for path in photos}
    if targets_loaded:
        compare_ids(
            reporter,
            ROOT / "images" / "principles" / "photos",
            file_ids,
            target_ids,
            "principle photo WebP files",
            "principle photo targets",
        )
    if metadata_loaded:
        compare_ids(
            reporter,
            ROOT / "images" / "principles" / "photos",
            file_ids,
            metadata_ids,
            "principle photo WebP files",
            "principle photo metadata",
        )

    credits_text = texts.get(credits_path)
    if credits_text is not None:
        anchors = Counter(match.group("id") for match in HTML_ID_RE.finditer(credits_text))
        for identifier in sorted(file_ids):
            expected_anchor = f"principle-photo-{identifier}"
            if anchors[expected_anchor] != 1:
                reporter.add(
                    credits_path,
                    f"must define anchor #{expected_anchor} exactly once "
                    f"(found {anchors[expected_anchor]})",
                )
            expected_local_path = f"images/principles/photos/{identifier}.webp"
            if expected_local_path not in credits_text:
                reporter.add(
                    credits_path,
                    f"does not record local file {expected_local_path}",
                )

    chapter_paths = {ROOT / chapter_name for chapter_name in NUMBERED_CHAPTERS}
    chapter_references = {
        reference.resolved
        for path, file_references in references.items()
        if path in chapter_paths
        for reference in file_references
        if reference.resolved is not None
    }
    for photo in photos:
        if photo.resolve() not in chapter_references:
            reporter.add(photo, "principle photo is not referenced by a numbered chapter")

    chapter_credit_ids = Counter(
        match.group("id")
        for path, text in texts.items()
        if path in chapter_paths
        for match in PRINCIPLE_PHOTO_CREDIT_LINK_RE.finditer(text)
    )
    for identifier in sorted(file_ids):
        if chapter_credit_ids[identifier] == 0:
            reporter.add(
                "principle photo credits",
                f"principle photo {identifier} has no chapter link to its credit anchor",
            )
    unexpected_credit_ids = sorted(set(chapter_credit_ids) - file_ids)
    if unexpected_credit_ids:
        reporter.add(
            "principle photo credits",
            "chapter credit links have no matching photo: "
            + ", ".join(unexpected_credit_ids),
        )


def check_principle_assets(
    texts: dict[Path, str],
    references: dict[Path, list[Reference]],
    reporter: Reporter,
) -> tuple[int, int, int]:
    principle_dir = ROOT / "images" / "principles"
    if not principle_dir.is_dir():
        reporter.add(principle_dir, "principle image directory is missing")
        return 0, 0, 0

    svgs = sorted(principle_dir.rglob("*.svg"))
    photo_dir = principle_dir / "photos"
    generated_dir = principle_dir / "generated"
    photos = sorted(photo_dir.rglob("*.webp")) if photo_dir.is_dir() else []
    generated = sorted(generated_dir.rglob("*.webp")) if generated_dir.is_dir() else []
    all_webps = sorted(principle_dir.rglob("*.webp"))

    if not svgs:
        reporter.add(principle_dir, "no principle SVG files found")
    if len(svgs) != EXPECTED_PRINCIPLE_SVG_COUNT:
        reporter.add(
            principle_dir,
            f"must contain {EXPECTED_PRINCIPLE_SVG_COUNT} principle SVGs "
            f"(found {len(svgs)})",
        )
    if len(photos) != EXPECTED_PRINCIPLE_PHOTO_COUNT:
        reporter.add(
            photo_dir,
            f"must contain {EXPECTED_PRINCIPLE_PHOTO_COUNT} principle photos "
            f"(found {len(photos)})",
        )
    for svg in svgs:
        try:
            root = ElementTree.parse(svg).getroot()
        except (ElementTree.ParseError, OSError) as exc:
            reporter.add(svg, f"is not a readable SVG XML document ({exc})")
            continue
        namespace = "{http://www.w3.org/2000/svg}"
        titles = root.findall(f"{namespace}title")
        descriptions = root.findall(f"{namespace}desc")
        if len(titles) != 1 or not "".join(titles[0].itertext()).strip():
            reporter.add(svg, "must contain exactly one non-empty top-level <title>")
        if len(descriptions) != 1 or not "".join(descriptions[0].itertext()).strip():
            reporter.add(svg, "must contain exactly one non-empty top-level <desc>")
        if root.get("role") != "img":
            reporter.add(svg, "root <svg> must declare role='img'")
        labelled_ids = set((root.get("aria-labelledby") or "").split())
        title_id = titles[0].get("id") if len(titles) == 1 else None
        description_id = descriptions[0].get("id") if len(descriptions) == 1 else None
        if not title_id or not description_id or not {title_id, description_id} <= labelled_ids:
            reporter.add(
                svg,
                "aria-labelledby must reference the top-level title and desc IDs",
            )
    generated_names = {path.name for path in generated}
    if generated_names != EXPECTED_GENERATED_PRINCIPLE_FILES:
        compare_ids(
            reporter,
            generated_dir,
            generated_names,
            EXPECTED_GENERATED_PRINCIPLE_FILES,
            "generated cutaway WebPs",
            "expected generated cutaways",
        )

    recognised_webps = {path.resolve() for path in photos + generated}
    unclassified_webps = [
        path for path in all_webps if path.resolve() not in recognised_webps
    ]
    for path in unclassified_webps:
        reporter.add(
            path,
            "principle WebP must be stored under photos/ or generated/",
        )

    referenced_paths = {
        reference.resolved
        for file_references in references.values()
        for reference in file_references
        if reference.resolved is not None
    }
    for svg in svgs:
        if svg.resolve() not in referenced_paths:
            reporter.add(svg, "principle SVG is not referenced by any Markdown file")

    chapter_paths = {ROOT / chapter_name for chapter_name in NUMBERED_CHAPTERS}
    chapter_referenced_paths = {
        reference.resolved
        for path, file_references in references.items()
        if path in chapter_paths
        for reference in file_references
        if reference.resolved is not None
    }
    for image in generated:
        if image.resolve() not in chapter_referenced_paths:
            reporter.add(
                image,
                "generated cutaway is not referenced by a numbered chapter",
            )

    check_principle_photo_inventory(photos, texts, references, reporter)
    return len(svgs), len(photos), len(generated)


def check_integrated_learning(texts: dict[Path, str], reporter: Reporter) -> None:
    """Check the parts overview and principles distributed with train chapters."""
    intro_path = ROOT / "01_how_trains_move.md"
    intro_text = texts.get(intro_path, "")
    intro_principles = [
        match.group("filename") for match in PRINCIPLE_PATH_RE.finditer(intro_text)
    ]
    if intro_principles != ["train-parts-exploded.svg"]:
        reporter.add(
            intro_path,
            "must contain exactly one train-parts-exploded.svg diagram "
            f"(found {intro_principles})",
        )

    principle_locations: dict[str, list[str]] = {}
    marker_locations: dict[str, str] = {}
    raw_chapter_principles: list[str] = []
    for chapter_name in CARD_CHAPTERS:
        path = ROOT / chapter_name
        text = texts.get(path, "")
        route_picker_count = text.count(ROUTE_PICKER_SUMMARY)
        if route_picker_count != 1:
            reporter.add(
                path,
                f"must contain exactly one folded route picker "
                f"(found {route_picker_count})",
            )
        route_targets = re.findall(r"\]\(#train-(\d{3})\)", text)
        if not route_targets:
            reporter.add(path, "folded route picker must link at least one train card")
        for target in route_targets:
            if f'<a id="train-{target}"></a>' not in text:
                reporter.add(
                    path,
                    f"route picker links #train-{target}, but that anchor is not "
                    "in this chapter",
                )
        chapter_principles = [
            match.group("filename") for match in PRINCIPLE_PATH_RE.finditer(text)
        ]
        raw_chapter_principles.extend(chapter_principles)
        if not chapter_principles:
            reporter.add(path, "must contain at least one integrated principle SVG")

        marker_tokens = list(INTEGRATED_MARKER_RE.finditer(text))
        marker_blocks = list(INTEGRATED_BLOCK_RE.finditer(text))
        raw_marker_count = text.count("<!-- integrated-learning:")
        if raw_marker_count != len(marker_tokens):
            reporter.add(
                path,
                "contains an integrated-learning marker that does not use the "
                "after-NNN start/end format",
            )
        if len(marker_tokens) != 2 * len(marker_blocks):
            reporter.add(
                path,
                f"integrated-learning markers are not paired "
                f"({len(marker_tokens)} markers, {len(marker_blocks)} complete blocks)",
            )

        for block_match in marker_blocks:
            number = block_match.group("number")
            body = block_match.group("body")
            marker_line = line_at(text, block_match.start())
            previous_cards = list(CARD_HEADING_RE.finditer(text, 0, block_match.start()))
            if not previous_cards or previous_cards[-1].group("number") != number:
                previous_number = (
                    previous_cards[-1].group("number") if previous_cards else "none"
                )
                reporter.add(
                    path,
                    f"principle after {number} must immediately follow card {number}; "
                    f"last preceding card is {previous_number}",
                    marker_line,
                )

            if number in marker_locations:
                reporter.add(
                    path,
                    f"principle marker after card {number} is duplicated; first seen in "
                    f"{marker_locations[number]}",
                    marker_line,
                )
            else:
                marker_locations[number] = chapter_name

            principle_paths = [
                match.group("filename") for match in PRINCIPLE_PATH_RE.finditer(body)
            ]
            if len(principle_paths) != 1:
                reporter.add(
                    path,
                    f"principle after card {number} must contain exactly one SVG "
                    f"(found {principle_paths})",
                    marker_line,
                )
            else:
                filename = principle_paths[0]
                principle_locations.setdefault(filename, []).append(chapter_name)
                expected_filename = EXPECTED_PRINCIPLE_AFTER_CARD.get(number)
                if expected_filename is None:
                    reporter.add(
                        path,
                        f"card {number} is not an approved principle attachment point",
                        marker_line,
                    )
                elif filename != expected_filename:
                    reporter.add(
                        path,
                        f"principle after card {number} uses {filename}; expected "
                        f"{expected_filename}",
                        marker_line,
                    )

            principle_headings = re.findall(r"^### 🔍 .+$", body, re.MULTILINE)
            if len(principle_headings) != 1:
                reporter.add(
                    path,
                    f"principle after card {number} must have exactly one child-facing "
                    f"'### 🔍' heading (found {len(principle_headings)})",
                    marker_line,
                )
            for label, count in (
                ("grownup summary", body.count(PRINCIPLE_GROWNUP_SUMMARY)),
                ("<details> opening tag", body.count("<details>")),
                ("</details> closing tag", body.count("</details>")),
            ):
                if count != 1:
                    reporter.add(
                        path,
                        f"principle after card {number} must have exactly one {label} "
                        f"(found {count})",
                        marker_line,
                    )
            if CARD_GROWNUP_SUMMARY in body:
                reporter.add(
                    path,
                    f"principle after card {number} uses the card-level grownup summary",
                    marker_line,
                )
            if "images/principles/generated/" in body and "不是实拍" not in body:
                reporter.add(
                    path,
                    f"generated cutaway after card {number} must say '不是实拍'",
                    marker_line,
                )

        matched_principles = [
            filename
            for block_match in marker_blocks
            for filename in (
                match.group("filename")
                for match in PRINCIPLE_PATH_RE.finditer(block_match.group("body"))
            )
        ]
        if Counter(matched_principles) != Counter(chapter_principles):
            reporter.add(
                path,
                "every principle SVG in a train chapter must live inside exactly one "
                "after-card learning block",
            )

    expected_marker_numbers = set(EXPECTED_PRINCIPLE_AFTER_CARD)
    actual_marker_numbers = set(marker_locations)
    missing_marker_numbers = sorted(expected_marker_numbers - actual_marker_numbers)
    unexpected_marker_numbers = sorted(actual_marker_numbers - expected_marker_numbers)
    if missing_marker_numbers:
        reporter.add(
            "integrated learning",
            "missing after-card principle markers: " + ", ".join(missing_marker_numbers),
        )
    if unexpected_marker_numbers:
        reporter.add(
            "integrated learning",
            "unexpected after-card principle markers: "
            + ", ".join(unexpected_marker_numbers),
        )

    principle_dir = ROOT / "images" / "principles"
    expected_child_principles = {
        path.relative_to(principle_dir).as_posix()
        for path in principle_dir.rglob("*.svg")
        if path.relative_to(principle_dir).as_posix()
        != "train-parts-exploded.svg"
    }
    actual_child_principles = set(principle_locations)
    missing = sorted(expected_child_principles - actual_child_principles)
    extra = sorted(actual_child_principles - expected_child_principles)
    if missing:
        reporter.add(
            "integrated learning",
            "principle SVGs missing from train chapters: " + ", ".join(missing),
        )
    if extra:
        reporter.add(
            "integrated learning",
            "unexpected principle SVGs in train chapters: " + ", ".join(extra),
        )
    for filename, locations in sorted(principle_locations.items()):
        if len(locations) != 1:
            reporter.add(
                "integrated learning",
                f"principle SVG {filename} occurs in {len(locations)} train chapters: "
                + ", ".join(locations),
            )

    if len(raw_chapter_principles) != len(EXPECTED_PRINCIPLE_AFTER_CARD):
        reporter.add(
            "integrated learning",
            f"train chapters must contain exactly {len(EXPECTED_PRINCIPLE_AFTER_CARD)} "
            f"principle SVG references (found {len(raw_chapter_principles)})",
        )

    for number in sorted(EXPECTED_CARD_NUMBERS):
        anchor = f'<a id="train-{number}"></a>'
        count = sum(texts.get(ROOT / chapter_name, "").count(anchor) for chapter_name in CARD_CHAPTERS)
        if count != 1:
            reporter.add(
                "train-card anchors",
                f"{anchor} must occur exactly once across train chapters (found {count})",
            )

    for retired_name in ("00_for_grownups.md", "13_spotter_games.md"):
        retired_path = ROOT / retired_name
        if retired_path.exists():
            reporter.add(retired_path, "retired chapter must not exist")

    for chapter_name in NUMBERED_CHAPTERS:
        path = ROOT / chapter_name
        text = texts.get(path, "")
        if "🎲" in text or "本章游戏" in text:
            reporter.add(path, "retired game content is still present")


def main() -> int:
    reporter = Reporter()
    texts: dict[Path, str] = {}
    headings: dict[Path, list[tuple[int, int]]] = {}
    references: dict[Path, list[Reference]] = {}

    markdown_paths = sorted(ROOT.rglob("*.md"))
    if not markdown_paths:
        reporter.add(ROOT, "no Markdown files found")
    for path in markdown_paths:
        text = read_utf8(path, reporter)
        if text is None:
            continue
        texts[path] = text
        file_headings, content_lines = scan_markdown(path, text, reporter)
        headings[path] = file_headings
        references[path] = collect_references(path, content_lines, reporter)

    check_chapters(texts, headings, references, reporter)
    cards = collect_cards(texts, reporter)
    check_credit_anchors(cards, texts, reporter)
    image_count = check_image_inventory(cards, reporter)
    check_integrated_learning(texts, reporter)
    principle_svg_count, principle_photo_count, generated_principle_count = (
        check_principle_assets(texts, references, reporter)
    )
    return reporter.finish(
        cards=len(cards),
        images=image_count,
        principle_svgs=principle_svg_count,
        principle_photos=principle_photo_count,
        generated_principles=generated_principle_count,
    )


if __name__ == "__main__":
    raise SystemExit(main())
