try:
    import smbclient

    smb_activated = True
except ImportError:
    smb_activated = False

from file_assets.auth import UsernamePassword
from typing import Optional

from file_assets.base import Host, Path


class SmbHost(Host):
    scheme = "smb"

    def __init__(self, auth: Optional[UsernamePassword] = None):
        if not smb_activated:
            raise ValueError("Samba is not available. Install met extras samba.")

        self.auth = auth

    def connect(self):
        smbclient.ClientConfig(username=self.auth.username, password=self.auth.password)

    def _open(self, path: "Path"):
        return smbclient.open_file(str(path), mode="w")
