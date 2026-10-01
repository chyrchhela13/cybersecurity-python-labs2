import json
import logging
import re
from collections import Counter
from pathlib import Path

LOGGER = logging.getLogger(__name__)

MASK_PATTERNS = (
    ("U", re.compile(r"[A-Z]")),
    ("l", re.compile(r"[a-z]")),
    ("d", re.compile(r"[0-9]")),
    ("w", re.compile(r"\s")),
    ("u", re.compile(r"[^\W\d_]", re.UNICODE)),
)


def iter_passwords(path: Path):
    with path.open("r", encoding="utf-8-sig") as source:
        for line in source:
            password = line.rstrip("\r\n")
            if password:
                yield password


def password_mask(password: str) -> str:
    result = []
    previous = None

    for character in password:
        category = "s"

        for symbol, pattern in MASK_PATTERNS:
            if pattern.fullmatch(character):
                category = symbol
                break

        if category != previous:
            result.append(category)
            previous = category

    return "".join(result)


def run_analysis(wordlist: Path, min_length: int, top_masks: int, output: Path):
    if min_length <= 0 or top_masks <= 0:
        raise ValueError("Числові параметри мають бути додатними")

    if wordlist.resolve() == output.resolve():
        raise ValueError("Вхідний файл і файл звіту мають відрізнятися")

    if output.exists() and wordlist.exists() and output.samefile(wordlist):
        raise ValueError("Вхідний файл і файл звіту мають відрізнятися")

    total = 0
    total_length = 0
    weak = 0
    masks = Counter()

    LOGGER.info("Читання словника: %s", wordlist)

    for password in iter_passwords(wordlist):
        total += 1
        total_length += len(password)
        weak += len(password) < min_length
        masks[password_mask(password)] += 1

        if total % 10_000 == 0:
            LOGGER.info("Оброблено паролів: %d", total)

    LOGGER.info("Оброблено паролів: %d", total)

    if total == 0:
        LOGGER.warning("Словник порожній")

    ranked = sorted(masks.items(), key=lambda item: (-item[1], item[0]))

    statistics = {
        "variant": 6,
        "source": str(wordlist),
        "total_passwords": total,
        "min_length": min_length,
        "weak_passwords": weak,
        "weak_percent": round(weak / total * 100, 2) if total else 0.0,
        "average_length": round(total_length / total, 2) if total else 0.0,
        "mask_counts": dict(ranked),
        "top_masks": [
            {
                "mask": mask,
                "count": count,
                "percent": round(count / total * 100, 2),
            }
            for mask, count in ranked[:top_masks]
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as destination:
        json.dump(statistics, destination, ensure_ascii=False, indent=2)
        destination.write("\n")

    LOGGER.info("Звіт збережено: %s", output)

    print("=== Аудит словника паролів: варіант 6 ===")
    print(f"Усього паролів: {total}")
    print(
        f"Слабких (довжина < {min_length}): {weak} "
        f"({statistics['weak_percent']:.2f}%)"
    )
    print(f"Середня довжина: {statistics['average_length']:.2f}")
    print(f"=== Топ-{top_masks} масок ===")

    for index, entry in enumerate(statistics["top_masks"], start=1):
        print(
            f"{index}. {entry['mask']}: {entry['count']} "
            f"({entry['percent']:.2f}%)"
        )