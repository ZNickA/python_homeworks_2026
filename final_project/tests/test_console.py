from collections.abc import Iterator
from pathlib import Path
from typing import cast

from pytest import CaptureFixture, MonkeyPatch

from final_project.client import AIClient
from final_project.config import Config
from final_project.console import _chat_once, _file_chunk_mode
from final_project.messages import Message


class FakeClient:
    def __init__(self) -> None:
        self.calls: list[list[Message]] = []

    def iter_answer(self, history: list[Message]) -> Iterator[str]:
        self.calls.append(history.copy())
        yield f'ok-{len(self.calls)}'


def make_config() -> Config:
    return Config(
        api_key='key',
        api_host='host',
        limit_message=10,
        limit_chars=None,
        temperature=0.2,
        system_prompt=None,
        model='gemma3:latest',
        stream=True,
    )


def test_chat_once_adds_answer(capsys: CaptureFixture[str]) -> None:
    fake_client = FakeClient()
    history: list[Message] = []

    _chat_once(cast(AIClient, fake_client), make_config(), history, 'hi')

    assert [message['content'] for message in history] == ['hi', 'ok-1']
    assert 'ok-1' in capsys.readouterr().out


def test_file_chunk_auto(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    path = tmp_path / 'text.txt'
    path.write_text('one\ntwo\nthree', encoding='utf-8')
    answers = iter([str(path), 'short'])

    def fake_input(_: str = '') -> str:
        return next(answers)

    fake_client = FakeClient()
    monkeypatch.setattr('builtins.input', fake_input)

    _file_chunk_mode(cast(AIClient, fake_client), make_config(), '/filechunk paragraph=2 -y')

    assert len(fake_client.calls) == 2
    assert fake_client.calls[0][0]['content'] == 'short\n\none\ntwo'
    assert fake_client.calls[1][0]['content'] == 'short\n\nthree'
