#include <unistd.h>
#include <stdio.h>
#include <string.h>
int x[100];
int main(int argc, char **argv) {
    char bob[10];
    memset(bob,0,sizeof(bob));
    read(0, bob, 9);
    bob[9]=0;
    if(strcmp(bob, "hello") == 0) {
        printf("hi");
        return 1;
    }
    printf("%s", bob);
}
