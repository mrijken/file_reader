import abc
from io import BytesIO
import tarfile
from typing import Dict, List, Type
import zipfile


class Archive(abc.ABC):
    extension_to_cls: Dict[str, Type["Archive"]] = {}
    extensions: List[str] = []

    def __init_subclass__(cls, **kwargs) -> None:
        for extension in cls.extensions:
            cls.extension_to_cls[extension] = cls

    @classmethod
    def get_archive(cls, extension, archive_file: BytesIO) -> "Archive":
        if extension not in cls.extension_to_cls:
            raise ValueError(f"{extension} is not found as registered extension")

        return cls.extension_to_cls[extension](archive_file)

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

    >>> z = TarFile(open("tests/resources/archive_content.tar", "rb"))
    >>> z.open("./folder/file3.txt").read() == b"file3"
    True

    >>> z = Archive.get_archive(".tar", open("tests/resources/archive_content.tar", "rb"))
    >>> z.open("./folder/file3.txt").read() == b"file3"
    True

    """

    extensions = [".tar", ".tgz", ".tar.gz"]

    def open(self, path):
        tar_file = tarfile.open(fileobj=self.archive_file, mode="r")
        return tar_file.extractfile(tar_file.getmember(path))


class ZipFile(Archive):
    """
    >>> z = ZipFile(open("tests/resources/archive_content.zip", "rb"))
    >>> z.open("folder/file3.txt").read() == b"file3"
    True

    """

    extensions = [".zip", ".dep"]

    def open(self, path):
        return zipfile.ZipFile(self.archive_file).open(path, "r")
