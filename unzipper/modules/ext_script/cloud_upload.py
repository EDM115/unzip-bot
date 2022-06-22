import subprocess

async def jsonized(command):
    run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    shell_ouput = run.stdout.read()[:-1].decode("utf-8")
    return shell_ouput.replace("true", "True")

async def bayfiles(file, url):
    try:
        uploaded = await jsonized(f"curl -F 'file=@{file}' {url}")
    except:
        uploaded = "Error happened on BayFiles upload (check connection, or retry later)"
    return uploaded
