import logging

import pytest

from pyenv_inspect import find_pyenv_python_executable
from pyenv_inspect.exceptions import UnsupportedImplementation
from pyenv_inspect.spec import PyenvPythonSpec

from tests.testlib import IS_POSIX, IS_WINDOWS


class TestFindPyenvPythonExecutable:
    if IS_POSIX:
        exec_name = 'python'
        bin_dir = 'bin'
    elif IS_WINDOWS:
        exec_name = 'python.exe'
        bin_dir = ''

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch, tmp_path):
        self.pyenv_root = tmp_path / 'pyenv_root'
        monkeypatch.setenv('PYENV_ROOT', str(self.pyenv_root))
        self.versions_dir = self.pyenv_root / 'versions'
        self.versions_dir.mkdir(parents=True)

    def prepare_version(self, version):
        bin_path = self.versions_dir / version / self.bin_dir
        bin_path.mkdir(parents=True)
        exec_path = bin_path / self.exec_name
        exec_path.touch(mode=0o777)
        return exec_path

    def prepare_versions(self, *versions):
        return [self.prepare_version(version) for version in versions]

    def prepare_env(self, name, version):
        self.prepare_version(version)
        env_path = self.versions_dir / version / 'envs' / name
        env_path.mkdir(parents=True)
        link_path = self.versions_dir / name
        link_path.symlink_to(env_path)

    @pytest.mark.parametrize('requested,expected', [
        ('3', '3.8.3'),
        (PyenvPythonSpec.from_string_spec('3'), '3.8.3'),
        ('3.7', '3.7.12'),
        (PyenvPythonSpec.from_string_spec('3.7'), '3.7.12'),
        ('3.7.1', '3.7.1'),
        (PyenvPythonSpec.from_string_spec('3.7.1'), '3.7.1'),
    ])
    def test_found(self, requested, expected):
        self.prepare_versions('3.7.2', '3.7.1', '3.7.12', '3.8.3')
        assert find_pyenv_python_executable(requested) == (
            self.versions_dir / expected / self.bin_dir / self.exec_name)

    def test_env_links_ignored(self, caplog: pytest.LogCaptureFixture):
        caplog.set_level(logging.WARNING)
        self.prepare_env('dev-env', '3.12.9')
        assert find_pyenv_python_executable('3.12') == (
            self.versions_dir / '3.12.9' / self.bin_dir / self.exec_name)
        assert len(caplog.messages) == 0

    @pytest.mark.parametrize('version', ['3.9', '3.7.3'])
    def test_not_found(self, version):
        self.prepare_versions('3.7.2', '3.8.3')
        assert find_pyenv_python_executable(version) is None

    def test_unsupported(self):
        with pytest.raises(UnsupportedImplementation):
            find_pyenv_python_executable('fakepython-3.7')
