/* ------------------------------------------------------------
name: "fx_delay"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxDelay -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxDelay_H__
#define  __FxDelay_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxDelay
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

static float FxDelay_faustpower2_f(float value) {
	return value * value;
}

class FxDelay : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fRec0[2];
	float fConst4;
	float fConst6;
	float fConst7;
	float fRec2[3];
	FAUSTFLOAT fHslider1;
	int IOTA0;
	float fVec0[131072];
	FAUSTFLOAT fHslider2;
	float fConst8;
	float fRec1[2];
	float fRec4[3];
	float fVec1[131072];
	float fRec3[2];
	
 public:
	FxDelay() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxDelay -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("filename", "fx_delay.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
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
		m->declare("name", "fx_delay");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 44.1f / fConst0;
		fConst2 = 1.0f - fConst1;
		float fConst3 = std::tan(14137.167f / fConst0);
		fConst4 = 2.0f * (1.0f - 1.0f / FxDelay_faustpower2_f(fConst3));
		float fConst5 = 1.0f / fConst3;
		fConst6 = (fConst5 + -1.4142135f) / fConst3 + 1.0f;
		fConst7 = 1.0f / ((fConst5 + 1.4142135f) / fConst3 + 1.0f);
		fConst8 = 0.001f * fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.22f);
		fHslider1 = FAUSTFLOAT(0.35f);
		fHslider2 = FAUSTFLOAT(375.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 3; l1 = l1 + 1) {
			fRec2[l1] = 0.0f;
		}
		IOTA0 = 0;
		for (int l2 = 0; l2 < 131072; l2 = l2 + 1) {
			fVec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec4[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 131072; l5 = l5 + 1) {
			fVec1[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec3[l6] = 0.0f;
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
	
	virtual FxDelay* clone() {
		return new FxDelay();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_delay");
		ui_interface->addHorizontalSlider("feedback", &fHslider1, FAUSTFLOAT(0.35f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.85f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("mix", &fHslider0, FAUSTFLOAT(0.22f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("time", &fHslider2, FAUSTFLOAT(375.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = fConst7 * float(fHslider1);
		float fSlow2 = fConst8 * float(fHslider2);
		int iSlow3 = int(fSlow2);
		int iSlow4 = std::min<int>(65537, std::max<int>(0, iSlow3 + 1));
		float fSlow5 = std::floor(fSlow2);
		float fSlow6 = fSlow2 - fSlow5;
		int iSlow7 = std::min<int>(65537, std::max<int>(0, iSlow3));
		float fSlow8 = fSlow5 + (1.0f - fSlow2);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fRec0[0] = fSlow0 + fConst2 * fRec0[1];
			float fTemp0 = 1.0f - fRec0[0];
			float fTemp1 = float(input0[i0]);
			fRec2[0] = fRec1[1] - fConst7 * (fConst6 * fRec2[2] + fConst4 * fRec2[1]);
			float fTemp2 = fTemp1 + fSlow1 * (fRec2[2] + fRec2[0] + 2.0f * fRec2[1]);
			fVec0[IOTA0 & 131071] = fTemp2;
			fRec1[0] = fSlow8 * fVec0[(IOTA0 - iSlow7) & 131071] + fSlow6 * fVec0[(IOTA0 - iSlow4) & 131071];
			output0[i0] = FAUSTFLOAT(fRec1[0] * fRec0[0] + fTemp1 * fTemp0);
			fRec4[0] = fRec3[1] - fConst7 * (fConst6 * fRec4[2] + fConst4 * fRec4[1]);
			float fTemp3 = float(input1[i0]);
			float fTemp4 = fTemp3 + fSlow1 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1]);
			fVec1[IOTA0 & 131071] = fTemp4;
			fRec3[0] = fSlow8 * fVec1[(IOTA0 - iSlow7) & 131071] + fSlow6 * fVec1[(IOTA0 - iSlow4) & 131071];
			output1[i0] = FAUSTFLOAT(fTemp3 * fTemp0 + fRec0[0] * fRec3[0]);
			fRec0[1] = fRec0[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
			IOTA0 = IOTA0 + 1;
			fRec1[1] = fRec1[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
