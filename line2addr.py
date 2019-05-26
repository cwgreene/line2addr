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

def green(string):
    return colorama.Fore.LIGHTGREEN_EX + string + colorama.Fore.RESET

def get_lines(binary, base_address=0x0):
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
                    [lpe.state.line].append((lpe.command, lpe.state.address+base_address)))
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
                    opcode, addr = addresses[0]
                    print("{} {:3} {} {}".format(yellownum(lineno, 3), opcode, redhex(addr, 8), line[:-1]))
                    for i, (opcode, addr) in enumerate(addresses[1:], 1):
                        print("{:3} {:3} {}".format("", opcode, redhex(addr, 8)))
                else:
                    print("{} {:3} {:8} {}".format(yellownum(lineno, 3), '', '', line[:-1]))
        else:
            print("{} is not references in the executable".format(filename))

def normalize_hex(hexstring):
    hs = hexstring
    if hexstring.startswith("0"):
        hs = hexstring[2:]
    elif hexstring.startswith("x"):
        hs = hexstring[1:]
    return int(hs, 16)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", "-b", required=True)
    parser.add_argument("--json-db", "-j", action="store_true")
    parser.add_argument("--file", "-f")
    parser.add_argument("--directory", "-d")
    parser.add_argument("--line", "-l", type=int)
    parser.add_argument("--base-address", "-a", default='0x0')
    options = parser.parse_args()

    base_address = normalize_hex(options.base_address)

    with open(options.binary, "rb") as binary:
        lines = get_lines(binary, base_address)
    if options.json_db:
        print(json.dumps(
            {
                "{}/{}".format(key[0], key[1]) : {
                    lineno : [[cmd_addr[0], hex(cmd_addr[1])] for cmd_addr in lines[key][lineno]]
                    for lineno in lines[key]
                }
                for key in lines
            }))
    if options.file and options.line:
        display_file_line(options.file, options.line, lines)
    if options.file and not options.line:
        display_file(options.file, lines)
    if options.directory:
        for srcfile in lines:
            fullsrcpath = os.path.join(srcfile[0], srcfile[1])
            fullpath = os.path.join(options.directory, fullsrcpath)
            print(green(fullpath + ":"))
            display_file(fullpath, lines)
main()
