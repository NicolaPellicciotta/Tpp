#include<string.h>

int memcpy_subarray(unsigned char *dst, unsigned char *src, 
                    int x, int y, 
                    int dst_w, int dst_h,
                    int src_w,
                    int itemsize){
  int i;
  unsigned char *row_p;
  int rowsize;

  rowsize=src_w*itemsize;

  row_p=src+rowsize*y+itemsize*x;

  for (i=0; i<dst_h; i++){
    memcpy(dst+i*dst_w*itemsize, row_p, dst_w*itemsize);
    row_p+=rowsize;
  }
  return 0;
} 

int byte2rgb(unsigned char *dst, unsigned char *src, int size){
  int i;
  for (i=0; i<size; i++){
    dst[3*i]=src[i];
    dst[3*i+1]=src[i];
    dst[3*i+2]=src[i];
  }
  return 0;
}
