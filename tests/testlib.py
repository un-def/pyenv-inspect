import json
from inspect import isfunction, signature
from pathlib import Path


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
