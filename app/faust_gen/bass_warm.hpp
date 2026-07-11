/* ------------------------------------------------------------
name: "bass_warm"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn BassWarm -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __BassWarm_H__
#define  __BassWarm_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS BassWarm
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

static float BassWarm_faustpower2_f(float value) {
	return value * value;
}

class BassWarm : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	float fRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	float fConst3;
	int iRec1[2];
	float fConst4;
	FAUSTFLOAT fHslider0;
	float fConst5;
	FAUSTFLOAT fHslider1;
	float fConst6;
	FAUSTFLOAT fHslider2;
	float fConst7;
	float fRec3[2];
	float fRec5[2];
	FAUSTFLOAT fHslider3;
	float fRec2[3];
	
 public:
	BassWarm() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn BassWarm -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "bass_warm.dsp");
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
		m->declare("name", "bass_warm");
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
		fConst1 = std::max<float>(1.0f, 0.005f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = 0.6f / std::max<float>(1.0f, 0.15f * fConst0);
		fConst4 = 1.0f / std::max<float>(1.0f, 0.25f * fConst0);
		fConst5 = 3.1415927f / fConst0;
		fConst6 = 0.25f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst7 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(5e+02f);
		fHslider1 = FAUSTFLOAT(3.0f);
		fHslider2 = FAUSTFLOAT(55.0f);
		fHslider3 = FAUSTFLOAT(0.8f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec5[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec2[l5] = 0.0f;
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
	
	virtual BassWarm* clone() {
		return new BassWarm();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("bass_warm");
		ui_interface->addHorizontalSlider("cutoff", &fHslider0, FAUSTFLOAT(5e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(1.2e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(55.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.8f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("res", &fHslider1, FAUSTFLOAT(3.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = fConst5 * float(fHslider0);
		float fSlow3 = 1.0f / float(fHslider1);
		float fSlow4 = float(fHslider2);
		float fSlow5 = std::max<float>(1.1920929e-07f, std::fabs(1.006f * fSlow4));
		float fSlow6 = fConst7 * fSlow5;
		float fSlow7 = 1.0f - fConst0 / fSlow5;
		float fSlow8 = std::max<float>(1.1920929e-07f, std::fabs(fSlow4));
		float fSlow9 = fConst7 * fSlow8;
		float fSlow10 = 1.0f - fConst0 / fSlow8;
		float fSlow11 = 0.5f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			fRec0[0] = fSlow0 + fRec0[1] * float(fVec0[1] >= fSlow0);
			float fTemp0 = fConst2 * fRec0[0];
			float fTemp1 = fConst1 - fRec0[0];
			iRec1[0] = iSlow1 * (iRec1[1] + 1);
			float fTemp2 = 1.0f - fConst4 * float(iRec1[0]);
			float fTemp3 = std::tan(fSlow2 * (0.75f * std::max<float>(0.0f, fTemp2 * std::min<float>(fTemp0, std::max<float>(fConst3 * fTemp1 + 1.0f, 0.4f))) + 0.25f));
			float fTemp4 = 1.0f / fTemp3;
			float fTemp5 = (fSlow3 + fTemp4) / fTemp3 + 1.0f;
			float fTemp6 = fSlow6 + fRec3[1] + -1.0f;
			int iTemp7 = fTemp6 < 0.0f;
			float fTemp8 = fSlow6 + fRec3[1];
			fRec3[0] = ((iTemp7) ? fTemp8 : fTemp6);
			float fRec4 = ((iTemp7) ? fTemp8 : fSlow6 + fRec3[1] + fSlow7 * fTemp6);
			float fTemp9 = fSlow9 + fRec5[1] + -1.0f;
			int iTemp10 = fTemp9 < 0.0f;
			float fTemp11 = fSlow9 + fRec5[1];
			fRec5[0] = ((iTemp10) ? fTemp11 : fTemp9);
			float fRec6 = ((iTemp10) ? fTemp11 : fSlow9 + fRec5[1] + fSlow10 * fTemp9);
			fRec2[0] = fSlow11 * (2.0f * fRec6 + -1.0f + 2.0f * fRec4 + -1.0f) * std::max<float>(0.0f, std::min<float>(fTemp0, std::max<float>(fConst6 * fTemp1 + 1.0f, 0.75f)) * fTemp2) - (fRec2[2] * ((fTemp4 - fSlow3) / fTemp3 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / BassWarm_faustpower2_f(fTemp3))) / fTemp5;
			float fTemp12 = 0.623f * ((fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) / fTemp5);
			output0[i0] = FAUSTFLOAT(fTemp12);
			output1[i0] = FAUSTFLOAT(fTemp12);
			fVec0[1] = fVec0[0];
			fRec0[1] = fRec0[0];
			iRec1[1] = iRec1[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
