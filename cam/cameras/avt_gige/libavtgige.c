#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <PvApi.h>
#define WIDTH 1280
#define HEIGHT 1024
#define MAXFRAMESIZE 1310720 //1280*1024
#define MAXSTRINGATTR 256

typedef struct 
{
    unsigned long   UID;
    tPvHandle       Handle;
} tCamera;

//global vars
unsigned long FrameSize;
tPvFrame *pendingFrame, *nextFrame;
char ImageBufferA[MAXFRAMESIZE];
char ImageBufferB[MAXFRAMESIZE];
tPvFrame FrameA, FrameB;
tCamera Camera;
unsigned long CAMCLOCKS_PER_SEC=4e7;
unsigned int roi_left=0,roi_top=0,roi_width=WIDTH,roi_height=HEIGHT;
double frames_per_second=20;
int STREAMING=0;

#define ERROR(msg, retval) strcpy(ErrMsg, msg); return retval;
#define ERRORS(msg, str) sprintf(ErrMsg, "%s %s", msg, str); return 1;



void _WaitForCamera()
{
	int i=0;
    while(!PvCameraCount() && i<500)
    {
        usleep(10000);
        i++;
    }
}


// get the first camera found
int _CameraGet()
{
    tPvUint32 count,connected;
    tPvCameraInfo list;

    count = PvCameraList(&list,1,&connected);
    if(count == 1)
    {
        Camera.UID = list.UniqueId;
        //printf("GigE Cam: got camera %s\n",list.SerialString);
        return 0;
    }
    else
        return 1;
}


// get and set cam attributes
int _cam_get_u32(char *name, unsigned long *val, char *ErrMsg)
{
    if(PvAttrUint32Get(Camera.Handle, name , val)){
        ERRORS("Failed to get attr: ", name)   
	} 
	return 0;
}


int _cam_set_u32(char *name, unsigned long val, char *ErrMsg)
{
	if(PvAttrUint32Set(Camera.Handle, name , val)){
        ERRORS("Failed to Set attr: ", name)   
	} 
	return 0;
}

int _cam_get_string(char *name, char *val, char *ErrMsg)
{
    if(PvAttrStringGet(Camera.Handle, name , val, MAXSTRINGATTR, NULL)){
        ERRORS("Failed to get attr: ", name)   
	} 
	return 0;
}

/*
int _cam_get_f32(char *name, float *val, char *ErrMsg)
{
    if(PvAttrFloat32Get(Camera.Handle, name , val)){
        ERRORS("Failed to get attr: ", name)   
	} 
	return 0;
}

int cam_get_u32(char *name, tPvUint32 *val, char *ErrMsg){
	char PvName[256];
	if (strcmp(name, "shutter")==0)
		strcpy(PvName, "ExposureValue");
	else if (strcmp(name, "gain")==0)
		strcpy(PvName, "GainValue");
	else {
		ERROR("Feature not available as uint32",1)
	}
	_cam_get_u32(PvName, val, ErrMsg);
	return 0;
}

int cam_get_string(char *name, char *val, char *ErrMsg){
	char PvName[256];
	if (strcmp(name, "model")==0)
		strcpy(PvName, "ModelName");
	else {
		ERROR("Feature not available as string",1)
	}
	_cam_get_string(PvName, val, ErrMsg);
	return 0;
}*/

int cam_get_roi(tPvUint32 *left, tPvUint32 *top, tPvUint32 *width, tPvUint32 *height, char *ErrMsg)
{
    *left=roi_left;//_cam_get_u32("RegionX", left, ErrMsg);
    *top=roi_top;//_cam_get_u32("RegionY", top, ErrMsg);
    *width=roi_width;//_cam_get_u32("Width", width, ErrMsg);
    *height=roi_height;//_cam_get_u32("Height", height, ErrMsg);
    return 0;
}

int cam_set_roi(tPvUint32 left, tPvUint32 top, tPvUint32 width, tPvUint32 height, char *ErrMsg)
{
    if (height>HEIGHT) {height=HEIGHT;}
    if (width>WIDTH) {width=WIDTH;}
    if (top+height>HEIGHT) { top=HEIGHT-height;} 
    if (left+width>WIDTH) { left=WIDTH-width;} 

    if (_cam_set_u32("RegionX", 0, ErrMsg)|| _cam_set_u32("RegionY", 0, ErrMsg)) {return 1;}
    if (_cam_set_u32("Width", width, ErrMsg)|| _cam_set_u32("Height", height, ErrMsg)) {return 1;}
    if (_cam_set_u32("RegionX", left, ErrMsg)|| _cam_set_u32("RegionY", top, ErrMsg)) {return 1;}

    roi_left=left;
    roi_top=top;
    roi_width=width;
    roi_height=height;
    return 0;
}

