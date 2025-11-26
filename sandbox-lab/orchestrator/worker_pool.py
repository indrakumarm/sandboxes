import asyncio
import os

BWRAP_BASE_CMD = [
    "bwrap",
    "--unshare-all",
    "--new-session",
    "--ro-bind", "/opt/alpine-root", "/",
    "--tmpfs", "/tmp",
    "--proc", "/proc",
    "--dev", "/dev",
]

WORKERS = 3  # number of sandboxes


class SandboxWorker:
    def __init__(self, id):
        self.id = id
        self.proc = None

    async def start(self):
        print(f"[worker-{self.id}] starting sandbox...")

        self.proc = await asyncio.create_subprocess_exec(
            *BWRAP_BASE_CMD,
            "--bind", os.getcwd(), "/workspace",
            "/bin/sh",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        print(f"[worker-{self.id}] sandbox ready.")

    async def run_job(self, command):
        """
        Send a command into the sandbox and read output.
        """
        self.proc.stdin.write((command + "\n").encode())
        await self.proc.stdin.drain()

        # Read until marker
        self.proc.stdin.write(b'echo __DONE__\n')
        await self.proc.stdin.drain()

        output = []

        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break
            text = line.decode().rstrip()
            if text == "__DONE__":
                break
            output.append(text)

        return "\n".join(output)


async def worker_loop(id, queue):
    worker = SandboxWorker(id)
    await worker.start()

    while True:
        job = await queue.get()
        if job is None:
           print(f"[worker-{id}] stopping sandbox...")
           worker.proc.terminate()
           await worker.proc.wait()
           return

        job_id, cmd, future = job

        print(f"[worker-{id}] running job {job_id}: {cmd}")
        output = await worker.run_job(cmd)
        future.set_result(output)
        queue.task_done()


async def main():
    queue = asyncio.Queue()
    workers = []

    # start worker pool
    for i in range(WORKERS):
        w = asyncio.create_task(worker_loop(i, queue))
        workers.append(w)

    # SUBMIT JOBS
    futures = []
    for i in range(10):
        fut = asyncio.get_event_loop().create_future()
        queue.put_nowait((i, f"echo job-{i}; id; ls /workspace", fut))
        futures.append(fut)

    # wait for results
    for i, fut in enumerate(futures):
        out = await fut
        print(f"\n=== RESULT job {i} ===\n{out}\n")

    # stop workers
    for _ in range(WORKERS):
        queue.put_nowait(None)

    for w in workers:
        await w

asyncio.run(main())

