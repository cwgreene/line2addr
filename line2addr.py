#!/usr/bin/env python3
import argparse
import json
import os

from collections import defaultdict as dd

import colorama

import elftools.elf.elffile as elf

def redhex(num, padding):
    return colorama.Fore.RED + ("{:"+str(padding)+"x}").format(num)+ colorama.Fore.RESET

def yellownum(num, padding):
    return colorama.Fore.YELLOW + ("{:" + str(padding) + "d}").format(num) + colorama.Fore.RESET

def get_lines(binary):
    belf = elf.ELFFile(binary)
    dwarf = belf.get_dwarf_info()
    lines = dd(lambda: dd(lambda:[]))
    for cu in dwarf.iter_CUs():
        lp = dwarf.line_program_for_CU(cu)
        files = lp['file_entry']
        directories = ["."] + [str(d, 'utf8') for d in lp['include_directory']]
        for lpe in lp.get_entries():
            if lpe.state:
                lfile = files[lpe.state.file-1]
                (lines[(directories[lfile['dir_index']], str(lfile['name'], 'utf8'))]
                    [lpe.state.line].append(lpe.state.address))
    return lines

def display_file_line(filename, lineno, lines):
    referenced_files = {pair[1]:(pair[0],pair[1]) for pair in lines}
    bf = os.path.basename(filename)
    reffile = referenced_files.get(bf, None)
    if reffile:
        for addr in lines[reffile][lineno]:
            print(hex(addr))
    else:
        print("{} is not references in the executable".format(filename))

def display_file(filename, lines):
    referenced_files = {pair[1]:(pair[0],pair[1]) for pair in lines}
    bf = os.path.basename(filename)

    with open(filename) as srcfile:
        reffile = referenced_files.get(bf, None)
        if reffile:
            for lineno, line in enumerate(srcfile.readlines(), 1):
                if lineno in lines[reffile]:
                    addresses = lines[reffile][lineno]
                    print("{} {} {}".format(yellownum(lineno, 3), redhex(addresses[0], 8), line[:-1]))
                    for i, addr in enumerate(addresses[1:], 1):
                        print("{:3} {}".format("", redhex(addr, 8)))
                else:
                    print("{} {:8} {}".format(yellownum(lineno, 3), '', line[:-1]))
        else:
            print("{} is not references in the executable".format(filename))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", "-b", required=True)
    parser.add_argument("--json-db", "-j", action="store_true")
    parser.add_argument("--file", "-f")
    parser.add_argument("--line", "-l", type=int)
    parser.add_argument("--display-file", "-d", action="store_true")
    options = parser.parse_args()

    with open(options.binary, "rb") as binary:
        lines = get_lines(binary)
    if options.json_db:
        print(json.dumps(
            {
                "{}/{}".format(key[0], key[1]) : {
                    lineno : list(map(hex, lines[key][lineno]))
                    for lineno in lines[key]
                }
                for key in lines
            }))
    if options.file and options.line:
        display_file_line(options.file, options.line, lines)
    if options.file and options.display_file:
        display_file(options.file, lines)
main()
