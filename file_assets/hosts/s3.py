try:
    import boto3

    s3_activated = True
except ImportError:
    s3_activated = False

from file_assets.base import Host, Path, Url


class S3Host(Host):
    scheme = "s3"

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str):
        if not s3_activated:
            raise ValueError("S3 is not available. Install met extras s3.")
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name
        )
        self.s3 = self.session.resource("s3")
        self.client = self.s3.client("s3")

    def _open(self, path: Path):
        if len(path.path_elements) != 2:
            raise ValueError("path %s is not a valid S3 path (bucket / filename)")
        bucket = path.path_elements[0]
        filename = path.path_elements[1]

        obj = self.client.get_object(Bucket=bucket, Key=filename)
        return obj["Body"]
