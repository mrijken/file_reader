import pathlib
from typing import IO, Optional, Union

from file_reader.base import Host, Path, Url


class LocalHost(Host):
    """
    >>> host = LocalHost()
    >>> p = host / "home"
    >>> p
    Path(LocalHost(.)/home)
    >>> host / "home" / "user" / "file.txt"
    Path(LocalHost(.)/home/user/file.txt)


    >>> p = LocalHost() / "pyproject.toml"
    >>> p.read_text()[:10]
    '[tool.poet'
    >>> p.read_bytes()[:10]
    b'[tool.poet'


    """

    _scheme = "file"

    def __init__(self, cwd: Optional[Union[pathlib.Path, str]] = None, home_dir=False, root=False):
        if cwd is not None:
            self.cwd = pathlib.Path(cwd) if isinstance(cwd, str) else cwd
        elif home_dir:
            self.cwd = pathlib.Path("~").expanduser()
        elif root:
            self.cwd = pathlib.Path("/")
        else:
            self.cwd = pathlib.Path(".")

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.cwd == other.cwd

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
        return f"LocalHost({self.cwd})"
