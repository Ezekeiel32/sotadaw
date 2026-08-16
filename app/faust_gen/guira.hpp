/* ------------------------------------------------------------
name: "guira"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Guira -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Guira_H__
#define  __Guira_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Guira
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

static float Guira_faustpower2_f(float value) {
	return value * value;
}

class Guira : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	FAUSTFLOAT fHslider0;
	float fConst8;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst9;
	float fRec2[2];
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec3[2];
	int iRec4[2];
	float fRec1[3];
	float fRec0[3];
	float fConst10;
	float fConst12;
	float fConst14;
	float fConst16;
	float fRec5[3];
	float fConst17;
	FAUSTFLOAT fHslider3;
	
 public:
	Guira() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Guira -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "guira.dsp");
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
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "guira");
		m->declare("noises.lib/name", "Faust Noise Generator Library");
		m->declare("noises.lib/version", "1.4.0");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
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
		float fConst1 = std::tan(4712.389f / fConst0);
		float fConst2 = Guira_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = 3.1415927f / fConst0;
		fConst9 = 1.0f / fConst0;
		fConst10 = 1.0f / (fConst2 * fConst6);
		float fConst11 = std::tan(22619.467f / fConst0);
		fConst12 = 2.0f * (1.0f - 1.0f / Guira_faustpower2_f(fConst11));
		float fConst13 = 1.0f / fConst11;
		fConst14 = (fConst13 + -0.33333334f) / fConst11 + 1.0f;
		float fConst15 = (fConst13 + 0.33333334f) / fConst11 + 1.0f;
		fConst16 = 1.0f / fConst15;
		fConst17 = 1.0f / (fConst11 * fConst15);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.6f);
		fHslider1 = FAUSTFLOAT(0.5f);
		fHslider2 = FAUSTFLOAT(2.2e+02f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec2[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fVec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec3[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec4[l4] = 0;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec1[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec0[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 3; l7 = l7 + 1) {
			fRec5[l7] = 0.0f;
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
	
	virtual Guira* clone() {
		return new Guira();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("guira");
		ui_interface->addHorizontalSlider("edge", &fHslider0, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider2, FAUSTFLOAT(2.2e+02f), FAUSTFLOAT(5e+01f), FAUSTFLOAT(1.2e+03f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("ridges", &fHslider1, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = std::tan(fConst8 * (2.6e+03f * fSlow0 + 2.8e+03f));
		float fSlow2 = 2.0f * (1.0f - 1.0f / Guira_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -0.625f) / fSlow1 + 1.0f;
		float fSlow5 = (fSlow3 + 0.625f) / fSlow1 + 1.0f;
		float fSlow6 = 1.0f / fSlow5;
		float fSlow7 = float(fHslider1);
		float fSlow8 = 0.5f * fSlow7;
		float fSlow9 = float(fHslider2);
		float fSlow10 = fConst9 * (0.35f * fSlow9 + 55.0f);
		float fSlow11 = 0.55f * fSlow7 + 0.45f;
		float fSlow12 = float(fButton0);
		float fSlow13 = std::max<float>(0.0f, std::min<float>(1.0f, 0.0055555557f * (fSlow9 + -1.8e+02f)));
		float fSlow14 = std::max<float>(1.0f, fConst0 * (0.02f * fSlow13 + 0.004f));
		float fSlow15 = 1.0f / fSlow14;
		float fSlow16 = 1.0f / std::max<float>(1.0f, fConst0 * (0.16f * fSlow13 + 0.045f));
		float fSlow17 = 1.0f / (fSlow1 * fSlow5);
		float fSlow18 = fConst17 * (0.5f * fSlow0 + 0.3f);
		float fSlow19 = 0.34f * float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			float fTemp0 = ((1 - iVec0[1]) ? 0.0f : fSlow10 + fRec2[1]);
			fRec2[0] = fTemp0 - std::floor(fTemp0);
			fVec1[0] = fSlow12;
			iRec3[0] = (iRec3[1] + (iRec3[1] > 0)) * (fSlow12 <= fVec1[1]) + (fSlow12 > fVec1[1]);
			float fTemp1 = float(iRec3[0]);
			iRec4[0] = 1103515245 * iRec4[1] + 12345;
			float fTemp2 = float(iRec4[0]) * std::max<float>(0.0f, std::min<float>(fSlow15 * fTemp1, fSlow16 * (fSlow14 - fTemp1) + 1.0f));
			fRec1[0] = 4.656613e-10f * fTemp2 * (fSlow11 * float(fRec2[0] < 0.28f) + 1.0f - fSlow8) - fSlow6 * (fSlow4 * fRec1[2] + fSlow2 * fRec1[1]);
			fRec0[0] = fSlow17 * (fRec1[0] - fRec1[2]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			fRec5[0] = 4.656613e-10f * fTemp2 - fConst16 * (fConst14 * fRec5[2] + fConst12 * fRec5[1]);
			float fTemp3 = fSlow19 * (fSlow18 * (fRec5[0] - fRec5[2]) + fConst10 * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]));
			output0[i0] = FAUSTFLOAT(fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp3);
			iVec0[1] = iVec0[0];
			fRec2[1] = fRec2[0];
			fVec1[1] = fVec1[0];
			iRec3[1] = iRec3[0];
			iRec4[1] = iRec4[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
