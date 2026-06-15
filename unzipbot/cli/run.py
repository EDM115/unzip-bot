from asyncio import create_subprocess_shell, run, subprocess

from unzipbot import LOGGER
from unzipbot.config.config import Config
from unzipbot.utils.files import calculate_memory_limit


async def run_shell_cmds(command) -> dict[str, str]:
    memlimit = calculate_memory_limit()
    cpulimit = Config.MAX_CPU_CORES_COUNT * Config.MAX_CPU_USAGE
    ulimit_cmd = [
        "ulimit",
        "-v",
        str(memlimit),
        "&&",
        "cpulimit",
        "-l",
        str(cpulimit),
        "--",
        command,
    ]
    ulimit_command = " ".join(ulimit_cmd)
    process = await create_subprocess_shell(
        cmd=ulimit_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash"
    )
    stdout, stderr = await process.communicate()

    e = stderr.decode(encoding="utf-8", errors="replace")
    o = stdout.decode(encoding="utf-8", errors="replace")
    LOGGER.info(msg=f"command : {command}")
    LOGGER.info(msg=f"stdout : {o}")
    LOGGER.info(msg=f"stderr : {e}")

    return {"output": o, "error": e}


def run_sync_shell_cmds(command: str) -> dict[str, str]:
    return run(run_shell_cmds(command))
