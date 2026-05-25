from pathlib import Path

import pytest

from pytest import MonkeyPatch

from final_project.files import FileInsertError, insert_files, read_text_file


def test_insert_files(tmp_path: Path) -> None:
    path = tmp_path / 'code.py'
    path.write_text('print(1)', encoding='utf-8')

    result = insert_files(f'What is wrong? @::{path}::')

    assert result == 'What is wrong? \nprint(1)'


def test_file_size_limit(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    path = tmp_path / 'big.txt'
    path.write_text('123', encoding='utf-8')
    monkeypatch.setattr('final_project.files.MAX_FILE_SIZE', 2)

    with pytest.raises(FileInsertError):
        read_text_file(path)
