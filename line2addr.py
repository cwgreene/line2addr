#!/usr/bin/env python3
import argparse
import json
import os

from collections import defaultdict as dd

import colorama

import elftools.elf.elffile as elf

def redhex(num, padding):
    if num == '':
        return ' '*padding
    return colorama.Fore.RED + ("{:"+str(padding)+"x}").format(num)+ colorama.Fore.RESET

def yellownum(num, padding):
    if num == '':
        return ' '*padding
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

def print_line(**kwargs):
    if kwargs['options']['display_dwarf']:
        print("{} {:3} {} {}".format(
            yellownum(kwargs['lineno'], 3),
            kwargs['opcode'],
            redhex(kwargs['addr'], 8),
            kwargs['line']))
    else:
        print("{} {} {}".format(
            yellownum(kwargs['lineno'], 3),
            redhex(kwargs['addr'], 8),
            kwargs['line']))


def display_file(filename, lines, display_options):
    referenced_files = {pair[1]:(pair[0],pair[1]) for pair in lines}
    bf = os.path.basename(filename)

    with open(filename) as srcfile:
        reffile = referenced_files.get(bf, None)
        if reffile:
            for lineno, line in enumerate(srcfile.readlines(), 1):
                if lineno in lines[reffile]:
                    addresses = lines[reffile][lineno]
                    opcode, addr = addresses[0]
                    print_line(lineno=lineno, opcode=opcode, addr=addr, line=line[:-1], options=display_options)
                    for i, (opcode, addr) in enumerate(addresses[1:], 1):
                        print_line(lineno='', opcode=opcode, addr=addr, line='', options=display_options)
                else:
                    print_line(lineno=lineno, opcode='', addr='', line=line[:-1], options=display_options)
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
    parser.add_argument("--binary", "-b", required=True,
        help="binary to resolve addresses for")
    parser.add_argument("--json-db", "-j", action="store_true",
        help="dump DWARF database to json output (WIP)")
    parser.add_argument("--file", "-f",
        help="print addresses for target FILE")
    parser.add_argument("--line", "-l", type=int,
        help="print address for target LINE instead (also needs FILE)")
    parser.add_argument("--directory", "-d",
        help="print addresses for all files provided src root DIRECTORY")
    parser.add_argument("--base-address", "-a", default='0x0',
        help="add BASE_ADDRESS to all addresses")
    parser.add_argument("--dwarf", action="store_true",
        help="display additional DWARF information for lines")
    options = parser.parse_args()

    base_address = normalize_hex(options.base_address)

    display_options = {"display_dwarf": options.dwarf }

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
        display_file(options.file, lines, display_options)
    if options.directory:
        for srcfile in lines:
            fullsrcpath = os.path.join(srcfile[0], srcfile[1])
            fullpath = os.path.join(options.directory, fullsrcpath)
            print(green(fullpath + ":"))
            display_file(fullpath, lines, display_options)
main()
