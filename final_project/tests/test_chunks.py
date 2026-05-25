import pytest

from final_project.chunks import ChunkError, parse_chunk_command, split_chunks


def test_split_by_paragraphs() -> None:
    options = parse_chunk_command('/filechunk paragraph=2 -y')

    assert options.auto is True
    assert split_chunks('one\ntwo\nthree', options) == ['one\ntwo', 'three']


def test_split_by_len() -> None:
    options = parse_chunk_command('/filechunk len=3')

    assert split_chunks('abcdefg', options) == ['abc', 'def', 'g']


def test_bad_chunk_size() -> None:
    with pytest.raises(ChunkError):
        parse_chunk_command('/filechunk len=0')
