/* ------------------------------------------------------------
name: "cowbell"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Cowbell -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Cowbell_H__
#define  __Cowbell_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Cowbell
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

static float Cowbell_faustpower2_f(float value) {
	return value * value;
}

class Cowbell : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iVec1[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fConst4;
	float fConst6;
	float fConst8;
	float fConst9;
	float fRec2[2];
	float fConst10;
	float fRec3[2];
	float fRec1[3];
	FAUSTFLOAT fHslider1;
	float fConst11;
	
 public:
	Cowbell() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Cowbell -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "cowbell.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
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
		m->declare("name", "cowbell");
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
		fConst1 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst2 = 1.0f / fConst1;
		float fConst3 = std::tan(3769.9111f / fConst0);
		fConst4 = 2.0f * (1.0f - 1.0f / Cowbell_faustpower2_f(fConst3));
		float fConst5 = 1.0f / fConst3;
		fConst6 = (fConst5 + -0.33333334f) / fConst3 + 1.0f;
		float fConst7 = (fConst5 + 0.33333334f) / fConst3 + 1.0f;
		fConst8 = 1.0f / fConst7;
		fConst9 = 587.0f / fConst0;
		fConst10 = 845.0f / fConst0;
		fConst11 = 0.5f / (fConst3 * fConst7);
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.11f);
		fHslider1 = FAUSTFLOAT(0.65f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iVec1[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec0[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 3; l5 = l5 + 1) {
			fRec1[l5] = 0.0f;
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
	
	virtual Cowbell* clone() {
		return new Cowbell();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("cowbell");
		ui_interface->addHorizontalSlider("decay", &fHslider0, FAUSTFLOAT(0.11f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider1, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow2 = fConst11 * float(fHslider1);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iVec1[0] = 1;
			iRec0[0] = (iRec0[1] + (iRec0[1] > 0)) * (fSlow0 <= fVec0[1]) + (fSlow0 > fVec0[1]);
			float fTemp0 = float(iRec0[0]);
			int iTemp1 = 1 - iVec1[1];
			float fTemp2 = ((iTemp1) ? 0.0f : fConst9 + fRec2[1]);
			fRec2[0] = fTemp2 - std::floor(fTemp2);
			float fTemp3 = ((iTemp1) ? 0.0f : fConst10 + fRec3[1]);
			fRec3[0] = fTemp3 - std::floor(fTemp3);
			fRec1[0] = float(fRec3[0] < 0.5f) + float(fRec2[0] < 0.5f) + (-1.0f - fConst8 * (fConst6 * fRec1[2] + fConst4 * fRec1[1]));
			float fTemp4 = fSlow2 * (fRec1[0] - fRec1[2]) * std::max<float>(0.0f, std::min<float>(fConst2 * fTemp0, fSlow1 * (fConst1 - fTemp0) + 1.0f));
			output0[i0] = FAUSTFLOAT(fTemp4);
			output1[i0] = FAUSTFLOAT(fTemp4);
			fVec0[1] = fVec0[0];
			iVec1[1] = iVec1[0];
			iRec0[1] = iRec0[0];
			fRec2[1] = fRec2[0];
			fRec3[1] = fRec3[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
		}
	}

};

#endif
