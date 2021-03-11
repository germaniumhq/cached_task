import os
import shutil
import time
import unittest

from cached_task import cached


class CachedTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.executed_count = 0
        shutil.rmtree("/tmp/.cache", ignore_errors=True)

        if os.path.exists("simple-out.txt"):
            os.remove("simple-out.txt")

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

        # file gets created + cached
        cached_code()

        # we remove the original output
        os.remove("simple-out.txt")

        # file should get restored from the cache
        cached_code()

        self.assertEqual(1, self.executed_count)
        self.assertTrue(os.path.isfile("simple-out.txt"))

        with open("simple-out.txt", "rt", encoding="utf-8") as f:
            simple_out_content = f.read()

        self.assertEqual("content", simple_out_content)
        timestamp = os.path.getmtime("simple-out.txt")

        time.sleep(0.001)

        # file should stay unchanged
        cached_code()
        timestamp2 = os.path.getmtime("simple-out.txt")

        self.assertEqual(timestamp, timestamp2)
