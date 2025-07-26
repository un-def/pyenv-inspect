import re

import pytest

from pyenv_inspect.exceptions import PathError
from pyenv_inspect.path import (
    get_pyenv_python_executable_path, get_pyenv_root,
    get_pyenv_versions_directory,
)

from tests.testlib import posix_test, windows_test


class BaseTestGetPyenvRoot:

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        for env_var in ['PYENV_ROOT', 'PYENV_HOME', 'PYENV']:
            monkeypatch.delenv(env_var, raising=False)

    @pytest.fixture
    def fake_home(self, tmp_path, monkeypatch):
        _fake_home = tmp_path / 'fake_home'
        _fake_home.mkdir()
        monkeypatch.setattr('pathlib.Path.home', lambda: _fake_home)
        return _fake_home

    @pytest.fixture
    def pyenv_root_custom(self, tmp_path):
        pyenv_root = tmp_path / 'pyenv_custom_path'
        pyenv_root.mkdir()
        return pyenv_root

    @pytest.fixture
    def pyenv_root_default():
        raise NotImplementedError

    def test_default_location(self, pyenv_root_default):
        assert get_pyenv_root() == pyenv_root_default

    def test_error_does_not_exist(self, pyenv_root_default):
        pyenv_root_default.rmdir()
        message = f'pyenv root does not exist: {pyenv_root_default}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_root()

    def test_error_not_a_directory(self, pyenv_root_default):
        pyenv_root_default.rmdir()
        pyenv_root_default.touch()
        message = f'pyenv root is not a directory: {pyenv_root_default}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_root()


@posix_test
class TestGetPyenvRootPOSIX(BaseTestGetPyenvRoot):

    @pytest.fixture
    def pyenv_root_default(self, fake_home):
        pyenv_root = fake_home / '.pyenv'
        pyenv_root.mkdir()
        return pyenv_root

    def test_custom_location(self, monkeypatch, pyenv_root_custom):
        monkeypatch.setenv('PYENV_ROOT', str(pyenv_root_custom))

        assert get_pyenv_root() == pyenv_root_custom

    def test_custom_location_from_win_envs_ignored(
        self, monkeypatch, pyenv_root_default, pyenv_root_custom,
    ):
        monkeypatch.setenv('PYENV_HOME', str(pyenv_root_custom))
        monkeypatch.setenv('PYENV', str(pyenv_root_custom))

        assert get_pyenv_root() == pyenv_root_default


@windows_test
class TestGetPyenvRootWindows(BaseTestGetPyenvRoot):

    @pytest.fixture
    def pyenv_root_default(self, fake_home):
        pyenv_root = fake_home / '.pyenv' / 'pyenv-win'
        pyenv_root.mkdir(parents=True)
        return pyenv_root

    @pytest.mark.parametrize('env_var', ['PYENV_ROOT', 'PYENV_HOME', 'PYENV'])
    def test_custom_location(self, monkeypatch, pyenv_root_custom, env_var):
        monkeypatch.setenv(env_var, str(pyenv_root_custom))

        assert get_pyenv_root() == pyenv_root_custom


class TestGetPyenvVersionsDirectory:

    @pytest.fixture
    def pyenv_root(self, tmp_path):
        path = tmp_path / 'pyenv_root'
        path.mkdir()
        return path

    @pytest.fixture
    def versions_dir(self, pyenv_root):
        _versions_dir = pyenv_root / 'versions'
        _versions_dir.mkdir()
        return _versions_dir

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch, pyenv_root):
        monkeypatch.setattr(
            'pyenv_inspect.path.get_pyenv_root', lambda: pyenv_root)

    def test_ok(self, versions_dir):
        assert get_pyenv_versions_directory() == versions_dir

    def test_error_does_not_exist(self, versions_dir):
        versions_dir.rmdir()
        message = f'pyenv versions path does not exist: {versions_dir}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_versions_directory()

    def test_error_not_a_directory(self, versions_dir):
        versions_dir.rmdir()
        versions_dir.touch()
        message = f'pyenv versions path is not a directory: {versions_dir}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_versions_directory()


class BaseTestGetPyenvPythonExecutablePath:

    @pytest.fixture
    def pyenv_root(self, tmp_path):
        path = tmp_path / 'pyenv_root'
        path.mkdir()
        return path

    @pytest.fixture
    def version_dir(self, pyenv_root):
        return pyenv_root / 'versions' / '3.10.4'

    @pytest.fixture
    def exec_path():
        raise NotImplementedError

    @pytest.fixture(autouse=True)
    def setup(self, exec_path):
        exec_path.parent.mkdir(parents=True)

    def test_ok(self, version_dir, exec_path):
        exec_path.touch(mode=0o777)

        assert get_pyenv_python_executable_path(version_dir) == exec_path

    def test_error_does_not_exist(self, version_dir):
        message = f'pyenv python binary does not exist: {version_dir}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_python_executable_path(version_dir)

    def test_error_not_a_file(self, version_dir, exec_path):
        exec_path.mkdir()
        message = f'pyenv python binary is not a file: {version_dir}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_python_executable_path(version_dir)


@posix_test
class TestGetPyenvPythonExecutablePathPOSIX(
    BaseTestGetPyenvPythonExecutablePath,
):

    @pytest.fixture
    def exec_path(self, version_dir):
        return version_dir / 'bin' / 'python'

    def test_error_not_executable(self, version_dir, exec_path):
        exec_path.touch(mode=0o666)
        message = f'pyenv python binary is not executable: {version_dir}'

        with pytest.raises(PathError, match=re.escape(message)):
            get_pyenv_python_executable_path(version_dir)


@windows_test
class TestGetPyenvPythonExecutablePathWindows(
    BaseTestGetPyenvPythonExecutablePath,
):

    @pytest.fixture
    def exec_path(self, version_dir):
        return version_dir / 'python.exe'
