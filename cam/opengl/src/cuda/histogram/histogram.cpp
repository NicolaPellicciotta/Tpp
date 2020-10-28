#include <cuda_runtime.h>
#include <stdio.h>
#include <stdlib.h>

// project include
#include "histogram_common.h"

extern "C" int histogram(uchar *d_Data, uint *h_HistogramGPU, uint byteCount)
{
    uint  *d_Histogram;

    cudaMalloc((void **)&d_Histogram, HISTOGRAM64_BIN_COUNT * sizeof(uint));

    initHistogram64();

    histogram64(d_Histogram, d_Data, byteCount);

    cudaMemcpy(h_HistogramGPU, d_Histogram, HISTOGRAM64_BIN_COUNT * sizeof(uint), cudaMemcpyDeviceToHost);


    closeHistogram64();

    cudaFree(d_Histogram);

    return 0;
}
