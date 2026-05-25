from pathlib import Path

from final_project.chunks import ChunkError, parse_chunk_command, split_chunks
from final_project.client import AIClient, ModelError
from final_project.config import Config, ConfigError, load_config
from final_project.files import FileInsertError, insert_files, read_text_file
from final_project.history import add_message
from final_project.messages import Message


QUIT = '\\q'


def run() -> int:
    try:
        config = load_config()
    except ConfigError as error:
        print(f'Config error: {error}')
        return 1

    if config is None:
        print('No config found. Set env variables or create final_project/config.yaml.')
        return 1

    client = AIClient(config)
    history: list[Message] = []

    while True:
        try:
            text = input('>>> ')
        except EOFError:
            return 0
        if text == QUIT:
            return 0
        if text == '/reset':
            history.clear()
            _clear_screen()
            continue
        if text.startswith('/file_chunk') or text.startswith('/filechunk'):
            _file_chunk_mode(client, config, text)
            continue
        _chat_once(client, config, history, text)


def _chat_once(client: AIClient, config: Config, history: list[Message], text: str) -> None:
    try:
        text = insert_files(text)
    except FileInsertError as error:
        print(f'File error: {error}')
        return

    add_message(history, 'user', text, config.limit_message, config.limit_chars)
    try:
        answer = _print_answer(client, history)
    except KeyboardInterrupt:
        print('\nRequest interrupted.')
        return
    except ModelError as error:
        print(f'Model error: {error}')
        return
    add_message(history, 'assistant', answer, config.limit_message, config.limit_chars)


def _file_chunk_mode(client: AIClient, config: Config, command: str) -> None:
    try:
        options = parse_chunk_command(command)
    except ChunkError as error:
        print(f'Chunk command error: {error}')
        return

    try:
        path = input('Введите путь до файла\n>>> ')
    except EOFError:
        return
    if path == QUIT:
        return
    try:
        text = read_text_file(Path(path), check_size=False)
    except FileInsertError as error:
        print(f'File error: {error}')
        return

    try:
        prompt = input('Принято. Что нужно сделать для каждого фрагмента (User Prompt)?\n>>> ')
    except EOFError:
        return
    if prompt == QUIT:
        return
    chunks = split_chunks(text, options)
    print('Принято. Начинаю обработку:')

    for index, chunk in enumerate(chunks):
        messages: list[Message] = [{'role': 'user', 'content': f'{prompt}\n\n{chunk}'}]
        try:
            _print_answer(client, messages)
        except KeyboardInterrupt:
            print('\nRequest interrupted.')
            return
        except ModelError as error:
            print(f'Model error: {error}')
            return
        if not options.auto and index != len(chunks) - 1:
            try:
                next_chunk = input('>>> ')
            except EOFError:
                return
            if next_chunk == QUIT:
                return

    print('Обработка файла завершена.')


def _print_answer(client: AIClient, history: list[Message]) -> str:
    parts = []
    for part in client.iter_answer(history):
        print(part, end='', flush=True)
        parts.append(part)
    print()
    return ''.join(parts)


def _clear_screen() -> None:
    print('\033[2J\033[H', end='')
