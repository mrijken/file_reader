from typing import IO
from file_reader import exceptions
from file_reader.base import Host, Path, Url


class S3Host(Host):
    _scheme = "s3"

    # TODO: make sure that only one path element can be used
    _max_path_elements = 1

    def __init__(self, bucket_name: str, region_name: str):
        self.bucket_name = bucket_name
        self.region_name = region_name

    def __repr__(self) -> str:
        return f"S3Host({self.bucket_name}@{self.region_name})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.bucket_name == other.bucket_name and self.region_name == other.region_name

    @classmethod
    def from_parsed_url(cls, parsed_url: Url) -> Path:
        raise NotImplemented

    def connect(self):
        self.session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )
        self.session = self.session.resource("s3")
        self.client = self.session.client("s3")

    def _open(self, path: Path) -> IO[bytes]:
        if not self.client:
            self.connect()

        if not self.client:
            raise exceptions.NotConnected

        if len(path.path_elements) != 2:
            raise ValueError("path %s is not a valid S3 path (bucket / filename)")
        bucket = path.path_elements[0]
        filename = path.path_elements[1]

        obj = self.client.get_object(Bucket=bucket, Key=filename)
        return obj["Body"]
