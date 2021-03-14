import re
from typing import List, Any, Dict, Tuple, Optional

from cached_task import RESOLVED_PARAMETERS, PARAMETERS, OUTPUTS


def resolve_parameters(input_params: PARAMETERS, args: Tuple[Any, ...], kw: Dict[str, Any]) -> RESOLVED_PARAMETERS:
    """
    Resolves the parameters against the current parameters called.
    """
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


def get_output_names(outputs: OUTPUTS, args: Tuple[Any, ...], kw: Dict[str, Any]) -> Optional[List[str]]:
    """
    Creates the glob expressions from the given input parameters.
    """
    if not outputs:
        return None

    if isinstance(outputs, str):
        outputs = [outputs]

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

