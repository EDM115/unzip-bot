from unzipbot.cli.run import run_exec_cmd


async def extract(archive_path: str, output_dir: str, password: str | None = None):
    args = ["7z", "x", f"-o{output_dir}", archive_path, "-y"]
    if password is not None:
        args.insert(3, f"-p{password}")

    return await run_exec_cmd(args)


async def test(archive_path: str, password: str | None = None):
    args = ["7z", "t", archive_path, "-y"]
    if password is not None:
        args.insert(2, f"-p{password}")

    return await run_exec_cmd(args)


async def split(input_path: str, output_path: str, size_bytes: int):
    return await run_exec_cmd(
        ["7z", "a", "-tzip", "-mx=0", output_path, input_path, f"-v{size_bytes}b"]
    )
