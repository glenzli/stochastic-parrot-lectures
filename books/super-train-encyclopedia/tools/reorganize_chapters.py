#!/usr/bin/env python3
"""Rebuild train-card chapters around child-facing themes and discoveries.

Card numbers and child-facing card bodies stay unchanged. Integrated principle
reveals are inserted from ``integrated_learning.py`` after the relevant card.
The script is intentionally strict so that a missing card or learning block
stops the rebuild instead of silently dropping content.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from integrated_learning import (
    LEARNING_BLOCKS_AFTER_CARD,
    validate_learning_blocks,
)


ROOT = Path(__file__).resolve().parents[1]

OLD_CARD_FILES = (
    "02_steam_pioneers.md",
    "03_electric_diesel_streamliners.md",
    "04_world_high_speed.md",
    "05_shinkansen_family.md",
    "06_japan_everyday.md",
    "07_japan_special_trains.md",
    "08_work_trains.md",
    "09_unusual_railways.md",
    "11_more_trains.md",
    "12_nankai_trains.md",
    "13_china_trains.md",
)

CARD_START_RE = re.compile(r"^## (?P<number>\d{3})｜", re.MULTILINE)
RAW_ADULT_NOTE_RE = re.compile(r"^> 给大人：(?P<body>[^\n]+)$", re.MULTILINE)
ADULT_NOTE_SUMMARY = "<summary>🔎 给大人看细节</summary>"


def fold_card_adult_note(block: str, number: int) -> str:
    """Fold one card's adult note exactly once."""
    raw_notes = list(RAW_ADULT_NOTE_RE.finditer(block))
    folded_notes = block.count(ADULT_NOTE_SUMMARY)

    if len(raw_notes) == 1 and folded_notes == 0:
        adult_body = raw_notes[0].group("body")
        folded = (
            "<details>\n"
            f"{ADULT_NOTE_SUMMARY}\n\n"
            f"{adult_body}\n\n"
            "</details>"
        )
        return RAW_ADULT_NOTE_RE.sub(folded, block, count=1)

    if len(raw_notes) == 0 and folded_notes == 1:
        if block.count("<details>") != 1 or block.count("</details>") != 1:
            raise RuntimeError(
                f"card {number:03d} has a malformed folded adult note"
            )
        return block

    raise RuntimeError(
        f"card {number:03d} must have exactly one raw or folded adult note; "
        f"raw={len(raw_notes)}, folded={folded_notes}"
    )


@dataclass(frozen=True)
class Station:
    title: str
    cards: tuple[int, ...]


@dataclass(frozen=True)
class Chapter:
    number: int
    filename: str
    title: str
    short_title: str
    intro: str
    stations: tuple[Station, ...]

    @property
    def cards(self) -> tuple[int, ...]:
        return tuple(number for station in self.stations for number in station.cards)


