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


class SFTPHost(Host):
    _scheme = "sftp"

    def __init__(
        self,
        hostname: str,
        auth: Optional[UsernamePassword] = None,
        auto_add_host_key=False,
    ):
        if not SSH_ACTIVATED:
            raise ValueError("SFTP is not available. Install met extras sftp.")

        self.hostname = hostname
        self.auth = auth
        self.auto_add_host_key = auto_add_host_key
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, auth=parsed_url.auth) / parsed_url.path

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        if self.auto_add_host_key:
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect(
                hostname=self.hostname,
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
