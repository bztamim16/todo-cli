import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path

import todo


class TodoTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        os.environ["TODO_FILE"] = str(Path(self.dir.name) / "todo.json")
        self.addCleanup(os.environ.pop, "TODO_FILE", None)

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            todo.main(list(argv))
        return out.getvalue()

    def test_empty_list(self):
        self.assertEqual(self.run_cli("list"), "Nothing to do!\n")

    def test_add_and_list(self):
        self.run_cli("add", "buy", "milk")
        self.run_cli("add", "walk the dog")
        self.assertEqual(self.run_cli(), "1. [ ] buy milk\n2. [ ] walk the dog\n")

    def test_done_hides_task_unless_all(self):
        self.run_cli("add", "buy milk")
        self.run_cli("add", "walk the dog")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("list"), "2. [ ] walk the dog\n")
        self.assertEqual(
            self.run_cli("list", "--all"), "1. [x] buy milk\n2. [ ] walk the dog\n"
        )

    def test_undo(self):
        self.run_cli("add", "buy milk")
        self.run_cli("done", "1")
        self.run_cli("undo", "1")
        self.assertEqual(self.run_cli("list"), "1. [ ] buy milk\n")

    def test_rm_does_not_reuse_lower_ids(self):
        self.run_cli("add", "one")
        self.run_cli("add", "two")
        self.run_cli("rm", "1")
        self.run_cli("add", "three")
        self.assertEqual(self.run_cli("list"), "2. [ ] two\n3. [ ] three\n")

    def test_clear_removes_only_completed(self):
        self.run_cli("add", "one")
        self.run_cli("add", "two")
        self.run_cli("done", "1")
        self.assertEqual(self.run_cli("clear"), "Cleared 1 completed task(s)\n")
        self.assertEqual(self.run_cli("list", "--all"), "2. [ ] two\n")

    def test_unknown_id_fails_without_saving(self):
        self.run_cli("add", "one")
        with self.assertRaises(SystemExit):
            self.run_cli("done", "1", "99")
        self.assertEqual(self.run_cli("list"), "1. [ ] one\n")


if __name__ == "__main__":
    unittest.main()
