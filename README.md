## line2addr

The standard tool `addr2line` converts an address from a binary to a
line in a file using DWARF debug information. This tool `line2addr`
converts a line into an address. It can also report all the addresses
associated with all the lines in a json representation.

Special thanks out to the fantastic [`pyelftools`](https://github.com/eliben/pyelftools)
library written by [Eli Bendersky](https://github.com/eliben/).

## Current features
### Display all addresses for a file
```
$ line2addr.py -b binaries/test -f binaries/test.c
  1          #include <unistd.h>
  2          #include <stdio.h>
  3          #include <string.h>
  4          int x[100];
  5      78a int main(int argc, char **argv) {
         799
  6              char bob[10];
  7      7a8     memset(bob,0,sizeof(bob));
  8      7be     read(0, bob, 9);
  9      7d4     bob[9]=0;
 10      7d8     if(strcmp(bob, "hello") == 0) {
 11      7ef         printf("hi");
 12      800         return 1;
 13              }
 14      807     printf("%s", bob);
 15      824 }
         83a
```
### Display all addresses for a specific line in a file
```
$ line2addr.py -b binaries/test -f binaries/test.c -l 10
0x7d8
```
### Dump line database as json
```
$ line2addr.py -b binaries/test -j | jq .
{
  "./test.c": {
    "5": [
      "0x78a",
      "0x799"
    ],
    "7": [
      "0x7a8"
    ],
    "8": [
      "0x7be"
    ],
    "9": [
      "0x7d4"
    ],
    "10": [
      "0x7d8"
    ],
    "11": [
      "0x7ef"
    ],
    "12": [
      "0x800"
    ],
    "14": [
      "0x807"
    ],
    "15": [
      "0x824",
      "0x83a"
    ]
  }
}
```
### Use an base address offset (WIP)
```
$ line2addr.py -b binaries/test -a 0x400000 -f binaries/test.c
  1          #include <unistd.h>
  2          #include <stdio.h>
  3          #include <string.h>
  4          int x[100];
  5   40078a int main(int argc, char **argv) {
      400799
  6              char bob[10];
  7   4007a8     memset(bob,0,sizeof(bob));
  8   4007be     read(0, bob, 9);
  9   4007d4     bob[9]=0;
 10   4007d8     if(strcmp(bob, "hello") == 0) {
 11   4007ef         printf("hi");
 12   400800         return 1;
 13              }
 14   400807     printf("%s", bob);
 15   400824 }
      40083a

```
### Use a base directory and display all files
```
$ ./line2addr.py -d binaries/ -b binaries/test2
binaries/dirtest/test.c:
  1          #include "test2.h"
  2          
  3      64a int main() {
  4      64e     g(3);
  5      65d }
         65f
binaries/dirtest/test2.c:
  1          #include <stdio.h>
  2      65f int g(int x) {
  3      66a     printf("%d\n", x);
  4      680 }
         683
```

### See additional DWARF information
```
$ line2addr.py -b binaries/test2 -d ./binaries/ --dwarf
./binaries/dirtest/test.c:
  1              #include "test2.h"
  2
  3  20      64a int main() {
  4  75      64e     g(3);
  5 229      65d }
      1      65f
./binaries/dirtest/test2.c:
  1              #include <stdio.h>
  2  19      65f int g(int x) {
  3 173      66a     printf("%d\n", x);
  4  89      680 }
      1      683
```
