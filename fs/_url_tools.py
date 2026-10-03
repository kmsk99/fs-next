import typing

import platform
import re
from urllib.parse import quote

if typing.TYPE_CHECKING:
    from typing import Text

_WINDOWS_PLATFORM = platform.system() == "Windows"


def url_quote(path_snippet):
    # type: (Text) -> Text
    """Quote a URL without quoting the Windows drive letter, if any.

    On Windows, it will separate drive letter and quote Windows
    path alone. Unix paths are quoted as URL path components without adding an authority.

    Arguments:
       path_snippet (str): a file path, relative or absolute.

    """
    # FS URLs already supply their scheme. pathname2url() started adding
    # an authority prefix for absolute paths in Python 3.14, which would
    # turn osfs:///tmp into osfs://///tmp. Quote the path component only.
    if _WINDOWS_PLATFORM:
        path_snippet = path_snippet.replace("\\", "/")
        if _has_drive_letter(path_snippet):
            drive, path = path_snippet.split(":", 1)
            return drive + ":" + quote(path, safe="/")
    return quote(path_snippet, safe="/")


def _has_drive_letter(path_snippet):
    # type: (Text) -> bool
    """Check whether a path contains a drive letter.

    Arguments:
       path_snippet (str): a file path, relative or absolute.

    Example:
        >>> _has_drive_letter("D:/Data")
        True
        >>> _has_drive_letter(r"C:\\System32\\ test")
        True
        >>> _has_drive_letter("/tmp/abc:test")
        False

    """
    windows_drive_pattern = ".:[/\\\\].*$"
    return re.match(windows_drive_pattern, path_snippet) is not None
