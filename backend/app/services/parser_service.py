import re


TASK_RULES = [
    {
        "label": "bad_sleep",
        "direction": "down",
        "patterns": ["bad sleep", "slept bad", "slept badly", "trash sleep"],
    },
    {
        "label": "small_talk",
        "direction": "down",
        "patterns": ["small talk", "strangers", "forced socializing", "forced socialising"],
    },
    {
        "label": "doomscrolling",
        "direction": "down",
        "patterns": ["doomscroll", "doomscrolled", "tiktok", "scrolling"],
    },
    {
        "label": "quiet_time",
        "direction": "up",
        "patterns": ["quiet time", "alone", "alone time"],
    },
    {
        "label": "music_session",
        "direction": "up",
        "patterns": ["music", "playlist", "listened to songs"],
    },
]


def normalize_log_text(text: str) -> str:
    normalized = text.strip().lower()
    normalized = re.sub(r"[\x00-\x1f\x7f]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def parse_log_text(text: str) -> list[dict[str, str]]:
    normalized = normalize_log_text(text)
    parsed_tasks = []
    seen_labels = set()

    for rule in TASK_RULES:
        if rule["label"] in seen_labels:
            continue

        for pattern in rule["patterns"]:
            if pattern in normalized:
                parsed_tasks.append(
                    {
                        "label": rule["label"],
                        "direction": rule["direction"],
                    }
                )
                seen_labels.add(rule["label"])
                break

    return parsed_tasks
