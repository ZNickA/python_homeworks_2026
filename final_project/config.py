import os
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    api_key: str
    api_host: str
    limit_message: int | None
    limit_chars: int | None
    temperature: float
    system_prompt: str | None
    model: str
    stream: bool


ENV_KEYS = {
    'api_key': 'API_KEY',
    'api_host': 'API_HOST',
    'limit_message': 'LIMIT_MESSAGE',
    'limit_chars': 'LIMIT_CHARS',
    'temperature': 'TEMPERATURE',
    'model': 'MODEL',
    'stream': 'STREAM',
}


def load_config(path: Path | None = None) -> Config | None:
    config_path = path or _find_config()
    if config_path is not None and not config_path.exists():
        config_path = None
    data = _read_yaml(config_path) if config_path is not None else {}
    has_settings = config_path is not None

    for key, env_key in ENV_KEYS.items():
        value = os.environ.get(env_key)
        if value is not None:
            data[key] = value
            has_settings = True

    if not has_settings:
        return None

    api_key = _required(data, 'api_key')
    api_host = _required(data, 'api_host').rstrip('/')
    if not api_host:
        raise ConfigError('api_host is empty')

    return Config(
        api_key=api_key,
        api_host=api_host,
        limit_message=_optional_int(data, 'limit_message'),
        limit_chars=_optional_int(data, 'limit_chars'),
        temperature=_temperature(data.get('temperature')),
        system_prompt=data.get('system_prompt') or None,
        model=data.get('model') or 'gemma3:latest',
        stream=_bool_value(data.get('stream')),
    )


def _find_config() -> Path | None:
    paths = (Path('config.yaml'), Path(__file__).with_name('config.yaml'))
    for path in paths:
        if path.exists():
            return path
    return None


def _read_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or ':' not in line:
            continue
        key, value = line.split(':', 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def _required(data: dict[str, str], key: str) -> str:
    value = data.get(key)
    if value:
        return value
    raise ConfigError(f'{key} is required')


def _optional_int(data: dict[str, str], key: str) -> int | None:
    value = data.get(key)
    if not value:
        return None
    try:
        result = int(value)
    except ValueError as error:
        raise ConfigError(f'{key} must be an integer') from error
    if result <= 0:
        raise ConfigError(f'{key} must be positive')
    return result


def _temperature(value: str | None) -> float:
    if not value:
        return 0.2
    try:
        result = float(value)
    except ValueError as error:
        raise ConfigError('temperature must be a number') from error
    if result < 0 or result > 1:
        raise ConfigError('temperature must be from 0 to 1')
    return result


def _bool_value(value: str | None) -> bool:
    if value is None:
        return True
    return value.lower() in {'1', 'true', 'yes', 'y', 'on'}
