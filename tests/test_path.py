import pytest

from pyenv_inspect.exceptions import PathError
from pyenv_inspect.path import (
    get_pyenv_python_executable_path, get_pyenv_root,
    get_pyenv_versions_directory,
)

from tests.testlib import BaseTestClass


@pytest.fixture
def pyenv_root(tmp_path):
    path = tmp_path / 'pyenv_root'
    path.mkdir()
    return path


class BaseTestGetPyenvRoot(BaseTestClass):

    def test_ok(pyenv_root):
        pyenv_root.mkdir()

        assert get_pyenv_root() == pyenv_root

    def test_error_does_not_exist(pyenv_root):
        message = f'pyenv root does not exist: {pyenv_root}'

        with pytest.raises(PathError, match=message):
            get_pyenv_root()

    def test_error_not_a_directory(pyenv_root):
        pyenv_root.touch()
        message = f'pyenv root is not a directory: {pyenv_root}'

        with pytest.raises(PathError, match=message):
            get_pyenv_root()


class TestGetPyenvRootFromEnvironment(BaseTestGetPyenvRoot):

    @pytest.fixture
    def pyenv_root(tmp_path):
        return tmp_path / 'pyenv_root'

    @pytest.fixture(autouse=True)
    def setup(monkeypatch, pyenv_root):
        monkeypatch.setenv('PYENV_ROOT', str(pyenv_root))


class TestGetPyenvRootFallback(BaseTestGetPyenvRoot):

    @pytest.fixture
    def pyenv_root(fake_home):
        return fake_home / '.pyenv'

    @pytest.fixture
    def fake_home(tmp_path):
        return tmp_path / 'home' / 'user'

    @pytest.fixture(autouse=True)
    def setup(monkeypatch, fake_home):
        fake_home.mkdir(parents=True)
        monkeypatch.setattr('pathlib.Path.home', lambda: fake_home)
        monkeypatch.delenv('PYENV_ROOT', raising=False)


class TestGetPyenvVersionsDirectory(BaseTestClass):

    @pytest.fixture
    def versions_dir(pyenv_root):
        return pyenv_root / 'versions'

    @pytest.fixture(autouse=True)
    def setup(monkeypatch, pyenv_root):
        monkeypatch.setattr(
            'pyenv_inspect.path.get_pyenv_root', lambda: pyenv_root)

    def test_ok(versions_dir):
        versions_dir.mkdir()

        assert get_pyenv_versions_directory() == versions_dir

    def test_error_does_not_exist(versions_dir):
        message = f'pyenv versions path does not exist: {versions_dir}'

        with pytest.raises(PathError, match=message):
            get_pyenv_versions_directory()

    def test_error_not_a_directory(versions_dir):
        versions_dir.touch()
        message = f'pyenv versions path is not a directory: {versions_dir}'

        with pytest.raises(PathError, match=message):
            get_pyenv_versions_directory()


class TestGetPyenvPythonExecutablePath(BaseTestClass):

    @pytest.fixture
    def version_dir(pyenv_root):
        return pyenv_root / 'versions' / '3.10.4'

    @pytest.fixture
    def exec_path(version_dir):
        return version_dir / 'bin' / 'python'

    @pytest.fixture(autouse=True)
    def setup(exec_path):
        exec_path.parent.mkdir(parents=True)

    def test_ok(version_dir, exec_path):
        exec_path.touch(mode=0o777)

        assert get_pyenv_python_executable_path(version_dir) == exec_path

    def test_error_does_not_exist(version_dir):
        message = f'pyenv python binary does not exist: {version_dir}'

        with pytest.raises(PathError, match=message):
            get_pyenv_python_executable_path(version_dir)

    def test_error_not_a_file(version_dir, exec_path):
        exec_path.mkdir()
        message = f'pyenv python binary is not a file: {version_dir}'

        with pytest.raises(PathError, match=message):
            get_pyenv_python_executable_path(version_dir)

    def test_error_not_executable(version_dir, exec_path):
        exec_path.touch(mode=0o666)
        message = f'pyenv python binary is not executable: {version_dir}'

        with pytest.raises(PathError, match=message):
            get_pyenv_python_executable_path(version_dir)
