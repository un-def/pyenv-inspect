import json
import os
from inspect import isfunction, signature
from pathlib import Path

import pytest


FIXTURE_PATH = Path(__file__).parent / 'spec_fixture.json'


with open(FIXTURE_PATH) as fobj:
    spec_fixture = json.load(fobj)


class BaseTestClassMeta(type):

    def __new__(cls, name, bases, namespace):
        for key, value in namespace.items():
            if not isfunction(value):
                continue
            try:
                first_arg = next(iter(signature(value).parameters))
            except StopIteration:
                first_arg = None
            if first_arg not in ['self', 'cls']:
                namespace[key] = staticmethod(value)
        return super().__new__(cls, name, bases, namespace)


class BaseTestClass(metaclass=BaseTestClassMeta):
    pass


IS_POSIX = os.name == 'posix'
IS_WINDOWS = os.name == 'nt'

assert IS_POSIX or IS_WINDOWS, os.name

posix_test = pytest.mark.skipif(not IS_POSIX, reason='requires posix')
windows_test = pytest.mark.skipif(not IS_WINDOWS, reason='requires windows')
