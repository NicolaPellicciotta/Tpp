#include "edtinc.h"
#include <string.h>
#define ERROR(msg, retval) strcpy(ErrMsg, msg); return retval;
//#define ERRORP(msg, errcode) sprintf(ErrMsg, "%s. code: %d", msg, errcode); return errcode;
#define ERRORS(msg, str) sprintf(ErrMsg, "%s %s", msg, str); return 1;

//sensor shape
#define CAMWIDTH 1280
#define CAMHEIGHT 1024
#define PIXELSIZE 1 //pixel depth in bytes
//Serial communication
#define SERIALBUFSIZE 256
char cmd[SERIALBUFSIZE];
char ans[SERIALBUFSIZE];


PdvDev *pdv_p;
char Msg[256]; //buffer string used as ErrMsg when calling functions internally

//we store roi globally there'sn library function to retrieve that
int roi_left=0, roi_top=0, roi_width=CAMWIDTH, roi_height=CAMHEIGHT; 
int STREAMING=0;
int total_timeouts=0;
int recover_after_timeout=0;


int roicpy(u_char *buf_p, u_char *image_p){
	memcpy(buf_p, image_p, roi_width*roi_height*PIXELSIZE);
}

int serial_command(char *cmd){
	int got;
	fprintf(stderr, "cmd=%s\n", cmd);
	pdv_serial_command(pdv_p, cmd);
	got=pdv_serial_wait(pdv_p,0,SERIALBUFSIZE);
	got=pdv_serial_read(pdv_p, ans, got);
	fprintf(stderr, "got=%d ans=%s\n", got, ans);

  if (ans[0]==21){
	  return 1;
  }
	

  return 0;
}

int cam_init(char *ErrMsg){
	//pdv_set_serial_parity(pdv_p,'n');
  return 0;
}

// Open available camera
int cam_open(char *ErrMsg){
    int unit = 0;
    int channel = 0;

    if ((pdv_p = pdv_open_channel(EDT_INTERFACE, unit, channel)) == NULL){
      ERROR("Failed to open the camera", 1)
    }

	//reset roi
    pdv_enable_roi(pdv_p, 1);
    //cam_set_roi(0, 0, CAMWIDTH, CAMHEIGHT, Msg);
    return 0;
}

// Close available camera
int cam_close(char *ErrMsg){
	if(pdv_close(pdv_p)){
		ERROR("Failed to close the camera",1)
	}	
 	return 0;
}

int cam_end(){
	return 0;
}


// capture a single frame
int cam_snap(u_char *buf_p, unsigned int  *timestamp, char *ErrMsg){
  u_char *image_p;
	u_int time[2]; //seconds and microseconds
	pdv_multibuf(pdv_p, 4);
	pdv_start_image(pdv_p);
  image_p=pdv_wait_image_timed(pdv_p, time);
  //image_p=pdv_wait_image(pdv_p);
	//*t_sec=((double)time[0])+((double)time[1])/1.e9;
	*timestamp=(unsigned int)(((double)time[0])*1.e6+((double)time[1])/1.e3);
	//fprintf(stderr, "%d %d\n", time[0], time[1]);
	//fprintf(stderr, "%f\n", t_sec);
  //check for timeouts
  if (pdv_timeouts(pdv_p) > 0){
    ERROR("Got timeout while acquiring frame", 1);
  }

  //copy frame buffer
  roicpy(buf_p, image_p);
	return 0;
}

//fps unused only for compatibility with prosilica
int cam_stream(int trig, char *ErrMsg){
    if (trig!=0) {ERROR("Trigger mode not implemented",1)}
	pdv_multibuf(pdv_p, 4);
	pdv_start_images(pdv_p, 0);
    STREAMING=1;
	return 0;
}

int cam_stop(char *ErrMsg){
	u_char *image_p;
	int nskip;
  pdv_start_images(pdv_p, 1);
	image_p=pdv_wait_last_image(pdv_p, &nskip);
  //pdv_flush_fifo(pdv_p);
  fprintf(stderr, "nskip=%d\n", nskip);
  STREAMING=0;
  pdv_stop_continuous(pdv_p);
  pdv_timeout_cleanup(pdv_p);
  return 0;
}

