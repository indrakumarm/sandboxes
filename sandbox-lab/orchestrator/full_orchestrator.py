import asyncio, tempfile, os

def pp(out: str, err: str):
    print("\n" + "="*20 + " STDOUT " + "="*20)
    print(out if out.strip() else "<empty>")
    print("="*20 + " STDERR " + "="*20)
    print(err if err.strip() else "<empty>")
    print("="*49 + "\n")

async def execute(code):
    with tempfile.TemporaryDirectory() as work:
        script = os.path.join(work, "r.sh")
        open(script, "w").write(code)

        cmd = [
            "bwrap", "--unshare-all", "--new-session",
            "--ro-bind", "/opt/alpine-root", "/",
            "--bind", work, "/workspace",
            "--tmpfs", "/tmp",
            "--proc", "/proc",
            "--dev", "/dev",
            "/bin/sh", "/workspace/r.sh"
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        out, err = await proc.communicate()
        return out.decode(), err.decode()

if __name__ == '__main__':
    code = """#!/bin/sh
echo "Inside sandbox via orchestrator"
id
touch /workspace/pytestfile
ls -la /workspace
"""
    out, err = asyncio.run(execute(code))
    pp(out, err)

