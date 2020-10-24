from file_assets.auth import UsernamePassword
import socket
from typing import Optional

try:
    import paramiko

    ssh_activated = True
except ImportError:
    ssh_activated = False


from file_assets import exceptions
from file_assets.base import Host, Path


class SFTPHost(Host):
    scheme = "sftp"

    def __init__(
        self,
        hostname: str,
        auth: Optional[UsernamePassword] = None,
        auto_add_host_key=False,
    ):
        self.hostname = hostname
        self.auth = auth
        self.auto_add_host_key = auto_add_host_key
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None

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
        except (paramiko.BadHostKeyException, paramiko.AuthenticationException, paramiko.SSHException, socket.error):
            raise exceptions.NoHostConnection
        self.sftp_client = self.ssh_client.open_sftp()

    def _open(self, path: Path):
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
