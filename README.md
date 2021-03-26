# file_reader

![Build](https://github.com/mrijken/file_reader/workflows/CI/badge.svg)
![Hits](https://hitcounter.pythonanywhere.com/count/tag.svg?url=https%3A%2F%2Fgithub.com%2Fmrijken%2Ffile_reader)

## Read almost all files from almost anywhere with one API

Uniform file reader for a lot of different file storages, like

- local filesystem
- http(s)
- ftp(s)
- smb
- sftp

Import dependencies for doctest

    >>> import file_reader
    >>> import file_reader.hosts
    >>> import pytest

## Usage

### Construct a Host and a Path

To read a file, you have to instantiate a host (like FTPHost) and get a path from it

    >>> host = file_reader.hosts.ftp.FTPHost('ftp.nluug.nl')
    >>> path = host / 'pub' / 'os' / 'Linux' / 'distr' / 'ubuntu-releases' / 'FOOTER.html'

    or

    >>> path = host.get_path("pub/os/Linux/distr/ubuntu-releases/FOOTER.html")

    >>> path
    Path(FTPHost(ftp.nluug.nl:21)/pub/os/Linux/distr/ubuntu-releases/FOOTER.html)

You can use that path to read the contents.


### Accces the conents like a file

Use it as a regular file object:

- with or without a context managers

    >>> with path.open() as f:
    ...     f.read()
    b'\n</div></body></html>\n'

    >>> with path.open('b') as f:
    ...     f.read()
    b'\n</div></body></html>\n'

    >>> with path.open('t') as f:
    ...     f.read()
    '\n</div></body></html>\n'

### Access the contents directly

Read the content direct from the path as text:

    >>> path.read_text()
    '\n</div></body></html>\n'

or as binary:

    >>> path.read_bytes()
    b'\n</div></body></html>\n'

### Create a Path from an url

You can construct a Host and Path by parsing an url, like:

    >>> file_reader.base.Host.from_url("ftp://marc:secret@ftp.nluug.nl/pub/os/Linux/distr/ubuntu-releases/FOOTER.html")
    Path(FTPHost(ftp.nluug.nl:21)/pub/os/Linux/distr/ubuntu-releases/FOOTER.html)

    >>> file_reader.base.Host.from_url("http://marc:secret@nu.nl/robots.txt")
    Path(HttpHost(nu.nl:80)/robots.txt)

    >>> file_reader.base.Host.from_url("package://file_reader/__init__.py")
    Path(Package(file_reader)/__init__.py)

## Possible hosts

For every supported file location, a host is defined which knows how to access the file. The following
hosts are supported

### System

This is the local filesystem of your machine. It can access all files from all already mounted drives.
It will use the credentials of the user who is running the python process.

You can use a path relative to the working directory

    >>> file_reader.hosts.local.LocalHost() / "file_reader" / "__init__.py"
    Path(LocalHost(.)/file_reader/__init__.py)

A path relative to the home dir of the current user can be used

    >>> file_reader.hosts.local.LocalHost(home_dir=True) / ".ssh" / "id_rsa.pub"
    Path(LocalHost(/home/...)/.ssh/id_rsa.pub)

Or an absolute path can be used:

    >>> file_reader.hosts.local.LocalHost(root=True) / "etc" / "hosts"
    Path(LocalHost(/)/etc/hosts)


### HTTP(S)

Via the GET method a file from a HTTP(S) location will be get.

    >>> path = file_reader.hosts.http.HttpHost("nu.nl") / "robots.txt"
    >>> path
    Path(HttpHost(nu.nl:80)/robots.txt)

    >>> file_reader.base.Host.from_url("http://nu.nl/robots.txt")
    Path(HttpHost(nu.nl:80)/robots.txt)

    >>> "User-agent" in path.read_text()
    True
    >>> path = file_reader.hosts.http.HttpsHost("nu.nl") / "robots.txt"
    >>> path
    Path(HttpsHost(nu.nl:443)/robots.txt)
    >>> "User-agent" in path.read_text()
    True

The ssl certificate of sites will be checked unless you disable it.

    >>> path = file_reader.hosts.http.HttpsHost("expired.badssl.com", verify_ssl=True)
    >>> import requests.exceptions
    >>> with pytest.raises(requests.exceptions.SSLError):
    ...     path.read_text()

    >>> path = file_reader.hosts.http.HttpsHost("expired.badssl.com", verify_ssl=False)
    >>> "expired.<br>badssl.com" in path.read_text()
    True

You can also specify an optional username and password for basic authentication.
Later on, we will add other authentication providers, like certificate or (Authroization) header.

    >>> path = file_reader.hosts.http.HttpsHost("nu.nl", auth=file_reader.auth.UsernamePassword("name", "secret")) / "robots.txt"


### FTP(S)

You can access ftp(s) sites:

    >>> path = file_reader.hosts.ftp.FTPHost("ftp.nluug.nl") / "pub" / "os" / "Linux" / "distr" / "ubuntu-releases" / "FOOTER.html"
    >>> path
    Path(FTPHost(ftp.nluug.nl:21)/pub/os/Linux/distr/ubuntu-releases/FOOTER.html)

    >>> file_reader.base.Host.from_url("ftp://ftp.nluug.nl/pub/os/Linux/distr/ubuntu-releases/FOOTER.html")
    Path(FTPHost(ftp.nluug.nl:21)/pub/os/Linux/distr/ubuntu-releases/FOOTER.html)

    >>> "</div></body></html>" in path.read_text()
    True

    >>> path = file_reader.hosts.ftp.FTPHost("test.rebex.net", auth=file_reader.auth.UsernamePassword("demo", "password")) / "pub" / "example" / "readme.txt"
    >>> "Welcome" in path.read_text()
    True

    >>> path = file_reader.hosts.ftp.FTPSHost("test.rebex.net", port=990, auth=file_reader.auth.UsernamePassword("demo", "password")) / "pub" / "example" / "readme.txt"
    >>> path
    Path(FTPSHost(test.rebex.net:990)/pub/example/readme.txt)

    >>> file_reader.base.Host.from_url("ftps://test.rebex.net:990/pub/example/readme.txt")
    Path(FTPSHost(test.rebex.net:990)/pub/example/readme.txt)

    >>> "Welcome" in path.read_text()
    True


### SFTP

    Note: Install with `pip install file_reader[ssh] to actually use SFTP

    >>> file_reader.hosts.sftp.SFTPHost("test.rebex.net", auth=file_reader.auth.UsernamePassword("demo", "password"), auto_add_host_key=True) / "pub" / "example" / "readme.txt"
    Path(SFTPHost(test.rebex.net:22)/pub/example/readme.txt)

    >>> file_reader.base.Host.from_url("sftp://test.rebex.net/pub/example/readme.txt")
    Path(SFTPHost(test.rebex.net:22)/pub/example/readme.txt)


### SMB

    Note: Install with `pip install file_reader[smb] to actually use SMB

    >>> file_reader.hosts.smb.SmbHost("server") / "share" / "folder" / "readme.txt"
    Path(SmbHost(server)/share/folder/readme.txt)

    >>> file_reader.base.Host.from_url("smb://server/share/folder/readme.txt")
    Path(SmbHost(server)/share/folder/readme.txt)


### S3

    Note: Install with `pip install file_reader[s3] to actually use S3

    >>> file_reader.hosts.s3.S3Host("filereaderpublic") / "test_folder" / "test_folder_2" / "test.txt"
    Path(S3Host(filereaderpublic)/test_folder/test_folder_2/test.txt)

    >>> file_reader.base.Host.from_url("s3://filereaderpublic/test_folder/test_folder_2/test.txt")
    Path(S3Host(filereaderpublic)/test_folder/test_folder_2/test.txt)

### HDFS

    Note: Install with `pip install file_reader[hdfs] to actually use HDFS

    >>> file_reader.hosts.hdfs.HdfsHost("localhost") / "pub" / "example" / "readme.txt"
    Path(HdfsHost(localhost)/pub/example/readme.txt)

    >>> file_reader.base.Host.from_url("hdfs://localhost/pub/example/readme.txt")
    Path(HdfsHost(localhost)/pub/example/readme.txt)


### Package

You can load every file within an installed Python Package, whether it is a Python or distributed data file.

    >>> path = file_reader.hosts.package.PythonPackage("file_reader") / "assets" / "test.txt"
    >>> "test" in path.read_text()
    True

## Archives

Also files in archives can be accessed.

    >>> path = file_reader.hosts.package.PythonPackage("file_reader") / "assets" / "test.zip" / "folder" / "file3.txt"
    >>> "file3" in path.read_text()
    True

When a path element has one of the known archive extensions, it will be read as an archive:

- .tar (tar)
- .tgz (tar)
- .tar.gz (tar)
- .zip (zip)
- .dep (zip)


## FAQ

Q Why do you only support reading files?

A For a lot of use cases reading files is sufficient. When you want to do more, like making directories, adding files,
removing files and changing permissions, the differences between the hosts became very big. Too big to use just
one API.
