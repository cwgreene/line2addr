## line2addr

`addr2line` converts a address from a binary to a line in a file using debug information. This
converts a line in a 

## Current features
### Display all addresses for a file
```
$ line2addr.py -b binaries/test -f binaries/test.c -d
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
line2addr.py -b binaries/test -j | jq .
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

