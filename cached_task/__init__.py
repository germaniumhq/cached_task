import functools
from typing import Callable, TypeVar

from cached_task.cache.file_cache import FileCache, INPUTS, OUTPUTS, RESOLVED_PARAMETERS, PARAMETERS
from cached_task.cache.local_file_cache import LocalFileCache
from cached_task.evaluation import resolve_parameters, get_output_names

T = TypeVar('T')

current_cache: FileCache = LocalFileCache()


def cached(
        inputs: INPUTS = None,
        params: PARAMETERS = None,
        outputs: OUTPUTS = None) -> Callable[..., Callable[..., T]]:
    """
    Invokes the code only if the inputs are not already cached. If they're cached,
    the files are simply written from the cache, and the wrapped function is not
    invoked.
    """
    def wrapper_builder(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def wrapper(*args, **kw) -> T:
            resolved_parameters = resolve_parameters(params, args, kw)
            hash_key = current_cache.get_hash_key(f, inputs, resolved_parameters)
            if current_cache.use_cached(hash_key):
                return None

            result = f(*args, **kw)
            outputs_names = get_output_names(outputs, args, kw)
            current_cache.cache_outputs(hash_key, outputs_names)

            return result

        return wrapper

    return wrapper_builder
