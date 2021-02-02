import pathlib
from typing import IO

from file_reader.base import Host, Path, Url


class SystemHost(Host):
    """
    >>> host = SystemHost()
    >>> p = host / "home"
    >>> p
    Path(Host(file, cwd=.), /home)
    >>> host / "home" / "user" / "file.txt"
    Path(Host(file, cwd=.), /home/user/file.txt)


    >>> p = SystemHost() / "pyproject.toml"
    >>> p.read_text()[:10]
    '[tool.poet'
    >>> p.read_bytes()[:10]
    b'[tool.poet'


    """

    _scheme = "file"

    def __init__(self, home_dir=False, root=False):
        self.cwd = pathlib.Path(".")
        if home_dir:
            self.cwd = pathlib.Path("~").expanduser()
        elif root:
            self.cwd = pathlib.Path("/")

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname) / parsed_url.path

    def _get_path(self, path: Path) -> pathlib.Path:
        current_path = self.cwd
        for element in path.path_elements:
            current_path = current_path / element

        return current_path

    def _open(self, path: "Path") -> IO[bytes]:
        return self._get_path(path).open("rb")

    def __repr__(self) -> str:
        return f"Host(file, cwd={self.cwd})"
