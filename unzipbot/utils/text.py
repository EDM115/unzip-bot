from collections.abc import AsyncGenerator, Iterable
from re import sub
from typing import TypeVar

T = TypeVar("T")


# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str) -> str:
    return sub(pattern="[*`_]", repl="", string=text)


async def async_generator(iterable: Iterable[T]) -> AsyncGenerator[T, None]:
    for item in iterable:
        yield item
