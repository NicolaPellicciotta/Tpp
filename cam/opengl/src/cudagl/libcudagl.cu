#include <cuda.h>
#include <cuda_gl_interop.h>
#include <stdio.h>
#define MAXNUMRESOURCES 100

#  define SAFE_CALL(call) {                                                 \
    cudaError err = call;                                                   \
    if( cudaSuccess != err) {                                               \
        sprintf(errMsg, "Cuda error in file '%s' in line %i : %s.\n",       \
                __FILE__, __LINE__, cudaGetErrorString(err) );              \
        return 1;                                                            \
    } }




//Global vars
struct cudaGraphicsResource *cuda_pbo[MAXNUMRESOURCES];
int next_resource_idx=0;
int INVERTED=0;

//also works if a skip call to initCuda ???
extern "C" int initCuda(char *errMsg)
{
  int device;
  SAFE_CALL(cudaGetDevice(&device));
  SAFE_CALL(cudaGLSetGLDevice(device));
  //cudaSetDeviceFlags(cudaDeviceMapHost);
  return 0;
}

//also works if a skip call to initCuda ???
extern "C" int makeCurrent(char *errMsg)
{
  int device;
  SAFE_CALL(cudaGetDevice(&device));
  SAFE_CALL(cudaGLSetGLDevice(device));
  //cudaSetDeviceFlags(cudaDeviceMapHost);
  return 0;
}


extern "C" int regbuf(GLuint pbo, int *resource_idx, char *errMsg){
  if (next_resource_idx >= MAXNUMRESOURCES){
    sprintf(errMsg, "Maximum number of resources exceeded");
    return 1;
  }
  *resource_idx=next_resource_idx;
  next_resource_idx+=1;

  SAFE_CALL(cudaGraphicsGLRegisterBuffer(&cuda_pbo[*resource_idx], pbo, cudaGraphicsMapFlagsNone));
  return 0;
}

extern "C"  int glmap(GLuint pbo, int resource_idx, void **d_ptr, char *errMsg)
{
  size_t num_bytes;
  SAFE_CALL(cudaGraphicsMapResources(1, &cuda_pbo[resource_idx], 0));
  SAFE_CALL(cudaGraphicsResourceGetMappedPointer(d_ptr, &num_bytes, cuda_pbo[resource_idx]));
  return 0;
}
  
extern "C"  int glunmap(GLuint pbo, int resource_idx, char *errMsg)
{
  SAFE_CALL(cudaGraphicsUnmapResources(1, &cuda_pbo[resource_idx], 0));
  return 0;
}
