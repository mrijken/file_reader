import abc
import dataclasses
import importlib
from io import BytesIO, StringIO
from typing import Dict, IO, Iterable, List, Optional, Tuple, Type, TypeVar, Union, overload, Protocol

from typing_extensions import Literal
from urllib3.util import parse_url

from file_reader.auth import UsernamePassword


@dataclasses.dataclass
class Url:
    scheme: str
    auth: Optional[UsernamePassword]
    hostname: str
    port: Optional[int]
    path: str
    query: Optional[str]
    fragment: Optional[str]


class Archive:
    _extension_to_cls: Dict[str, Type["Archive"]] = {}
    _extensions: List[str] = []

    def __init_subclass__(cls, **kwargs) -> None:
        for extension in cls._extensions:
            cls._extension_to_cls[extension] = cls

    @classmethod
    def get_archive_cls_for_filename(cls, filename: str) -> Optional[Type["Archive"]]:
        for extension, archive_cls in cls._extension_to_cls.items():
            if filename.endswith(extension):
                return archive_cls
        return None

    def __init__(self, path: "Path"):
        self._path = path

    def __truediv__(self, other: str) -> "Path":
        if not other.startswith("/"):
            other = "/" + other
        return Path(self, other.split("/"))

    @property
    def root_path(self) -> "Path":
        return Path(self, [])

    def __repr__(self) -> str:
        return f"Archive({self._path})"

    def _open(self, path: "Path") -> IO[bytes]:
        raise NotImplemented

    def read_text(self, path: "Path") -> str:
        return self.read_bytes(path).decode()

    def read_bytes(self, path: "Path") -> bytes:
        with self._open(path) as f:
            return f.read()


class Path:
    def __init__(self, root: Union["Host", "Archive"], path_elements: Iterable[str] = None) -> None:
        self._root = root
        self._path_elements: Tuple[str, ...] = tuple(path_elements) if path_elements else tuple()

    @property
    def path_elements(self) -> Tuple[str, ...]:
        """
        >>> (Path("host") / "root" / "child").path_elements
        ('root', 'child')
        """
        return self._path_elements

    def __str__(self) -> str:
        """
        >>> str(Path("host") / "root" / "child")
        'root/child'
        """
        return "/".join(self._path_elements)

    def _load_plugins(self):
        importlib.import_module("file_reader.archive")

    def __truediv__(self, other: str) -> "Path":
        """
        Get a new Path with a child of Path

        >>> p = Path(None)
        >>> p.path_elements == ()
        True
        >>> p = p / "root"
        >>> p.path_elements == ("root",)
        True
        >>> p = p / "child"
        >>> p.path_elements == ("root", "child")
        True

        """
        path = self.__class__(self._root, self.path_elements + (other,))

        if "." in other:
            self._load_plugins()
            archive_cls = Archive.get_archive_cls_for_filename(other)
            if archive_cls:
                return Path(archive_cls(path))
        return path

    def __repr__(self) -> str:
        """
        >>> repr(Path("host") / "root" / "child")
        'Path(host, root/child)'
        """
        return f"Path({self._root}, {str(self)})"

    def read_text(self) -> str:
        return self._root.read_text(self)

    def read_bytes(self) -> bytes:
        return self._root.read_bytes(self)

    @overload
    def open(self, mode: Literal["b"]) -> BytesIO:
        ...

    @overload
    def open(self, mode: Literal["t"]) -> StringIO:
        ...

    def open(self, mode: Union[Literal["t"], Literal["b"]] = "b") -> IO:
        if mode == "b":
            return BytesIO(self.read_bytes())

        return StringIO(self.read_text())


class Host(abc.ABC):
    _scheme: str = "unknown"

    _subclasses: List[Type["Host"]] = []

    def __init_subclass__(cls, **kwargs):
        cls._subclasses.append(cls)

    @classmethod
    def from_url(cls, url_str: str) -> Path:
        """
        >>> Host.from_url("ftp://ftp.nluug.nl/pub/os/Linux/distr/ubuntu-releases/FOOTER.html")
        Path(Host(ftp), /pub/os/Linux/distr/ubuntu-releases/FOOTER.html)
        """
        parsed_url = parse_url(url_str)
        auth = None
        if parsed_url.auth:
            auth = UsernamePassword(*parsed_url.auth.split(":"))
        url = Url(
            parsed_url.scheme,
            auth,
            parsed_url.hostname,
            parsed_url.port,
            parsed_url.path,
            parsed_url.query,
            parsed_url.fragment,
        )

        for host_cls in cls._subclasses:
            if parsed_url.scheme == host_cls._scheme:
                return host_cls.from_parsed_url(url)

        raise ValueError(f"scheme {parsed_url.scheme} is not known")

    @classmethod
    @abc.abstractmethod
    def from_parsed_url(cls: Type["Host"], parsed_url: Url) -> "Path":
        ...

    def __truediv__(self, other: str) -> Path:
        if not other.startswith("/"):
            other = "/" + other
        return Path(self, other.split("/"))
    
    def get_path(self, path: str) -> Path:
        return Path(self, path.split("/"))

    @property
    def root_path(self) -> Path:
        return Path(self, [])

    def __repr__(self) -> str:
        return f"Host({self._scheme})"

    def _open(self, path: Path) -> IO:
        raise NotImplemented

    def read_text(self, path: Path) -> str:
        return self.read_bytes(path).decode()

    def read_bytes(self, path: Path) -> bytes:
        with self._open(path) as f:
            return f.read()
