import pathlib

import pkg_resources
from file_assets import exceptions
from file_assets.base import Host, Path, Url


class PythonPackage(Host):
    """
    >>> p = PythonPackage("urllib3") / "_version.py"
    >>> "__version__" in p.read_text()
    True
    >>> b"__version__" in p.read_bytes()
    True
    """

    scheme = "package"

    def __init__(self, package_name: str) -> None:
        self.package_name = package_name

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.host) / parsed_url.path

    def _get_path(self, path: Path) -> pathlib.Path:
        prov = pkg_resources.get_provider(self.package_name)
        if isinstance(prov, pkg_resources.ZipProvider):
            raise exceptions.FileNotAccessable
        return pathlib.Path(pkg_resources.resource_filename(self.package_name, "/".join(path.path_elements)))

    def _open(self, path: "Path"):
        return self._get_path(path).open("rb")