import pytest

from pyenv_inspect.spec import Implementation, PyenvPythonSpec

from tests.testlib import spec_fixture


@pytest.mark.parametrize('actual,expected', [(
    PyenvPythonSpec.from_string_spec(spec_dict['string_spec']),
    PyenvPythonSpec(
        spec_dict['string_spec'],
        Implementation(spec_dict['implementation']),
        spec_dict['version'],
    ),
) for spec_dict in spec_fixture['specs']])
def test_python_spec(actual, expected):
    assert actual == expected
