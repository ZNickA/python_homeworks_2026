import json
from collections.abc import Iterator
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from final_project.config import Config
from final_project.messages import Message


class ModelError(Exception):
    pass


class AIClient:
    def __init__(self, config: Config) -> None:
        self.config = config

    def iter_answer(self, history: list[Message]) -> Iterator[str]:
        messages = self._with_system_prompt(history)
        if self.config.stream:
            yield from self._stream_answer(messages)
        else:
            yield self._plain_answer(messages)

    def _with_system_prompt(self, history: list[Message]) -> list[Message]:
        messages: list[Message] = []
        if self.config.system_prompt:
            messages.append({'role': 'system', 'content': self.config.system_prompt})
        messages.extend(history)
        return messages

    def _request(self, messages: list[Message], stream: bool) -> Request:
        payload: dict[str, Any] = {
            'model': self.config.model,
            'messages': messages,
            'temperature': self.config.temperature,
            'stream': stream,
        }
        return Request(
            f'{self.config.api_host}/chat/completions',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.config.api_key}',
            },
            method='POST',
        )

    def _plain_answer(self, messages: list[Message]) -> str:
        try:
            with urlopen(self._request(messages, False), timeout=300) as response:
                data: object = json.loads(response.read().decode('utf-8'))
        except HTTPError as error:
            raise ModelError(_http_error_text(error)) from error
        except URLError as error:
            raise ModelError(f'connection error: {error.reason}') from error
        except json.JSONDecodeError as error:
            raise ModelError('server returned bad json') from error
        return _message_content(data)

    def _stream_answer(self, messages: list[Message]) -> Iterator[str]:
        try:
            with urlopen(self._request(messages, True), timeout=300) as response:
                for raw_line in response:
                    line = raw_line.decode('utf-8').strip()
                    if not line.startswith('data:'):
                        continue
                    data_text = line[5:].strip()
                    if data_text == '[DONE]':
                        break
                    data: object = json.loads(data_text)
                    yield _stream_content(data)
        except HTTPError as error:
            raise ModelError(_http_error_text(error)) from error
        except URLError as error:
            raise ModelError(f'connection error: {error.reason}') from error
        except json.JSONDecodeError as error:
            raise ModelError('server returned bad json') from error


def _http_error_text(error: HTTPError) -> str:
    text = error.read().decode('utf-8', 'replace')
    if text:
        return f'http error {error.code}: {text}'
    return f'http error {error.code}'


def _message_content(data: object) -> str:
    first = _first_choice(data)
    message = first.get('message')
    if isinstance(message, dict):
        content = message.get('content')
        if isinstance(content, str):
            return content
    raise ModelError('server response has no answer')


def _stream_content(data: object) -> str:
    first = _first_choice(data)
    delta = first.get('delta')
    if isinstance(delta, dict):
        content = delta.get('content')
        if isinstance(content, str):
            return content
    return ''


def _first_choice(data: object) -> dict[str, object]:
    if isinstance(data, dict):
        choices = data.get('choices')
        if isinstance(choices, list) and choices and isinstance(choices[0], dict):
            return choices[0]
    raise ModelError('server response has no choices')
