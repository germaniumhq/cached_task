import unittest

from cached_task._cache.cache import resolve_globs


class GlobResolverTest(unittest.TestCase):
    def test_glob(self):
        result = resolve_globs(
            [
                "tests/**",
            ]
        )

        expected_result = [
            "tests/__init__.py",
            "tests/cached_task_test.py",
            "tests/glob_resolver_test.py",
            "tests/simple.txt",
        ]

        self.assertEqual(expected_result, result)

    def test_exclude_in_glob(self):
        result = resolve_globs(
            [
                "tests/**",
                "!tests/glob_resolver_test.py",
            ]
        )

        expected_result = [
            "tests/__init__.py",
            "tests/cached_task_test.py",
            "tests/simple.txt",
        ]

        self.assertEqual(expected_result, result)
