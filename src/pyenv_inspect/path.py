from __future__ import annotations

import os
from pathlib import Path

from .exceptions import PathError


def get_pyenv_root() -> Path:
    try:
        pyenv_root = Path(os.environ['PYENV_ROOT']).resolve()
    except KeyError:
        pyenv_root = Path.home() / '.pyenv'
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


def get_pyenv_python_bin_path(version_dir: Path) -> Path:
    bin_path = (version_dir / 'bin' / 'python').resolve()
    if not bin_path.exists():
        raise PathError(f'pyenv python executable does not exist: {bin_path}')
    if not bin_path.is_file():
        raise PathError(f'pyenv python executable is not a file: {bin_path}')
    return bin_path
