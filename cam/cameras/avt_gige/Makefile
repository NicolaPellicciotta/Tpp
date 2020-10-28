include ARCH

libgige.so: libavtgige.c
	gcc $(RPATH) $(TARGET) $(CFLAGS) -fPIC -shared libavtgige.c $(SALIB) -o libavtgige.so $(SOLIB) $(PVLIB)

install: libavtgige.so
	cp libavtgige.so /usr/lib/

clean:
	rm -rf *.so
