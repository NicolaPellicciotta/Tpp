#include "edtinc.h"
#include <string.h>
#define ERROR(msg, retval) strcpy(ErrMsg, msg); return retval;
//#define ERRORP(msg, errcode) sprintf(ErrMsg, "%s. code: %d", msg, errcode); return errcode;
#define ERRORS(msg, str) sprintf(ErrMsg, "%s %s", msg, str); return 1;

//sensor shape
#define CAMWIDTH 1920
#define CAMHEIGHT 1336
#define PIXELSIZE 2 //pixel depth in bytes

//Serial communication
#define SERIALBUFSIZE 256
char cmd[SERIALBUFSIZE];
char ans[SERIALBUFSIZE];


PdvDev *pdv_p;
char Msg[256]; //buffer string used as ErrMsg when calling functions internally

//we store roi globally there'sn library function to retrieve that
int roi_left=0, roi_top=0, roi_width=1920, roi_height=1336; 

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
		cam_set_roi(0, 0, CAMWIDTH, CAMHEIGHT, Msg);
		pdv_multibuf(pdv_p, 4);
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
int cam_snap(u_char *buf_p, double *t_sec, char *ErrMsg){
  u_char *image_p;
	u_int time[2]; //seconds and microseconds
	pdv_start_image(pdv_p);
  image_p=pdv_wait_image_timed(pdv_p, time);
  //image_p=pdv_wait_image(pdv_p);
	*t_sec=((double)time[0])+((double)time[1])/1.e9;
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
int cam_stream(int nframes, float fps, char *ErrMsg){
	pdv_start_images(pdv_p, nframes);
	return 0;
}

// capture a single frame from a stream
int cam_capture(u_char *buf_p, double *t_sec, char *ErrMsg){
  u_char *image_p;
	u_int time[2]; //seconds and microseconds
  image_p=pdv_wait_image_timed(pdv_p, time);
  //image_p=pdv_wait_image(pdv_p);
	*t_sec=((double)time[0])+((double)time[1])/1.e9;
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

int cam_capture_tofile(char * filename, double *t_sec, char *ErrMsg){
  FILE *fd;
  u_char *image_p;
	u_int time[2]; //seconds and microseconds

  fd=fopen(filename, "w");
  image_p=pdv_wait_image_timed(pdv_p, time);
  //image_p=pdv_wait_image(pdv_p);
	*t_sec=((double)time[0])+((double)time[1])/1.e9;
	//fprintf(stderr, "%d %d\n", time[0], time[1]);
	//fprintf(stderr, "%f\n", t_sec);
  //check for timeouts
  if (pdv_timeouts(pdv_p) > 0){
    ERROR("Got timeout while acquiring frame", 1);
  }
  //copy frame buffer
  roiwrite(fd, image_p);
  fclose(fd);
	return 0;
}



int roicpy(u_char *buf_p, u_char *image_p){
  int i;
  u_char *src_p, *dest_p;

	//memcpy(buf_p, image_p, roi_width*roi_height*PIXELSIZE);
  for (i=0; i<roi_height; i++){
		src_p=image_p+PIXELSIZE*(i*CAMWIDTH+roi_left);
		dest_p=buf_p+PIXELSIZE*i*roi_width;
		memcpy(dest_p, src_p, PIXELSIZE*roi_width);
	}
}

int roiwrite(FILE *fd, u_char *image_p){
  int i;
  u_char *src_p;

	//memcpy(buf_p, image_p, roi_width*roi_height*PIXELSIZE);
  for (i=0; i<roi_height; i++){
		src_p=image_p+PIXELSIZE*(i*CAMWIDTH+roi_left);
		fwrite(src_p, 2, roi_width, fd);
	}
}


int cam_stop(char *ErrMsg){
	u_char *image_p;
	int nskip;
  pdv_start_images(pdv_p, 1);
	image_p=pdv_wait_last_image(pdv_p, &nskip);
  //pdv_flush_fifo(pdv_p);
  fprintf(stderr, "nskip=%d\n", nskip);
  return 0;
}

int cam_serial_command(char *cmd){
	int got;
	fprintf(stderr, "cmd=%s\n", cmd);
	pdv_serial_command(pdv_p, cmd);
	got=pdv_serial_wait(pdv_p,0,SERIALBUFSIZE);
	got=pdv_serial_read(pdv_p, ans, got);
	fprintf(stderr, "got=%d ans=%s\n", got, ans);
  return 0;
}

/*************************************************
 * Features set and get
 * ***********************************************/

int cam_get_shutter(double *val, char *ErrMsg){
	cam_serial_command("?AET");
	*val=atof(ans+4);
	return 0;
}

int cam_set_shutter(double val, char *ErrMsg){
	if (val>10. || val <2.e-5){
		ERROR("valid shutter range: 20us to 10s", 1);
	}
	sprintf(cmd, "AET %.6f", val);
	cam_serial_command(cmd);
	return 0;
}


int cam_set_roi(int left, int top, int width, int height, char *ErrMsg){	

  if (top+height>1336){
    ERROR("ROI top+height exceeds 1336", 1)
  }

  if (top+roi_height<=1336){
    sprintf(cmd, "SVO %d", top+8);
	  cam_serial_command(cmd);
  }

	sprintf(cmd, "SVW %d", height);
	cam_serial_command(cmd);

  if (top+roi_height>1336){
    sprintf(cmd, "SVO %d", top+8);
	  cam_serial_command(cmd);
  }

  //only needs info on width and height to correctly grab frame, leave 0 other pars!
  pdv_set_roi(pdv_p, 0, CAMWIDTH, 0, height);

	//store roi data
	roi_left=left;
	roi_top=top;
	roi_width=width;
	roi_height=height;

	return 0;
}


