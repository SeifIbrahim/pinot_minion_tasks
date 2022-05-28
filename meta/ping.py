from returns.result import Result, Success, Failure
from typing import Optional
import subprocess
import time
import os
import signal


def start_collecting(dump_file: str, address: str) -> Result[int, str]:
    """
    Function that starts collecting last mile latency
    :param address: address of the border router
    :return: Failure with error or success with pid and filename
    """
    f = open(dump_file, "w")
    proc = subprocess.Popen(["ping", "-D", address], stdout=f)
    time.sleep(2)
    if proc.poll() is None:
        return Success(proc.pid)

    return Failure(f"Process terminated with return code {proc.poll()}")


def stop_collecting(pid: Optional[int] = None) -> Result[str, str]:
    """
    Kills either all ping proc, or the one, that mentioned in agrs
    :param pid: process id
    :return: Success or Failure with relevant info
    """
    if pid is None:
        line = ["killall", "ping"]
        proc = subprocess.Popen(line,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()

        if out != b"" or err != b"":
            return Failure(f"out: {out}, err: {err}")
    else:
        line = ["kill", f"{pid}"]
        os.kill(pid, signal.SIGINT)

    time.sleep(2)  # for ping to finish file

    return Success("ping stopped")
