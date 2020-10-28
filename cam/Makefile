clean:
	cd cameras/hamamatsu; make clean
	cd cameras/mikrotron; make clean
	cd cameras/basler; make clean
	cd cameras/avt_gige; make clean
	cd opengl/src/cuda; make clean
	cd opengl/src/cudagl; make clean
	cd opengl/src/cutils; make clean

all:
	if [ -d /opt/EDTpdv ]; then cd cameras/hamamatsu; make; fi
	if [ -d /opt/EDTpdv ]; then cd cameras/mikrotron; make; fi
	if [ -d /opt/pylon3 ]; then cd cameras/basler; make; fi
	if [ -d /opt/AVT_GigE_SDK ]; then cd cameras/avt_gige; make; fi
	cd opengl/src/cuda; make
	cd opengl/src/cudagl; make
	cd opengl/src/cutils; make


install:
	if [ -d /opt/EDTpdv ]; then cd cameras/hamamatsu; make install; fi
	if [ -d /opt/EDTpdv ]; then cd cameras/mikrotron; make install; fi
	if [ -d /opt/pylon3 ]; then cd cameras/basler; make install; fi
	if [ -d /opt/AVT_GigE_SDK ]; then cd cameras/avt_gige; make install; fi
	cd opengl/src/cuda; make install
	cd opengl/src/cudagl; make install
	cd opengl/src/cutils; make install




