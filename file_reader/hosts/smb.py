import logging
from io import BytesIO
from typing import IO, Optional

try:
    import smbclient

    SMB_ACTIVATED = True
except ImportError:
    SMB_ACTIVATED = False


from file_reader.auth import UsernamePassword
from file_reader.base import Host, Path, Url

logger = logging.getLogger(__name__)


class SmbHost(Host):
    _scheme = "smb"

    def __init__(self, hostname: str, auth: Optional[UsernamePassword] = None):
        if not SMB_ACTIVATED:
            logger.warning("Samba is not available. Install with `pip install file_reader[smb]`")

        self.hostname = hostname
        self.auth = auth

    def __repr__(self) -> str:
        return f"SmbHost({self.hostname})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.hostname == other.hostname

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, auth=parsed_url.auth) / parsed_url.path

    def connect(self):
        if not SMB_ACTIVATED:
            raise ValueError("Samba is not available. Install with `pip install file_reader[smb]`")

        smbclient.ClientConfig(username=self.auth.username, password=self.auth.password)

    def _open(self, path: Path) -> IO[bytes]:
        self.connect()

        bytes_io = BytesIO()
        with smbclient.open_file("\\\\" + self.hostname + "\\" + str(path).replace("/", "\\"), mode="rb") as f:
            bytes_io.write(f.read())
            bytes_io.seek(0)

        return bytes_io
