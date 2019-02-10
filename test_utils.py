import utils
import pytest


def test_parse_free_output():
    sample_output = b"""
              total        used        free      shared  buff/cache   available
Mem:        7963500     2717740      973420      582872     4272340     4218632
Swap:       8388604           4     8388600
"""
    actual_result = utils.parse_free_output(sample_output)
    expected_result = utils.SwapMem(free=8388600, used=4)

    assert expected_result == actual_result


def test_mkswapfile():
    expected_cmd = [
        ["fallocate", "-l", "100M", "/home/.swap/swapfile1"],
        ["mkswap", "/home/.swap/swapfile1"],
    ]
    assert (
        utils.mkswapfile(path="/home/.swap/swapfile1", size=100, dryrun=True)
        == expected_cmd
    )


def test_activate_swapfile():
    expected_cmd = ["swapon", "/home/.swap/swapfile1", "-p", "500"]
    assert (
        utils.activate_swapfile(
            utils.SwapFile(path="/home/.swap/swapfile1", prio=500), dryrun=True
        )
        == expected_cmd
    )


def test_new_swapfile():
    current_swapfiles = [
        utils.SwapFile("/prefix/file1", 1000),
        utils.SwapFile("/prefix/file3", 960),
        utils.SwapFile("/prefix/file4", 955),
        utils.SwapFile("/prefix/file6", 950),
    ]
    prefix = "/prefix/file"
    assert utils.new_swapfile_path(prefix, current_swapfiles) == utils.SwapFile(
        path="/prefix/file7", prio=949
    )

def test_new_swapfile_empty():
    current_swapfiles = [
    ]
    prefix = "/prefix/file"
    assert utils.new_swapfile_path(prefix, current_swapfiles) == utils.SwapFile(
        path="/prefix/file1", prio=32767
    )

def test_new_swapfile_exhausted_prio():
    current_swapfiles = [
        utils.SwapFile("/prefix/file1", 1000),
        utils.SwapFile("/prefix/file3", 960),
        utils.SwapFile("/prefix/file4", 0),
        utils.SwapFile("/prefix/file6", -1),
    ]
    prefix = "/prefix/file"
    assert utils.new_swapfile_path(prefix, current_swapfiles) == utils.SwapFile(
        path="/prefix/file7", prio=-1
    )
