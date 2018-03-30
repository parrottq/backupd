#!/bin/python
"""
Backup script using hardlinks to save space
"""

from os import listdir, link
from shutil import copy
from os.path import isfile, join as join_path
from hashlib import sha256


def hash_file(path):
    """
    Produce a sha256 hash of a file
    """
    hash_ob = sha256()

    # This should be a multiple of the block sizes
    hash_update_size = hash_ob.block_size * 1024

    # Doing hashing in increments saves memory
    with open(path, 'rb') as file_ob:
        while True:
            file_seg = file_ob.read(hash_update_size)
            if not file_seg:
                break

            hash_ob.update(file_seg)

    return hash_ob.hexdigest()

def hash_dir(path):
    """
    Hash all files in a directory
    """
    dir_hashs = {}

    for file_path in listdir(path):
        if not isfile(join_path(path, file_path)):
            continue

        file_hash = hash_file(join_path(path, file_path))

        if file_hash not in dir_hashs:
            dir_hashs[file_hash] = []

        dir_hashs[file_hash].append(file_path)

    return dir_hashs

def dict_intersect(*dicts):
    """
    Finds intersecting keys in dict
    """
    # Convert to sets for comparison
    # This will discard values
    sets = [set(dict_ob.keys()) for dict_ob in dicts]
    set_intersected = set.intersection(*sets)

    # Merge values back with intersected keys
    dict_intersected = {}
    for intersect_key in set_intersected:
        dict_intersected[intersect_key] = [dict_ob[intersect_key] for dict_ob in dicts]

    return dict_intersected

def snapshot_dir(backup_previous, backup_reference, backup_gen):
    """
    Generate a snapshot based of a previous snapshot and the current files
    """
    hash_old = hash_dir(backup_previous)
    hash_new = hash_dir(backup_reference)

    print(" " * 16 + f": {backup_previous} -> {backup_reference}")

    # ID files that have been moved
    # value[0] + value[1] all have the same hashes so
    # they will be hard linked together
    for key, value in dict_intersect(hash_old, hash_new).items():
        print(f"{key[:16]}: {value[0]} -> {value[1]}")

        # Hard link files
        for file_name in value[1]:
            link(join_path(backup_previous, value[0][0]), join_path(backup_gen, file_name))

        # These hashes have been processed so
        # they are removed from the next steps
        hash_new.pop(key)
        hash_old.pop(key)

    # File created
    # Create new files in directory
    # Files with same hash will be hard linked to save space
    for key, value in hash_new.items():
        print(f"{key[:16]}: null -> {value}")

        for file_name in value:
            copy(join_path(backup_reference, file_name), join_path(backup_gen, file_name))

    # Files that no longer exist
    # Nothing has to be put in the lates snapshot
    for key, value in hash_old.items():
        print(f"{key[:16]}: {value} -> null")

if __name__ == "__main__":
    # Where all the new files will be place
    backup_gen = "backups/"

    # The last backup to compare against
    backup_previous = "t/1"

    # The working version of the files
    backup_reference = "t/2"

    snapshot_dir(backup_previous, backup_reference, backup_gen)
