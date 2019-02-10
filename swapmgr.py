#! /usr/bin/env python3

import utils
import time
import signal
import os

SWAP_PREFIX = "/home/.swap/swapfile"
SWAP_SIZE = 32

CREATE_THRESHOLD = SWAP_SIZE / 2
REMOVE_THRESHOLD = SWAP_SIZE + 3 * (SWAP_SIZE / 4)


def main():
    keep_running = True

    def handler(*args):
        nonlocal keep_running
        keep_running = False

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    swapfiles = utils.detect_swapfiles(SWAP_PREFIX)
    for f in swapfiles:
        print("found swapfile: ", f.path)

    while keep_running:
        time.sleep(60)
        swapmem = utils.parse_free_output(utils.call_free())
        if swapmem.free < CREATE_THRESHOLD:
            new_file = utils.new_swapfile_path(SWAP_PREFIX, swapfiles)
            try:
                utils.mkswapfile(new_file.path, SWAP_SIZE)
            except Exception:
                try:
                    os.remove(new_file.path)
                except Exception:
                    pass
                raise
            try:
                utils.activate_swapfile(new_file)
            except Exception:
                os.remove(new_file.path)
                raise

            swapfiles.append(new_file)

        elif swapmem.free > REMOVE_THRESHOLD:
            utils.remove_swapfile(swapfiles.pop().path)


if __name__ == "__main__":
    main()
