from final_project.messages import Message


def add_message(
    history: list[Message],
    role: str,
    content: str,
    limit_message: int | None,
    limit_chars: int | None,
) -> None:
    history.append({'role': role, 'content': content})
    trim_history(history, limit_message, limit_chars)


def trim_history(
    history: list[Message],
    limit_message: int | None,
    limit_chars: int | None,
) -> None:
    if limit_message is not None:
        while len(history) > limit_message:
            history.pop(0)

    if limit_chars is not None:
        while len(history) > 1 and count_chars(history) > limit_chars:
            history.pop(0)
        if history and count_chars(history) > limit_chars:
            history[0]['content'] = history[0]['content'][-limit_chars:]


def count_chars(history: list[Message]) -> int:
    return sum(len(message['content']) for message in history)
