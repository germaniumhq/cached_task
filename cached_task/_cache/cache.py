import glob
import hashlib
import inspect
import io
import os
import textwrap
from typing import Set, Callable, List, Iterable, Optional
import logging

from cached_task import INPUTS, RESOLVED_PARAMETERS


LOG = logging.Logger(__name__)


def resolve_globs(globs: Optional[Iterable[str]]) -> List[str]:
    """
    Resolve a bunch of globs to an actual list of files. You
    can also exclude files from the set by prefixing the
    expression with `!`.
    """
    result: Set[str] = set()

    if not globs:
        return []

    if isinstance(globs, str):
        globs = [globs]

    for glob_path in globs:
        found_items = False
        is_glob_exclude = glob_path.startswith("!")
        is_glob_optional = glob_path.startswith("?") or is_glob_exclude

        glob_expression = (
            glob_path[1:] if is_glob_exclude or is_glob_optional else glob_path
        )

        for file_name in glob.iglob(glob_expression, recursive=True):
            found_items = True

            # Optional files should be optional, so not existing. This means we shouldn't
            # try to read hashes out of them later.
            if not os.path.exists(file_name) and is_glob_optional:
                continue

            # Folder entries are ignored, since there's nothing to hash.
            if os.path.isdir(file_name):
                continue

            if not is_glob_exclude:
                result.add(file_name)
                continue

            try:
                result.remove(file_name)
            except KeyError as e:
                LOG.info(f"{file_name} not found in {result}", e)

        if not found_items and not is_glob_optional:
            raise Exception(
                f"No files were given for glob {glob_path} "
                f"(expression: {glob_expression})"
            )

    items = list(result)
    items.sort()

    return items


def file_sha256(input_file: str):
    try:
        hash = hashlib.sha256()
        data = bytearray(4096)

        with io.FileIO(input_file, "rb") as f:
            while readed_bytes := f.readinto(data):
                hash.update(data[:readed_bytes])

        return hash
    except Exception as e:
        raise Exception(f"Failure reading {input_file} to compute sha256 digest", e)


def compute_hash_key(
    f: Callable, inputs: INPUTS, resolved_parameters: RESOLVED_PARAMETERS
) -> str:
    """
    Computes a hash from the code of the steps, the input file names and their
    content. With this hash, we'll store an entry in the blob store that
    points to a serialized cached output.
    """
    hash = hashlib.sha256()
    code = textwrap.dedent(inspect.getsource(f)).encode("utf-8")
    hash.update(code)

    # resolve_inputs returns the files sorted, with only relative paths
    for input_file in resolve_globs(inputs):
        hash.update(input_file.encode("utf-8"))
        hash.update(file_sha256(input_file).digest())

    # resolved_parameters are strings
    if resolved_parameters:
        for resolved_param in resolved_parameters:
            hash.update(resolved_param.encode("utf-8"))

    return hash.hexdigest()