CHAPTERS = (
    Chapter(
        2,
        "02_steam_origins.md",
        "第二章：呼哧呼哧，火车从蒸汽开始",
        "蒸汽火车的诞生",
        "最早的机车像装上轮子的锅炉。后来，它们学会拉煤、拉客车，也长成了真正的钢铁巨人。我们从 1804 年出发，看看蒸汽火车怎样一步步长大。",
        (
            Station("锅炉第一次装上轮子", (1, 2, 3, 4)),
            Station("蒸汽火车去看世界", (5, 6, 7)),
            Station("为山路和重载想办法", (8, 9)),
            Station("速度明星与钢铁巨人", (10, 11, 12, 13, 14)),
        ),
    ),
    Chapter(
        3,
        "03_power_revolution.md",
        "第三章：电力、柴油和新能量",
        "电力、柴油和新能量",
        "火车不只会烧煤。它们学会从电线取电，让柴油机带着发电机工作，还把电装进电池，试着使用氢能。把这些车放在一起，就能看见动力怎样一次次换新办法。",
        (
            Station("电先出发", (15, 17)),
            Station("柴油快车和老地铁", (19, 20, 22)),
            Station("把新能量装进车上", (121, 123, 127, 96, 122)),
        ),
    ),
    Chapter(
        4,
        "04_high_speed_pioneers.md",
        "第四章：高速列车怎样长大",
        "高速列车怎样长大",
        "1964 年，圆鼻子的 0 系把高速铁路故事推到新一页。后来，英国、法国、德国、西班牙、中国等地也接力前进。本章挑出各地发展路上的关键一站，按出生年代看看高速列车怎样长大。",
        (
            Station("高速时代的第一棒", (42, 25, 29, 43, 44)),
            Station("更多国家加入接力", (30, 31, 45, 32)),
            Station("跨进新世纪", (48, 52, 33, 34, 54)),
            Station("中国与台湾的新伙伴", (36, 37, 151, 150, 38)),
        ),
    ),
    Chapter(
        5,
        "05_high_speed_specialists.md",
        "第五章：高速列车各有绝招",
        "高速列车各有绝招",
        "高速列车不只是鼻子长。有的能在普通山路线上前进，有的叠成两层，有的会检查轨道，还有的专门挑战未来速度。一起找找每辆快车最特别的本领。",
        (
            Station("迷你新干线", (46, 50, 57, 62)),
            Station("双层大个子", (47, 51)),
            Station("雪国与长隧道", (49, 56, 58, 59)),
            Station("高速也有不同长相", (35, 39, 40, 55)),
            Station("新一代高速伙伴", (41, 61, 152)),
            Station("医生、样车和试验车", (53, 60, 160)),
        ),
    ),
    Chapter(
        6,
        "06_city_trains.md",
        "第六章：城市里的站站停",
        "城市里的站站停",
        "城市列车常常开门、关门，再开向下一站。地铁钻进地底，有轨电车穿过街道，通勤电车一次接走许多人。它们的脸和车门不一样，工作却都很忙。",
        (
            Station("日本通勤长队", (63, 64, 65, 66, 67)),
            Station("世界大城市伙伴", (137, 139, 141, 159)),
            Station("地铁钻进地下", (69, 70, 114, 71)),
            Station("电车穿过街道", (28, 75)),
            Station("私铁的新朋友", (130, 131, 134)),
        ),
    ),
    Chapter(
        7,
        "07_regional_trains.md",
        "第七章：穿过田野、海边和小城",
        "地方与区域列车",
        "离开大城市，列车会穿过雪地、稻田、海岸和许多小站。它们不一定最快，却把每天上学、上班和回家的人送到很远。窗外的风景，也是这章的一部分。",
        (
            Station("穿过雪国和群山", (124, 142)),
            Station("城市之间快进快出", (125, 156, 126, 68, 74)),
            Station("田野、海边和小巷", (128, 136, 129)),
        ),
    ),
    Chapter(
        8,
        "08_express_airport.md",
        "第八章：去机场和远方的特急",
        "机场与远方特急",
        "有些列车少停几站，带大家去机场、另一座城市或很远的目的地。它们有的会倾斜过弯，有的能和普通车厢牵手，还有的把行李和座位安排得特别舒服。",
        (
            Station("特急老前辈", (76, 77, 79, 80)),
            Station("往机场冲的快车", (72, 132)),
            Station("会倾斜过弯", (82, 84, 91)),
            Station("南海小伙伴", (133, 143, 144, 148)),
            Station("看窗和坐得舒服", (73, 93, 94, 97, 135)),
            Station("世界城际车", (140, 153)),
        ),
    ),
    Chapter(
        9,
        "09_sleeper_scenic.md",
        "第九章：会睡觉、看风景和变装",
        "卧铺、观光与角色列车",
        "坐火车有时不只是赶路。有人在车上睡觉，有人望着森林和大海，还有列车穿上卡通、木头或小鱼的新衣服。慢慢看，它们把旅程本身变成了目的地。",
        (
            Station("车上睡一晚", (16, 83, 88)),
            Station("大窗把风景装进来", (81, 87, 89, 95)),
            Station("展望席三代", (78, 86, 92)),
            Station("角色和彩绘列车", (85, 90, 149)),
        ),
    ),
    Chapter(
        10,
        "10_work_trains.md",
        "第十章：火车头和铁路工作队",
        "火车头和铁路工作队",
        "有些列车把动力分在许多节车厢里；有些火车头自己不装乘客，专门拉着客车或货车前进。除雪车和工程车还会照顾铁路。想找跑在高速线上的检测车，可以去[第五章](05_high_speed_specialists.md)看看黄色医生。",
        (
            Station("火车头老前辈", (18, 21, 23, 24)),
            Station("世界火车头", (26, 99, 154, 155)),
            Station("搬大箱子", (100, 101)),
            Station("除雪和修路", (98, 102)),
        ),
    ),
    Chapter(
        11,
        "11_unusual_guideways.md",
        "第十一章：骑梁、倒挂、胶轮和磁浮",
        "特别的导轨列车",
        "两根钢轨不是唯一的路线。有的车骑在梁上，有的挂在轨道下面，有的穿着橡胶鞋，还有的被磁力托起来。先找轨道在哪里，再猜它怎样前进。",
        (
            Station("倒挂在轨道下面", (103, 106, 107)),
            Station("骑在轨道梁上", (104, 105, 157)),
            Station("被磁力托起来", (108, 109, 110, 158)),
            Station("穿橡胶鞋走导轨", (111, 112, 113, 138)),
        ),
    ),
    Chapter(
        12,
        "12_mountain_railways.md",
        "第十二章：爬山的火车",
        "爬山的火车",
        "山地列车不都使用齿轨或缆索。有的仍靠普通钢轮，沿着弯道和缓一些的坡慢慢升高；有的让齿轮咬住齿轨，还有的由缆索拉动。把这些办法放在一起，看看火车怎样从山脚走向山顶。",
        (
            Station("钢轮沿山路慢慢爬", (115, 145, 146, 147)),
            Station("齿轮咬住中间齿轨", (27, 116)),
            Station("缆索拉上山", (117, 118, 120)),
            Station("又吊着、又被缆索拉", (119,)),
        ),
    ),
)


