import subprocess
import json

async def jsonized(command):
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shell_output = str(run.stdout.read()[:-1].decode("utf-8"))
    if "true" in shell_output:
        shell_output.replace("true", "True")
    elif "false" in shell_output:
        shell_output.replace("false", "False")
    else:
        pass
    return json.loads(shell_output)

async def bayfiles(file, url):
    try:
        uploaded = await jsonized(f"curl -F 'file=@{file}' {url}")
    except:
        uploaded = "Error happened on BayFiles upload (check connection, or retry later)"
    return uploaded