int cam_get_shape(tPvUint32 *width, tPvUint32 *height, char *ErrMsg)
{
	_cam_get_u32("SensorWidth", width, ErrMsg);
	_cam_get_u32("SensorHeight", height, ErrMsg);
	return 0;
}


int cam_get_shutter(double *val, char *ErrMsg)
{
	tPvUint32  u32val;
	if (_cam_get_u32("ExposureValue", &u32val, ErrMsg)!=0)
		return 1;
	*val=((double)u32val)/1.e6;
	return 0;
}

int cam_set_shutter(double val, char *ErrMsg)
{
	tPvUint32  u32val;
	u32val=(tPvUint32)(val*1e6);
	if (_cam_set_u32("ExposureValue", u32val, ErrMsg)!=0)
		return 1;
	return 0;
}


int cam_get_model(char *val, char *ErrMsg)
{
    if (_cam_get_string("ModelName", val, ErrMsg)!=0)
        return 1;
    return 0;
}

int cam_get_framerate(double *fps, char *ErrMsg)
{
    *fps=frames_per_second;
    return 0;
}

int cam_set_framerate(double fps, char *ErrMsg)
{
    frames_per_second=fps;
    return 0;
}

int cam_get_gain(tPvUint32 *val, char *ErrMsg)
{
    if (_cam_get_u32("GainValue", val, ErrMsg)!=0)
        return 1;
    return 0;
}

int cam_set_gain(tPvUint32 val, char *ErrMsg)
{
	if (_cam_set_u32("GainValue", val, ErrMsg)!=0)
		return 1;
	return 0;
	}

int cam_set_format(char *formatstr,char *ErrMsg)
{
    if (strncmp(formatstr,"MONO8",5)!=0)
    {ERROR("Only MONO8 format is avaible",1)}
    return 0;
}

int cam_get_format(char *formatstr,char *ErrMsg)
{
    strcpy(formatstr,"MONO8");
    return 0;
}

// Open available camera
int cam_open(char *ErrMsg)
{
    //tPvUint32 lMaxSize = 8228;
	if(PvCameraOpen(Camera.UID,ePvAccessMaster,&(Camera.Handle)))
    {ERROR("Failed to open the camera",1)}
    // get the last packet size set on the camera
    //PvAttrUint32Get(Camera.Handle,"PacketSize",&lMaxSize);
    // adjust the packet size according to the current network capacity
    //PvCaptureAdjustPacketSize(Camera.Handle,1024);
	//printf("packetsize: %lu\n", lMaxSize);
	return 0;
} 

// Close available camera
int cam_close(char *ErrMsg)
{
	if(	PvCameraClose(Camera.Handle))
    {ERROR("Failed to close the camera",1)}	
 	return 0;
}

// Uninitialize API
int cam_end()
{
	PvUnInitialize();
	return 0;
}

// Initialize API and grab first available camera ID
int cam_init(char *ErrMsg)
{
	//init global vars
	FrameA.ImageBuffer=ImageBufferA;
	FrameB.ImageBuffer=ImageBufferB;
	FrameA.Context[0]="A";
	FrameB.Context[0]="B";
	// PvAPI init
	if(PvInitialize()) {ERROR("Failed to initialise the API",1)}

	// wait for a camera to be plugged
	_WaitForCamera();
    // get a camera from the list
	if(_CameraGet())
    {
		PvUnInitialize();
		ERROR("Failed to find a camera",1)
	}
    
	return 0;
}