def extract_cards() -> dict[int, str]:
    cards: dict[int, str] = {}
    candidates = {ROOT / name for name in OLD_CARD_FILES}
    candidates.update(ROOT / chapter.filename for chapter in CHAPTERS)

    for path in sorted(candidates):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        matches = list(CARD_START_RE.finditer(text))
        for index, match in enumerate(matches):
            number = int(match.group("number"))
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[match.start() : end]
            block = re.split(r"\n---[ \t]*(?:\n|\Z)", block, maxsplit=1)[0].rstrip()
            block = fold_card_adult_note(block, number)
            previous = cards.get(number)
            if previous is not None and previous != block:
                raise RuntimeError(f"card {number:03d} has conflicting copies")
            cards[number] = block

    expected = set(range(1, 161))
    actual = set(cards)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RuntimeError(f"card inventory mismatch; missing={missing}, extra={extra}")
    return cards


def validate_mapping() -> dict[int, int]:
    card_to_chapter: dict[int, int] = {}
    for chapter in CHAPTERS:
        for number in chapter.cards:
            if number in card_to_chapter:
                raise RuntimeError(
                    f"card {number:03d} appears in chapters "
                    f"{card_to_chapter[number]} and {chapter.number}"
                )
            card_to_chapter[number] = chapter.number

    expected = set(range(1, 161))
    actual = set(card_to_chapter)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RuntimeError(f"chapter mapping mismatch; missing={missing}, extra={extra}")
    return card_to_chapter


def navigation(index: int) -> str:
    chapter = CHAPTERS[index]
    if index == 0:
        previous = "[← 把火车拆开看看](01_how_trains_move.md)"
    else:
        before = CHAPTERS[index - 1]
        previous = f"[← {before.short_title}]({before.filename})"

    links = [previous, "[🏠 全书首页](README.md)"]
    if index + 1 < len(CHAPTERS):
        after = CHAPTERS[index + 1]
        links.append(f"[{after.short_title} →]({after.filename})")
    return " · ".join(links)


