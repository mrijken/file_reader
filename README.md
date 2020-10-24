# file_assets

## Read almost all files from almost anywhere with one API

Uniform file reader for a lot of different file storages, like

- local filesystem
- http(s)
- ftp(s)
- smb
- sftp


    >>> import file_assets
    >>> import pytest

## Usage


### Construct a Host and a Path

    >>> path = file_assets.hosts.ftp.FTPHost('ftp.nluug.nl') / 'pub' / 'os' / 'Linux' / 'distr' / 'ubuntu-releases' / 'FOOTER.html'
    >>> path
    Path(Host(ftp), /pub/os/Linux/distr/ubuntu-releases/FOOTER.html)

### Accces the conents like a file

Use it as a regular file object:

- with or without a context managers

    >>> with path.open() as f:
    ...     f.read()
    '\n</div></body></html>\n'

    >>> f = path.open()
    >>> f.read()
    '\n</div></body></html>\n'
    >>> f.close()

- in text (default) or binary mode

    >>> with path.open('b') as f:
    ...     f.read()
    b'\n</div></body></html>\n'

- with a specified size

    >>> with path.open('b') as f:
    ...     f.read(3)
    b'\n</'
    >>> f.close()

### Access the contents direct

Read the content direct from the path as text:

    >>> path.read_text()
    '\n</div></body></html>\n'

    >>> path.read_text(3)
    '\n</'

or as binary:

    >>> path.read_bytes()
    b'\n</div></body></html>\n'

    >>> path.read_bytes(3)
    b'\n</'

### Create a Path from an url

You can construct a Host and Path by parsing an url, like:

    >>> file_assets.base.Host.from_url("ftp://marc:secret@ftp.nluug.nl/pub/os/Linux/distr/ubuntu-releases/FOOTER.html")
    Path(Host(ftp), /pub/os/Linux/distr/ubuntu-releases/FOOTER.html)

    >>> file_assets.base.Host.from_url("http://marc:secret@nu.nl/robots.txt")
    Path(Host(http), /robots.txt)

    >>> file_assets.base.Host.from_url("package://file_assets/__init__.py")
    Path(Host(package), /__init__.py)

## Possible hosts

For every supported file location, a host is defined which knows how to access the file. The following
hosts are supported

### System

This is the local filesystem of your machine. It can access all files from all already mounted drives.
It will use the credentials of the user who is running the python process.

You can use a path relative to the working directory

    >>> file_assets.hosts.system.SystemHost() / "file_assets" / "__init__.py"
    Path(Host(file, cwd=.), /file_assets/__init__.py)

A path relative to the home dir of the current user can be used

    >>> file_assets.hosts.system.SystemHost(home_dir=True) / ".ssh" / "id_rsa.pub"
    Path(Host(file, cwd=/home/...), /.ssh/id_rsa.pub)

Or an absolute path can be used:

    >>> file_assets.hosts.system.SystemHost(root=True) / "etc" / "hosts"
    Path(Host(file, cwd=/), /etc/hosts)


### HTTP(S)

Via the GET method a file from a HTTP(S) location will be get.

    >>> path = file_assets.hosts.http.HttpHost("nu.nl") / "robots.txt"
    >>> path
    Path(Host(http), /robots.txt)
    >>> "User-agent" in path.read_text()
    True

    >>> path = file_assets.hosts.http.HttpsHost("nu.nl") / "robots.txt"
    >>> path
    Path(Host(https), /robots.txt)
    >>> "User-agent" in path.read_text()
    True

The ssl certificate of sites will be checked unless you disable it.

    >>> path = file_assets.hosts.http.HttpsHost("expired.badssl.com", verify_ssl=True).root_path
    >>> import requests.exceptions
    >>> with pytest.raises(requests.exceptions.SSLError):
    ...     path.read_text()

    >>> path = file_assets.hosts.http.HttpsHost("expired.badssl.com", verify_ssl=False).root_path
    >>> "expired.<br>badssl.com" in path.read_text()
    True

You can also specify an optional username and password for basic authentication.
Later on, we will add other authentication providers, like certificate or (Authroization) header.

    >>> path = file_assets.hosts.http.HttpsHost("nu.nl", auth=file_assets.auth.UsernamePassword("name", "secret")) / "robots.txt"


### FTP(S)

You can access ftp(s) sites:

    >>> path = file_assets.hosts.ftp.FTPHost("ftp.nluug.nl") / "pub" / "os" / "Linux" / "distr" / "ubuntu-releases" / "FOOTER.html"
    >>> "</div></body></html>" in path.read_text()
    True

    >>> path = file_assets.hosts.ftp.FTPHost("test.rebex.net", auth=file_assets.auth.UsernamePassword("demo", "password")) / "pub" / "example" / "readme.txt"
    >>> "Welcome" in path.read_text()
    True

    >>> path = file_assets.hosts.ftp.FTPSHost("test.rebex.net", port=990, auth=file_assets.auth.UsernamePassword("demo", "password")) / "pub" / "example" / "readme.txt"
    >>> "Welcome" in path.read_text()
    True


### SFTP

    >>> path = file_assets.hosts.sftp.SFTPHost("test.rebex.net", auth=file_assets.auth.UsernamePassword("demo", "password"), auto_add_host_key=True) / "pub" / "example" / "readme.txt"

    #>>> "Welcome" in path.read_text()
    #True


### SMB

    >>> path = file_assets.hosts.smb.SmbHost("localhost") / "pub" / "example" / "readme.txt"

### S3

    >>> path = file_assets.hosts.s3.S3Host("access_key", "secret", "region") / "pub" / "example" / "readme.txt"


### HDFS

    >>> path = file_assets.hosts.hdfs.HdfsHost("localhost") / "pub" / "example" / "readme.txt"


### Package

You can load every file within an installed Python Package, whether it is a Python or distributed data file.

    >>> path = file_assets.hosts.package.PythonPackage("file_assets") / "exceptions.py"
    >>> "class FileNotAccessable(Exception):" in path.read_text()
    True



## FAQ

Q Why do you only support reading files?

A For a lot of use cases reading files is sufficient. When you want to do more, like making directories, adding files,
removing files and changing permissions, the differences between the hosts became very big. Too big to use just
one API.
