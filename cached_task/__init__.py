import functools
from typing import Callable, TypeVar

from cached_task.cache.file_cache import FileCache, INPUTS, OUTPUTS
from cached_task.cache.local_file_cache import LocalFileCache

T = TypeVar('T')

current_cache: FileCache = LocalFileCache()


def cached(
        inputs: INPUTS,
        outputs: OUTPUTS = None) -> Callable[..., Callable[..., T]]:
    """
    Invokes the code only if the inputs are not already cached. If they're cached,
    the files are simply written from the cache, and the wrapped function is not
    invoked.
    """
    def wrapper_builder(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def wrapper(*args, **kw) -> T:
            hash_key = current_cache.get_hash_key(f, inputs)
            if current_cache.use_cached(hash_key):
                return None

            result = f(*args, **kw)
            current_cache.cache_outputs(hash_key, outputs)

            return result

        return wrapper

    return wrapper_builder
