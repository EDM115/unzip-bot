from unzipbot.cli.run import run_exec_cmd


async def extract(archive_path: str, output_dir: str, password: str | None = None):
    args = ["unrar", "x", archive_path, output_dir, "-y"]
    if password is not None:
        args.insert(4, f"-p{password}")

    return await run_exec_cmd(args)


async def test(archive_path: str, password: str | None = None):
    args = ["unrar", "t", archive_path, "-y"]
    if password is not None:
        args.insert(3, f"-p{password}")

    return await run_exec_cmd(args)
