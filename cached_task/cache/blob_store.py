import os
import shutil


class BlobStore:
    def __contains__(self, store_file_name: str) -> bool:
        store_path = self._store_path(store_file_name)
        return os.path.isfile(store_path)

    def store_file(self, store_file_name: str, file_path: str) -> None:
        store_path = self._store_path(store_file_name)
        dir_name = os.path.dirname(store_path)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        return shutil.copyfile(file_path, store_path)

    def restore_file(self, store_file_name: str, file_path: str) -> None:
        store_path = self._store_path(store_file_name)
        dir_name = os.path.dirname(file_path)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        return shutil.copyfile(store_path, file_path)

    def store_string(self, store_file_name: str, value: str) -> None:
        store_path = self._store_path(store_file_name)
        dir_name = os.path.dirname(store_path)

        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(store_path, "wt", encoding="utf-8") as f:
            f.write(value)

    def read_string(self, store_file_name: str) -> str:
        store_path = self._store_path(store_file_name)
        with open(store_path, "rt", encoding="utf-8") as f:
            return f.read()

    def _store_path(self, store_file_name: str) -> str:
        """
        Resolves the absolute path to the file
        """
        return os.path.join("/tmp/.cache/", store_file_name)