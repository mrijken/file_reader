import ftplib
import socket
from io import BytesIO
from typing import IO, Any, Dict, Optional

from file_reader import exceptions
from file_reader.auth import UsernamePassword
from file_reader.base import Host, Path, Url


class FTPHost(Host):
    r"""
    >>> import pytest

    >>> p = FTPHost.from_url("ftps://ftp.nluug.nl/pub/os/Linux/distr/ubuntu-releases/FOOTER.html")
    >>> "</div></body></html>" in p.read_text()
    True
    >>> b"</div></body></html>" in p.read_bytes()
    True

    >>> p = FTPHost.from_url("ftp://ftp.nluug.nl/wrong_file")
    >>> with pytest.raises(exceptions.FileNotAccessable):
    ...     p.read_text()

    >>> p = FTPHost.from_url("ftp://ftp.wrong_host.nl/readme")
    >>> with pytest.raises(exceptions.NoHostConnection):
    ...     p.read_text()

    >>> p = FTPHost.from_url("ftp://demo:password@test.rebex.net/pub/example/readme.txt")
    >>> 'Welcome,\r\n\r\nyou are connected using' in p.read_text()
    True
    """

    _scheme = "ftp"

    def __init__(self, hostname: str, port: int = 21, auth: Optional[UsernamePassword] = None) -> None:
        self.hostname = hostname
        self.port = port
        self.auth = auth
        self.connection: Optional[ftplib.FTP] = None

    def __repr__(self) -> str:
        return f"FTPHost({self.hostname}:{self.port})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.hostname == other.hostname and self.port == other.port

    def connect(self):
        try:
            self.connection = ftplib.FTP(self.hostname)
        except socket.gaierror as exc:
            raise exceptions.NoHostConnection() from exc
        kwargs: Dict[str, Any] = {}
        if self.auth:
            kwargs.update(user=self.auth.username, passwd=self.auth.password)
        self.connection.login(**kwargs)

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, parsed_url.port or 21, auth=parsed_url.auth) / parsed_url.path

    def _open(self, path: Path) -> IO[bytes]:
        if not self.connection:
            self.connect()

        if not self.connection:
            raise exceptions.NotConnected

        self.connection.cwd("/" + "/".join(path.path_elements[:-1]))

        mem_file = BytesIO()

        try:
            self.connection.retrbinary("RETR " + path.path_elements[-1], mem_file.write)
        except ftplib.error_perm as exc:
            raise exceptions.FileNotAccessable() from exc

        mem_file.seek(0)

        return mem_file

    def __del__(self):
        if self.connection:
            self.connection.quit()


class FTPSHost(FTPHost):
    r"""
    >>> p = FTPSHost.from_url("ftps://demo:password@test.rebex.net/pub/example/readme.txt")
    >>> 'Welcome,\r\n\r\nyou are connected using' in p.read_text()
    True
    """

    _scheme = "ftps"

    def __init__(self, hostname: str, port: int = 990, auth: Optional[UsernamePassword] = None) -> None:
        super().__init__(hostname, port=port, auth=auth)

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, parsed_url.port or 990, auth=parsed_url.auth) / parsed_url.path

    def __repr__(self) -> str:
        return f"FTPSHost({self.hostname}:{self.port})"
