from unzipbot.cli.run import run_exec_cmd


async def decompress(input_path: str, output_dir: str):
    return await run_exec_cmd(["zstd", "-f", "--output-dir-flat", output_dir, "-d", input_path])
