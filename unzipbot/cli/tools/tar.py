from unzipbot.cli.run import run_exec_cmd


async def extract(archive_path: str, output_dir: str):
    return await run_exec_cmd(["tar", "-xvf", archive_path, "-C", output_dir])
