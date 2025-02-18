"""
Utilities for converting to LNT's test format.

LNT formats are described by dictionaries with 'name', 'read', and 'write'
fields. Only the 'name' field is required. The 'read' field should be a
callable taking a path_or_file object, the 'write' function should be a
callable taking a Python object to write, and the path_or_file to write to.
"""

from __future__ import absolute_import
from typing import List, Dict
try:
    from plistlib import readPlist  # noqa: F401  # used to test exception
    from .PlistFormat2 import format as plist  # for Python 2
except ImportError:
    from .PlistFormat import format as plist  # for Python 3
from .JSONFormat import format as json

formats = [plist, json]  # type: List[Dict]
formats_by_name = dict((f['name'], f) for f in formats)  # type: Dict[str, Dict]
format_names = list(formats_by_name.keys())  # type: List[str]


def get_format(name):
    """get_format(name) -> [format]

    Loookup a format object by name.
    """

    return formats_by_name.get(name)


def guess_format(path_or_file):
    """guess_format(path_or_file) -> [format]

    Guess which format should be used to load the given file and return it, if
    found.
    """

    # Check that files are seekable.
    is_file = False
    if not isinstance(path_or_file, str):
        is_file = True
        path_or_file.seek(0)

    matches = None
    for f in formats:
        # Check if the path matches this format, ignoring exceptions.
        try:
            try:
                if not f['predicate'](path_or_file):
                    continue
            except Exception:
                continue
        finally:
            if is_file:
                # Reset seek.
                path_or_file.seek(0)

        # Reject anything which matches multiple formats.
        if matches:
            return None

        matches = f

    return matches


def read_any(path_or_file, format_name):
    """read_any(path_or_file, format_name) -> [format]

    Attempt to read any compatible LNT test format file. The format_name can be
    an actual format name, or "<auto>".
    """
    # Figure out the input format.
    if format_name == '<auto>':
        f = guess_format(path_or_file)
        if f is None:
            if isinstance(path_or_file, str):
                raise ValueError("unable to guess input format for %r" % (
                    path_or_file,))
            else:
                raise ValueError("unable to guess input format for file")
    else:
        f = get_format(format_name)
        if f is None or not f.get('read'):
            raise ValueError("unknown input format: %r" % format_name)

    return f['read'](path_or_file)


__all__ = ['get_format', 'guess_format', 'read_any'] + format_names
