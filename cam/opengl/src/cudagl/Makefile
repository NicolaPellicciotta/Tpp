CUDA_COMMON_IDIR=/home/roberto/NVIDIA_GPU_Computing_SDK/C/common/inc
FLAGS=-Xcompiler -fPIC

libcudagl.so: libcudagl.cu
	nvcc libcudagl.cu -shared $(FLAGS) -o libcudagl.so


#-I$(CUDA_COMMON_IDIR)

install: libcudagl.so
	cp libcudagl.so /usr/lib

clean:
	rm *.so
