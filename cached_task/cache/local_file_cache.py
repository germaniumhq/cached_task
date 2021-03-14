from typing import Callable

from cached_task import INPUTS, OUTPUTS, RESOLVED_PARAMETERS
from cached_task.cache import file_cache
from cached_task.cache.blob_store import BlobStore
from cached_task.cache.cache import compute_hash_key, resolve_globs, file_sha256
from cached_task.cache.cached_outputs import CachedOutputs


class LocalFileCache(file_cache.FileCache):
    def __init__(self) -> None:
        self.blob_store = BlobStore()

    def get_hash_key(
        self, f: Callable, inputs: INPUTS, resolved_parameters: RESOLVED_PARAMETERS
    ) -> str:
        return compute_hash_key(f, inputs, resolved_parameters)

    def use_cached(self, hash_key: str) -> bool:
        if hash_key not in self.blob_store:
            return False

        cached_outputs_str = self.blob_store.read_string(hash_key)
        cached_outputs: CachedOutputs = CachedOutputs.from_string(cached_outputs_str)

        for file_path, file_hash in cached_outputs.files.items():
            self.blob_store.restore_file(file_hash, file_path)

        return True

    def cache_outputs(self, hash_key: str, outputs: OUTPUTS) -> None:
        resolved_files = resolve_globs(outputs)
        cached_outputs = CachedOutputs()

        for single_file in resolved_files:
            hexdigest = file_sha256(single_file).hexdigest()
            cached_outputs.files[single_file] = hexdigest
            self.blob_store.store_file(hexdigest, single_file)

        self.blob_store.store_string(hash_key, str(cached_outputs))
