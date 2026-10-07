"""按 gitignore 规则判断路径。"""

import functools
import re


class Counter:
    """记录比较次数。"""

    def __init__(self):
        self.scanned = 0


def _is_literal(segment):
    return "*" not in segment and "?" not in segment and "[" not in segment


def _translate(body):
    """把 gitignore 通配模式翻译成正则：* 不跨 /，** 跨目录。"""
    out = []
    i = 0
    n = len(body)
    while i < n:
        ch = body[i]
        if ch == "*":
            if body[i:i + 2] == "**":
                if body[i:i + 3] == "**/":
                    out.append("(?:.*/)?")
                    i += 3
                    continue
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
        elif ch == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(ch))
        i += 1
    return re.compile("".join(out) + r"\Z")


class _Rule:
    __slots__ = ("order", "negate", "dir_only", "anchored", "regex", "key")

    def __init__(self, order, raw):
        self.order = order
        body = raw
        self.negate = body.startswith("!")
        if self.negate:
            body = body[1:]
        self.dir_only = body.endswith("/")
        if self.dir_only:
            body = body[:-1]
        self.anchored = body.startswith("/")
        if self.anchored:
            body = body[1:]
        if "/" in body:
            self.anchored = True
        if body:
            self.regex = _translate(body)
            if self.anchored:
                first = body.split("/", 1)[0]
                self.key = first if _is_literal(first) else None
            else:
                self.key = body if _is_literal(body) else None
        else:
            self.regex = None
            self.key = None


@functools.lru_cache(maxsize=None)
def _build_index(patterns):
    """按规则首段（或名字本身）建索引；无法索引的进全局桶。"""
    global_rules = []
    keyed = {}
    for order, raw in enumerate(patterns):
        rule = _Rule(order, raw)
        if rule.regex is None:
            continue
        if rule.key is None:
            global_rules.append(rule)
        else:
            keyed.setdefault(rule.key, []).append(rule)
    return tuple(global_rules), keyed


def _prefixes(path, isdir):
    """产出 (前缀, 前缀是否为目录)：所有祖先目录加上路径本身。"""
    parts = path.split("/")
    for i in range(1, len(parts)):
        yield "/".join(parts[:i]), True
    yield path, isdir


def _rule_matches(rule, path, isdir):
    for prefix, prefix_isdir in _prefixes(path, isdir):
        if rule.dir_only and not prefix_isdir:
            continue
        target = prefix if rule.anchored else prefix.rsplit("/", 1)[-1]
        if rule.regex.match(target):
            return True
    return False


def is_ignored(patterns, path, isdir, counter):
    global_rules, keyed = _build_index(tuple(patterns))
    path = path.strip("/")
    candidates = list(global_rules)
    seen = set()
    for segment in path.split("/"):
        if segment in seen:
            continue
        seen.add(segment)
        bucket = keyed.get(segment)
        if bucket:
            candidates.extend(bucket)
    best_order = -1
    result = False
    for rule in candidates:
        counter.scanned += 1
        if rule.order > best_order and _rule_matches(rule, path, isdir):
            best_order = rule.order
            result = not rule.negate
    return result


def ignored(patterns, paths, counter):
    return [p for p, isdir in paths if is_ignored(patterns, p, isdir, counter)]
