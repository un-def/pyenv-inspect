import json
import os
from pathlib import Path

import pytest


FIXTURE_PATH = Path(__file__).parent / 'spec_fixture.json'


with open(FIXTURE_PATH) as fobj:
    spec_fixture = json.load(fobj)


IS_POSIX = os.name == 'posix'
IS_WINDOWS = os.name == 'nt'

assert IS_POSIX or IS_WINDOWS, os.name

posix_test = pytest.mark.skipif(not IS_POSIX, reason='requires posix')
windows_test = pytest.mark.skipif(not IS_WINDOWS, reason='requires windows')
