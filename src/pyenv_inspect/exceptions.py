from __future__ import annotations


class PyenvInspectError(Exception):
    message = 'generic error'

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message

    def __str__(self) -> str:
        return self.message


class PathError(PyenvInspectError):
    message = 'path error'


class ParseError(PyenvInspectError):
    message = 'generic parse error'


class SpecParseError(ParseError):
    message = 'spec parse error'


class VersionParseError(ParseError):
    message = 'version parse error'


class UnsupportedImplementation(PyenvInspectError):
    message = 'only CPython is currently supported'
