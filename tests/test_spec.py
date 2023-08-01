import pytest

from pyenv_inspect.exceptions import UnsupportedImplementation
from pyenv_inspect.spec import Implementation, PyenvPythonSpec

from tests.testlib import spec_fixture


_python_spec_parametrize_values = []
for spec_dict in spec_fixture['specs']:
    assert spec_dict.get('_checked', True), f'not checked: {spec_dict}'
    _python_spec_parametrize_values.append((
        PyenvPythonSpec.from_string_spec(spec_dict['string_spec']),
        PyenvPythonSpec(
            spec_dict['string_spec'],
            Implementation(spec_dict['implementation']),
            spec_dict['version'],
        ),
    ))


@pytest.mark.parametrize('actual,expected', _python_spec_parametrize_values)
def test_python_spec(actual, expected):
    assert actual == expected


@pytest.mark.parametrize('raise_exception', [False, True])
def test_is_supported(raise_exception):
    spec = PyenvPythonSpec.from_string_spec('3.10.3')

    result = spec.is_supported(raise_exception=raise_exception)

    assert result is True


def test_is_not_supported():
    spec = PyenvPythonSpec.from_string_spec('unsupported-3.10.3')

    result = spec.is_supported()

    assert result is False


def test_is_not_supported_raise_exception():
    spec = PyenvPythonSpec.from_string_spec('unsupported-3.10.3')

    with pytest.raises(UnsupportedImplementation):
        spec.is_supported(raise_exception=True)
