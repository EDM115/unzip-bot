from os import remove, stat, walk
from os.path import join
from re import Match, findall, search
from shutil import rmtree
from typing import Any

from psutil import disk_usage, virtual_memory

from unzipbot.config.config import Config
from unzipbot.i18n.strings import rar_file_pattern, volume_file_pattern


def calculate_memory_limit() -> int:
    if Config.MAX_RAM_AMOUNT_KB != -1:
        return int(Config.MAX_RAM_AMOUNT_KB * Config.MAX_RAM_USAGE / 100)

    # we may need to use virtual_memory().available instead of total
    total_memory: int = virtual_memory().total
    memory_limit_kb = int(total_memory * Config.MAX_RAM_USAGE / 100 / 1024)

    return memory_limit_kb


def get_size(doc_f: str) -> int:
    try:
        fsize: int = stat(path=doc_f).st_size
        return fsize
    except OSError:
        return -1


async def get_files(path: str) -> list[str]:
    """
    Get files in directory as a list
    """
    path_list: list[str] = [
        val
        for sublist in [[join(i[0], j) for j in i[2]] for i in walk(top=path)]
        for val in sublist
    ]

    return sorted(path_list)


async def cleanup_macos_artifacts(path: str) -> None:
    for root, dirs, files in walk(top=path):
        for name in files:
            if name == ".DS_Store":
                remove(path=join(root, name))
        for name in dirs:
            if name == "__MACOSX":
                rmtree(join(root, name))


def sufficient_disk_space(required_space: int) -> bool:
    disk_used = disk_usage("/")
    free_space: int = disk_used.free
    total_space: int = disk_used.total
    five_percent_total: float = total_space * 0.05

    if free_space >= required_space and free_space >= five_percent_total:
        return True

    return False


# Function to extract the sequence number from filenames
def get_sequence_number(filename: str, pattern: str) -> int | float:
    match: Match[str] | None = search(pattern=pattern, string=filename)

    if match:
        # Extract the numeric part from the matched pattern
        num_match: list[Any] = findall(pattern=r"\d+", string=match.group())

        if num_match:
            return int(num_match[-1])

    # Use infinity if no number is found (ensures this file is always last)
    return float("inf")


# Function to find the file with the lowest sequence
def find_lowest_sequence_file(files: list[str]) -> tuple[str, str]:
    if not files:
        raise IndexError("No files to match")

    # Match the files against the patterns
    rar_matches: list[str] = [
        f for f in files if search(pattern=rar_file_pattern, string=f)
    ]
    volume_matches: list[str] = [
        f for f in files if search(pattern=volume_file_pattern, string=f)
    ]

    # Handle RAR pattern cases
    if rar_matches:
        # Separate .rX and .partX.rar cases
        r_files: list[str] = [
            f
            for f in rar_matches
            if f.endswith(".rar") or search(pattern=r"\.r\d+$", string=f)
        ]
        part_files: list[str] = [
            f for f in rar_matches if search(pattern=r"part\d+\.rar$", string=f)
        ]

        # Priority: .partX.rar -> .rX
        if part_files:
            return (
                min(
                    part_files,
                    key=lambda x: get_sequence_number(filename=x, pattern=r"part\d+"),
                ),
                "rar",
            )
        elif r_files:
            return (
                min(
                    r_files,
                    key=lambda x: get_sequence_number(filename=x, pattern=r"\.r\d+$"),
                ),
                "rar",
            )

    # Handle other cases
    if volume_matches:
        return (
            min(
                volume_matches,
                key=lambda x: get_sequence_number(filename=x, pattern=r"\.\d+$"),
            ),
            "volume",
        )

    raise IndexError("No matching files found")