// enqueue and capture a single frame
int cam_snap(char *buf, unsigned long *timestamp, char *ErrMsg)
{
    // set the camera in capture mode
    if(PvCaptureStart(Camera.Handle)||PvAttrEnumSet(Camera.Handle,"FrameStartTriggerMode","Freerun"))
    {ERROR("Could not start capture in Freerun",-1)}

	// set FrameSize
	if(PvAttrUint32Get(Camera.Handle,"TotalBytesPerFrame",&FrameSize))
    {ERROR("Couldn't get FrameSize",-2)}
    FrameA.ImageBufferSize = FrameSize;
	
	// enqueue frame
	if(PvCaptureQueueFrame(Camera.Handle, &FrameA, NULL))
    {ERROR("Couldn't enqueue frame",-3)}

    // and set the acquisition mode into continuous
    if(PvCommandRun(Camera.Handle,"AcquisitionStart"))
    {ERROR("Couldn't start acquisition",-4)}

    //printf("waiting for the frame to be done ...\n");
    if(PvCaptureWaitForFrameDone(Camera.Handle,&(FrameA),1000) == ePvErrTimeout)
    {
        PvCommandRun(Camera.Handle,"AcquisitionStop");
        PvCaptureEnd(Camera.Handle);
        PvCaptureQueueClear(Camera.Handle);
    	ERROR("Timeout while waiting for frame",-5)
    }

    if(FrameA.Status != ePvErrSuccess)
    {
        PvCommandRun(Camera.Handle,"AcquisitionStop");
        PvCaptureEnd(Camera.Handle);
        ERROR("Got frame with error", (int)FrameA.Status)
    }

    if(PvCommandRun(Camera.Handle,"AcquisitionStop")||PvCaptureEnd(Camera.Handle))
    {ERROR("Couldn't stop acquisition",-6)}

    //copy frame buffer
	memcpy(buf, FrameA.ImageBuffer, FrameSize);
	*timestamp=FrameA.TimestampLo;
	return 0;
}

// start fixed rate streaming
int cam_stream(int trig, char *ErrMsg)
{
    if (trig!=0)
    {ERROR("Trigger mode not implemented",1)}

	// set FrameSize
	if(PvAttrUint32Get(Camera.Handle,"TotalBytesPerFrame",&FrameSize))
    {ERROR("Couldn't get FrameSize",1)}
	
    FrameA.ImageBufferSize = FrameSize;
    FrameB.ImageBufferSize = FrameSize;

    // set the camera in capture mode
    if(PvAttrFloat32Set(Camera.Handle, "FrameRate" , frames_per_second) || PvAttrEnumSet(Camera.Handle,"FrameStartTriggerMode","FixedRate") || PvCaptureStart(Camera.Handle))
    {ERROR("Could not start capture with FixedRate",1)}

	// enqueue frames
	if(PvCaptureQueueFrame(Camera.Handle, &FrameA, NULL)||PvCaptureQueueFrame(Camera.Handle, &FrameB, NULL))
    {ERROR("Couldn't enqueue frames",1)}

	pendingFrame=&FrameB;
	nextFrame=&FrameA;
		
    // and set the acquisition mode into continuous
    if(PvCommandRun(Camera.Handle,"AcquisitionStart"))
    {ERROR("Couldn't start acquisition",1)}

    STREAMING=1;
        
    return 0;
}

// Captures oldest enqueued frame
int cam_capture(char *buf,  unsigned long *timestamp, char *ErrMsg)
{
	tPvFrame *tmp;

    if (PvCaptureWaitForFrameDone(Camera.Handle,nextFrame,1000) == ePvErrTimeout)
    {ERROR("Timeout while waiting for frame",1)}
    
    if(nextFrame->Status != ePvErrSuccess)
    {ERROR( "Got frame with error", (int)nextFrame->Status)}
    
    //copy data
	memcpy(buf, nextFrame->ImageBuffer, FrameSize);
	*timestamp=nextFrame->TimestampLo;

	if(PvCaptureQueueFrame(Camera.Handle, nextFrame, NULL))
    {ERROR("Couldn't renqueue frame",1)}

	//requeue frame	
	tmp=nextFrame;
	nextFrame=pendingFrame;
	pendingFrame=tmp;
	
	return 0;
}

// Stop streaming
int cam_stop(char *ErrMsg)
{
    if(PvCommandRun(Camera.Handle,"AcquisitionStop") || PvCaptureEnd(Camera.Handle) || PvCaptureQueueClear(Camera.Handle))
    {ERROR("Couldn't stop acquisition",1)}
    STREAMING=0;
    return 0;
}

int cam_get_clocks_per_sec(double *cps, char *ErrMsg)
{
    *cps=(double)CAMCLOCKS_PER_SEC;
    return 0;
}

int cam_streaming(int *val, char *ErrMsg)
{
    *val=STREAMING;
    return 0;
}

int cam_get_micron_per_pixel(double *val, char ErrMsg)
{
    *val=6.7;
    return 0;
}


