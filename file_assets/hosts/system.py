import pathlib

from file_assets.base import Host, Path


class SystemHost(Host):
    """
    >>> host = SystemHost()
    >>> p = host / "home"
    >>> p
    Path(Host(file, cwd=.), /home)
    >>> host / "home" / "user" / "file.txt"
    Path(Host(file, cwd=.), /home/user/file.txt)


    >>> p = SystemHost() / "pyproject.toml"
    >>> with p.open('t') as f:
    ...     first_read = f.read(4)
    ...     second_read = f.read(1)
    >>> isinstance(first_read, str)
    True
    >>> first_read == '[too'
    True
    >>> second_read == 'l'
    True

    >>> with p.open('b') as f:
    ...     first_read = f.read(4)
    ...     second_read = f.read(1)
    >>> isinstance(first_read, bytes)
    True
    >>> first_read == b"[too"
    True
    >>> second_read == b"l"
    True

    """

    scheme = "file"

    def __init__(self, home_dir=False, root=False):
        self.cwd = pathlib.Path(".")
        if home_dir:
            self.cwd = pathlib.Path("~").expanduser()
        elif root:
            self.cwd = pathlib.Path("/")

    def _get_path(self, path: Path) -> pathlib.Path:
        current_path = self.cwd
        for element in path.path_elements:
            current_path = current_path / element

        return current_path

    def _open(self, path: "Path"):
        return self._get_path(path).open("rb")

    def __repr__(self) -> str:
        return f"Host(file, cwd={self.cwd})"
