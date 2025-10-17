import operator
import re
from functools import cached_property, partial
from typing import Callable, Optional, TypeVar, Union, overload

from .exceptions import VersionParseError


VERSION_PATTERN = (
    r'(?P<base>\d(?:\.\d+){0,2})'
    r'(?P<pre>(?:a|b|rc)\d+)?'
    r'(?P<free_threaded>t)?'
    r'(?P<dev>-dev)?'
)
VERSION_REGEX = re.compile(VERSION_PATTERN)


class _comparison:
    op: Callable[[object, object], bool]

    _T = TypeVar('_T')

    def __set_name__(self, owner, name):
        self.op = getattr(operator, name)

    @overload
    def __get__(
        self, instance: None, owner: Optional[type[_T]] = None,
    ) -> "_comparison":
        ...

    @overload
    def __get__(
        self, instance: _T, owner: Optional[type[_T]] = None,
    ) -> Callable[[object], bool]:
        ...

    def __get__(
        self, instance: Optional[_T], owner: Optional[type[_T]] = None
    ) -> Union["_comparison", Callable[[object], bool]]:
        if instance is None:
            return self
        return partial(self._compare, instance)

    def _compare(self, left: object, right: object) -> bool:
        if not isinstance(left, Version):
            return NotImplemented
        if not isinstance(right, Version):
            return NotImplemented
        if left._free_threaded != right._free_threaded:
            raise TypeError(
                f'threading model must be the same: {left}, {right}')
        return self.op(left._comparable, right._comparable)


class Version:

    def __init__(
        self,
        base: tuple[int, ...],
        pre: Optional[tuple[str, int]] = None,
        dev: bool = False,
        free_threaded: bool = False,
    ) -> None:
        self._base = base
        self._pre = pre
        self._dev = dev
        self._free_threaded = free_threaded

    @property
    def base(self) -> tuple[int, ...]:
        return self._base

    @property
    def pre(self) -> Optional[tuple[str, int]]:
        return self._pre

    @property
    def dev(self) -> bool:
        return self._dev

    @property
    def free_threaded(self) -> bool:
        return self._free_threaded

    @cached_property
    def _base_short(self) -> tuple[int, ...]:
        base = self._base
        for offset in range(len(base) - 1, -1, -1):
            if base[offset]:
                return base[:offset + 1]
        return ()

    @cached_property
    def _hash(self) -> int:
        return hash((self._base_short, self._pre, self._dev))

    @cached_property
    def _string_version(self) -> str:
        string_version = '.'.join(map(str, self._base))
        if self._pre:
            string_version = f'{string_version}{self._pre[0]}{self._pre[1]}'
        if self._free_threaded:
            string_version = f'{string_version}t'
        if self._dev:
            string_version = f'{string_version}-dev'
        return string_version

    @cached_property
    def _comparable(
        self,
    ) -> tuple[tuple[int, ...], int, int, Optional[tuple[str, int]]]:
        return (
            self._base_short,
            -1 if self._dev else 0,
            -1 if self._pre else 0,
            self._pre if self._pre else None,
        )

    @classmethod
    def from_string_version(cls, string_version: str) -> Optional["Version"]:
        match = VERSION_REGEX.fullmatch(string_version)
        if not match:
            raise VersionParseError(string_version)
        fields = match.groupdict()
        base = tuple(map(int, fields['base'].split('.')))
        pre: Optional[tuple[str, int]] = None
        if _pre := fields['pre']:
            if _pre.startswith('rc'):
                pre = ('rc', int(_pre[2:]))
            else:
                pre = (_pre[0], int(_pre[1:]))
        dev = bool(fields['dev'])
        free_threaded = bool(fields['free_threaded'])
        return cls(base=base, pre=pre, dev=dev, free_threaded=free_threaded)

    def __str__(self) -> str:
        return self._string_version

    def __repr__(self) -> str:
        return f'Version {self}'

    def __hash__(self) -> int:
        return self._hash

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, Version):
            return False
        if self._free_threaded != item._free_threaded:
            return False
        if self._dev != item._dev:
            return False
        if self._pre != item._pre:
            return False
        if len(self._base) > len(item._base):
            return False
        if self._dev or item._dev:
            item_base = item._base
        else:
            item_base = item._base[:len(self._base)]
        return self._base == item_base

    __eq__ = _comparison()   # type: ignore
    __ne__ = _comparison()   # type: ignore
    __lt__ = _comparison()
    __le__ = _comparison()
    __gt__ = _comparison()
    __ge__ = _comparison()
