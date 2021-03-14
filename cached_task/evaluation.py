import re
from typing import Any, Dict, Tuple, Optional, Iterable

from cached_task import RESOLVED_PARAMETERS, PARAMETERS, OUTPUTS

VARIABLE_RE = re.compile(r"{(.*?)}")


def resolve_cache_parameters(
    input_params: PARAMETERS, args: Tuple[Any, ...], kw: Dict[str, Any]
) -> RESOLVED_PARAMETERS:
    """
    Resolves the values of the parameters to be cached, against
    the actual parameters of the call.
    """
    if not input_params:
        return None

    if not kw and not args:
        raise Exception(
            f"Unable to resolve parameters {input_params}, since no params "
            f"are available for the function."
        )

    if isinstance(input_params, str):
        input_params = [input_params]

    result = []

    context = dict(kw)
    context["args"] = args

    for input_param in input_params:
        result.append(str(eval(input_param, context, context)))

    return result


def get_output_names(
    outputs: OUTPUTS, args: Tuple[Any, ...], kw: Dict[str, Any]
) -> Optional[Iterable[str]]:
    """
    Creates the glob expressions from the given input parameters.
    """
    if not outputs:
        return None

    if isinstance(outputs, str):
        outputs = [outputs]

    found_variable_output_name = False

    for output in outputs:
        if "{" in output:
            found_variable_output_name = True
            break

    if not found_variable_output_name:
        return outputs

    result = []
    context = dict(kw)
    context["args"] = args

    def replace_function(m):
        return str(eval(m.group(1), context, context))

    for output in outputs:
        output_replaced = VARIABLE_RE.sub(replace_function, output)
        result.append(output_replaced)

    return result
