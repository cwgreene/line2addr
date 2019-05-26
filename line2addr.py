import argparse

from collections import defaultdict as dd

import elftools.elf.elffile as elf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f")
    parser.add_argument("--binary", "-b", required=True)
    options = parser.parse_args()

    with open(options.binary, "rb") as binary:
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
    print(lines)
main()
