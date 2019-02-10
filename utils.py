from collections import namedtuple
import subprocess
import os
from pathlib import Path

SwapMem = namedtuple("SwapMem", ["free", "used"])
SwapFile = namedtuple("SwapFile", ["path", "prio"])


def check_run(cmd):
    msg = """Error when running "{}": it returned {}.

stdout:
{}

stderr:
{}"""
    ret = subprocess.run(cmd, capture_output=True)
    print("running {}".format(" ".join(cmd)))
    if ret.returncode != 0:
        raise Exception(
            msg.format(" ".join(cmd), ret.returncode, ret.stdout.decode(), ret.stderr)
        )
    return ret


def call_free():
    ret = check_run(["free", "-m"])
    return ret.stdout


def parse_free_output(free_output):
    swapline = [x for x in free_output.splitlines() if x.startswith(b"Swap")][0]
    segments = swapline.split()
    return SwapMem(free=int(segments[3]), used=int(segments[2]))


def mkswapfile(path, size, dryrun=False):
    cmds = [["fallocate", "-l", str(size) + "M", path], ["mkswap", path]]
    if dryrun:
        return cmds
    for cmd in cmds:
        check_run(cmd)


def activate_swapfile(file, dryrun=False):
    cmd = ["swapon", file.path, '-p', str(file.prio)]
    if dryrun:
        return cmd
    check_run(cmd)


def detect_swapfiles(prefix):
    cmd = ["swapon", "--show=NAME,PRIO"]
    ret = check_run(cmd)
    enabled_swapfiles = ret.stdout.decode().splitlines()[1:]
    enabled_swapfiles = [f.split() for f in enabled_swapfiles if f.startswith(prefix)]
    result = [SwapFile(path=segs[0], prio=int(segs[1])) for segs in enabled_swapfiles]
    return result

# FIXME
# def delete_not_enabled_swapfiles(prefix, enabled_swapfiles):
#     enabled_paths = set(f.path for f in enabled_swapfiles)
#     directory = Path(prefix)
#     if not directory.is_dir()
#         directory.as_posix().
#     directory.iterdir()


def new_swapfile_path(prefix, current_swapfiles):
    suffixes = [int(p.path.lstrip(prefix)) for p in current_swapfiles]
    new_suffix = str(1 + max(suffixes, default=0))
    lowest_prio = min((f.prio for f in current_swapfiles), default=32768)
    new_prio = -1 if lowest_prio == -1 else lowest_prio - 1
    return SwapFile(path=prefix + new_suffix, prio=new_prio)


def remove_swapfile(path, dryrun=False):
    cmd = ["swapoff", path]
    if dryrun:
        return cmd
    check_run(cmd)
    os.remove(path)