// capture a single frame from a stream
int cam_capture(u_char *buf_p, unsigned int *timestamp, char *ErrMsg){
  int timeouts;
  u_char *image_p;
	u_int time[2]; //seconds and microseconds
  //fprintf(stderr, "capturing...");
  image_p=pdv_wait_last_image_timed(pdv_p, time);
  //fprintf(stderr, "got it\n");
  //image_p=pdv_get_last_image(pdv_p);
  //image_p=pdv_wait_image(pdv_p);
	*timestamp=(unsigned int)(((double)time[0])*1.e6+((double)time[1])/1.e3);
	//*t_sec=((double)time[0])+((double)time[1])/1.e9;
	//fprintf(stderr, "%d %d\n", time[0], time[1]);
	//fprintf(stderr, "%f\n", t_sec);
  //check for timeouts
  timeouts=pdv_timeouts(pdv_p);
  if (timeouts > total_timeouts){
    total_timeouts=timeouts;
    fprintf(stderr,"timeouts: %d\n", timeouts);
    pdv_timeout_restart(pdv_p, TRUE);
    ERROR("Got timeout while acquiring frame", 1);
  } else if (recover_after_timeout){
    recover_after_timeout=0;
    pdv_timeout_restart(pdv_p, TRUE);
    fprintf(stderr,"recovering\n");
  }

  //copy frame buffer
  //fprintf(stderr, "copying...");
  roicpy(buf_p, image_p);
  //fprintf(stderr, "done\n");
	return 0;
}


/*************************************************
 * Features set and get
 * ***********************************************/

int cam_get_shutter(double *t_sec, char *ErrMsg){
  int t_us;
	serial_command(":t?");
  ans[6]=0;
  sscanf(ans, "%06x", &t_us);
	*t_sec=((double)(t_us))/1.e6;
	return 0;
}

int cam_set_shutter(double t_sec, char *ErrMsg){
  int t_us;
  t_us=(unsigned int)(t_sec*1.e6);
	if (t_us <2){
		ERROR("valid shutter range: >2 us", 1);
	}
	sprintf(cmd, ":t%.06x", t_us); 
	if (serial_command(cmd)){
    ERROR("Invalid shutter: valid range 2us-1/fps", 1);
  };
  return 0;
}

int cam_get_framerate(double *fps, char *ErrMsg){
  int ifps;
	serial_command(":q?");
  ans[6]=0;
  sscanf(ans, "%06x", &ifps);
	*fps=(double)ifps;
	return 0;
}

int cam_set_framerate(double fps, char *ErrMsg){
	if (fps < 1){
		ERROR("Invalid fps: fps should be greater than 1", 1);
	}
	sprintf(cmd, ":q%.06x", (int)fps); 
	if (serial_command(cmd)){
    ERROR("Invalid fps: fps is too high for current ROI", 1);
  };
  return 0;
}


int cam_get_gain(int *val, char *ErrMsg){
	ERROR("Function not implemented", 1);
}

int cam_set_gain(int val, char *ErrMsg){
	ERROR("Function not implemented", 1);
}

int cam_get_roi(int *left, int *top, int *width, int *height, char *ErrMsg){
  *left=roi_left;
  *top=roi_top;
  *width=roi_width;
  *height=roi_height;
  return 0;
}

int cam_set_roi(int left, int top, int width, int height, char *ErrMsg){	
  //TODO: handle cam serial errors

  height=(height/8)*8; //arbitrary ROI heights should be possible according to the manual but it freezes with odd numbers
  width=(width/8)*8;

  if (height>CAMHEIGHT){
    top=0;
    height=CAMHEIGHT;
  } else if (top+height>CAMHEIGHT){
    top=CAMHEIGHT-height;
  }

  if (width>CAMWIDTH){
    left=0;
    width=CAMWIDTH;
  } else if (left+width>CAMWIDTH){
    left=CAMWIDTH-width;
  }

  left=(left/24)*24;
  pdv_set_roi(pdv_p, 0, width, 0, height);

  sprintf(cmd, ":d%.03x%.03x%.03x%.03x", left, top, width, height);
	serial_command(cmd);

	//store roi data
	roi_left=left;
	roi_top=top;
	roi_width=width;
	roi_height=height;

	return 0;
}

int cam_get_format(char *format, char *ErrMsg){
  sprintf(format, "MONO8");
  return 0;
}


int cam_set_format(char *format, char *ErrMsg){
	ERROR("Function not implemented", 1);
}

int cam_get_shape(int *width, int *height, char *ErrMsg){
  *width=CAMWIDTH;
  *height=CAMHEIGHT;
  return 0;
}

int cam_get_clocks_per_sec(double *cps, char *ErrMsg){
  *cps=1.e6;
  return 0;
}

int cam_streaming(int *val, char *ErrMsg){
  *val=STREAMING;
  return 0;
}

int cam_get_micron_per_pixel(double *val, char ErrMsg)
{
    *val=14.;
    return 0;
}
