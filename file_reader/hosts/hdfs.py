import logging
from io import BytesIO
from typing import IO, Optional

try:
    import pyarrow.hdfs

    HDFS_ACTIVATED = True
except ImportError:
    HDFS_ACTIVATED = False

from file_reader import exceptions
from file_reader.auth import UsernamePassword
from file_reader.base import Host, Path, Url

logger = logging.getLogger(__name__)


class HdfsHost(Host):
    _scheme = "hdfs"

    def __init__(
        self,
        hostname: str,
    ):
        if not HDFS_ACTIVATED:
            logger.warning("HDFS is not available. Install with `pip install file_reader[hdfs]`.")

        self.hostname = hostname
        self.connection: Optional[pyarrow.hdfs.HadoopFileSystem] = None

    def __repr__(self) -> str:
        return f"HdfsHost({self.hostname})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.hostname == other.hostname

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname) / parsed_url.path

    def connect(self):
        if not HDFS_ACTIVATED:
            raise ValueError("HDFS is not available. Install with `pip install file_reader[hdfs]`.")

        self.connection = pyarrow.hdfs.connect(self.hostname)

    def _open(self, path: Path) -> IO[bytes]:
        if not self.connection:
            self.connect()

        if not self.connection:
            raise exceptions.NotConnected

        bytes_io = BytesIO()
        with self.connection.open("/".join(path.path_elements), mode="rb") as f:
            bytes_io.write(f.read())
            bytes_io.seek(0)

        return bytes_io

    def __del__(self):
        pass
