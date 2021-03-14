import os
import shutil
import unittest

import time

from cached_task import cached


class Context:
    def __init__(self, name: str) -> None:
        self.nested = {"name": name}


class CachedTaskTest(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.executed_count = 0
        # FIXME: make the cache configurable
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
        @cached(
            inputs="simple.txt",
            params="args[0].nested['name']",
            outputs="simple-out-{args[0].nested['name']}.txt",
        )
        def cached_code(context: Context):
            self.executed_count += 1
            with open(f"simple-out-{context.nested['name']}.txt", "wt") as f:
                f.write("content")

        # file gets created + cached
        cached_code(Context("a"))
        cached_code(Context("b"))

        # we remove the original output
        os.remove("simple-out-a.txt")
        os.remove("simple-out-b.txt")

        # file should get restored from the cache
        cached_code(Context("a"))
        cached_code(Context("b"))

        self.assertEqual(2, self.executed_count)  # once for a, and once for b
        self.assertTrue(os.path.isfile("simple-out-a.txt"))

        with open("simple-out-a.txt", "rt", encoding="utf-8") as f:
            simple_out_content = f.read()

        self.assertEqual("content", simple_out_content)
        timestamp = os.path.getmtime("simple-out-a.txt")

        time.sleep(0.001)

        # file should stay unchanged
        cached_code(Context("a"))
        cached_code(Context("b"))
        timestamp2 = os.path.getmtime("simple-out-a.txt")

        self.assertEqual(timestamp, timestamp2)
