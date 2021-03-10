import logging
from typing import IO, Optional

try:
    import boto3
    from botocore.vendored.six import BytesIO

    S3_ACTIVATED = True
except ImportError:
    S3_ACTIVATED = False

from file_reader import exceptions
from file_reader.base import Host, Path, Url

logger = logging.getLogger(__name__)


class S3Host(Host):
    _scheme = "s3"

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Specify the acces key and secret key in the parameter or
        an environment parameter (see https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).
        """
        if not S3_ACTIVATED:
            logger.warning("S3 is not available. Install with `pip install file_reader[s3]`.")

        self.bucket_name = bucket_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self._client = None

    def __repr__(self) -> str:
        return f"S3Host({self.bucket_name})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.bucket_name == other.bucket_name

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        return cls(parsed_url.hostname) / "/".join(parsed_url.path.split("/"))

    def connect(self):
        if not S3_ACTIVATED:
            raise ValueError("S3 is not available. Install with `pip install file_reader[s3]`.")

        self._client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    def _open(self, path: Path) -> IO[bytes]:
        if not self._client:
            self.connect()

        if not self._client:
            raise exceptions.NotConnected

        filename = "/".join(path.path_elements)

        bytes_io = BytesIO()
        self._client.download_fileobj(self.bucket_name, filename, bytes_io)
        bytes_io.seek(0)
        return bytes_io
