import glob
import glob
import hashlib
import inspect
import textwrap
from typing import Set, Callable, List, Iterable

from cached_task import INPUTS


def resolve_globs(globs: Iterable[str]) -> List[str]:
    result: Set[str] = set()

    if not globs:
        return []

    if isinstance(globs, str):
        globs = [globs]

    for glob_path in globs:
        found_items = False

        for file_name in glob.iglob(glob_path):
            found_items = True
            result.add(file_name)

        if not found_items:
            raise Exception(f"No files were given for glob {glob_path}")

    items = list(result)
    items.sort()

    return items


def file_sha256(input_file: str):
    try:
        hash = hashlib.sha256()
        data = bytearray(4096)

        with open(input_file, 'rb') as f:
            while readed_bytes := f.readinto(data):
                hash.update(data[:readed_bytes])

        return hash
    except Exception as e:
        raise Exception(f"Failure reading {input_file} to compute sha256 digest", e)


def compute_hash_key(f: Callable, inputs: INPUTS) -> str:
    """
    Computes a hash from the code of the steps, the input file names and their
    content. With this hash, we'll store an entry in the blob store that
    points to a serialized cached output.
    """
    hash = hashlib.sha256()
    code = textwrap.dedent(inspect.getsource(f)).encode('utf-8')
    hash.update(code)

    # resolve_inputs returns the files sorted, with only relative paths
    for input_file in resolve_globs(inputs):
        hash.update(input_file.encode('utf-8'))
        hash.update(file_sha256(input_file).digest())

    return hash.hexdigest()
