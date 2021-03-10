import logging
import socket
from typing import IO, Optional

try:
    import paramiko

    SSH_ACTIVATED = True
except ImportError:
    SSH_ACTIVATED = False

from file_reader import exceptions
from file_reader.auth import UsernamePassword
from file_reader.base import Host, Path, Url

logger = logging.getLogger(__name__)


class SFTPHost(Host):
    r"""

    >>> SFTPHost.from_url("sftp://demo:demo@demo.wftpserver.com:2222/download/Winter.jpg")
    Path(SFTPHost(demo.wftpserver.com:2222)/download/Winter.jpg)

    """

    _scheme = "sftp"

    def __init__(
        self,
        hostname: str,
        port: int = 22,
        auth: Optional[UsernamePassword] = None,
        auto_add_host_key=False,
    ):
        if not SSH_ACTIVATED:
            logger.warning("SFTP is not available. Install with `pip install file_reader[sftp]`.")

        self.hostname = hostname
        self.port = port
        self.auth = auth
        self.auto_add_host_key = auto_add_host_key
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None

    def __repr__(self) -> str:
        return f"SFTPHost({self.hostname}:{self.port})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.hostname == other.hostname and self.port == other.port

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, port=parsed_url.port or 22, auth=parsed_url.auth) / parsed_url.path

    def connect(self):
        if not SSH_ACTIVATED:
            raise ValueError("SFTP is not available. Install with `pip install file_reader[sftp]`.")

        self.ssh_client = paramiko.SSHClient()
        if self.auto_add_host_key:
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.auth.username if self.auth else None,
                password=self.auth.password if self.auth else None,  # pkey=pkey, key_filename=key_filename
            )
        except (
            paramiko.BadHostKeyException,
            paramiko.AuthenticationException,
            paramiko.SSHException,
            socket.error,
        ) as exc:
            raise exceptions.NoHostConnection from exc

        self.sftp_client = self.ssh_client.open_sftp()

    def _open(self, path: Path) -> IO[bytes]:
        if not self.sftp_client:
            self.connect()

        if not self.sftp_client:
            raise exceptions.NotConnected

        return self.sftp_client.open("/".join(path.path_elements), mode="rb")

    def __del__(self):
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
