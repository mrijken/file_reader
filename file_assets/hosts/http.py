from io import SEEK_END, SEEK_SET, BytesIO
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from file_assets import exceptions
from file_assets.auth import UsernamePassword
from file_assets.base import Host, Path, Url


class ResponseStream:
    def __init__(self, request_iterator):
        self._bytes = BytesIO()
        self._iterator = request_iterator

    def _load_all(self):
        self._bytes.seek(0, SEEK_END)
        for chunk in self._iterator:
            self._bytes.write(chunk)

    def _load_until(self, goal_position):
        current_position = self._bytes.seek(0, SEEK_END)
        while current_position < goal_position:
            try:
                current_position = self._bytes.write(next(self._iterator))
            except StopIteration:
                break

    def tell(self):
        return self._bytes.tell()

    def read(self, size=None):
        left_off_at = self._bytes.tell()
        if size is None:
            self._load_all()
        else:
            goal_position = left_off_at + size
            self._load_until(goal_position)

        self._bytes.seek(left_off_at)
        return self._bytes.read(size)

    def seek(self, position, whence=SEEK_SET):
        if whence == SEEK_END:
            self._load_all()
        else:
            self._bytes.seek(position, whence)

    def close(self):
        pass


class HttpHost(Host):
    """
    >>> host = HttpHost("www.nu.nl")
    >>> p = (host / "index.html")
    >>> "<html" in p.read_text()
    True
    >>> b"<html" in p.read_bytes()
    True
    >>> with p.open('t') as f:
    ...     f.read(4)
    ...     f.tell()
    ...     f.seek(0)
    ...     f.tell()
    ...     f.read(4)
    '\\n<!D'
    4
    0
    '\\n<!D'
    """

    scheme = "http"

    verify_ssl = True

    def __init__(self, hostname: str, port: int = None, auth: Optional[UsernamePassword] = None):
        self.hostname = hostname
        self.port = port
        self.auth = auth

    def get_url(self, path: "Path"):
        return (
            f"{self.scheme}://{self.hostname}{':'+ str(self.port) if self.port else ''}/{'/'.join(path.path_elements)}"
        )

    def _open(self, path: "Path"):
        kwargs: Dict[str, Any] = {}
        if self.auth:
            kwargs["auth"] = HTTPBasicAuth(self.auth.username, self.auth.password)
        response = requests.get(self.get_url(path), stream=True, verify=self.verify_ssl, **kwargs)
        if response.status_code != 200:
            raise exceptions.FileNotAccessable

        return ResponseStream(response.iter_content(1000))

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, parsed_url.port, auth=parsed_url.auth) / parsed_url.path


class HttpsHost(HttpHost):
    """
    >>> host = HttpsHost("www.nu.nl")
    >>> p = (host / "index.html")
    >>> "<html" in p.read_text()
    True
    >>> b"<html" in p.read_bytes()
    True
    >>> with p.open('t') as f:
    ...     first_read = f.read(4)
    ...     second_read = f.read(4)
    >>> first_read == '\\n<!D'
    True
    >>> second_read  == 'OCTY'
    True

    """

    scheme = "https"

    def __init__(self, hostname: str, port: int = None, auth: Optional[UsernamePassword] = None, verify_ssl=False):
        super().__init__(hostname, port, auth)
        self.verify_ssl = verify_ssl
