import argparse
import colorama
import os

from collections import defaultdict as dd

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
        for lpe in lp.get_entries():
            if lpe.state:
                lfile = files[lpe.state.file-1]
                lines [(lfile['dir_index'], lfile['name'])][lpe.state.line].append(lpe.state.address)
    return lines

def display_file(filename, lines):
    referenced_files = {pair[1]:(pair[0],pair[1]) for pair in lines}
    bf = bytes(os.path.basename(filename), 'utf8')

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
    parser.add_argument("--file", "-f")
    parser.add_argument("--binary", "-b", required=True)
    options = parser.parse_args()

    with open(options.binary, "rb") as binary:
        lines = get_lines(binary)
    if options.file:
        display_file(options.file, lines)
main()
