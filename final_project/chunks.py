from dataclasses import dataclass


class ChunkError(Exception):
    pass


@dataclass(frozen=True)
class ChunkOptions:
    paragraphs: int = 1
    char_len: int | None = None
    auto: bool = False


def parse_chunk_command(command: str) -> ChunkOptions:
    paragraphs = 1
    char_len: int | None = None
    auto = False

    for part in command.split()[1:]:
        if part == '-y':
            auto = True
        elif part.startswith('paragraph='):
            paragraphs = _positive_int(part, 'paragraph=')
        elif part.startswith('len='):
            char_len = _positive_int(part, 'len=')

    return ChunkOptions(paragraphs=paragraphs, char_len=char_len, auto=auto)


def split_chunks(text: str, options: ChunkOptions) -> list[str]:
    if options.char_len is not None:
        return [text[i : i + options.char_len] for i in range(0, len(text), options.char_len)]

    lines = [line for line in text.splitlines() if line.strip()]
    if not lines and text:
        return [text]
    return [
        '\n'.join(lines[i : i + options.paragraphs])
        for i in range(0, len(lines), options.paragraphs)
    ]


def _positive_int(text: str, prefix: str) -> int:
    try:
        result = int(text.removeprefix(prefix))
    except ValueError as error:
        raise ChunkError(f'{prefix[:-1]} must be a positive integer') from error
    if result <= 0:
        raise ChunkError(f'{prefix[:-1]} must be positive')
    return result
