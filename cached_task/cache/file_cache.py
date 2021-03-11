import abc
from typing import Union, Iterable, Optional, Callable

INPUTS = Union[str, Iterable[str]]
OUTPUTS = Optional[Union[str, Iterable[str]]]


class FileCache(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_hash_key(self, f: Callable, inputs: INPUTS) -> str:
        """
        Computes the hash key for the cache for the given function code
        and file glob inputs. The inputs are resolved.
        """
        pass

    @abc.abstractmethod
    def use_cached(self, hash_key: str) -> bool:
        """
        Checks if the current inputs, for the given function represented
        by this hash_key are cached. If they are, it writes the outputs,
        and returns true. If they're not cached it returns false, and
        does nothing.

        To obtain a hash_key call `get_hash_key`.
        """
        pass

    @abc.abstractmethod
    def cache_outputs(self, hash_key: str, outputs: OUTPUTS) -> None:
        """
        Store the current outputs into the cache, and associates them
        with the inputs.
        """
        pass
