import json
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / 'spec_fixture.json'


with open(FIXTURE_PATH) as fobj:
    spec_fixture = json.load(fobj)