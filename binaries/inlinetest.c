int f(int x) {
    return x+1;
}

int g(int y) {
    int x = f(y+1);
    int z = f(y+2);
    return x + z + f(y) + f(y);
}

int h(int y) {
    int acc = 0;
    for (int i = 0; i < y; i++)
        acc += f(y+i) + 7;
    return acc;
}

int main(int argc) {
    int g_r = g(argc);
    int h_r = h(argc);
    return g_r + h_r;
}
