import tarfile
import zipfile
from io import BytesIO
from typing import IO

from file_reader.base import Archive, Path
from file_reader.exceptions import FileNotAccessable


class TarFile(Archive):
    """
    >>> from file_reader.hosts.local import LocalHost
    >>> p = LocalHost() / "tests" / "resources" / "archive_content.tar" / "." / "folder" / "file3.txt"

    >>> repr(p)
    'Path(Archive(tests/resources/archive_content.tar)/./folder/file3.txt)'

    >>> p.read_bytes() == b"file3"
    True
    >>> p.read_text() == "file3"
    True

    """

    _extensions = [".tar", ".tgz", ".tar.gz"]

    def _open(self, path: Path) -> IO[bytes]:
        tar_file = tarfile.open(fileobj=BytesIO(self._path.read_bytes()), mode="r")
        member = tar_file.extractfile(tar_file.getmember(str(path)))
        if member is None:
            raise FileNotAccessable

        return member


class ZipFile(Archive):
    """
    >>> from file_reader.hosts.local import LocalHost
    >>> p = LocalHost() / "tests" / "resources" / "archive_content.zip" / "folder" / "file3.txt"
    >>> repr(p)
    'Path(Archive(tests/resources/archive_content.zip)/folder/file3.txt)'

    >>> p.read_bytes() == b"file3"
    True
    >>> p.read_text() == "file3"
    True

    """

    _extensions = [".zip", ".dep"]

    def _open(self, path: Path) -> IO[bytes]:
        return zipfile.ZipFile(BytesIO(self._path.read_bytes())).open(str(path), "r")
