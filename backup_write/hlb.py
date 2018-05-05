#!/bin/python
"""
Backup script using hardlinks to save space
"""

from os import listdir, link, walk, makedirs
from shutil import copy
from os.path import exists, isfile, isdir, join as join_path
from hashlib import sha256
from multiprocessing import Pool

colours = {
        "reset": "\x1b[0m",
        "green": "\x1b[32m"
    }


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

def hash_dir(path, full_path=False):
    """
    Hash all files in a directory
    """
    dir_hashs = {}

    for file_name in listdir(path):
        relative_path = join_path(path, file_name)

        if not isfile(relative_path):
            continue

        file_hash = hash_file(relative_path)

        if file_hash not in dir_hashs:
            dir_hashs[file_hash] = []

        dir_hashs[file_hash].append(relative_path if full_path else file_name)

    return dir_hashs

def _hash_file(path):
    """
    Hash a file while also returning the path
    """
    # The path needs to be returned because hashs do not always finish sequentially
    return (path, hash_file(path))

def hash_tree(path):
    """
    Hash all files in a directory tree
    """
    file_list = recursive_files(path)
    file_count = 0

    dir_hashs = {}
    with Pool(processes=8) as pool:
        for file_path, file_hash in pool.imap_unordered(_hash_file, file_list):
            file_count += 1
            print(f"({file_count}/{len(file_list)}) {file_path}")

            # Create an entry for this hash if it does not already exist
            if file_hash not in dir_hashs:
                dir_hashs[file_hash] = []

            # Add the file to the hash list
            dir_hashs[file_hash].append(file_path)

    return dir_hashs

def recursive_files(path):
    """
    Recursivly return a list of all files
    """
    full_path_files = []

    for dir_path, dirs, file_names in walk(path):
        for file_name in file_names:
            full_path_files.append(join_path(dir_path, file_name))

    return full_path_files

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

def make_parent_dir(path):
    parent_dir = '/'.join(path.split("/")[:-1])
    if not exists(path):
        makedirs(parent_dir, exist_ok=True)

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

def colour_text(text):
    return colours["green"] + text + colours["reset"]

def snapshot_tree(backup_previous, backup_reference, backup_gen):

    print("Hashing previous files...")
    hash_old = hash_tree(backup_previous)
    print("Hashing current files...")
    hash_new = hash_tree(backup_reference)

    print()

    for key, value in dict_intersect(hash_old, hash_new).items():
        print(colour_text(key[:16])+":")
        for dest in value[0]:
            print(f"<- {dest}")
        for dest in value[1]:
            print(f"-> {dest}")

        for file_path in value[1]:
            dest = file_path.replace(backup_reference, backup_gen, 1)
            make_parent_dir(dest)
            link(value[0][0], dest)

        hash_old.pop(key)
        hash_new.pop(key)

    for key, value in hash_new.items():
        print(colour_text(key[:16])+":")
        print("<- null")
        for dest in value:
            print(f"-> {dest}")

        for file_name in value:
            dest = file_name.replace(backup_reference, backup_gen, 1)
            make_parent_dir(dest)
            copy(file_name, dest)

    for key, value in hash_old.items():
        print(colour_text(key[:16])+":")
        for dest in value:
            print(f"<- {dest}")
        print("-> null")


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Snapshot a directory.")
    parser.add_argument("previous", help="The previous snapshot")
    parser.add_argument("current", help="The working directory")
    parser.add_argument("destination", help="The directory the next snapshot will be generated in")

    arguments = parser.parse_args()

    for argument, value in arguments.__dict__.items():
        if not isdir(value):
            print(f"{argument}: {value} is not a directory")
            exit()

    snapshot_tree(arguments.previous, arguments.current, arguments.destination)


