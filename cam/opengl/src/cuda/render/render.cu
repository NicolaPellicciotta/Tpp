#include <math.h>
#define uint8 unsigned char
#define uint16 unsigned short int

__global__ void _u162g8_kernel(void *d_data, void *d_tex, int size, int thres, int vmin, int vmax)
{
    uint8 data8;
    //uint8 r,g;
    uint16 data16, data16_scaled;
    uint16 *data_p=(uint16 *)d_data;
    uint8 *tex_p=(uint8 *)d_tex;

    int idx = blockIdx.x*blockDim.x+threadIdx.x;
    //uint16 factor = (uint16)(4096./(vmax-vmin));
      
      
    data16=data_p[idx];


    if(idx<size){
      if (data16>vmax){
        data16_scaled=4095;
      } else if (data16 < vmin){
        data16_scaled=0;
      } else {
        data16_scaled=(data16-vmin)*4096/(vmax-vmin);
      }

      data8=(uint8)(data16_scaled/16);

      if (data16==4095){ 
        tex_p[3*idx]=255;
        tex_p[3*idx+1]=0;
        tex_p[3*idx+2]=0;
      }else if(data16<thres){
        tex_p[3*idx]=data8*.75;
        tex_p[3*idx+1]=data8*.75;
        tex_p[3*idx+2]=data8;
      }else{
        tex_p[3*idx]=data8;
        tex_p[3*idx+1]=data8;
        tex_p[3*idx+2]=data8;
      }
    }
}

__global__ void _u82g8_kernel(void *d_data, void *d_tex, int size, int thres, int vmin, int vmax)
{
    uint8 data8, data8_scaled;
    //uint16 data16, data16_scaled;
    uint8 *data_p=(uint8 *)d_data;
    uint8 *tex_p=(uint8 *)d_tex;

    int idx = blockIdx.x*blockDim.x+threadIdx.x;
    //uint16 factor = (uint16)(4096./(vmax-vmin));
      
      
    data8=data_p[idx];


    if(idx<size){
      if (data8>vmax){
        data8_scaled=255;
      } else if (data8 < vmin){
        data8_scaled=0;
      } else {
        data8_scaled=(data8-vmin)*255/(vmax-vmin);
      }

      if (data8==255){ 
        tex_p[3*idx]=255;
        tex_p[3*idx+1]=0;
        tex_p[3*idx+2]=0;
      }else if(data8<thres){
        tex_p[3*idx]=data8_scaled*.75;
        tex_p[3*idx+1]=data8_scaled*.75;
        tex_p[3*idx+2]=data8_scaled;
      }else{
        tex_p[3*idx]=data8_scaled;
        tex_p[3*idx+1]=data8_scaled;
        tex_p[3*idx+2]=data8_scaled;
      }
    }
}

__global__ void _u82rgb8_kernel(void *d_data, void *d_tex, int size, int w, int thres, int vmin, int vmax)
{
    float datafg;   
    uint8 data8r,data8g,data8b;
    uint8 *data_p=(uint8 *)d_data;
    uint8 *tex_p=(uint8 *)d_tex;

    int idx = blockIdx.x*blockDim.x+threadIdx.x; 
    int idrow=(idx/(w/2));
    int idcol=(idx%(w/2));
    int idxrgb=idcol*2+idrow*w*2;

    if (idxrgb+w+1<size)
    {
        /*data8r=data_p[idxrgb];
        datafg=(float)data_p[idxrgb+1];
        datafg+=(float)data_p[idxrgb+w];
        data8b=data_p[idxrgb+w+1];*/
        datafg=(float)data_p[idxrgb];
        datafg+=(float)data_p[idxrgb+w+1];
        datafg*=0.4;
        data8r=data_p[idxrgb+w];
        data8b=data_p[idxrgb+1];

        if (data8r>vmax) {data8r=255;} 
        else if (data8r<vmin) {data8r=0;} 
        else {data8r=(data8r-vmin)*255/(vmax-vmin);}

        if (data8b>vmax) {data8b=255;} 
        else if (data8b<vmin) {data8b=0;} 
        else {data8b=(data8b-vmin)*255/(vmax-vmin);}

        if (datafg>vmax) {data8g=255;} 
        else if (datafg<vmin) {data8g=0;} 
        else {data8g=(datafg-vmin)*255/(vmax-vmin);}

        tex_p[3*(idxrgb)    ]=data8r;
        tex_p[3*(idxrgb)    +1]=data8g;
        tex_p[3*(idxrgb)    +2]=data8b;

        tex_p[3*(idxrgb+1)  ]=data8r;
        tex_p[3*(idxrgb+1)  +1]=data8g;
        tex_p[3*(idxrgb+1)  +2]=data8b;

        tex_p[3*(idxrgb+w)  ]=data8r;
        tex_p[3*(idxrgb+w)  +1]=data8g;
        tex_p[3*(idxrgb+w)  +2]=data8b;

        tex_p[3*(idxrgb+w+1)]=data8r;
        tex_p[3*(idxrgb+w+1)+1]=data8g;
        tex_p[3*(idxrgb+w+1)+2]=data8b;
    }
}


/*
__global__ void _u162f32_kernel(void *d_raw, void *d_preproc, int size)
{
    uint16 *raw_p=(uint16 *)d_raw;
    float32 *preproc_p=(float32 *)d_preproc;
 
    int idx = blockIdx.x*blockDim.x+threadIdx.x;
      
    if(idx<size){
      preproc_p[idx]=(float32)raw_p[idx];
    }
}

extern "C"  void uint16_to_float32(void *d_raw, void *d_preproc, int size)
{
  _u162f32_kernel<<<10020,256>>>(d_raw, d_preproc, size);
}


extern "C"  void float32_to_gray8(void *d_data, void *d_tex, int size, int thres, int vmin, int vmax)
{
  _f322g8_kernel<<<10020,256>>>(d_data, d_tex, size, thres, vmin, vmax, INVERTED);
}
*/

extern "C"  void uint16_to_gray8(void *d_data, void *d_tex, int size, int thres, int vmin, int vmax)
{
  int numBlocks=(int)(ceil(size/256.));
  _u162g8_kernel<<<numBlocks,256>>>(d_data, d_tex, size, thres, vmin, vmax);
}

extern "C"  void uint8_to_gray8(void *d_data, void *d_tex, int size, int thres, int vmin, int vmax)
{
  int numBlocks=(int)(ceil(size/256.));
  _u82g8_kernel<<<numBlocks,256>>>(d_data, d_tex, size, thres, vmin, vmax);
}

extern "C"  void uint8_to_rgb8(void *d_data, void *d_tex, int size, int w, int thres, int vmin, int vmax)
{
  int numBlocks=(int)(ceil(size/4/256.));//each thread takes 4 pixels
  _u82rgb8_kernel<<<numBlocks,256>>>(d_data, d_tex, size, w, thres, vmin, vmax);
}

/*extern "C"  void gray8(void *d_data, void *d_tex, int x, int y, int w, int h, uint8 thres, int vmin, int vmax)
{
  _gray8_kernel<<<10020,256>>>(d_data, d_tex, x, y, w, h, thres, vmin, vmax);
}*/