def render_chapter(index: int, cards: dict[int, str]) -> str:
    chapter = CHAPTERS[index]
    nav = navigation(index)
    route = "\n".join(
        f"- [🚉 第{station_index}站：{station.title}]"
        f"(#train-{station.cards[0]:03d})（{len(station.cards)} 辆车）"
        for station_index, station in enumerate(chapter.stations, start=1)
    )
    route_picker = (
        "<details>\n"
        "<summary>🚉 选一个小站</summary>\n\n"
        "今天挑一个小站就好，不用一次看完。\n\n"
        f"{route}\n\n"
        "</details>"
    )
    station_sections = []
    for station_index, station in enumerate(chapter.stations, start=1):
        card_sections = []
        for number in station.cards:
            anchored_card = f'<a id="train-{number:03d}"></a>\n\n{cards[number]}'
            learning = LEARNING_BLOCKS_AFTER_CARD.get(number)
            if learning:
                anchored_card += (
                    "\n\n---\n\n"
                    f"<!-- integrated-learning:after-{number:03d}:start -->\n"
                    f"{learning.rstrip()}\n"
                    f"<!-- integrated-learning:after-{number:03d}:end -->"
                )
            card_sections.append(anchored_card)
        station_body = "\n\n---\n\n".join(card_sections)
        station_section = (
            f"> 🚉 **第{station_index}站｜{station.title}**\n\n{station_body}"
        )
        station_sections.append(station_section)
    body = "\n\n---\n\n".join(station_sections)
    return (
        f"# {chapter.title}\n\n"
        f"{nav}\n\n"
        f"{chapter.intro}\n\n"
        "看到 **🔍 打开看看**，可以停下来拆开一个小秘密，也可以先跳过继续看车。\n\n"
        f"{route_picker}\n\n"
        f"{body}\n\n"
        "---\n\n"
        f"{nav}\n"
    )


def update_metadata(card_to_chapter: dict[int, int]) -> None:
    metadata_path = ROOT / "image_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    for item in metadata:
        match = re.match(r"t(?P<number>\d{3})-", item["id"])
        if not match:
            continue
        number = int(match.group("number"))
        item["chapter"] = f"{card_to_chapter[number]:02d}"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    targets_path = ROOT / "tools" / "image_targets.json"
    targets = targets_path.read_text(encoding="utf-8")

    def replace_target(match: re.Match[str]) -> str:
        number = int(match.group("number"))
        chapter = card_to_chapter[number]
        return f'{match.group("prefix")}{chapter:02d}{match.group("suffix")}'

    target_re = re.compile(
        r'(?P<prefix>"id":"t(?P<number>\d{3})-[^"\n]+"[^\n]*?"chapter":")'
        r'\d+(?P<suffix>")'
    )
    targets, count = target_re.subn(replace_target, targets)
    if count != 160:
        raise RuntimeError(f"updated {count} image targets instead of 160")
    targets_path.write_text(targets, encoding="utf-8")


def remove_old_files() -> None:
    keep = {chapter.filename for chapter in CHAPTERS}
    for name in (
        *OLD_CARD_FILES,
        "00_for_grownups.md",
        "10_spotter_games.md",
        "13_spotter_games.md",
    ):
        if name in keep:
            continue
        path = ROOT / name
        if path.exists():
            path.unlink()


def main() -> None:
    validate_learning_blocks()
    cards = extract_cards()
    card_to_chapter = validate_mapping()
    unexpected_learning_cards = sorted(
        set(LEARNING_BLOCKS_AFTER_CARD) - set(card_to_chapter)
    )
    if unexpected_learning_cards:
        raise RuntimeError(
            f"learning blocks point to unknown cards: {unexpected_learning_cards}"
        )
    for index, chapter in enumerate(CHAPTERS):
        (ROOT / chapter.filename).write_text(
            render_chapter(index, cards),
            encoding="utf-8",
        )
    update_metadata(card_to_chapter)
    remove_old_files()

    counts = ", ".join(
        f"{chapter.number:02d}:{len(chapter.cards)}" for chapter in CHAPTERS
    )
    print(
        "Reorganized 160 cards with 24 card-anchored principles across "
        f"11 chapters ({counts})."
    )


if __name__ == "__main__":
    main()
