import subprocess

async def terminal(command):
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shell_ouput = run.stdout.read()[:-1].decode("utf-8")
    return shell_ouput

async def bayfiles(file, url):
    try:
        uploaded = await terminal(f"curl -F 'file=@{file}' {url}").replace("true", "True")
    except:
        uploaded = "Error happened on BayFiles upload (check connection, or retry later)"
    return uploaded
