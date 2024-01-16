from __future__ import annotations

import os
from pathlib import Path

from .exceptions import PathError


_PYENV_WIN = os.name == 'nt'
if _PYENV_WIN:
    _PYENV_ROOT_ENV_VARS = ('PYENV_ROOT', 'PYENV_HOME', 'PYENV')
    _PYENV_ROOT_DEFAULT = '.pyenv/pyenv-win'
    _PYTHON_EXECUTABLE = 'python.exe'
else:
    _PYENV_ROOT_ENV_VARS = ('PYENV_ROOT',)
    _PYENV_ROOT_DEFAULT = '.pyenv'
    _PYTHON_EXECUTABLE = 'bin/python'


def get_pyenv_root() -> Path:
    for env_var in _PYENV_ROOT_ENV_VARS:
        try:
            pyenv_root = Path(os.environ[env_var]).resolve()
            break
        except KeyError:
            pass
    else:
        pyenv_root = Path.home() / _PYENV_ROOT_DEFAULT
    if not pyenv_root.exists():
        raise PathError(f'pyenv root does not exist: {pyenv_root}')
    if not pyenv_root.is_dir():
        raise PathError(f'pyenv root is not a directory: {pyenv_root}')
    return pyenv_root


def get_pyenv_versions_directory() -> Path:
    pyenv_root = get_pyenv_root()
    versions_dir = (pyenv_root / 'versions').resolve()
    if not versions_dir.exists():
        raise PathError(f'pyenv versions path does not exist: {versions_dir}')
    if not versions_dir.is_dir():
        raise PathError(
            f'pyenv versions path is not a directory: {versions_dir}')
    return versions_dir


def get_pyenv_python_executable_path(version_dir: Path) -> Path:
    exec_path = (version_dir / _PYTHON_EXECUTABLE).resolve()
    if not exec_path.exists():
        raise PathError(f'pyenv python binary does not exist: {exec_path}')
    if not exec_path.is_file():
        raise PathError(f'pyenv python binary is not a file: {exec_path}')
    if not _PYENV_WIN and not os.access(exec_path, os.X_OK):
        raise PathError(f'pyenv python binary is not executable: {exec_path}')
    return exec_path
