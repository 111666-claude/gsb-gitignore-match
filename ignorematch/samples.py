"""固定场景，用来复现题面里的锚点。"""

import json

from . import core


def _line(obj):
    print(json.dumps(obj, ensure_ascii=False))


def run(name):
    if name == "negate":
        out = core.is_ignored(["*.log", "!keep.log"], "keep.log", False, core.Counter())
        _line({"ignored": out})
        return 0
    if name == "star":
        out = core.is_ignored(["a/*.txt"], "a/b/c.txt", False, core.Counter())
        _line({"ignored": out})
        return 0
    if name == "anchor":
        out = core.is_ignored(["/a.txt"], "sub/a.txt", False, core.Counter())
        _line({"ignored": out})
        return 0
    if name == "dironly":
        out = core.is_ignored(["build/"], "build", False, core.Counter())
        _line({"ignored": out})
        return 0
    if name == "work":
        patterns = ["d%04d/" % i for i in range(800)]
        paths = [("d%04d/f.txt" % i, False) for i in range(800)]
        counter = core.Counter()
        core.ignored(patterns, paths, counter)
        _line({"rules": 800, "scanned": counter.scanned})
        return 0
    raise SystemExit("未知场景：" + name)
