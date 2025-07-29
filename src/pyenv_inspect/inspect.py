from __future__ import annotations

import logging
from pathlib import Path

from .exceptions import ParseError, UnsupportedImplementation
from .path import (
    get_pyenv_python_executable_path, get_pyenv_versions_directory,
)
from .spec import PyenvPythonSpec
from .version import Version


log = logging.getLogger(__name__)


def find_pyenv_python_executable(spec: PyenvPythonSpec | str) -> Path | None:
    if not isinstance(spec, PyenvPythonSpec):
        if not isinstance(spec, str):
            raise TypeError(f'unexpected spec type: {type(spec)}')
        spec = PyenvPythonSpec.from_string_spec(spec)
    spec.is_supported(raise_exception=True)
    requested_version = Version.from_string_version(spec.version)
    log.debug('requested %s', requested_version)
    best_match_version: Version | None = None
    best_match_dir: Path | None = None
    versions_dir = get_pyenv_versions_directory()
    for version_dir in versions_dir.iterdir():
        if _is_pyenv_virtualenv_symlink(version_dir):
            continue
        try:
            _spec = PyenvPythonSpec.from_string_spec(version_dir.name)
            _spec.is_supported(raise_exception=True)
            version = Version.from_string_version(_spec.version)
        except (ParseError, UnsupportedImplementation) as exc:
            log.warning('%s: %s', type(exc), exc)
            continue
        if version not in requested_version:
            continue
        log.debug('proposed %s', version)
        if not best_match_version or version > best_match_version:
            best_match_version = version
            best_match_dir = version_dir
    if not best_match_version:
        return None
    log.debug('accepted %s', best_match_version)
    return get_pyenv_python_executable_path(best_match_dir)


def _is_pyenv_virtualenv_symlink(path: Path) -> bool:
    # {versions_dir}/{name} -> {versions_dir}/{version}/envs/{name}
    if not path.is_symlink():
        return False
    real_path = path.resolve()
    return (
        real_path.is_relative_to(path.parent)
        and real_path.parent.name == 'envs'
        and real_path.name == path.name
    )
