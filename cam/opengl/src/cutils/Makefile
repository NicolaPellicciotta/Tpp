OPTS = -Wall -O2
FLAGS=


libcutils.so: libcutils.c
	gcc -shared -fPIC $(FLAGS) libcutils.c -o libcutils.so

install: libcutils.so
	cp libcutils.so /usr/lib/

clean:  
	rm *.so
