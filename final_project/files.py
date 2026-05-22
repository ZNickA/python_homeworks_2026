import re
from pathlib import Path


MAX_FILE_SIZE = 5 * 1024 * 1024
FILE_PATTERN = re.compile(r'@::(.*?)::')


class FileInsertError(Exception):
    pass


def insert_files(text: str) -> str:
    result = text
    for filename in FILE_PATTERN.findall(text):
        content = read_text_file(Path(filename))
        result = result.replace(f'@::{filename}::', f'\n{content}')
    return result


def read_text_file(path: Path, check_size: bool = True) -> str:
    try:
        if check_size and path.stat().st_size > MAX_FILE_SIZE:
            raise FileInsertError(f'{path} is bigger than 5 MB')
        return path.read_text(encoding='utf-8')
    except OSError as error:
        raise FileInsertError(f'cannot read {path}') from error
    except UnicodeDecodeError as error:
        raise FileInsertError(f'{path} is not a text file') from error
