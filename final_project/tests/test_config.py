from pathlib import Path

import pytest
from pytest import MonkeyPatch

from final_project.config import ConfigError, load_config


ENV_KEYS = (
    'API_KEY',
    'API_HOST',
    'LIMIT_MESSAGE',
    'LIMIT_CHARS',
    'TEMPERATURE',
    'MODEL',
    'STREAM',
)


def clean_env(monkeypatch: MonkeyPatch) -> None:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_load_config_file_and_env_priority(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    clean_env(monkeypatch)
    path = tmp_path / 'config.yaml'
    path.write_text(
        '\n'.join(
            [
                'api_key: file-key',
                'api_host: http://localhost:11434/v1/',
                'limit_message: 5',
                'limit_chars: 100',
                'temperature: 0.4',
                'system_prompt: Be short',
                'model: old-model',
                'stream: false',
            ],
        ),
        encoding='utf-8',
    )
    monkeypatch.setenv('API_KEY', 'env-key')
    monkeypatch.setenv('MODEL', 'gemma3:latest')

    config = load_config(path)

    assert config is not None
    assert config.api_key == 'env-key'
    assert config.api_host == 'http://localhost:11434/v1'
    assert config.limit_message == 5
    assert config.limit_chars == 100
    assert config.temperature == 0.4
    assert config.system_prompt == 'Be short'
    assert config.model == 'gemma3:latest'
    assert config.stream is False


def test_load_config_without_settings(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    clean_env(monkeypatch)

    assert load_config(tmp_path / 'missing.yaml') is None


def test_bad_temperature(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    clean_env(monkeypatch)
    path = tmp_path / 'config.yaml'
    path.write_text('api_key: key\napi_host: host\ntemperature: 2', encoding='utf-8')

    with pytest.raises(ConfigError):
        load_config(path)
