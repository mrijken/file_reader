try:
    import smbclient

    smb_activated = True
except ImportError:
    smb_activated = False

from typing import Optional

from file_assets.base import Host, Path


class SmbHost(Host):
    scheme = "smb"

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        if not smb_activated:
            raise ValueError("Samba is not available. Install met extras samba.")
        smbclient.ClientConfig(username=username, password=password)

    def _open(self, path: "Path"):
        return smbclient.open_file(str(path), mode="w")
