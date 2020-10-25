import abc
from io import BytesIO
import tarfile
import zipfile


class Archive(abc.ABC):
    def __init__(self, archive_file: BytesIO) -> None:
        self.archive_file = archive_file

    @abc.abstractmethod
    def open(self, path) -> BytesIO:
        pass


class TarFile(Archive):
    """
    >>> z = TarFile(open("tests/resources/archive_content.tar", "rb"))
    >>> z.open("./folder/file3.txt").read() == b"file3"
    True

    """

    extension = ".tar"

    def open(self, path):
        tar_file = tarfile.open(fileobj=self.archive_file, mode="r")
        return tar_file.extractfile(tar_file.getmember(path))


class TarGzFile(Archive):
    """
    >>> z = TarFile(open("tests/resources/archive_content.tar", "rb"))
    >>> z.open("./folder/file3.txt").read() == b"file3"
    True

    """

    extension = ".tar.gz"


class ZipFile(Archive):
    """
    >>> z = ZipFile(open("tests/resources/archive_content.zip", "rb"))
    >>> z.open("folder/file3.txt").read() == b"file3"
    True

    """

    extension = ".zip"

    def open(self, path):
        return zipfile.ZipFile(self.archive_file).open(path, "r")
