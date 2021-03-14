import functools
import re
from typing import Callable, TypeVar, Dict, Any, List, Optional

from cached_task.cache.file_cache import FileCache, INPUTS, OUTPUTS, RESOLVED_PARAMETERS, PARAMETERS
from cached_task.cache.local_file_cache import LocalFileCache

T = TypeVar('T')

current_cache: FileCache = LocalFileCache()


def resolve_parameters(args: List[Any], kw: Dict[str, Any], input_params: PARAMETERS) -> RESOLVED_PARAMETERS:
    if not input_params:
        return None

    if not kw and not args:
        raise Exception(f"Unable to resolve parameters {input_params}, since no params "
                        f"are available for the function.")

    if isinstance(input_params, str):
        input_params = [ input_params ]

    result = []

    context = dict(kw)
    context["args"] = args

    for input_param in input_params:
        result.append(str(eval(input_param, context, context)))

    return result


def get_output_names(outputs: OUTPUTS, args: List[Any], kw: Dict[str, Any]) -> Optional[List[str]]:
    if not outputs:
        return None

    if isinstance(outputs, str):
        outputs = [ outputs ]

    result = []
    context = dict(kw)
    context["args"] = args

    def replace_function(m):
        return str(eval(m.group(1), context, context))

    VARIABLE_RE = re.compile(r'{(.*?)}')

    for output in outputs:
        output_replaced = VARIABLE_RE.sub(replace_function, output)
        result.append(output_replaced)

    return result


def cached(
        input_files: INPUTS = None,
        input_params: PARAMETERS = None,
        outputs: OUTPUTS = None) -> Callable[..., Callable[..., T]]:
    """
    Invokes the code only if the inputs are not already cached. If they're cached,
    the files are simply written from the cache, and the wrapped function is not
    invoked.
    """
    def wrapper_builder(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def wrapper(*args, **kw) -> T:
            resolved_parameters = resolve_parameters(args, kw, input_params)
            hash_key = current_cache.get_hash_key(f, input_files, resolved_parameters)
            if current_cache.use_cached(hash_key):
                return None

            result = f(*args, **kw)
            outputs_names = get_output_names(outputs, args, kw)
            current_cache.cache_outputs(hash_key, outputs_names)

            return result

        return wrapper

    return wrapper_builder
