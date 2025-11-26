import asyncio

async def run(code):
    proc = await asyncio.create_subprocess_exec(
        "bwrap", "--unshare-all", "--new-session",
        "--ro-bind", "/opt/alpine-root", "/",
        "--tmpfs", "/tmp",
        "--proc", "/proc",
        "--dev", "/dev",
        "/bin/sh", "-c", code,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    return out.decode(), err.decode()

print(asyncio.run(run("echo 'sandbox OK'")))

