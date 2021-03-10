from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from file_reader import exceptions
from file_reader.auth import UsernamePassword
from file_reader.base import Host, Path, Url


class HttpHost(Host):
    """
    >>> host = HttpHost("www.nu.nl")
    >>> p = (host / "index.html")
    >>> "<html" in p.read_text()
    True
    >>> b"<html" in p.read_bytes()
    True
    """

    _scheme = "http"

    def __init__(self, hostname: str, port: int = 80, auth: Optional[UsernamePassword] = None):
        self._hostname = hostname
        self._port = port
        self._auth = auth
        self._verify_ssl = False

    def __repr__(self) -> str:
        return f"HttpHost({self._hostname}:{self._port})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._hostname == other._hostname and self._port == other._port

    def _get_url(self, path: "Path"):
        return f"{self._scheme}://{self._hostname}{':'+ str(self._port) if self._port else ''}/{'/'.join(path.path_elements)}"

    def read_text(self, path: Optional["Path"] = None) -> str:
        if path is None:
            path = self.root_path

        return self._get_response(path).text

    def read_bytes(self, path: Optional["Path"] = None) -> bytes:
        if path is None:
            path = self.root_path

        return self._get_response(path).content

    def _get_response(self, path: "Path"):
        kwargs: Dict[str, Any] = {}

        if self._auth:
            kwargs["auth"] = HTTPBasicAuth(self._auth.username, self._auth.password)

        response = requests.get(self._get_url(path), stream=True, verify=self._verify_ssl, **kwargs)

        if response.status_code != 200:
            raise exceptions.FileNotAccessable

        return response

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, parsed_url.port or 80, auth=parsed_url.auth) / parsed_url.path


class HttpsHost(HttpHost):
    """
    >>> host = HttpsHost("www.nu.nl")
    >>> p = (host / "index.html")
    >>> "<html" in p.read_text()
    True
    >>> b"<html" in p.read_bytes()
    True

    """

    _scheme = "https"

    def __init__(self, hostname: str, port: int = 443, auth: Optional[UsernamePassword] = None, verify_ssl=True):
        super().__init__(hostname, port, auth)
        self._verify_ssl = verify_ssl

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, parsed_url.port or 443, auth=parsed_url.auth) / parsed_url.path

    def __repr__(self) -> str:
        return f"HttpsHost({self._hostname}:{self._port})"
