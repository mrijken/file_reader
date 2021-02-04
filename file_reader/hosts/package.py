import pathlib
from typing import IO

import pkg_resources

from file_reader import exceptions
from file_reader.base import Host, Path, Url


class PythonPackage(Host):
    """
    >>> p = PythonPackage("urllib3") / "_version.py"
    >>> "__version__" in p.read_text()
    True
    >>> b"__version__" in p.read_bytes()
    True

    """

    _scheme = "package"

    def __init__(self, package_name: str) -> None:
        self.package_name = package_name

    def __repr__(self) -> str:
        return f"Package({self.package_name})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.package_name == other.package_name

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname) / parsed_url.path

    def _get_path(self, path: Path) -> pathlib.Path:
        prov = pkg_resources.get_provider(self.package_name)
        if isinstance(prov, pkg_resources.ZipProvider):
            raise exceptions.FileNotAccessable
        return pathlib.Path(pkg_resources.resource_filename(self.package_name, "/".join(path.path_elements)))

    def _open(self, path: "Path") -> IO[bytes]:
        return self._get_path(path).open("rb")
