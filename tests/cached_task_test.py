import os
import unittest

from cached_task import cached


class CachedTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.executed_count = 0

    def test_cache_create_marker(self):
        @cached(inputs=["simple.txt"])
        def cached_code():
            self.executed_count += 1

        for i in range(2):
            cached_code()

        self.assertEqual(1, self.executed_count)

    def test_cache_outputs_get_cached(self):
        @cached(inputs="simple.txt", outputs="simple-out.txt")
        def cached_code():
            self.executed_count += 1
            with open("simple-out.txt", "wt") as f:
                f.write("content")

        cached_code()

        os.remove("simple-out.txt")
        cached_code()

        self.assertEqual(1, self.executed_count)
        self.assertTrue(os.path.isfile("simple-out.txt"))

        with open("simple-out.txt", "rt", encoding="utf-8") as f:
            simple_out_content = f.read()

        self.assertEqual("content", simple_out_content)
