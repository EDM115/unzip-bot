from collections.abc import Sequence

from unzipbot.cli.run import run_exec_cmd


async def run_ffmpeg(args: Sequence[str]):
    return await run_exec_cmd(["ffmpeg", *args])


async def make_thumbnail(input_path: str, output_path: str, timestamp: str = "00:00:01"):
    return await run_ffmpeg(
        ["-y", "-ss", timestamp, "-i", input_path, "-frames:v", "1", output_path]
    )
