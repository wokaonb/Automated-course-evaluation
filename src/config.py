import tomllib
from pathlib import Path

_cfg = tomllib.loads(Path('config.toml').read_text(encoding='utf-8'))

BASE_URL: str = _cfg['site']['base_url']
USER_NAME: str = _cfg['credentials']['username']
USER_PASSWORD: str = _cfg['credentials']['password']
HEADLESS: bool = _cfg['browser']['headless']
VIEWPORT: dict = _cfg['browser']['viewport']
LOCALE: str = _cfg['browser']['locale']

STORAGE_FILE: str = 'storage.json'
MANAGER_URL: str = f'{BASE_URL}/dashboard/analysis'
