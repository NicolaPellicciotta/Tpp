OPTS = -Wall -O2
IDIR = /opt/EDTpdv
LDIR = /opt/EDTpdv
LIBS = -lpdv -lpthread -lm -ldl
FLAGS = -D_x64 -D_LINUX -fPIC


liborca.so: liborca.c
	gcc -shared $(FLAGS) -I$(IDIR) -L$(LDIR) liborca.c -o liborca.so $(LIBS)

install: liborca.so
	cp liborca.so /usr/lib/

clean:  
	rm -rf *.so
