/* sf2_extract — render one note from a SoundFont to a stereo PCM16 WAV one-shot.
   usage: sf2_extract <sf2> <bank> <preset> <key> <vel0-127> <holdSec> <maxSec> <out.wav>
   Renders hold, releases, then continues until silence (or maxSec). */
#define TSF_IMPLEMENTATION
#include "tsf.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static void wr32(FILE*f,unsigned v){fputc(v&255,f);fputc((v>>8)&255,f);fputc((v>>16)&255,f);fputc((v>>24)&255,f);}
static void wr16(FILE*f,unsigned v){fputc(v&255,f);fputc((v>>8)&255,f);}

int main(int argc,char**argv){
    if(argc<9){fprintf(stderr,"args\n");return 2;}
    const char*sf=argv[1]; int bank=atoi(argv[2]),preset=atoi(argv[3]),key=atoi(argv[4]);
    float vel=atoi(argv[5])/127.0f; double holdS=atof(argv[6]),maxS=atof(argv[7]);
    const char*out=argv[8];
    const int SR=44100, CH=2, BS=1024;

    tsf* f=tsf_load_filename(sf);
    if(!f){fprintf(stderr,"cannot load %s\n",sf);return 1;}
    tsf_set_output(f,TSF_STEREO_INTERLEAVED,SR,0.0f);
    int pi=tsf_get_presetindex(f,bank,preset);
    if(pi<0){fprintf(stderr,"no preset bank=%d preset=%d\n",bank,preset);return 1;}
    tsf_note_on(f,pi,key,vel);

    long holdN=(long)(holdS*SR), maxN=(long)(maxS*SR);
    short*buf=malloc(sizeof(short)*BS*CH);
    short*all=malloc(sizeof(short)*maxN*CH);
    long n=0; int released=0; int silentChunks=0;
    while(n<maxN){
        int todo=BS; if(n+todo>maxN)todo=(int)(maxN-n);
        tsf_render_short(f,buf,todo,0);
        memcpy(all+n*CH,buf,sizeof(short)*todo*CH);
        if(!released&&n+todo>=holdN){tsf_note_off(f,pi,key);released=1;}
        if(released){
            double acc=0; for(int i=0;i<todo*CH;i++){double v=buf[i]/32768.0;acc+=v*v;}
            if(sqrt(acc/(todo*CH))<1e-4){ if(++silentChunks>=3){n+=todo;break;} } else silentChunks=0;
        }
        n+=todo;
    }
    /* trim trailing digital silence */
    long end=n; while(end>1 && abs(all[(end-1)*CH])<8 && abs(all[(end-1)*CH+1])<8) end--;
    if(end<n/50) end=n; /* keep something */

    FILE*w=fopen(out,"wb"); if(!w){fprintf(stderr,"cannot write %s\n",out);return 1;}
    unsigned data=(unsigned)(end*CH*2);
    fwrite("RIFF",1,4,w);wr32(w,36+data);fwrite("WAVE",1,4,w);
    fwrite("fmt ",1,4,w);wr32(w,16);wr16(w,1);wr16(w,CH);wr32(w,SR);wr32(w,SR*CH*2);wr16(w,CH*2);wr16(w,16);
    fwrite("data",1,4,w);wr32(w,data);fwrite(all,2,end*CH,w);fclose(w);
    fprintf(stderr,"%s key=%d %.2fs\n",out,key,(double)end/SR);
    return 0;
}
