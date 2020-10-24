import socket
from typing import Optional

try:
    import pyarrow.hdfs

    HDFS_ACTIVATED = True
except ImportError:
    HDFS_ACTIVATED = False

from file_assets import exceptions
from file_assets.auth import UsernamePassword
from file_assets.base import Host, Path, Url


class HdfsHost(Host):
    scheme = "hdfs"

    def __init__(
        self,
        hostname: str,
    ):
        if not HDFS_ACTIVATED:
            raise ValueError("HDFS is not available. Install met extras hdfs.")

        self.hostname = hostname
        self.connection: Optional[pyarrow.hdfs.HadoopFileSystem] = None

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname) / parsed_url.path

    def connect(self):
        self.connection = pyarrow.hdfs.connect(self.hostname)

    def _open(self, path: Path):
        if not self.connection:
            self.connect()

        if not self.connection:
            raise exceptions.NotConnected

        return self.connection.open("/".join(path.path_elements), mode="rb")

    def __del__(self):
        pass
