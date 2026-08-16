/* ------------------------------------------------------------
name: "fx_dubdelay"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxDubdelay -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxDubdelay_H__
#define  __FxDubdelay_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxDubdelay
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

static float FxDubdelay_faustpower2_f(float value) {
	return value * value;
}

class FxDubdelay : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	int IOTA0;
	FAUSTFLOAT fHslider1;
	float fConst2;
	float fRec1[3];
	FAUSTFLOAT fHslider2;
	float fRec0[131072];
	float fConst3;
	float fConst4;
	FAUSTFLOAT fHslider3;
	float fRec2[2];
	float fRec4[3];
	float fRec3[131072];
	
 public:
	FxDubdelay() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxDubdelay -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("delays.lib/name", "Faust Delay Library");
		m->declare("delays.lib/version", "1.1.0");
		m->declare("filename", "fx_dubdelay.dsp");
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
		m->declare("name", "fx_dubdelay");
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
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 0.001f * fConst0;
		fConst3 = 44.1f / fConst0;
		fConst4 = 1.0f - fConst3;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2.2e+03f);
		fHslider1 = FAUSTFLOAT(375.0f);
		fHslider2 = FAUSTFLOAT(0.55f);
		fHslider3 = FAUSTFLOAT(1.0f);
	}
	
	virtual void instanceClear() {
		IOTA0 = 0;
		for (int l0 = 0; l0 < 3; l0 = l0 + 1) {
			fRec1[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 131072; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec2[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 131072; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
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
	
	virtual FxDubdelay* clone() {
		return new FxDubdelay();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_dubdelay");
		ui_interface->addHorizontalSlider("damp", &fHslider0, FAUSTFLOAT(2.2e+03f), FAUSTFLOAT(4e+02f), FAUSTFLOAT(8e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("feedback", &fHslider2, FAUSTFLOAT(0.55f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.85f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("mix", &fHslider3, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("time", &fHslider1, FAUSTFLOAT(375.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / FxDubdelay_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 1.4142135f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = fConst2 * float(fHslider1);
		int iSlow7 = int(fSlow6);
		int iSlow8 = std::min<int>(65537, std::max<int>(0, iSlow7 + 1)) + 1;
		float fSlow9 = std::floor(fSlow6);
		float fSlow10 = fSlow6 - fSlow9;
		int iSlow11 = std::min<int>(65537, std::max<int>(0, iSlow7)) + 1;
		float fSlow12 = fSlow9 + (1.0f - fSlow6);
		float fSlow13 = float(fHslider2) / fSlow4;
		float fSlow14 = fConst3 * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fRec1[0] = fSlow12 * fRec0[(IOTA0 - iSlow11) & 131071] + fSlow10 * fRec0[(IOTA0 - iSlow8) & 131071] - fSlow5 * (fSlow3 * fRec1[2] + fSlow1 * fRec1[1]);
			float fTemp0 = float(input0[i0]);
			fRec0[IOTA0 & 131071] = fTemp0 + fSlow13 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1]);
			fRec2[0] = fSlow14 + fConst4 * fRec2[1];
			float fTemp1 = 1.0f - fRec2[0];
			output0[i0] = FAUSTFLOAT(fTemp0 * fTemp1 + fRec2[0] * fRec0[IOTA0 & 131071]);
			fRec4[0] = fSlow12 * fRec3[(IOTA0 - iSlow11) & 131071] + fSlow10 * fRec3[(IOTA0 - iSlow8) & 131071] - fSlow5 * (fSlow3 * fRec4[2] + fSlow1 * fRec4[1]);
			float fTemp2 = float(input1[i0]);
			fRec3[IOTA0 & 131071] = fTemp2 + fSlow13 * (fRec4[2] + fRec4[0] + 2.0f * fRec4[1]);
			output1[i0] = FAUSTFLOAT(fTemp2 * fTemp1 + fRec2[0] * fRec3[IOTA0 & 131071]);
			IOTA0 = IOTA0 + 1;
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec2[1] = fRec2[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
		}
	}

};

#endif
