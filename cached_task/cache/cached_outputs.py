from typing import Dict
import yaml


class CachedOutputs:
    def __init__(self) -> None:
        self.files: Dict[str, str] = dict()  # file full relative path -> blob hash

    @classmethod
    def from_string(cls, cached_outputs_str) -> "CachedOutputs":
        result = CachedOutputs()
        result.files = yaml.safe_load(cached_outputs_str)

        return result

    def __str__(self) -> str:
        return yaml.safe_dump(self.files)
