from final_project.history import add_message, count_chars
from final_project.messages import Message


def test_message_limit_keeps_newest() -> None:
    history: list[Message] = []

    add_message(history, 'user', 'one', 2, None)
    add_message(history, 'assistant', 'two', 2, None)
    add_message(history, 'user', 'three', 2, None)

    assert [message['content'] for message in history] == ['two', 'three']


def test_char_limit_removes_old_messages() -> None:
    history: list[Message] = []

    add_message(history, 'user', 'abc', None, 5)
    add_message(history, 'assistant', 'def', None, 5)

    assert [message['content'] for message in history] == ['def']
    assert count_chars(history) == 3


def test_char_limit_cuts_single_big_message() -> None:
    history: list[Message] = []

    add_message(history, 'user', 'abcdef', None, 3)

    assert history == [{'role': 'user', 'content': 'def'}]
