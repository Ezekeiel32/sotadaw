/* ------------------------------------------------------------
name: "crash_noise"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn CrashNoise -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __CrashNoise_H__
#define  __CrashNoise_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS CrashNoise
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float CrashNoise_faustpower2_f(float value) {
	return value * value;
}

class CrashNoise : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	int iRec1[2];
	float fVec0[2];
	float fRec0[3];
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst2;
	float fRec4[2];
	float fRec3[3];
	float fRec2[3];
	FAUSTFLOAT fButton0;
	int iVec1[2];
	FAUSTFLOAT fHslider3;
	int iConst3;
	int iRec6[2];
	float fConst4;
	float fRec5[2];
	FAUSTFLOAT fHslider4;
	
 public:
	CrashNoise() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn CrashNoise -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsre:author", "Julius O. Smith III");
		m->declare("envelopes.lib/adsre:licence", "STK-4.3");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "crash_noise.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "crash_noise");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 5.0265484f / fConst0;
		fConst2 = 3.1415927f / fConst0;
		iConst3 = int(0.002f * fConst0);
		fConst4 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(3e+02f);
		fHslider1 = FAUSTFLOAT(1.0f);
		fHslider2 = FAUSTFLOAT(0.8f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(1.8f);
		fHslider4 = FAUSTFLOAT(0.6f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iRec1[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iVec1[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec6[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec5[l8] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual CrashNoise* clone() {
		return new CrashNoise();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("crash_noise");
		ui_interface->addHorizontalSlider("decay", &fHslider3, FAUSTFLOAT(1.8f), FAUSTFLOAT(0.3f), FAUSTFLOAT(5.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(3e+02f), FAUSTFLOAT(5e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("shimmer", &fHslider1, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider2, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::max<float>(2.5e+03f, 12.0f * float(fHslider0));
		float fSlow1 = std::tan(fConst1 * fSlow0);
		float fSlow2 = 2.0f * (1.0f - 1.0f / CrashNoise_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -0.45454547f) / fSlow1 + 1.0f;
		float fSlow5 = (fSlow3 + 0.45454547f) / fSlow1 + 1.0f;
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = 0.5f * (float(fHslider1) / (fSlow1 * fSlow5));
		float fSlow8 = std::tan(fConst2 * (1e+04f * float(fHslider2) + 6e+03f));
		float fSlow9 = 2.0f * (1.0f - 1.0f / CrashNoise_faustpower2_f(fSlow8));
		float fSlow10 = 1.0f / fSlow8;
		float fSlow11 = (fSlow10 + -1.4142135f) / fSlow8 + 1.0f;
		float fSlow12 = 1.0f / ((fSlow10 + 1.4142135f) / fSlow8 + 1.0f);
		float fSlow13 = std::tan(fConst2 * fSlow0);
		float fSlow14 = CrashNoise_faustpower2_f(fSlow13);
		float fSlow15 = 2.0f * (1.0f - 1.0f / fSlow14);
		float fSlow16 = 1.0f / fSlow13;
		float fSlow17 = (fSlow16 + -1.0f) / fSlow13 + 1.0f;
		float fSlow18 = (fSlow16 + 1.0f) / fSlow13 + 1.0f;
		float fSlow19 = 1.0f / fSlow18;
		float fSlow20 = 1.0f - fSlow16;
		float fSlow21 = 4.656613e-10f / fSlow13;
		float fSlow22 = 1.0f / (fSlow16 + 1.0f);
		float fSlow23 = 1.0f / (fSlow14 * fSlow18);
		int iSlow24 = float(fButton0) > 0.0f;
		float fSlow25 = float(fHslider3);
		float fSlow26 = float(iSlow24);
		float fSlow27 = 0.7f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iRec1[0] = 1103515245 * iRec1[1] + 12345;
			float fTemp0 = float(iRec1[0]);
			fVec0[0] = fTemp0;
			fRec0[0] = 4.656613e-10f * fTemp0 - fSlow6 * (fSlow4 * fRec0[2] + fSlow2 * fRec0[1]);
			fRec4[0] = fSlow22 * (fSlow21 * (fTemp0 - fVec0[1]) - fSlow20 * fRec4[1]);
			fRec3[0] = fRec4[0] - fSlow19 * (fSlow17 * fRec3[2] + fSlow15 * fRec3[1]);
			fRec2[0] = fSlow23 * (fRec3[2] + (fRec3[0] - 2.0f * fRec3[1])) - fSlow12 * (fSlow11 * fRec2[2] + fSlow9 * fRec2[1]);
			iVec1[0] = iSlow24;
			int iTemp1 = iSlow24 - iVec1[1];
			iRec6[0] = iSlow24 * (iRec6[1] + 1);
			int iTemp2 = (iRec6[0] < iConst3) | (iTemp1 * (iTemp1 > 0));
			float fTemp3 = 0.1447178f * ((iSlow24) ? ((iTemp2) ? 0.002f : fSlow25) : fSlow25);
			int iTemp4 = std::fabs(fTemp3) < 1.1920929e-07f;
			float fTemp5 = ((iTemp4) ? 0.0f : std::exp(-(fConst4 / ((iTemp4) ? 1.0f : fTemp3))));
			fRec5[0] = (1.0f - fTemp5) * ((iSlow24) ? ((iTemp2) ? fSlow26 : 0.0f) : 0.0f) + fTemp5 * fRec5[1];
			float fTemp6 = tanhf(fSlow27 * CrashNoise_faustpower2_f(fRec5[0]) * (fSlow12 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) + fSlow7 * (fRec0[0] - fRec0[2])));
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iRec1[1] = iRec1[0];
			fVec0[1] = fVec0[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec4[1] = fRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			iVec1[1] = iVec1[0];
			iRec6[1] = iRec6[0];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
