/* ------------------------------------------------------------
name: "acid303"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Acid303 -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Acid303_H__
#define  __Acid303_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Acid303
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

static float Acid303_faustpower2_f(float value) {
	return value * value;
}

class Acid303 : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst4;
	FAUSTFLOAT fHslider4;
	float fConst5;
	float fConst6;
	FAUSTFLOAT fHslider5;
	float fConst7;
	float fRec3[2];
	float fRec2[3];
	FAUSTFLOAT fHslider6;
	
 public:
	Acid303() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Acid303 -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "acid303.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "acid303");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
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
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / std::max<float>(1.0f, 0.1f * fConst0);
		fConst2 = std::max<float>(1.0f, 0.005f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 3.1415927f / fConst0;
		fConst5 = 1.0f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst6 = 0.4f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst7 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.18f);
		fHslider1 = FAUSTFLOAT(0.6f);
		fHslider2 = FAUSTFLOAT(3.5e+03f);
		fHslider3 = FAUSTFLOAT(3e+02f);
		fHslider4 = FAUSTFLOAT(8.0f);
		fHslider5 = FAUSTFLOAT(55.0f);
		fHslider6 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
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
	
	virtual Acid303* clone() {
		return new Acid303();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("acid303");
		ui_interface->addHorizontalSlider("accent", &fHslider1, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("cutoff", &fHslider3, FAUSTFLOAT(3e+02f), FAUSTFLOAT(8e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.18f), FAUSTFLOAT(0.05f), FAUSTFLOAT(0.6f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("envmod", &fHslider2, FAUSTFLOAT(3.5e+03f), FAUSTFLOAT(0.0f), FAUSTFLOAT(8e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider5, FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider6, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("res", &fHslider4, FAUSTFLOAT(8.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(16.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 0.9f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = float(fHslider1);
		float fSlow4 = float(fHslider2) * (fSlow3 + 0.5f);
		float fSlow5 = float(fHslider3);
		float fSlow6 = 1.0f / (float(fHslider4) + 8.0f * fSlow3);
		float fSlow7 = std::max<float>(1.1920929e-07f, std::fabs(float(fHslider5)));
		float fSlow8 = fConst7 * fSlow7;
		float fSlow9 = 1.0f - fConst0 / fSlow7;
		float fSlow10 = float(fHslider6);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec0[1] >= fSlow0);
			float fTemp1 = fConst3 * fRec1[0];
			float fTemp2 = fConst2 - fRec1[0];
			float fTemp3 = std::tan(fConst4 * std::min<float>(1.2e+04f, fSlow5 + fSlow4 * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fSlow2 * fTemp2 + 1.0f, 0.1f)) * (1.0f - fConst1 * fTemp0))));
			float fTemp4 = 1.0f / fTemp3;
			float fTemp5 = (fSlow6 + fTemp4) / fTemp3 + 1.0f;
			float fTemp6 = fSlow8 + fRec3[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow8 + fRec3[1];
			fRec3[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec4 = ((iTemp7) ? fTemp8 : fSlow8 + fRec3[1] + fSlow9 * fTemp6);
			fRec2[0] = 2.0f * fRec4 + (-1.0f - (fRec2[2] * ((fTemp4 - fSlow6) / fTemp3 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / Acid303_faustpower2_f(fTemp3))) / fTemp5);
			float fTemp9 = 0.8f * tanhf(fSlow10 * ((fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) * std::max<float>(0.0f, std::min<float>(fTemp1, std::max<float>(fConst6 * fTemp2 + 1.0f, 0.6f)) * (1.0f - fConst5 * fTemp0)) / fTemp5));
			output0[i0] = FAUSTFLOAT(fTemp9);
			output1[i0] = FAUSTFLOAT(fTemp9);
			fVec0[1] = fVec0[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
