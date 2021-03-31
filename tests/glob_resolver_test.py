import unittest

from cached_task._cache.cache import resolve_globs


class GlobResolverTest(unittest.TestCase):
    def test_glob(self):
        result = resolve_globs(
            [
                "tests/**",
                "!**/*.pyc",
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
                "!**/*.pyc",
            ]
        )

        expected_result = [
            "tests/__init__.py",
            "tests/cached_task_test.py",
            "tests/simple.txt",
        ]

        self.assertEqual(expected_result, result)

    def test_only_files_get_included(self):
        result = resolve_globs(
            [
                "tests/**",
                "!**/*.pyc",
            ]
        )

        expected_result = [
            "tests/__init__.py",
            "tests/cached_task_test.py",
            "tests/glob_resolver_test.py",
            "tests/nested_folder/nested-file.txt",
            "tests/simple.txt",
        ]

        self.assertEqual(expected_result, result)
