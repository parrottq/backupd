#!/bin/python
from shutil import copytree, rmtree
from os import listdir

if __name__ == "__main__":
    # Get rid of whatever was there before
    try:
        rmtree("/home/writer/Backup")
    except FileNotFoundError:
        pass

    # Get latest snapshot
    copytree(
            "/var/lib/backupd/snapshots/" + sorted(listdir("/var/lib/backupd/snapshots/"))[-1],
            "/home/writer/Backup"
            )

