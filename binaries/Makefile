all: test test2 test3 multiplefiles

test: test.c
	gcc test.c -g -o test

test2: dirtest/test.c dirtest/test2.c
	mkdir -p temp
	gcc -g -c dirtest/test.c -o temp/test.o
	gcc -g -c dirtest/test2.c -o temp/test2.o
	gcc temp/test.o temp/test2.o -o test2

test3: inlinetest.c
	gcc -O2 -g inlinetest.c -o inlinetest

multiplefiles: ./multiplefiles/root1/identical/test.c ./multiplefiles/root2/identical/test.c
	gcc -g ./multiplefiles/root1/identical/test.c -c -o ./multiplefiles/root1/identical/test.o
	gcc -g ./multiplefiles/root2/identical/test.c -c -o ./multiplefiles/root2/identical/test.o
	gcc ./multiplefiles/root1/identical/test.o ./multiplefiles/root2/identical/test.o -o multiplefiles_bin


clean:
	rm -rf temp test2 test multiplefiles_bin
