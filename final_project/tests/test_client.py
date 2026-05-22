import pytest

from final_project.client import ModelError, _message_content, _stream_content


def test_message_content() -> None:
    data = {'choices': [{'message': {'content': 'hello'}}]}

    assert _message_content(data) == 'hello'


def test_stream_content() -> None:
    data = {'choices': [{'delta': {'content': 'he'}}]}

    assert _stream_content(data) == 'he'


def test_bad_response() -> None:
    with pytest.raises(ModelError):
        _message_content({})
