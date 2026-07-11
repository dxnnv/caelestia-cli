import re
from functools import lru_cache

# (?L) is intentionally excluded, as local matching is
# discouraged and Unicode matching is instead preferred.
_PREFIX_FLAGS = re.compile(r"^(?P<anchor>\^?)(?P<groups>(?:\(\?[aimsux]+\))+)")

def normalize_regex_flags(pattern_string: str) -> str:
    match = _PREFIX_FLAGS.match(pattern_string)
    if match is None:
        return pattern_string

    groups = match.group("groups")
    flags = re.findall(r"\(\?([aiLmsux]+)\)", groups)

    # Deduplicate while keeping flag order
    combined = "".join(
        flag
        for flag in "aiLmsux"
        if any(flag in group for group in flags)
    )

    remainder = pattern_string[match.end():]
    anchor = match.group("anchor")

    return f"(?{combined}){anchor}{remainder}"

@lru_cache(maxsize=256)
def parse_pattern(pattern_str) -> re.Pattern[str] | None:
    normalized = normalize_regex_flags(pattern_str)

    try:
        pattern = re.compile(normalized)
        return pattern
    except re.error:
        return None


def regex_matches(pattern_str, text) -> bool:
    pattern = parse_pattern(pattern_str)
    return pattern is not None and pattern.fullmatch(text) is not None
