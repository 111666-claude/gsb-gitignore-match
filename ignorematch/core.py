"""按 gitignore 规则判断路径。"""

import re


class Counter:
    """记录比较次数。"""

    def __init__(self):
        self.scanned = 0


class _Rule:
    __slots__ = ("order", "negate", "dir_only", "full_path", "regex")

    def __init__(self, order, negate, dir_only, full_path, regex):
        self.order = order
        self.negate = negate
        self.dir_only = dir_only
        self.full_path = full_path
        self.regex = regex


def _translate(body):
    """`*` 不跨 `/`，`**` 跨目录。"""
    out = []
    i = 0
    n = len(body)
    while i < n:
        ch = body[i]
        if ch == "*":
            if i + 1 < n and body[i + 1] == "*":
                out.append(".*")
                i += 2
            else:
                out.append("[^/]*")
                i += 1
        elif ch == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(ch))
            i += 1
    return "".join(out)


def _literal_key(body, full_path):
    """规则能按首段/名字建索引时返回字面键，否则返回 None。"""
    if full_path:
        head = body.split("/", 1)[0]
        if "*" not in head and "?" not in head:
            return head
        return None
    if "*" not in body and "?" not in body:
        return body
    return None


def _build(patterns):
    by_name = {}
    general = []
    for order, raw in enumerate(patterns):
        negate = raw.startswith("!")
        body = raw[1:] if negate else raw
        dir_only = body.endswith("/")
        if dir_only:
            body = body[:-1]
        anchored = body.startswith("/")
        if anchored:
            body = body[1:]
        if body == "":
            continue
        full_path = anchored or "/" in body
        regex = re.compile("^" + _translate(body) + "$")
        rule = _Rule(order, negate, dir_only, full_path, regex)
        key = _literal_key(body, full_path)
        if key is None:
            general.append(rule)
        else:
            by_name.setdefault(key, []).append(rule)
    return by_name, general


_index_cache = {}


def _index(patterns):
    key = tuple(patterns)
    built = _index_cache.get(key)
    if built is None:
        built = _build(patterns)
        _index_cache[key] = built
    return built


def is_ignored(patterns, path, isdir, counter):
    by_name, general = _index(patterns)
    parts = path.split("/")
    found = {}
    for rule in general:
        found[rule.order] = rule
    for part in parts:
        for rule in by_name.get(part, ()):
            found[rule.order] = rule
    candidates = [found[k] for k in sorted(found)]

    depth = len(parts)
    level = None
    for d in range(1, depth + 1):
        prefix_isdir = d < depth or isdir
        base = parts[d - 1]
        prefix = None
        level = None
        for rule in candidates:
            counter.scanned += 1
            if rule.dir_only and not prefix_isdir:
                continue
            if rule.full_path:
                if prefix is None:
                    prefix = "/".join(parts[:d])
                target = prefix
            else:
                target = base
            if rule.regex.match(target):
                level = not rule.negate
        if level:
            # 被忽略目录下的路径一定被忽略。
            return True
    return bool(level)


def ignored(patterns, paths, counter):
    return [p for p, isdir in paths if is_ignored(patterns, p, isdir, counter)]
