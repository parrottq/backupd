#!/bin/python
from subprocess import call
from datetime import datetime
from os import listdir, mkdir

dest = "/var/lib/backupd/"
blank_time = "0000-00-00T00:00:00.0"

def backup():
    try:
        previous_snapshot = sorted(listdir(dest))[-1]
    except IndexError:
        # IndexError is no previous snapshot
        mkdir(f"/var/lib/backupd/{blank_time}")
        previous_snapshot = blank_time

    # Prepare the next snapshot directory
    next_snapshot = dest + datetime.now().isoformat()
    mkdir(next_snapshot)

    # Run the snapshot script
    call(["hlb", dest + previous_snapshot, "/home/writer/Backup", next_snapshot])

if __name__ == "__main__":
    backup()
