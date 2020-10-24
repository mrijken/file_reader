import abc
import dataclasses
from typing import IO, List, Optional, Type, TypeVar, overload

from typing_extensions import Literal
from urllib3.util import parse_url

from file_assets.auth import UsernamePassword


@dataclasses.dataclass
class Url:
    scheme: str
    auth: Optional[UsernamePassword]
    hostname: str
    port: Optional[int]
    path: str
    query: Optional[str]
    fragment: Optional[str]


class FileObject:
    chunk_size = 0
    pointer: Optional[IO] = None
    mode = "t"

    def __init__(self, path: "Path") -> None:
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.close()

    def close(self):
        if self.pointer:
            self.pointer.close()
        self.pointer = None


class Bytes(FileObject):
    mode = "b"

    def read(self, chunk_size=-1) -> bytes:
        self.chunk_size = chunk_size
        return self.path.read_bytes(file=self)


class Text(FileObject):
    mode = "t"

    def read(self, chunk_size=-1) -> str:
        self.chunk_size = chunk_size
        return self.path.read_text(file=self)


class Path:
    def __init__(self, host: "Host", path_elements: List[str] = None):
        self.host = host
        self.path_elements = path_elements or []

    def __str__(self):
        return "/".join(self.path_elements)

    def __truediv__(self, other: str) -> "Path":
        return self.__class__(self.host, self.path_elements + [other])

    def __repr__(self) -> str:
        return f"Path({self.host}, {str(self)})"

    def read_text(self, chunk_size: int = -1, file: FileObject = None) -> str:
        return self.host.read_text(self, chunk_size, file=file)

    def read_bytes(self, chunk_size: int = -1, file: FileObject = None) -> bytes:
        return self.host.read_bytes(self, chunk_size, file=file)

    @overload
    def open(self, mode: Literal["t"]) -> Text:
        ...

    @overload
    def open(self, mode: Literal["b"]) -> Bytes:
        ...

    def open(self, mode="t") -> FileObject:
        if mode == "t":
            return Text(self)

        return Bytes(self)


class Host(abc.ABC):
    """"""

    scheme: str = "unkown"
    subclasses: List[Type["Host"]] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    path_cls = Path

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

        for host_cls in cls.subclasses:
            if parsed_url.scheme == host_cls.scheme:
                return host_cls.from_parsed_url(url)

        raise ValueError(f"scheme {parsed_url.scheme} is not known")

    @classmethod
    @abc.abstractmethod
    def from_parsed_url(cls: Type["Host"], parsed_url: Url) -> "Path":
        ...

    def __truediv__(self, other: str) -> Path:
        if not other.startswith("/"):
            other = "/" + other
        return self.path_cls(self, other.split("/"))

    @property
    def root_path(self) -> Path:
        return self.path_cls(self, [])

    def __repr__(self) -> str:
        return f"Host({self.scheme})"

    @abc.abstractmethod
    def _open(self, path: Path) -> IO:
        ...

    def read_text(self, path: Path, chunk_size: int = -1, file: FileObject = None) -> str:
        return self.read_bytes(path, chunk_size, file).decode()

    def read_bytes(self, path: Path, chunk_size: int = -1, file: FileObject = None) -> bytes:
        if file is None:
            if chunk_size == -1:
                return self._open(path).read()
            return self._open(path).read(chunk_size)

        if file.pointer is None:
            file.pointer = self._open(path)

        if file.chunk_size == -1:
            return file.pointer.read()

        return file.pointer.read(file.chunk_size)
