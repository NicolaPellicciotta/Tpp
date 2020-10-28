CUDA_COMMON_IDIR=/usr/local/cuda/samples/common/inc
FLAGS=-Xcompiler -fPIC

libcudacam.so: render/render.o histogram/histogram64.o histogram/histogram.o
	nvcc render/render.o histogram/histogram.o histogram/histogram64.o -shared $(FLAGS) -o libcudacam.so -lm


render/render.o:  render/render.cu
	nvcc render/render.cu -c $(FLAGS) -o render/render.o


histogram/histogram64.o: histogram/histogram64.cu histogram/histogram_common.h
	nvcc histogram/histogram64.cu -c $(FLAGS) -I$(CUDA_COMMON_IDIR) -o histogram/histogram64.o


histogram/histogram.o: histogram/histogram.cpp histogram/histogram_common.h
	nvcc histogram/histogram.cpp -c $(FLAGS) -I$(CUDA_COMMON_IDIR) -o histogram/histogram.o

install: libcudacam.so
	cp libcudacam.so /usr/lib

clean:
	rm render/*.o histogram/*.o
