try:
    import smbclient

    SMB_ACTIVATED = True
except ImportError:
    SMB_ACTIVATED = False

from typing import Optional

from file_assets.auth import UsernamePassword
from file_assets.base import Host, Path, Url


class SmbHost(Host):
    scheme = "smb"

    def __init__(self, hostname: str, auth: Optional[UsernamePassword] = None):
        if not SMB_ACTIVATED:
            raise ValueError("Samba is not available. Install met extras samba.")

        self.hostname = hostname
        self.auth = auth

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname, auth=parsed_url.auth) / parsed_url.path

    def connect(self):
        smbclient.ClientConfig(username=self.auth.username, password=self.auth.password)

    def _open(self, path: Path):
        return smbclient.open_file("\\\\\\" + self.hostname + str(path).replace("/", "\\\\"), mode="w")
