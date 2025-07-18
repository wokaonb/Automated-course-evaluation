import tomllib
from pathlib import Path

_cfg = tomllib.loads(Path('config.toml').read_text(encoding='utf-8'))

BASE_URL = _cfg['site']['base_url']
USER_NAME = _cfg['credentials']['username']
USER_PASSWORD = _cfg['credentials']['password']
HEADLESS = _cfg['browser']['headless']
VIEWPORT = _cfg['browser']['viewport']
LOCALE = _cfg['browser']['locale']


MANAGER_URL = f'{BASE_URL}/dashboard/analysis'
