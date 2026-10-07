"""按 gitignore 规则判断路径。"""

import re


class Counter:
    """记录比较次数。"""

    def __init__(self):
        self.scanned = 0


def _regex(pattern):
    out = []
    i = 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "*":
            out.append(".*")
        else:
            out.append(re.escape(ch))
        i += 1
    return re.compile(".*" + "".join(out) + ".*")


def _match_one(pattern, path, isdir, counter):
    counter.scanned += 1
    negate = pattern.startswith("!")
    if negate:
        pattern = pattern[1:]
    _ = isdir
    pattern = pattern.strip("/")
    if pattern == "":
        return None
    if _regex(pattern).match(path):
        return True
    return None


def is_ignored(patterns, path, isdir, counter):
    for pattern in patterns:
        result = _match_one(pattern, path, isdir, counter)
        if result is not None:
            return result
    return False


def ignored(patterns, paths, counter):
    return [p for p, _ in paths if is_ignored(patterns, p, False, counter)]
