import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ignorematch import core


class IgnoreMatchTest(unittest.TestCase):
    def test_simple_match(self):
        self.assertTrue(core.is_ignored(["*.log"], "a.log", False, core.Counter()))

    def test_no_match(self):
        self.assertFalse(core.is_ignored(["*.log"], "a.txt", False, core.Counter()))

    def test_empty_patterns(self):
        self.assertFalse(core.is_ignored([], "a.txt", False, core.Counter()))

    def test_dir_pattern_covers_child(self):
        self.assertTrue(core.is_ignored(["build/"], "build/f.txt", False, core.Counter()))

    def test_anchored_root_file(self):
        self.assertTrue(core.is_ignored(["/a.txt"], "a.txt", False, core.Counter()))

    def test_counter_counts(self):
        counter = core.Counter()
        core.is_ignored(["*.log"], "a.log", False, counter)
        self.assertGreater(counter.scanned, 0)


if __name__ == "__main__":
    unittest.main()
