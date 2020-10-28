OPTS = -Wall -O2
IDIR = /opt/EDTpdv
LDIR = /opt/EDTpdv
LIBS = -lpdv -lpthread -lm -ldl
FLAGS = -fPIC -D_x64 -D_LINUX 
//FLAGS = -fPIC


libmikrotron.so: libmikrotron.c
	gcc  $(FLAGS) -I$(IDIR) -L$(LDIR) libmikrotron.c -shared -o libmikrotron.so $(LIBS)

install: libmikrotron.so
	cp libmikrotron.so /usr/lib/

clean:  
	rm -rf *.so
