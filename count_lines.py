# !/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time


def log_print(message, log_type="INFO"):

    print(
        "[{DateOfMessage}] - [{TypeOfMessage}] - "
        "{Message}".format(
            DateOfMessage=time.strftime("%d.%m.%Y %H:%M:%S", time.gmtime()),
            TypeOfMessage=log_type.upper(),
            Message=message
    )
    )


def main(_excludes, path_to, do_count):
    lines = 0
    characters = 0
    print_file_name = False
    for root, dirs, files in os.walk(path_to, topdown=True):
        if True not in [False if exclude not in root else True
                        for exclude in _excludes]:
            for name in files:
                if True not in [False if exclude not in name else True
                                for exclude in _excludes]:
                    if print_file_name is True:
                        log_print(os.path.join(root, name))
                    if do_count is True:
                        with open(os.path.join(root, name)) as file:
                            for line in file:
                                characters += len(line)
                                lines += 1

        else:
            pass
    log_print("The processed files contain:")
    log_print("lines: {Lines}".format(Lines=lines))
    log_print("characters: {Characters}".format(Characters=characters))

if __name__ == "__main__":
    excludes = [
        "env",
        "logs",
        "__pycache__",
        "icons",
        "LC_MESSAGES",
        "config.ini",
        # "setup.py"
            ]
    path_to_files = "./src"
    count = True

    main(
        _excludes=excludes,
        path_to=path_to_files,
        do_count=count
    )
