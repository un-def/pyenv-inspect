import pytest

from pyenv_inspect.exceptions import VersionParseError
from pyenv_inspect.version import Version

from tests.testlib import spec_fixture


@pytest.mark.parametrize('string_version', [
    spec_dict['version']
    for spec_dict in spec_fixture['specs']
    if spec_dict['implementation'] == 'cpython'
])
def test_parse_fixture_cpython_specs(string_version):
    Version.from_string_version(string_version)


def test_parse_error():
    with pytest.raises(VersionParseError):
        Version.from_string_version('1.a.0')


@pytest.mark.parametrize('str_v1,str_v2,expected', [
    ('2', '2.0.0', True),
    ('2.0', '2.0.0', True),
    ('2.0-dev', '2.0.0-dev', True),
    ('2.0a1', '2.0.0a1', True),
    ('2.0.1', '2.0', False),
    ('2.0', '2.0.0-dev', False),
    ('2.0a1', '2.0', False),
    ('2.0a1', '2.0a2', False),
    ('2.0a1', '2.0b1', False),
    ('3.14t', '3.14.0t', True),
])
def test_eq_ne(str_v1, str_v2, expected):
    v1 = Version.from_string_version(str_v1)
    v2 = Version.from_string_version(str_v2)

    eq_result = v1 == v2
    ne_result = v1 != v2

    assert eq_result is expected
    assert ne_result is (not expected)


@pytest.mark.parametrize('str_v1,str_v2', [
    ('3.14t', '3.14'),
    ('3.14', '3.14t'),
])
def test_eq_ne_threading_model_error(str_v1, str_v2):
    v1 = Version.from_string_version(str_v1)
    v2 = Version.from_string_version(str_v2)

    with pytest.raises(TypeError, match='threading model'):
        v1 == v2
    with pytest.raises(TypeError, match='threading model'):
        v1 != v2


@pytest.mark.parametrize('str_v1,str_v2,expected', [
    ('2', '2.0.0', False),
    ('2.0', '2.0.0', False),
    ('2', '2.0.1', True),
    ('2.0.0', '2.0.1', True),
    ('2.0', '2.0.1', True),
    ('2.0.1', '2.0.0', False),
    ('2.0.1', '2', False),
    ('2.0-dev', '2.0', True),
    ('2.1-dev', '2.0', False),
    ('2.0a3', '2.0', True),
    ('2.0a4', '2.0a5', True),
    ('2.0a10', '2.0a2', False),
    ('2.0.1b3', '2.0.0', False),
    ('2.0b3', '2.0a7', False),
    ('2.0a7', '2.0b3', True),
])
def test_lt_ge(str_v1, str_v2, expected):
    v1 = Version.from_string_version(str_v1)
    v2 = Version.from_string_version(str_v2)

    lt_result = v1 < v2
    ge_result = v1 >= v2

    assert lt_result is expected
    assert ge_result is (not expected)


@pytest.mark.parametrize('str_v1,str_v2,expected', [
    ('2', '2.0.0', False),
    ('2.0', '2.0.0', False),
    ('2.0.0', '2.0.1', False),
    ('2', '2.0.1', False),
    ('2.0', '2.0.1', False),
    ('2.0.1', '2.0.0', True),
    ('2.0.1', '2', True),
    ('2.0-dev', '2.0', False),
    ('2.1-dev', '2.0', True),
    ('2.0a3', '2.0', False),
    ('2.0a4', '2.0a5', False),
    ('2.0a10', '2.0a2', True),
    ('2.0.1b3', '2.0.0', True),
    ('2.0b3', '2.0a7', True),
    ('2.0a7', '2.0b3', False),
])
def test_gt_le(str_v1, str_v2, expected):
    v1 = Version.from_string_version(str_v1)
    v2 = Version.from_string_version(str_v2)

    gt_result = v1 > v2
    le_result = v1 <= v2

    assert gt_result is expected
    assert le_result is (not expected)


@pytest.mark.parametrize('str_v1,str_v2,expected', [
    ('2.6.7', '2', True),
    ('2.6.7', '3', False),
    ('2.6.7', '2.6', True),
    ('2.6.7', '2.6.7', True),
    ('2.6', '2.6.7', False),
    ('2.6.7', '2.7', False),
    ('2.6.7-dev', '2.6', False),
    ('2.6.7', '2.6-dev', False),
    ('2.6.7-dev', '2.6-dev', False),
    ('2.6.7-dev', '2.6.7-dev', True),
    ('2.6.8-dev', '2.6.7-dev', False),
    ('2.6.7a3', '2.6', False),
    ('2.6.7a3', '2.6.7b3', False),
    ('2.6.7a3', '2.6.8a3', False),
    ('2.6.7a3', '2.6.7a3', True),
    ('3.14.0t', '3.14t', True),
    ('3.14.0t', '3.14', False),
    ('3.14.0', '3.14t', False),
    ('3.14.0', '3.14', True),
])
def test_contains(str_v1, str_v2, expected):
    v1 = Version.from_string_version(str_v1)
    v2 = Version.from_string_version(str_v2)

    result = v1 in v2

    assert result is expected
