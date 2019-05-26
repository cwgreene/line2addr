test: test.c
	gcc test.c -g -o test

test2: dirtest/test.c dirtest/test2.c
	mkdir -p temp
	gcc -g -c dirtest/test.c -o temp/test.o
	gcc -g -c dirtest/test2.c -o temp/test2.o
	gcc temp/test.o temp/test2.o -o test2
	
