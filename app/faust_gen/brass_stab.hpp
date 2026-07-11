/* ------------------------------------------------------------
name: "brass_stab"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn BrassStab -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __BrassStab_H__
#define  __BrassStab_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS BrassStab
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

static float BrassStab_faustpower2_f(float value) {
	return value * value;
}

class BrassStab : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fRec1[2];
	float fConst3;
	float fConst4;
	float fConst5;
	FAUSTFLOAT fHslider0;
	float fConst6;
	float fConst7;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst8;
	FAUSTFLOAT fHslider3;
	float fConst9;
	float fRec3[2];
	float fRec5[2];
	float fRec7[2];
	FAUSTFLOAT fHslider4;
	float fRec2[3];
	
 public:
	BrassStab() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn BrassStab -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/asr:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "brass_stab.dsp");
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
		m->declare("name", "brass_stab");
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
		float fConst1 = std::max<float>(1.0f, 0.1f * fConst0);
		fConst2 = 1.0f / fConst1;
		fConst3 = std::max<float>(1.0f, 0.004f * fConst0);
		fConst4 = 1.0f / fConst3;
		fConst5 = 0.65f / fConst1;
		fConst6 = 3.1415927f / fConst0;
		fConst7 = 1.0f / std::max<float>(1.0f, 0.12f * fConst0);
		fConst8 = 1.0f / std::max<float>(1.0f, 0.05f * fConst0);
		fConst9 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.7f);
		fHslider1 = FAUSTFLOAT(0.012f);
		fHslider2 = FAUSTFLOAT(0.25f);
		fHslider3 = FAUSTFLOAT(2.2e+02f);
		fHslider4 = FAUSTFLOAT(0.6f);
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
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec5[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec7[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec2[l6] = 0.0f;
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
	
	virtual BrassStab* clone() {
		return new BrassStab();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("brass_stab");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.012f), FAUSTFLOAT(0.002f), FAUSTFLOAT(0.2f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bite", &fHslider0, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(0.25f), FAUSTFLOAT(0.05f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider3, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider4, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = 5.2e+03f * float(fHslider0) + 1.2e+03f;
		float fSlow3 = std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow4 = 1.0f / fSlow3;
		float fSlow5 = 0.38f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow6 = float(fHslider3);
		float fSlow7 = 1.006f * fSlow6;
		float fSlow8 = 0.5f * fSlow6;
		float fSlow9 = 0.42553192f * float(fHslider4);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec0[1] >= fSlow0);
			float fTemp1 = std::tan(fConst6 * (fSlow2 * std::max<float>(0.0f, std::min<float>(fConst4 * fRec1[0], std::max<float>(fConst5 * (fConst3 - fRec1[0]) + 1.0f, 0.35f)) * (1.0f - fConst2 * fTemp0)) + 5e+02f));
			float fTemp2 = 1.0f / fTemp1;
			float fTemp3 = (fTemp2 + 0.71428573f) / fTemp1 + 1.0f;
			float fTemp4 = 0.03f * std::max<float>(0.0f, std::min<float>(fConst8 * fRec1[0], 1.0f) - fConst8 * fTemp0) + 0.97f;
			float fTemp5 = std::max<float>(1.1920929e-07f, std::fabs(fSlow7 * fTemp4));
			float fTemp6 = fRec3[1] + fConst9 * fTemp5;
			float fTemp7 = fTemp6 + -1.0f;
			int iTemp8 = fTemp7 < 0.0f;
			fRec3[0] = ((iTemp8) ? fTemp6 : fTemp7);
			float fRec4 = ((iTemp8) ? fTemp6 : fTemp6 + fTemp7 * (1.0f - fConst0 / fTemp5));
			float fTemp9 = std::max<float>(1.1920929e-07f, std::fabs(fSlow6 * fTemp4));
			float fTemp10 = fRec5[1] + fConst9 * fTemp9;
			float fTemp11 = fTemp10 + -1.0f;
			int iTemp12 = fTemp11 < 0.0f;
			fRec5[0] = ((iTemp12) ? fTemp10 : fTemp11);
			float fRec6 = ((iTemp12) ? fTemp10 : fTemp10 + fTemp11 * (1.0f - fConst0 / fTemp9));
			float fTemp13 = std::max<float>(1.1920929e-07f, std::fabs(fSlow8 * fTemp4));
			float fTemp14 = fRec7[1] + fConst9 * fTemp13;
			float fTemp15 = fTemp14 + -1.0f;
			int iTemp16 = fTemp15 < 0.0f;
			fRec7[0] = ((iTemp16) ? fTemp14 : fTemp15);
			float fRec8 = ((iTemp16) ? fTemp14 : fTemp14 + fTemp15 * (1.0f - fConst0 / fTemp13));
			fRec2[0] = fSlow9 * (0.35f * (2.0f * fRec8 + -1.0f) - 2.0f * (1.0f - (fRec6 + fRec4))) * std::max<float>(0.0f, std::min<float>(fSlow4 * fRec1[0], std::max<float>(fSlow5 * (fSlow3 - fRec1[0]) + 1.0f, 0.62f)) * (1.0f - fConst7 * fTemp0)) - (fRec2[2] * ((fTemp2 + -0.71428573f) / fTemp1 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / BrassStab_faustpower2_f(fTemp1))) / fTemp3;
			float fTemp17 = 0.91f * ((fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) / fTemp3);
			output0[i0] = FAUSTFLOAT(fTemp17);
			output1[i0] = FAUSTFLOAT(fTemp17);
			fVec0[1] = fVec0[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
